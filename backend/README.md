# LockIner Backend

FastAPI backend with SQLite database for personal finance management.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── database.py           # SQLAlchemy engine and session
│   ├── models.py             # ORM models (Transaction, Receipt, Category, MonthlyImport)
│   ├── schemas.py            # Pydantic schemas for validation
│   ├── init_db.py            # Database initialization script
│   └── main.py               # FastAPI application
├── data/
│   └── scrooge.db            # SQLite database (created on init)
├── uploads/                  # Uploaded receipt images
├── requirements.txt          # Python dependencies
└── Dockerfile                # Docker configuration
```

## Database Schema

### Tables

1. **transactions** - Financial transactions from bank statements
   - `id`, `date`, `amount`, `description`, `category`, `receipt_id`, `notes`, `created_at`

2. **receipts** - Scanned receipts with OCR data
   - `id`, `image_path`, `scan_date`, `merchant`, `total`, `items_json`, `raw_ocr_response`, `verified`, `created_at`

3. **categories** - Expense categories with budgets
   - `id`, `name`, `budget_limit`, `icon`, `color`

4. **monthly_imports** - Import history tracking
   - `id`, `month`, `filename`, `transactions_count`, `imported_at`

### Default Categories

The database is seeded with 8 Polish expense categories:

| Name      | Icon | Color   |
|-----------|------|---------|
| Jedzenie  | 🍔   | #FF6B6B |
| Transport | 🚗   | #4ECDC4 |
| Zakupy    | 🛒   | #95E1D3 |
| Rachunki  | 💡   | #F38181 |
| Rozrywka  | 🎮   | #AA96DA |
| Zdrowie   | 💊   | #FCBAD3 |
| Dom       | 🏠   | #A8D8EA |
| Inne      | 📦   | #C7CEEA |

## Getting Started

### Using Docker (Recommended)

```bash
# Start backend container
docker compose up backend

# Initialize database
docker exec -it scrooge-backend python -m app.init_db

# Or via API endpoint
curl -X POST http://localhost:8000/init-db
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="sqlite:///./data/scrooge.db"

# Initialize database
python -m app.init_db

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Operations

### Initialize Database

```bash
# Safe initialization (won't drop existing tables)
python -m app.init_db

# Reset database (WARNING: deletes all data!)
python -m app.init_db --reset

# Verify database structure
python -m app.init_db --verify
```

### Interactive SQL Shell

```bash
# Using Docker
docker exec -it scrooge-backend sqlite3 /data/scrooge.db

# SQLite commands
.tables                     # List all tables
.schema transactions        # Show table schema
SELECT * FROM categories;   # Query data
.quit                       # Exit
```

### Backup & Restore

```bash
# Backup database
docker cp scrooge-backend:/data/scrooge.db ./backups/scrooge_$(date +%Y%m%d).db

# Restore database
docker cp ./backups/scrooge_20240110.db scrooge-backend:/data/scrooge.db
```

## API Endpoints

### Health Check

```bash
GET /                  # Root endpoint
GET /health            # Health check
GET /db-status         # Database statistics
```

### Database Management

```bash
POST /init-db          # Initialize database (dev only)
POST /init-db?reset=true  # Reset database (DANGEROUS!)
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

```bash
DATABASE_URL=sqlite:////data/scrooge.db  # Database path (Docker)
# or
DATABASE_URL=sqlite:///./data/scrooge.db  # Database path (local)
```

## Common Queries

### Get Transactions for Month

```sql
SELECT * FROM transactions
WHERE strftime('%Y-%m', date) = '2024-01'
ORDER BY date DESC;
```

### Spending by Category

```sql
SELECT
  category,
  COUNT(*) as count,
  SUM(ABS(amount)) as total,
  AVG(ABS(amount)) as average
FROM transactions
WHERE amount < 0
  AND strftime('%Y-%m', date) = '2024-01'
GROUP BY category
ORDER BY total DESC;
```

### Transactions with Receipts

```sql
SELECT
  t.id,
  t.date,
  t.amount,
  t.description,
  r.merchant,
  r.image_path
FROM transactions t
LEFT JOIN receipts r ON t.receipt_id = r.id
WHERE t.receipt_id IS NOT NULL
ORDER BY t.date DESC;
```

## SQLAlchemy Models

All models are defined in `app/models.py`:

- **Transaction** - Financial transactions
- **Receipt** - Scanned receipts with OCR
- **Category** - Expense categories
- **MonthlyImport** - Import history

Foreign key constraints are enabled automatically.

## Pydantic Schemas

All request/response schemas are in `app/schemas.py`:

- Transaction schemas: `TransactionCreate`, `TransactionUpdate`, `TransactionResponse`
- Receipt schemas: `ReceiptCreate`, `ReceiptUpdate`, `ReceiptResponse`
- Category schemas: `CategoryCreate`, `CategoryUpdate`, `CategoryResponse`
- Analytics schemas: `MonthSummary`, `CategorySpending`

## Testing

```bash
# Run tests (once implemented)
pytest

# Check database status via API
curl http://localhost:8000/db-status
```

## Notes

- SQLite database is stored in `/data/scrooge.db` (Docker volume)
- Uses TEXT for dates (ISO 8601 format: YYYY-MM-DD)
- Foreign keys are enabled automatically
- WAL mode enabled for better concurrency
- Indexes on frequently queried columns (`date`, `category`, `merchant`)

## Next Steps

1. Implement API routers:
   - `routers/transactions.py` - Transaction CRUD operations
   - `routers/receipts.py` - Receipt upload and OCR
   - `routers/categories.py` - Category management
   - `routers/analytics.py` - Statistics and reporting
   - `routers/import_csv.py` - CSV import functionality

2. Add authentication (if needed for multi-user)

3. Implement receipt OCR service using Claude API

4. Add CSV parser for bank statement import

5. Create analytics queries for spending insights
