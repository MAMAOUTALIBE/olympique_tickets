#!/bin/sh
set -e

DB_HOST=${DB_HOST:-postgres}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
DB_ENGINE=${DB_ENGINE:-postgresql}

wait_for_db() {
  if [ "$DB_ENGINE" = "postgresql" ] || [ "$DB_ENGINE" = "postgres" ]; then
    until PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
      echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
      sleep 2
    done
  elif [ "$DB_ENGINE" = "mariadb" ] || [ "$DB_ENGINE" = "mysql" ]; then
    until mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --password="$DB_PASSWORD" --silent; do
      echo "Waiting for MariaDB/MySQL at $DB_HOST:$DB_PORT..."
      sleep 2
    done
  fi
}

wait_for_db

python manage.py migrate --noinput

if [ "${DISABLE_COLLECTSTATIC}" != "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
