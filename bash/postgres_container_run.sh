source .env

podman run -d --name postgres-prawobiorca \
  -e POSTGRES_PASSWORD="$RELATIONAL_DB_PASSWORD" -e POSTGRES_USER="$RELATIONAL_DB_USER" \
  -e POSTGRES_DB="$RELATIONAL_DB_NAME" -p "$RELATIONAL_DB_PORT":5432 -v \
  postgres-prawobiorca:/var/lib/postgresql postgres:18