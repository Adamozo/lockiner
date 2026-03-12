"""
Jednorazowy import Open Food Facts → MongoDB + Meilisearch.

Uruchom z katalogu /app wewnątrz kontenera backend:
    python -m scripts.import_off /ścieżka/do/openfoodfacts-products.jsonl.gz

Lub lokalnie (poza Dockerem):
    python -m scripts.import_off ./openfoodfacts-products.jsonl.gz

Plik JSONL do pobrania (~9GB skompresowany):
    https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz
"""
import asyncio
import gzip
import json
import sys
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
import meilisearch

BATCH_SIZE = 1000
MEILI_BATCH_SIZE = 5000

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB = "lockiner_food"
MEILI_URL = "http://localhost:7700"
MEILI_MASTER_KEY = "lockiner_meili_secret_key_min16chars"

# Nadpisz jeśli uruchamiasz wewnątrz kontenera Docker
import os
MONGODB_URL = os.getenv("MONGODB_URL", MONGODB_URL)
MONGODB_DB = os.getenv("MONGODB_DB", MONGODB_DB)
MEILI_URL = os.getenv("MEILI_URL", MEILI_URL)
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", MEILI_MASTER_KEY)


def _extract_doc(p: dict) -> dict | None:
    code = p.get("code", "").strip()
    if not code:
        return None

    product_name = p.get("product_name") or p.get("product_name_en") or p.get("product_name_pl")
    if not product_name:
        return None

    nutriments = p.get("nutriments", {})

    return {
        "code": code,
        "product_name": product_name.strip(),
        "product_name_pl": p.get("product_name_pl"),
        "product_name_en": p.get("product_name_en"),
        "brands": p.get("brands"),
        "quantity": p.get("quantity"),
        "serving_size": p.get("serving_size"),
        "ingredients_text": p.get("ingredients_text"),
        "ingredients_text_pl": p.get("ingredients_text_pl"),
        "nutriscore_grade": p.get("nutriscore_grade"),
        "nova_group": p.get("nova_group"),
        "ecoscore_grade": p.get("ecoscore_grade"),
        "lang": p.get("lang"),
        "countries_tags": p.get("countries_tags", []),
        "categories_tags": p.get("categories_tags", []),
        "labels_tags": p.get("labels_tags", []),
        "image_url": p.get("image_front_small_url") or p.get("image_small_url"),
        "image_url_full": p.get("image_front_url"),
        # Wartości odżywcze na 100g
        "calories": nutriments.get("energy-kcal_100g"),
        "protein": nutriments.get("proteins_100g"),
        "carbohydrates": nutriments.get("carbohydrates_100g"),
        "fat": nutriments.get("fat_100g"),
        "fiber": nutriments.get("fiber_100g"),
        "sugar": nutriments.get("sugars_100g"),
        "sodium": nutriments.get("sodium_100g"),
        "salt": nutriments.get("salt_100g"),
        "saturated_fat": nutriments.get("saturated-fat_100g"),
    }


async def import_to_mongo(path: Path) -> int:
    client = AsyncIOMotorClient(MONGODB_URL)
    collection = client[MONGODB_DB]["off_products"]

    print("Tworzę indeksy MongoDB...")
    await collection.create_index("code", unique=True, sparse=True)
    await collection.create_index("product_name")
    await collection.create_index("lang")
    await collection.create_index("countries_tags")

    batch, total, skipped = [], 0, 0
    opener = gzip.open if str(path).endswith(".gz") else open

    print(f"Importuję z: {path}")
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                p = json.loads(line)
                doc = _extract_doc(p)
                if doc is None:
                    skipped += 1
                    continue
                batch.append(doc)

                if len(batch) >= BATCH_SIZE:
                    try:
                        await collection.insert_many(batch, ordered=False)
                    except Exception:
                        # Ignoruj duplikaty (upsert nie jest potrzebny przy pierwszym imporcie)
                        pass
                    total += len(batch)
                    batch = []
                    if total % 100_000 == 0:
                        print(f"  MongoDB: {total:,} produktów (pominięto: {skipped:,})")
            except (json.JSONDecodeError, Exception):
                skipped += 1
                continue

    if batch:
        try:
            await collection.insert_many(batch, ordered=False)
        except Exception:
            pass
        total += len(batch)

    client.close()
    print(f"MongoDB gotowe: {total:,} produktów (pominięto: {skipped:,})")
    return total


def index_meilisearch():
    print("Konfiguruję Meilisearch...")
    client = meilisearch.Client(MEILI_URL, MEILI_MASTER_KEY)
    index = client.index("products")

    index.update_settings({
        "searchableAttributes": ["product_name", "product_name_pl", "product_name_en", "brands", "code"],
        "filterableAttributes": ["lang", "nutriscore_grade", "countries_tags", "nova_group"],
        "sortableAttributes": ["nutriscore_grade"],
        "displayedAttributes": ["code", "product_name", "product_name_pl", "brands",
                                "nutriscore_grade", "image_url", "lang", "calories",
                                "protein", "carbohydrates", "fat"],
        "rankingRules": [
            "words", "typo", "proximity", "attribute", "sort", "exactness"
        ],
    })

    print("Indeksuję produkty w Meilisearch (może trwać dłużej)...")

    async def fetch_and_send():
        mongo = AsyncIOMotorClient(MONGODB_URL)
        collection = mongo[MONGODB_DB]["off_products"]

        batch = []
        total = 0
        async for doc in collection.find(
            {"product_name": {"$ne": None}},
            {"code": 1, "product_name": 1, "product_name_pl": 1, "brands": 1,
             "nutriscore_grade": 1, "lang": 1, "image_url": 1, "calories": 1,
             "protein": 1, "carbohydrates": 1, "fat": 1, "_id": 0}
        ):
            doc["id"] = doc["code"]
            batch.append(doc)
            if len(batch) >= MEILI_BATCH_SIZE:
                index.add_documents(batch)
                total += len(batch)
                batch = []
                if total % 500_000 == 0:
                    print(f"  Meilisearch: {total:,} dokumentów")

        if batch:
            index.add_documents(batch)
            total += len(batch)

        mongo.close()
        print(f"Meilisearch: wysłano {total:,} dokumentów (indeksowanie trwa w tle)")

    asyncio.run(fetch_and_send())


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openfoodfacts-products.jsonl.gz")

    if not path.exists():
        print(f"BŁĄD: Plik nie istnieje: {path}")
        print()
        print("Pobierz plik OFF:")
        print("  wget https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz")
        sys.exit(1)

    asyncio.run(import_to_mongo(path))
    index_meilisearch()
