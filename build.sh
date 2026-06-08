#!/bin/bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
pip install -r requirements.txt
python manage.py collectstatic --no-input
