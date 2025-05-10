#!/bin/bash
set -e  # Exit on error

# Change to the backend directory
cd "$(dirname "$0")"

# Make sure the script is executable
chmod +x fix_alembic.py

# Run the alembic version fix script
echo "Fixing alembic version table..."
python3 fix_alembic.py

# Run the migrations
echo "Running database migrations..."
alembic upgrade reset_migrations
alembic upgrade head 