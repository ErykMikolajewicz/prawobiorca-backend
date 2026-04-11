import subprocess


def run_command(cmd):
    return subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)


def container_exists(name):
    result = run_command('podman ps -a --format "{{.Names}}"')
    return name in result.stdout.splitlines()


def container_running(name):
    result = run_command('podman ps --format "{{.Names}}"')
    return name in result.stdout.splitlines()


def run_container_if_not_running(name, args):
    if container_exists(name):
        if container_running(name):
            print(f"Container {name} is already running - pass.")
        else:
            print(f"Container {name} already exists, but not running, launching.")
            subprocess.run(["podman", "start", name], check=True)
    else:
        print(f"Create and launch container {name}.")
        cmd = f"podman run -d --name {name} {args}"
        subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    run_container_if_not_running(
        "postgres_db_prawobiorca",
        "-e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432 -v pg_data:/var/lib/postgresql postgres:18",
    )

    run_container_if_not_running(
        "qdrant_db_prawobiorca",
        "-p 127.0.0.1:6333:6333 -p 127.0.0.1:6334:6334 -v qdrant_data:/qdrant/storage qdrant/qdrant:latest",
    )

    run_container_if_not_running("text_transformator", "-p 127.0.0.1:8080:8080 text_transformator")

    subprocess.run(
        [
            "granian",
            "--port",
            "8000",
            "--host",
            "127.0.0.1",
            "--interface",
            "asgi",
            "--ssl-certificate",
            "certificate.crt",
            "--ssl-keyfile",
            "private.key",
            "--reload",
            "--access-log",
            "main:prawobiorca",
        ],
        check=True,
    )
