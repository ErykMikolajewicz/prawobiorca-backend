import subprocess


def image_exists(name: str) -> bool:
    result = subprocess.run(["podman", "image", "exists", name])
    return result.returncode == 0


def main():
    if not image_exists("localhost/prawobiorca-backend:latest") and not image_exists("prawobiorca-backend:latest"):
        print("Building prawobiorca-backend image...")
        subprocess.run(["podman", "image", "build", "--tag=prawobiorca-backend", "."], check=True)

    if not image_exists("localhost/embedding-service:latest") and not image_exists("embedding-service:latest"):
        print("Building embedding-service image...")
        subprocess.run(
            ["podman", "image", "build", "--tag=embedding-service", "embedding-service"],
            check=True,
        )

    if not image_exists("localhost/extraction-service:latest") and not image_exists("extraction-service:latest"):
        print("Building extraction-service image...")
        subprocess.run(
            ["podman", "image", "build", "--tag=extraction-service", "extraction-service"],
            check=True,
        )

    if not image_exists("localhost/prawobiorca-frontend:latest") and not image_exists("prawobiorca-frontend:latest"):
        print("Warning: prawobiorca-frontend:latest image not found. Frontend may not respond until built.")

    subprocess.run(["podman", "network", "create", "--ignore", "prawobiorca-net"], check=True)

    print("Deploying local environment with podman play kube...")
    subprocess.run(
        ["podman", "play", "kube", "--network", "prawobiorca-net", "cicd/k8s/local/local-deployment.yaml"],
        check=True,
    )
    print("\nLocal deployment is running.")
    print("Nginx Ingress available at http://localhost:8080")
    print("  - Frontend: http://localhost:8080/")
    print("  - API:      http://localhost:8080/api")
    print("  - Docs:     http://localhost:8080/docs")
    print("  - OpenAPI:  http://localhost:8080/openapi.json")
    print("  - Storage:  http://localhost:8080/storage/")
    print("\nTo stop the deployment run: poe run_locally_down")


if __name__ == "__main__":
    main()
