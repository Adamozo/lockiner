"""Generic backup export service.

Scans all SQLAlchemy mapped classes to discover personal data automatically,
then exports user + household data into an AES-256 encrypted ZIP.
"""

import io
import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Tables that should NEVER appear in a backup export
EXCLUDED_TABLES = {
    "users",
    "vouchers",
    "backup_settings",
    "household_backup_settings",
    "food_categories",
    "food_products",
    "food_product_aliases",
    "notifications",           # global admin-created notifications
    "alembic_version",
}


# ---------------------------------------------------------------------------
# Internal helpers — SQLAlchemy mapper scanning
# ---------------------------------------------------------------------------

def _get_mapper_registry():
    """Return the global SQLAlchemy mapper registry."""
    from ..database import Base
    return Base.registry.mappers


def _row_to_dict(obj) -> dict[str, Any]:
    """Convert a SQLAlchemy model instance to a plain dict."""
    insp = inspect(obj)
    return {col.key: getattr(obj, col.key) for col in insp.mapper.column_attrs}


def _get_direct_user_tables() -> dict[str, type]:
    """
    All mapped classes that have a direct FK column named user_id pointing to users.id,
    excluding EXCLUDED_TABLES.
    Returns {table_name: model_class}.
    """
    result = {}
    for mapper in _get_mapper_registry():
        cls = mapper.class_
        table = mapper.local_table
        if table.name in EXCLUDED_TABLES:
            continue
        for col in table.columns:
            for fk in col.foreign_keys:
                if fk.column.table.name == "users" and col.name == "user_id":
                    result[table.name] = cls
                    break
    return result


def _get_child_tables(parent_table_names: set[str]) -> dict[str, tuple[type, str, str]]:
    """
    Find mapped classes whose FK references any table in parent_table_names
    (but are NOT themselves direct user tables, and NOT in EXCLUDED_TABLES).

    Returns {child_table_name: (cls, fk_col_name, parent_table_name)}
    """
    result = {}
    for mapper in _get_mapper_registry():
        cls = mapper.class_
        table = mapper.local_table
        if table.name in EXCLUDED_TABLES:
            continue
        if table.name in parent_table_names:
            continue
        for col in table.columns:
            for fk in col.foreign_keys:
                if fk.column.table.name in parent_table_names:
                    result[table.name] = (cls, col.name, fk.column.table.name)
                    break
    return result


# ---------------------------------------------------------------------------
# Personal data export
# ---------------------------------------------------------------------------

async def _fetch_rows(db: AsyncSession, cls: type, filter_col: str, filter_val: Any) -> list[dict]:
    """Fetch all rows of `cls` where `filter_col == filter_val`."""
    col_attr = getattr(cls, filter_col, None)
    if col_attr is None:
        return []
    result = await db.execute(select(cls).where(col_attr == filter_val))
    return [_row_to_dict(obj) for obj in result.scalars().all()]


async def _fetch_rows_in(db: AsyncSession, cls: type, filter_col: str, filter_vals: list[Any]) -> list[dict]:
    """Fetch all rows of `cls` where `filter_col IN filter_vals`."""
    if not filter_vals:
        return []
    col_attr = getattr(cls, filter_col, None)
    if col_attr is None:
        return []
    result = await db.execute(select(cls).where(col_attr.in_(filter_vals)))
    return [_row_to_dict(obj) for obj in result.scalars().all()]


# Junction tables that act as ownership links: the junction table name maps to
# (fk_col_in_junction pointing to entity, entity_model_name, entity_table_name)
_JUNCTION_TABLE_MAP = {
    "user_transactions":    ("transaction_id", "Transaction",    "transactions"),
    "user_receipts":        ("receipt_id",     "Receipt",        "receipts"),
    "user_categories":      ("category_id",    "Category",       "categories"),
    "user_budget_settings": ("budget_settings_id", "BudgetSettings", "budget_settings"),
}

_HOUSEHOLD_JUNCTION_TABLE_MAP = {
    "household_transactions":    ("transaction_id", "Transaction",    "transactions"),
    "household_receipts":        ("receipt_id",     "Receipt",        "receipts"),
    "household_categories":      ("category_id",    "Category",       "categories"),
    "household_budget_settings": ("budget_settings_id", "BudgetSettings", "budget_settings"),
}


def _get_model_class(table_name: str) -> type | None:
    """Return the mapped class for a table name."""
    for mapper in _get_mapper_registry():
        if mapper.local_table.name == table_name:
            return mapper.class_
    return None


