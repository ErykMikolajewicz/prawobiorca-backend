podman pod create --name prawobiorca-backend-pod -p 8000:8000
podman run -d --pod prawobiorca-backend-pod --name prawobiorca-backend-container prawobiorca-backend-dev
podman run -d --pod prawobiorca-backend-pod --name postgres-prawobiorca-db -e POSTGRES_PASSWORD=password postgres:latest
podman run -d --pod prawobiorca-backend-pod --name qdrant-prawobiorca-db qdrant/qdrant:latest