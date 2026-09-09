"""Common pytest fixtures for integration tests.

These fixtures handle container initialization of the embedding service.
"""

import os
import subprocess
from typing import Generator

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import HttpWaitStrategy

from tests.consts import EMBEDDING_SERVICE_IMAGE_TAG, EMBEDDING_SERVICE_PORT, STARTUP_TIMEOUT


@pytest.fixture(scope="session", autouse=True)
def configure_podman():
    subprocess.run(["systemctl", "--user", "enable", "--now", "podman.socket"])

    uid = os.getuid()
    podman_sock = f"unix:///run/user/{uid}/podman/podman.sock"

    os.environ["DOCKER_HOST"] = podman_sock


@pytest.fixture(scope="session")
def embedding_service_container() -> Generator[DockerContainer, None, None]:
    wait_strategy = HttpWaitStrategy(
        EMBEDDING_SERVICE_PORT,
        "/health",
    ).with_startup_timeout(STARTUP_TIMEOUT)

    with (
        DockerContainer(EMBEDDING_SERVICE_IMAGE_TAG)
        .with_exposed_ports(EMBEDDING_SERVICE_PORT)
        .waiting_for(wait_strategy)
    ) as embedding_service:
        yield embedding_service
