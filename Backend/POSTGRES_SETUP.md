# PostgreSQL Database Setup for Public Services Backend

## Overview

The backend now supports **optional PostgreSQL integration**. If PostgreSQL is not available, the application gracefully falls back to **file-based JSON storage** (existing behavior).

## Quick Start (PostgreSQL Optional)

### Without PostgreSQL (File-Based Storage — Default)

If PostgreSQL is not set up, the backend automatically uses local JSON files in `data/`:

```bash
cd Backend
pip install -r requirements.txt
python server.py
```

The server will print:
```
⚠️  Database initialization skipped: (psycopg2.OperationalError) ...
```

This is normal. The API will work with file-based storage.

### With PostgreSQL (Full Database Setup)

#### Step 1: Install PostgreSQL

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run the installer and follow the wizard
- Remember the superuser password

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Step 2: Create Database and User

Connect to PostgreSQL and run:

```sql
-- Connect as superuser
psql -U postgres

-- Create database
CREATE DATABASE public_services;

-- Create user (if not exists)
CREATE USER postgres WITH PASSWORD 'postgres';

-- Grant privileges
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET default_transaction_deferrable TO on;
ALTER ROLE postgres SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE public_services TO postgres;

-- Exit
\q
```

#### Step 3: Update `.env` Configuration

Modify `Backend/.env` to match your PostgreSQL setup:

```env
PORT=8888
JWT_SECRET=your-super-secret-jwt-key-change-in-production-1299069306
JWT_EXPIRES_IN=7d
FLASK_ENV=development

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=public_services
DB_USER=postgres
DB_PASSWORD=postgres
```

#### Step 4: Run the Backend

```bash
cd Backend
pip install -r requirements.txt
python server.py
```

The server will print:
```
✅ PostgreSQL database initialized
```

Alternatively, manually initialize the database:
```bash
python scripts/init_db.py
```

## Troubleshooting

### Error: `FATAL: password authentication failed for user "postgres"`

- Verify PostgreSQL is running
- Check `.env` credentials match your setup
- Reset PostgreSQL password:
  ```bash
  # macOS/Linux
  sudo -u postgres psql
  ALTER USER postgres WITH PASSWORD 'postgres';
  ```

### Error: `FATAL: database "public_services" does not exist`

Run this to create the database:
```bash
psql -U postgres -c "CREATE DATABASE public_services;"
```

### Server runs but shows "⚠️  Database initialization skipped"

This is **expected and safe** — the backend is using file-based storage. PostgreSQL is optional.

## Architecture

- **File-based storage** (default): Uses `models/user.py`, `models/application.py`, etc. that read/write from `data/*.json`
- **PostgreSQL** (optional): Uses SQLAlchemy models for database persistence

Models in `models/db.py` are prepared for SQLAlchemy but not yet integrated into routes.

## Future Enhancements

To migrate routes to PostgreSQL models:

1. Create new SQLAlchemy model classes in `models/` (e.g., `models/user_db.py`)
2. Update routes (`routes/*.py`) to import and use database models
3. Migrate data from JSON to database (create migration script)

For now, all routes use file-based JSON storage and work without PostgreSQL.

## Connection Details

- **Host:** `localhost` (default from `.env`)
- **Port:** `5432` (PostgreSQL default)
- **Database:** `public_services`
- **User:** `postgres`
- **Connection pool:** Pre-ping enabled, recyclable after 1 hour

See `models/db.py` for SQLAlchemy configuration.
