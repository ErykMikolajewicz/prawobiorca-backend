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


def main():
    run_container_if_not_running(
        "postgres_db_prawobiorca",
        "-e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432"
        " -v pg-data:/var/lib/postgresql pgvector:0.8.4-pg18-trixie",
    )

    run_container_if_not_running(
        "rustfs",
        "-p 127.0.0.1:9000:9000 -p 127.0.0.1:9001:9001 -v rustfs-data:/data rustfs/rustfs:latest",
    )

    run_container_if_not_running("embedding-service", "-p 127.0.0.1:8081:8080 embedding-service")
    run_container_if_not_running("extraction-service", "-p 127.0.0.1:8082:8080 extraction-service")
    run_container_if_not_running("redis", "-p 127.0.0.1:6379:6379 redis:8-alpine")

    subprocess.run(
        [
            "granian",
            "--port",
            "8000",
            "--host",
            "127.0.0.1",
            "--interface",
            "asgi",
            "--reload",
            "--access-log",
            "main:prawobiorca",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
