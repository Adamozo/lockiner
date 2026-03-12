"""
Wzbogaca istniejące dokumenty OFF o pole `search_text` i reindeksuje Meilisearch.

Uruchom po import_off.py:
    docker run --rm --network lockiner_lockiner-network \
      -e MONGODB_URL=mongodb://lockiner-mongodb:27017 \
      -e MONGODB_DB=lockiner_food \
      -e MEILI_URL=http://lockiner-meilisearch:7700 \
      -e MEILI_MASTER_KEY=lockiner_meili_secret_key_min16chars \
      lockiner-backend python -m scripts.enrich_off_search
"""
import asyncio
import os
import re
from motor.motor_asyncio import AsyncIOMotorClient
import meilisearch

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "lockiner_food")
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "")

MEILI_BATCH = 5000
MONGO_BATCH = 5000


def normalize_tag(tag: str) -> str:
    """'pl:pierogi-ruskie' → 'pierogi ruskie', 'en:plant-based-foods' → 'plant based foods'"""
    # Usuń prefix języka (pl:, en:, fr:, itd.)
    tag = re.sub(r'^[a-z]{2}:', '', tag)
    # Zamień myślniki na spacje
    return tag.replace('-', ' ').strip()


def build_search_text(doc: dict) -> str:
    """
    Buduje pole do wyszukiwania łącząc:
    - nazwy produktu (PL, EN, oryginalna)
    - marki
    - znormalizowane tagi kategorii (bez prefiksu języka)
    """
    parts = []

    for field in ('product_name_pl', 'product_name_en', 'product_name'):
        val = doc.get(field)
        if val and val.strip():
            parts.append(val.strip())

    brands = doc.get('brands')
    if brands:
        parts.append(brands.strip())

    for tag in (doc.get('categories_tags') or []):
        normalized = normalize_tag(tag)
        if normalized and len(normalized) > 2:
            parts.append(normalized)

    # Deduplikuj zachowując kolejność
    seen = set()
    unique = []
    for p in parts:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return ' | '.join(unique)


async def enrich_mongodb(client: AsyncIOMotorClient) -> int:
    """Dodaje pole search_text do każdego dokumentu w MongoDB."""
    collection = client[MONGODB_DB]["off_products"]
    total = 0
    bulk_ops = []

    from pymongo import UpdateOne

    async for doc in collection.find({}, {"_id": 1, "product_name": 1, "product_name_pl": 1,
                                         "product_name_en": 1, "brands": 1, "categories_tags": 1}):
        search_text = build_search_text(doc)
        bulk_ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"search_text": search_text}}))

        if len(bulk_ops) >= MONGO_BATCH:
            await collection.bulk_write(bulk_ops, ordered=False)
            total += len(bulk_ops)
            print(f"  MongoDB enriched: {total:,}")
            bulk_ops = []

    if bulk_ops:
        await collection.bulk_write(bulk_ops, ordered=False)
        total += len(bulk_ops)

    print(f"MongoDB enrichment done: {total:,} dokumentów")
    return total


def update_meilisearch_settings(meili: meilisearch.Client):
    """Dodaje search_text do searchable attributes."""
    index = meili.index("products")
    index.update_settings({
        "searchableAttributes": [
            "search_text",        # NOWE — zawiera wszystko
            "product_name",
            "product_name_pl",
            "product_name_en",
            "brands",
            "code",
        ],
        "filterableAttributes": ["lang", "nutriscore_grade", "countries_tags", "nova_group"],
        "sortableAttributes": ["nutriscore_grade"],
        "displayedAttributes": [
            "code", "product_name", "product_name_pl", "brands",
            "nutriscore_grade", "image_url", "lang", "calories",
            "protein", "carbohydrates", "fat", "search_text",
        ],
    })
    print("Meilisearch settings updated")


async def reindex_meilisearch(client: AsyncIOMotorClient, meili: meilisearch.Client):
    """Re-indeksuje wszystkie dokumenty z nowym polem search_text."""
    collection = client[MONGODB_DB]["off_products"]
    index = meili.index("products")

    batch = []
    total = 0

    async for doc in collection.find(
        {"product_name": {"$ne": None}},
        {"code": 1, "product_name": 1, "product_name_pl": 1, "brands": 1,
         "nutriscore_grade": 1, "lang": 1, "image_url": 1, "calories": 1,
         "protein": 1, "carbohydrates": 1, "fat": 1, "search_text": 1, "_id": 0}
    ):
        doc["id"] = doc["code"]
        batch.append(doc)

        if len(batch) >= MEILI_BATCH:
            index.add_documents(batch)
            total += len(batch)
            batch = []
            if total % 500_000 == 0:
                print(f"  Meilisearch: {total:,} dokumentów")

    if batch:
        index.add_documents(batch)
        total += len(batch)

    print(f"Meilisearch reindex done: {total:,} dokumentów (indeksowanie trwa w tle)")


async def main():
    mongo = AsyncIOMotorClient(MONGODB_URL)
    meili = meilisearch.Client(MEILI_URL, MEILI_MASTER_KEY)

    print("=== Krok 1: Wzbogacanie MongoDB o search_text ===")
    await enrich_mongodb(mongo)

    print("\n=== Krok 2: Aktualizacja ustawień Meilisearch ===")
    update_meilisearch_settings(meili)

    print("\n=== Krok 3: Re-indeksowanie Meilisearch ===")
    await reindex_meilisearch(mongo, meili)

    mongo.close()
    print("\nGotowe!")


if __name__ == "__main__":
    asyncio.run(main())
