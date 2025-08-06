#!/bin/sh

# Run Alembic migrations (log errors but do not exit on failure)
echo "Running Alembic migrations..."
alembic upgrade head || echo "Alembic migration failed, continuing anyway. Check logs."

# Start the FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 80 