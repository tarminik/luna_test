#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
migrated=false
for i in $(seq 1 30); do
    if alembic upgrade head; then
        echo "Migrations applied."
        migrated=true
        break
    fi
    echo "  attempt $i — PostgreSQL not ready, retrying in 1s..."
    sleep 1
done

if [ "$migrated" != true ]; then
    echo "ERROR: Failed to apply migrations after 30 attempts."
    exit 1
fi

python -m app.seed

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
