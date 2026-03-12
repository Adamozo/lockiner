"""
Klienty dla zewnętrznych baz danych: MongoDB (katalog OFF) i Meilisearch (wyszukiwanie).
"""
from motor.motor_asyncio import AsyncIOMotorClient
import meilisearch
from app.config import get_settings

settings = get_settings()

mongo_client = AsyncIOMotorClient(settings.mongodb_url)
mongo_db = mongo_client[settings.mongodb_db]
off_collection = mongo_db["off_products"]

meili_client = meilisearch.Client(settings.meili_url, settings.meili_master_key)
meili_products = meili_client.index("products")
