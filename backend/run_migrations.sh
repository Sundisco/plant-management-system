#!/bin/bash
set -e  # Exit on error

# Change to the backend directory
cd "$(dirname "$0")"

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Reset alembic_version table using direct SQL
echo "Resetting alembic_version table..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f reset_alembic.sql

# Run the migrations
echo "Running database migrations..."
alembic upgrade new_head 