async def export_personal_data(db: AsyncSession, user_id: int) -> dict[str, list[dict]]:
    """
    Level 1: all tables with direct user_id FK → users.id
    Level 2: children of level-1 tables (e.g. exercises → workouts)
    Level 3: grandchildren (e.g. exercise_sets → exercises)
    Also resolves junction tables to their actual entity rows.
    """
    data: dict[str, list[dict]] = {}

    # ── Level 1: direct user tables ──────────────────────────────────────────
    direct = _get_direct_user_tables()
    level1_ids: dict[str, list[int]] = {}  # table_name → list of PKs

    for table_name, cls in direct.items():
        rows = await _fetch_rows(db, cls, "user_id", user_id)
        data[table_name] = rows
        level1_ids[table_name] = [r["id"] for r in rows if "id" in r]

        # Resolve junction → actual entity
        if table_name in _JUNCTION_TABLE_MAP:
            fk_col, _entity_name, entity_table = _JUNCTION_TABLE_MAP[table_name]
            entity_ids = [r[fk_col] for r in rows if fk_col in r]
            if entity_ids:
                entity_cls = _get_model_class(entity_table)
                if entity_cls:
                    entity_rows = await _fetch_rows_in(db, entity_cls, "id", entity_ids)
                    data.setdefault(entity_table, [])
                    # Deduplicate by id
                    existing_ids = {r["id"] for r in data[entity_table]}
                    data[entity_table].extend(r for r in entity_rows if r["id"] not in existing_ids)

    # ── Level 2: children of level-1 tables ──────────────────────────────────
    level2_tables = _get_child_tables(set(level1_ids.keys()))
    level2_ids: dict[str, list[int]] = {}

    for child_table, (child_cls, fk_col, parent_table) in level2_tables.items():
        parent_ids = level1_ids.get(parent_table, [])
        rows = await _fetch_rows_in(db, child_cls, fk_col, parent_ids)
        data[child_table] = rows
        level2_ids[child_table] = [r["id"] for r in rows if "id" in r]

    # ── Level 3: grandchildren of level-2 tables ──────────────────────────────
    level3_tables = _get_child_tables(set(level2_ids.keys()))

    for child_table, (child_cls, fk_col, parent_table) in level3_tables.items():
        if child_table in data:
            continue  # already handled
        parent_ids = level2_ids.get(parent_table, [])
        rows = await _fetch_rows_in(db, child_cls, fk_col, parent_ids)
        data[child_table] = rows

    return data


# ---------------------------------------------------------------------------
# Household data export
# ---------------------------------------------------------------------------

async def export_household_data(db: AsyncSession, household_id: int) -> dict[str, list[dict]]:
    """
    Export all data belonging to a specific household.
    """
    data: dict[str, list[dict]] = {}

    # Household entity itself
    from ..models import Household
    hh_rows = await _fetch_rows(db, Household, "id", household_id)
    data["households"] = hh_rows

    # Household members
    from ..models import HouseholdMember
    data["household_members"] = await _fetch_rows(db, HouseholdMember, "household_id", household_id)

    # Junction tables → actual entities
    for junction_table, (fk_col, _entity_name, entity_table) in _HOUSEHOLD_JUNCTION_TABLE_MAP.items():
        junction_cls = _get_model_class(junction_table)
        if not junction_cls:
            continue
        junction_rows = await _fetch_rows(db, junction_cls, "household_id", household_id)
        data[junction_table] = junction_rows

        entity_ids = [r[fk_col] for r in junction_rows if fk_col in r]
        if entity_ids:
            entity_cls = _get_model_class(entity_table)
            if entity_cls:
                entity_rows = await _fetch_rows_in(db, entity_cls, "id", entity_ids)
                data.setdefault(entity_table, [])
                existing_ids = {r["id"] for r in data[entity_table]}
                data[entity_table].extend(r for r in entity_rows if r["id"] not in existing_ids)

    # Food inventory for this household
    from ..models import FoodInventory
    data["food_inventory"] = await _fetch_rows(db, FoodInventory, "household_id", household_id)

    # Food pending imports for this household
    from ..models import FoodPendingImport
    pending = await _fetch_rows(db, FoodPendingImport, "household_id", household_id)
    data["food_pending_imports"] = pending

    # Food pending import items
    from ..models import FoodPendingImportItem
    pending_ids = [r["id"] for r in pending if "id" in r]
    data["food_pending_import_items"] = await _fetch_rows_in(
        db, FoodPendingImportItem, "pending_import_id", pending_ids
    )

    return data


# ---------------------------------------------------------------------------
# Full user backup (personal + all households)
# ---------------------------------------------------------------------------

async def export_full_user_data(db: AsyncSession, user_id: int) -> dict[str, list[dict]]:
    """Combine personal data + data for all households the user belongs to."""
    from ..models import HouseholdMember

    data = await export_personal_data(db, user_id)

    result = await db.execute(
        select(HouseholdMember).where(
            HouseholdMember.user_id == user_id,
            HouseholdMember.status == "active",
        )
    )
    memberships = result.scalars().all()

    for membership in memberships:
        hh_data = await export_household_data(db, membership.household_id)
        for table_name, rows in hh_data.items():
            key = f"household_{membership.household_id}_{table_name}"
            data[key] = rows

    return data


# ---------------------------------------------------------------------------
# ZIP builder
# ---------------------------------------------------------------------------

def build_zip(data: dict, password: str) -> bytes:
    """Build an AES-256 encrypted ZIP containing data.json."""
    try:
        import pyzipper
    except ImportError:
        raise RuntimeError(
            "pyzipper is required for encrypted backup. "
            "Install it with: pip install pyzipper"
        )

    payload = {
        "metadata": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "app": "LockIner",
            "version": "1.0",
        },
        "data": data,
    }

    buf = io.BytesIO()
    with pyzipper.AESZipFile(
        buf,
        "w",
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES,
    ) as zf:
        zf.setpassword(password.encode())
        zf.writestr(
            "data.json",
            json.dumps(payload, default=str, ensure_ascii=False, indent=2),
        )
    return buf.getvalue()
