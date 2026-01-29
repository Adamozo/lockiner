#!/usr/bin/env python3
"""
Database initialization script for LockIner.

This script creates all tables and seeds initial data (categories).
Run this script once to initialize the database.

Usage:
    python -m app.init_db

    Or via API endpoint:
    curl -X POST http://localhost:8000/init-db
"""

import sys
from sqlalchemy import text

from .database import SessionLocal
from .models import Category, Transaction, Receipt, MonthlyImport, BudgetSettings, FoodCategory


def init_database():
    """
    Seed initial data.

    Tables are managed by Alembic migrations (alembic upgrade head).
    This function only handles data seeding.
    """

    print("=" * 60)
    print("LockIner Database Seeding")
    print("=" * 60)

    # Seed categories
    seed_categories()

    # Seed food categories
    seed_food_categories()

    print("\n" + "=" * 60)
    print("Database seeding completed successfully!")
    print("=" * 60)


def seed_categories():
    """
    Seed default expense categories.

    Categories are based on typical Polish expense categories with
    emoji icons and color codes for UI visualization.
    """

    db = SessionLocal()

    try:
        # Check if categories already exist
        existing_count = db.query(Category).count()
        if existing_count > 0:
            print(f"\nCategories already exist ({existing_count} found). Skipping seed.")
            return

        print("\nSeeding default categories...")

        default_categories = [
            {
                "name": "Jedzenie",
                "icon": "🍔",
                "color": "#FF6B6B",
                "budget_limit": None,
            },
            {
                "name": "Transport",
                "icon": "🚗",
                "color": "#4ECDC4",
                "budget_limit": None,
            },
            {
                "name": "Zakupy",
                "icon": "🛒",
                "color": "#95E1D3",
                "budget_limit": None,
            },
            {
                "name": "Rachunki",
                "icon": "💡",
                "color": "#F38181",
                "budget_limit": None,
            },
            {
                "name": "Rozrywka",
                "icon": "🎮",
                "color": "#AA96DA",
                "budget_limit": None,
            },
            {
                "name": "Zdrowie",
                "icon": "💊",
                "color": "#FCBAD3",
                "budget_limit": None,
            },
            {
                "name": "Dom",
                "icon": "🏠",
                "color": "#A8D8EA",
                "budget_limit": None,
            },
            {
                "name": "Inne",
                "icon": "📦",
                "color": "#C7CEEA",
                "budget_limit": None,
            },
        ]

        for cat_data in default_categories:
            category = Category(**cat_data)
            db.add(category)
            print(f"  + {cat_data['icon']} {cat_data['name']} ({cat_data['color']})")

        db.commit()
        print(f"\nSuccessfully seeded {len(default_categories)} categories.")

    except Exception as e:
        db.rollback()
        print(f"\nError seeding categories: {str(e)}")
        raise

    finally:
        db.close()


