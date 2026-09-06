import subprocess
from pathlib import Path

from manifests import MANIFESTS

IGNORED_DIRS = {".venv", "__pycache__"}

IMAGES = (
    ("prawobiorca-backend", ".", ("Containerfile", "pyproject.toml", "uv.lock", "main.py", "app")),
    ("embedding-service", "embedding-service", ("embedding-service",)),
    ("extraction-service", "extraction-service", ("extraction-service",)),
)


def image_created_at(name: str) -> float | None:
    result = subprocess.run(
        ["podman", "image", "inspect", name, "--format", "{{.Created.Unix}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return float(result.stdout.strip())


def newest_source_change(sources: tuple[str, ...]) -> float:
    newest = 0.0
    for source in sources:
        path = Path(source)
        if path.is_file():
            newest = max(newest, path.stat().st_mtime)
            continue
        for entry in path.rglob("*"):
            if IGNORED_DIRS & set(entry.parts) or not entry.is_file():
                continue
            newest = max(newest, entry.stat().st_mtime)
    return newest


def build_images():
    for name, context, sources in IMAGES:
        created_at = image_created_at(f"localhost/{name}:latest") or image_created_at(f"{name}:latest")
        if created_at is None:
            print(f"Building {name} image...")
        elif newest_source_change(sources) > created_at:
            print(f"Sources changed since {name} image was built, rebuilding...")
        else:
            continue
        subprocess.run(["podman", "image", "build", f"--tag={name}", context], check=True)

    if image_created_at("localhost/prawobiorca-frontend:latest") is None:
        print("Warning: prawobiorca-frontend:latest image not found. Frontend may not respond until built.")


def main():
    build_images()

    subprocess.run(["podman", "network", "create", "--ignore", "prawobiorca-net"], check=True)

    print("Deploying local environment with podman kube play...")
    for manifest, configmaps in MANIFESTS:
        print(f"Applying {manifest.name}...")
        command = ["podman", "kube", "play", "--replace", "--network", "prawobiorca-net"]
        for configmap in configmaps:
            command += ["--configmap", str(configmap)]
        command.append(str(manifest))
        subprocess.run(command, check=True)

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
