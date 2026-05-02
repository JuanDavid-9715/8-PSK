#!/usr/bin/env bash
# Build script para Render.com

set -o errexit

pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input