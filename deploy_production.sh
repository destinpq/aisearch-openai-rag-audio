#!/usr/bin/env bash
# Safe production deploy script for this repo.
# Usage: review and run `./deploy_production.sh` from the repo root.

set -euo pipefail

# Defaults
RESTART_SERVICE=""
BACKUP_KEEP=5

usage() {
  echo "Usage: $0 [--restart <service-name>] [--no-backup]"
  echo "       $0 --target <frontend|frontend-next>"
  echo "  --restart <service-name>   Restart the named systemd/pm2 service after deploy"
  echo "  --no-backup                Skip creating a timestamped backup of backend/static"
  exit 1
}

# Parse args
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      shift
      TARGET="$1"
      shift
      ;;
    --restart)
      shift
      RESTART_SERVICE="$1"
      shift
      ;;
    --no-backup)
      NO_BACKUP=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_STATIC_DIR="$ROOT_DIR/backend/static"

echo "[deploy] Starting safe deploy from $ROOT_DIR"

if [ "${TARGET-}" = "frontend-next" ]; then
  SRC_PROJECT_DIR="$ROOT_DIR/frontend-next"
else
  SRC_PROJECT_DIR="$FRONTEND_DIR"
fi

if [ ! -d "$SRC_PROJECT_DIR" ]; then
  echo "[deploy] Source project directory not found: $SRC_PROJECT_DIR"
  exit 1
fi

echo "[deploy] Installing frontend dependencies (npm ci)"
(cd "$SRC_PROJECT_DIR" && npm ci)

echo "[deploy] Building frontend production bundle for $SRC_PROJECT_DIR"
(cd "$SRC_PROJECT_DIR" && npm run build)

DIST_DIR=""
if [ "${TARGET-}" = "frontend-next" ]; then
  # Next.js outputs to .next and optionally can be exported; we'll prefer a static export if present
  if [ -d "$SRC_PROJECT_DIR/out" ]; then
    DIST_DIR="$SRC_PROJECT_DIR/out"
  else
    # If not exported, copy the .next static assets instead (not ideal). We'll use out if available.
    DIST_DIR="$SRC_PROJECT_DIR/.next"
  fi
else
  DIST_DIR="$FRONTEND_DIR/dist"
fi
SRC_DIR=""
if [ -d "$DIST_DIR" ]; then
  SRC_DIR="$DIST_DIR"
else
  # Some Vite configs output directly to backend/static (observed). If so, use that.
  if [ -d "$BACKEND_STATIC_DIR" ] && [ -f "$BACKEND_STATIC_DIR/index.html" ]; then
    echo "[deploy] Build appears to have written directly to $BACKEND_STATIC_DIR"
    SRC_DIR="$BACKEND_STATIC_DIR"
  else
    echo "[deploy] Expected build output not found at $DIST_DIR and no files in $BACKEND_STATIC_DIR"
    exit 1
  fi
fi

echo "[deploy] Preparing backend static directory: $BACKEND_STATIC_DIR"
mkdir -p "$BACKEND_STATIC_DIR"
if [ "$SRC_DIR" = "$BACKEND_STATIC_DIR" ]; then
  echo "[deploy] Build output already in backend static directory; no copy needed."
else
  echo "[deploy] Creating backup of existing backend static (unless --no-backup)"
  if [ -z "${NO_BACKUP-}" ]; then
    TS=$(date -u +"%Y%m%dT%H%M%SZ")
    BACKUP_DIR="$ROOT_DIR/backups/static.$TS"
    echo "[deploy] Backing up $BACKEND_STATIC_DIR -> $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    cp -a "$BACKEND_STATIC_DIR/." "$BACKUP_DIR/" || true
    # prune old backups
    if command -v ls >/dev/null 2>&1; then
      ls -1dt "$ROOT_DIR/backups/static."* 2>/dev/null | tail -n +$((BACKUP_KEEP+1)) | xargs -r rm -rf || true
    fi
  else
    echo "[deploy] --no-backup specified; skipping backup"
  fi

  echo "[deploy] Copying frontend build to backend static directory"
  rm -rf "$BACKEND_STATIC_DIR"/*
  cp -r "$SRC_DIR"/* "$BACKEND_STATIC_DIR/"
  echo "[deploy] Deploy files copied."
fi

echo "[deploy] Next steps (manual):"
echo "  - Verify static files in $BACKEND_STATIC_DIR"
echo "  - Restart backend process if needed (examples commented below)"

if [ -n "$RESTART_SERVICE" ]; then
  echo "[deploy] Restart requested for service: $RESTART_SERVICE"
  if command -v systemctl >/dev/null 2>&1; then
    echo "[deploy] Restarting systemd service: $RESTART_SERVICE"
    sudo systemctl restart "$RESTART_SERVICE"
  elif command -v pm2 >/dev/null 2>&1; then
    echo "[deploy] Restarting pm2 process: $RESTART_SERVICE"
    pm2 restart "$RESTART_SERVICE" || true
  else
    echo "[deploy] No supported service manager found (systemctl or pm2). Manual restart required."
  fi
else
  echo "[deploy] No restart requested. To restart automatically, re-run with --restart <service-name>"
  echo "# Examples you can run manually:" 
  echo "# sudo systemctl restart converse-backend"
  echo "# pm2 restart ecosystem.config.js --only converse-backend"
  echo "# (cd /path/to/backend && ./start.sh)"
fi

echo "[deploy] Done."
