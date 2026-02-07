#!/bin/sh
set -e

# Ensure upload dir exists and is owned by appuser
mkdir -p "${UPLOAD_DIR:-/data/uploads}"

# If running as root, fix ownership so non-root can write
if [ "$(id -u)" = "0" ]; then
  chown -R appuser:appuser "${UPLOAD_DIR:-/data/uploads}"
fi

# Drop to appuser and run app
exec su appuser -c "python app.py"