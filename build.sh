#!/bin/bash
echo "Building project..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear

if [ -n "$DATABASE_URL" ]; then
  echo "Running migrations..."
  python3 manage.py migrate --noinput
else
  echo "DATABASE_URL not set. Skipping migrations."
fi
