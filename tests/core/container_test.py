import pytest

from komposer.cli import DEFAULT_DOCKER_IMAGE
from komposer.core.container import generate_container_environment, generate_containers
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context


@pytest.mark.parametrize(
    "service",
    [
        pytest.param(
            docker_compose.Service(command="python run.py"), id="No environment nor env_file"
        ),
        pytest.param(
            docker_compose.Service(command="python run.py", environment=[]),
            id="Empty environment array nor env_file",
        ),
        pytest.param(
            docker_compose.Service(command="python run.py", environment={}),
            id="Empty environment dict nor env_file",
        ),
    ],
)
def test_generate_container_environment_no_env_variables(
    context: Context, service: docker_compose.Service
) -> None:
    """
    GIVEN a Docker Compose services
        AND no env_file nor environment are set
    WHEN generating a container environment
    THEN an empty list is returned
    """

    # WHEN
    actual = generate_container_environment(context, service)

    # THEN
    assert list(actual) == []


@pytest.mark.parametrize(
    "services, expected",
    [
        pytest.param({}, [], id="No services"),
        pytest.param(
            {"my-service": docker_compose.Service(command="python run.py")},
            [
                kubernetes.Container(
                    name="my-service",
                    restartPolicy=None,
                    image=DEFAULT_DOCKER_IMAGE,
                    args=["python", "run.py"],
                )
            ],
            id="Service with no image",
        ),
        pytest.param(
            {"my-service": docker_compose.Service(command="python run.py", ports=["5434:5432"])},
            [
                kubernetes.Container(
                    name="my-service",
                    restartPolicy=None,
                    image=DEFAULT_DOCKER_IMAGE,
                    args=["python", "run.py"],
                    ports=[kubernetes.ContainerPort(containerPort=5432, hostPort=5434)],
                )
            ],
            id="Service with port mapping",
        ),
        pytest.param(
            {
                "my-service": docker_compose.Service(
                    command="python run.py", restart=docker_compose.RestartPolicy.ALWAYS
                )
            },
            [
                kubernetes.Container(
                    name="my-service",
                    restartPolicy=kubernetes.RestartPolicy.ON_FAILURE,
                    image=DEFAULT_DOCKER_IMAGE,
                    args=["python", "run.py"],
                    ports=[],
                )
            ],
            id="Service with restart policy",
        ),
    ],
)
def test_generate_containers(
    context: Context, services: docker_compose.Services, expected: list[kubernetes.Container]
) -> None:
    """
    GIVEN a Docker Compose services
    WHEN generating containers
    THEN a list of containers is returned
    """
    # WHEN
    actual = generate_containers(context, services)

    # THEN
    assert actual == expected