def seed_food_categories():
    """
    Seed default food categories.

    Categories for food products with default expiry days and storage tips.
    """

    db = SessionLocal()

    try:
        # Check if food categories already exist
        existing_count = db.query(FoodCategory).count()
        if existing_count > 0:
            print(f"\nFood categories already exist ({existing_count} found). Skipping seed.")
            return

        print("\nSeeding default food categories...")

        default_food_categories = [
            {
                "name": "Nabial",
                "icon": "milk",
                "color": "#3B82F6",
                "default_expiry_days": 7,
                "storage_tips": "Przechowuj w lodowce w temperaturze 2-6C. Sprawdz date waznosci przed uzyciem.",
            },
            {
                "name": "Mieso",
                "icon": "beef",
                "color": "#EF4444",
                "default_expiry_days": 3,
                "storage_tips": "Swieze mieso przechowuj w lodowce do 3 dni lub zamroz. Po rozmrozeniu zuzyj w ciagu 24h.",
            },
            {
                "name": "Warzywa",
                "icon": "carrot",
                "color": "#22C55E",
                "default_expiry_days": 7,
                "storage_tips": "Wiekszos warzyw przechowuj w lodowce. Ziemniaki i cebule w ciemnym, suchym miejscu.",
            },
            {
                "name": "Owoce",
                "icon": "apple",
                "color": "#F97316",
                "default_expiry_days": 5,
                "storage_tips": "Niektore owoce (banany, jablka) dojrzewaja w temperaturze pokojowej. Jagody przechowuj w lodowce.",
            },
            {
                "name": "Pieczywo",
                "icon": "sandwich",
                "color": "#EAB308",
                "default_expiry_days": 4,
                "storage_tips": "Przechowuj w temperaturze pokojowej lub zamroz. Unikaj lodowki - przyspiesza czerstwienie.",
            },
            {
                "name": "Mrozonki",
                "icon": "snowflake",
                "color": "#06B6D4",
                "default_expiry_days": 90,
                "storage_tips": "Przechowuj w zamrazarce w temp. -18C lub nizszej. Nie zamrazaj ponownie rozmrozonej zywnosci.",
            },
            {
                "name": "Konserwy",
                "icon": "package",
                "color": "#8B5CF6",
                "default_expiry_days": 365,
                "storage_tips": "Przechowuj w suchym, chlodnym miejscu. Po otwarciu przechowuj w lodowce i zuzyj w ciagu kilku dni.",
            },
            {
                "name": "Napoje",
                "icon": "glass-water",
                "color": "#EC4899",
                "default_expiry_days": 30,
                "storage_tips": "Nieotwarte napoje przechowuj w temperaturze pokojowej. Po otwarciu wiekszos w lodowce.",
            },
            {
                "name": "Slodycze",
                "icon": "cookie",
                "color": "#78350F",
                "default_expiry_days": 180,
                "storage_tips": "Przechowuj w suchym, chlodnym miejscu z dala od swiatla. Czekolade chron przed wysokimi temperaturami.",
            },
            {
                "name": "Przyprawy",
                "icon": "flame",
                "color": "#737373",
                "default_expiry_days": 365,
                "storage_tips": "Przechowuj w szczelnych pojemnikach z dala od swiatla i wilgoci. Mielone traca aromat szybciej.",
            },
            {
                "name": "Ryby",
                "icon": "fish",
                "color": "#0EA5E9",
                "default_expiry_days": 2,
                "storage_tips": "Swieze ryby przechowuj w lodowce max 2 dni. Najlepiej zamrozic jesli nie zuzyjesz od razu.",
            },
            {
                "name": "Jaja",
                "icon": "egg",
                "color": "#FBBF24",
                "default_expiry_days": 28,
                "storage_tips": "Przechowuj w lodowce ostrzejszym koncem w dol. Sprawdz swiezosc przed uzyciem.",
            },
        ]

        for cat_data in default_food_categories:
            category = FoodCategory(**cat_data)
            db.add(category)
            print(f"  + {cat_data['name']} (expiry: {cat_data['default_expiry_days']} days)")

        db.commit()
        print(f"\nSuccessfully seeded {len(default_food_categories)} food categories.")

    except Exception as e:
        db.rollback()
        print(f"\nError seeding food categories: {str(e)}")
        raise

    finally:
        db.close()


def verify_database():
    """
    Verify database structure and contents.

    Prints table information and row counts.
    """

    print("\nVerifying database structure...")

    db = SessionLocal()

    try:
        # Check table existence and row counts
        tables = [
            ("transactions", Transaction),
            ("receipts", Receipt),
            ("categories", Category),
            ("monthly_imports", MonthlyImport),
            ("budget_settings", BudgetSettings),
            ("food_categories", FoodCategory),
        ]

        print("\nTable status:")
        print("-" * 50)

        for table_name, model in tables:
            count = db.query(model).count()
            print(f"  {table_name:20s} - {count:5d} rows")

        print("-" * 50)

        # List all categories
        categories = db.query(Category).all()
        if categories:
            print("\nAvailable categories:")
            for cat in categories:
                budget_info = f"(budget: {cat.budget_limit})" if cat.budget_limit else ""
                print(f"  {cat.icon} {cat.name:15s} {cat.color:10s} {budget_info}")

    except Exception as e:
        print(f"\nError verifying database: {str(e)}")
        raise

    finally:
        db.close()


def reset_database():
    """
    Reset database by re-seeding data.

    NOTE: Table management is handled by Alembic migrations.
    Use 'alembic downgrade base' + 'alembic upgrade head' to recreate tables.
    """

    print("\n" + "!" * 60)
    print("WARNING: To reset tables, use Alembic migrations:")
    print("  alembic downgrade base")
    print("  alembic upgrade head")
    print("!" * 60)

    init_database()
    verify_database()


if __name__ == "__main__":
    """
    Command-line interface for database initialization.

    Usage:
        python -m app.init_db          # Initialize database (safe, won't drop)
        python -m app.init_db --reset  # Reset database (DANGEROUS!)
        python -m app.init_db --verify # Verify database structure
    """

    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            reset_database()
        elif sys.argv[1] == "--verify":
            verify_database()
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        init_database()
        verify_database()
