source config/relational_db.env

podman run -d --name postgres-prawobiorca \
  -e POSTGRES_PASSWORD="$PASSWORD" -e POSTGRES_USER="$DB_USER" -e POSTGRES_DB="$DB_NAME" \
  -p "$PORT":5432 -v postgres-prawobiorca:/var/lib/postgresql/data:Z \
  postgres:latest