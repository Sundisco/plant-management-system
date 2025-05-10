#!/bin/bash
set -e  # Exit on error

# Change to the backend directory
cd "$(dirname "$0")"

# Parse DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
DB_URL=${DATABASE_URL#postgresql://}
DB_USER=${DB_URL%%:*}
DB_PASS=${DB_URL#*:}
DB_PASS=${DB_PASS%%@*}
DB_HOST=${DB_URL#*@}
DB_HOST=${DB_HOST%%/*}
DB_NAME=${DB_URL#*/}

# Reset alembic_version table using direct SQL
echo "Resetting alembic_version table..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f reset_alembic.sql

# Run the migrations
echo "Running database migrations..."
alembic upgrade new_head 