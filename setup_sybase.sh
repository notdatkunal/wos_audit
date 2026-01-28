#!/usr/bin/env bash
set -e

# =========================
# CONFIG (edit if needed)
# =========================
CONTAINER_NAME="sybase-ase"
SYBASE_SERVER="MYSYBASE"
SA_USER="sa"
SA_PASS="StrongPassword123"

DB_NAME="auditdb"
APP_LOGIN="audit_user"
APP_PASS="Audit@123"
APP_USER="audit_user"

WAIT_SECONDS=120

# =========================
# FUNCTIONS
# =========================
log() {
  echo "[SYBASE] $1"
}

die() {
  echo "[ERROR] $1" >&2
  exit 1
}

# =========================
# CHECKS
# =========================
command -v docker >/dev/null 2>&1 || die "Docker not found"

docker inspect "$CONTAINER_NAME" >/dev/null 2>&1 \
  || die "Container $CONTAINER_NAME not found"

# =========================
# START CONTAINER
# =========================
log "Starting container if not running..."
docker start "$CONTAINER_NAME" >/dev/null 2>&1 || true

# =========================
# WAIT FOR SYBASE
# =========================
log "Waiting for Sybase to be ready..."
SECONDS=0
until docker exec "$CONTAINER_NAME" bash -c \
  "source /opt/sybase/SYBASE.sh && isql -U$SA_USER -P$SA_PASS -S$SYBASE_SERVER -b -Q 'select 1'" \
  >/dev/null 2>&1
do
  sleep 5
  if [ $SECONDS -gt $WAIT_SECONDS ]; then
    die "Sybase did not start within $WAIT_SECONDS seconds"
  fi
done

log "Sybase is ready"

# =========================
# SQL SETUP
# =========================
log "Creating database, login, and user..."

docker exec "$CONTAINER_NAME" bash -c "
source /opt/sybase/SYBASE.sh
isql -U$SA_USER -P$SA_PASS -S$SYBASE_SERVER <<'SQL'
if not exists (select 1 from sysdatabases where name = '$DB_NAME')
begin
  create database $DB_NAME
end
go

if not exists (select 1 from syslogins where name = '$APP_LOGIN')
begin
  sp_addlogin '$APP_LOGIN', '$APP_PASS'
end
go

use $DB_NAME
go

if not exists (select 1 from sysusers where name = '$APP_USER')
begin
  sp_adduser '$APP_LOGIN', '$APP_USER'
end
go

grant all to $APP_USER
go
SQL
"

log "Setup complete 🎉"

# =========================
# DONE
# =========================
log "Database: $DB_NAME"
log "Login: $APP_LOGIN"
log "User: $APP_USER"
