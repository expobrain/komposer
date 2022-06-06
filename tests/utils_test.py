import textwrap
from pathlib import Path

import pytest

from komposer.core.base import parse_docker_compose_file
from komposer.types.docker_compose import DockerCompose, Service
from komposer.utils import to_kubernetes_name


@pytest.mark.parametrize(
    "compose_content, expected",
    [
        pytest.param(
            textwrap.dedent(
                """
                services:
                    my_service:
                        image: my-docker-hub/my-image:latest
                        ports:
                        - "8080:8080"
                        command: ./scripts/my-script.sh
                        env_file: .env.dockercompose
            """
            ),
            DockerCompose(
                services={
                    "my_service": Service(
                        image="my-docker-hub/my-image:latest",
                        ports=["8080:8080"],
                        command="./scripts/my-script.sh",
                        env_file=Path(".env.dockercompose"),
                    )
                }
            ),
            id="Single service with image+ports+env_file",
        ),
        pytest.param(
            textwrap.dedent(
                """
                services:
                    my_service:
                        image: my-docker-hub/my-image:latest
                        ports:
                        - "8080:8080"
                        command: ./scripts/my-script.sh
                        environment:
                        - MY_ENV_VARIABLE=my-value
            """
            ),
            DockerCompose(
                services={
                    "my_service": Service(
                        image="my-docker-hub/my-image:latest",
                        ports=["8080:8080"],
                        command="./scripts/my-script.sh",
                        environment=["MY_ENV_VARIABLE=my-value"],
                    )
                }
            ),
            id="Single service with image+ports+environment as array",
        ),
        pytest.param(
            textwrap.dedent(
                """
                services:
                    my_service:
                        image: my-docker-hub/my-image:latest
                        ports:
                        - "8080:8080"
                        command: ./scripts/my-script.sh
                        environment:
                            MY_ENV_VARIABLE: my-value
            """
            ),
            DockerCompose(
                services={
                    "my_service": Service(
                        image="my-docker-hub/my-image:latest",
                        ports=["8080:8080"],
                        command="./scripts/my-script.sh",
                        environment={"MY_ENV_VARIABLE": "my-value"},
                    )
                }
            ),
            id="Single service with image+ports+environment as map",
        ),
        pytest.param(
            textwrap.dedent(
                """
                services:
                    my_service:
                        build: .
                        command: ./scripts/my-script.sh
            """
            ),
            DockerCompose(services={"my_service": Service(command="./scripts/my-script.sh")}),
            id="Single service",
        ),
    ],
)
def test_parse_docker_compose_file(
    temporary_path: Path, compose_content: str, expected: DockerCompose
) -> None:
    """
    GIVEN a Docker Compose file
    WHEN parsing the file
    THEN the file is parsed
    """
    # GIVEN
    compose_path = temporary_path / "docker-compose.yaml"
    compose_path.write_text(compose_content)

    # WHEN
    actual = parse_docker_compose_file(compose_path)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param(".env", "env", id="Dotfile"),
        pytest.param(".env", "env", id="Dotfile uppercase"),
        pytest.param(".env.dockerfile", "env-dockerfile", id="Dotfile with extension"),
        pytest.param(".env", "env", id="Normal file"),
        pytest.param("env.dockerfile", "env-dockerfile", id="Normal file with extension"),
        pytest.param("env/dockerfile", "env-dockerfile", id="File under directory"),
    ],
)
def test_to_kubernetes_name(string: str, expected: str) -> None:
    """
    GIVEN a string
    WHEN converting to a Kubernetes name
    THEN is the expected
    """
    # WHEN
    actual = to_kubernetes_name(string)

    # THEN
    assert actual == expected
