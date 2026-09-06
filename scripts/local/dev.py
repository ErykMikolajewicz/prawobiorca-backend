import os
import signal
import subprocess

RUSTFS_CORS_ALLOWED_ORIGINS = "http://localhost:4173,http://localhost:5173,http://localhost:8080"
WORKER_SHUTDOWN_TIMEOUT = 3


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


def run_worker():
    print("Launching taskiq worker.")
    # Own session, so Ctrl+C in the terminal does not reach the worker - stop_worker owns its lifecycle.
    return subprocess.Popen(
        ["taskiq", "worker", "src.framework.workers.regulations:broker", "--reload", "--reload-dir", "src"],
        start_new_session=True,
    )


def stop_worker(worker):
    print("Stopping taskiq worker.")
    # The whole group, because taskiq leaves worker and forkserver children behind.
    process_group = os.getpgid(worker.pid)
    os.killpg(process_group, signal.SIGTERM)
    try:
        worker.wait(timeout=WORKER_SHUTDOWN_TIMEOUT)
    except subprocess.TimeoutExpired:
        os.killpg(process_group, signal.SIGKILL)
        worker.wait()


def main():
    run_container_if_not_running(
        "postgres_db_prawobiorca",
        "-e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432"
        " -v pg-data:/var/lib/postgresql pgvector:0.8.4-pg18-trixie",
    )

    run_container_if_not_running(
        "rustfs",
        f"-e RUSTFS_CORS_ALLOWED_ORIGINS={RUSTFS_CORS_ALLOWED_ORIGINS}"
        " -p 127.0.0.1:9000:9000 -p 127.0.0.1:9001:9001 -v rustfs-data:/data rustfs/rustfs:latest",
    )

    run_container_if_not_running("embedding-service", "-p 127.0.0.1:8081:8080 embedding-service")
    run_container_if_not_running("extraction-service", "-p 127.0.0.1:8082:8080 extraction-service")
    run_container_if_not_running("redis", "-p 127.0.0.1:6379:6379 redis:8-alpine")

    worker = run_worker()
    try:
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
                "src.main:prawobiorca",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        pass
    finally:
        stop_worker(worker)


if __name__ == "__main__":
    main()
