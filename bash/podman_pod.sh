podman pod create --name prawobiorca-backend-pod -p 8000:8000
podman run -d --pod prawobiorca-backend-pod --name prawobiorca-backend-app prawobiorca-backend-dev
podman run -d --pod prawobiorca-backend-pod --name postgres-prawobiorca -e POSTGRES_PASSWORD=password postgres:latest
podman run -d --pod prawobiorca-backend-pod --name qdrant-prawobiorca qdrant/qdrant:latest
podman run -d --pod prawobiorca-backend-pod --name redis-prawobiorca redis:latest
