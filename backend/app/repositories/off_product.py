"""
Repozytorium Open Food Facts — wyszukiwanie w MongoDB + Meilisearch.
"""
from app.external_db import off_collection, meili_products


class OFFProductRepository:

    async def get_by_barcode(self, code: str) -> dict | None:
        """Zwraca pełny dokument produktu po kodzie EAN."""
        return await off_collection.find_one({"code": code}, {"_id": 0})

    async def search_by_name(
        self,
        query: str,
        lang: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Wyszukuje produkty po nazwie przez Meilisearch.
        Zwraca kompletne dokumenty z MongoDB (Meilisearch daje tylko lekkie pola).
        """
        search_params: dict = {
            "limit": limit,
            "offset": offset,
        }
        if lang:
            search_params["filter"] = f'lang = "{lang}"'

        results = meili_products.search(query, search_params)
        hits = results.get("hits", [])
        if not hits:
            return []

        # Pobierz pełne dane z MongoDB zachowując kolejność z Meilisearch
        codes = [h["code"] for h in hits if "code" in h]
        if not codes:
            return []

        products_map = {
            p["code"]: p
            async for p in off_collection.find(
                {"code": {"$in": codes}}, {"_id": 0}
            )
        }

        return [products_map[code] for code in codes if code in products_map]
