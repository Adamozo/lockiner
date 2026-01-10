#!/usr/bin/env python3
"""
Generate vouchers for user registration.

This script creates vouchers and inserts them into the database,
then exports them to a CSV file.

Usage:
    docker compose exec backend python /app/scripts/generate_vouchers.py
"""

import asyncio
import csv
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone

import sys
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Voucher, Base


# Number of vouchers to generate
NUM_VOUCHERS = 100

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://scrooge:scrooge_secret@postgres:5432/scrooge_db")

# Output CSV file path (mounted volume)
CSV_OUTPUT_PATH = Path("/app/scripts/vouchers.csv")


def generate_voucher_code() -> str:
    """Generate a unique voucher code (UUID format)."""
    return str(uuid.uuid4())


async def main():
    """Generate vouchers and save to database and CSV."""
    print(f"Generating {NUM_VOUCHERS} vouchers...")
    print(f"Using DATABASE_URL: {DATABASE_URL[:50]}...")

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Generate vouchers
    vouchers_data = []
    async with async_session() as session:
        for i in range(NUM_VOUCHERS):
            code = generate_voucher_code()
            voucher = Voucher(
                code=code,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            session.add(voucher)
            vouchers_data.append({
                'code': code,
                'created_at': voucher.created_at
            })

        await session.commit()
        print(f"✓ Inserted {NUM_VOUCHERS} vouchers into database")

    # Export to CSV (both in container and mapped to host)
    with open(CSV_OUTPUT_PATH, 'w', newline='') as csvfile:
        fieldnames = ['code', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for voucher in vouchers_data:
            writer.writerow(voucher)

    print(f"✓ Exported vouchers to {CSV_OUTPUT_PATH}")
    print(f"\nDone! Generated {NUM_VOUCHERS} vouchers.")

    # Print first few voucher codes as sample
    print("\nSample voucher codes:")
    for i, v in enumerate(vouchers_data[:5]):
        print(f"  {i+1}. {v['code']}")
    print("  ...")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
