#!/bin/sh
set -e

mkdir -p /app/media/categories /app/staticfiles
chown -R webuser:webuser /app/media /app/staticfiles 2>/dev/null || true
chmod -R 755 /app/media 2>/dev/null || true

exec "$@"

