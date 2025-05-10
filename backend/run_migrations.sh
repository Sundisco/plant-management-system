#!/bin/bash

# Run the alembic version fix script
echo "Fixing alembic version table..."
python fix_alembic.py

# Run the migrations
echo "Running database migrations..."
alembic upgrade head 