import pytest

from komposer.core.service import generate_services
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.types.kubernetes import Metadata
from tests.fixtures import make_labels


@pytest.mark.parametrize(
    "services, expected",
    [
        pytest.param({}, [], id="No services"),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py", ports=["8080:8080"])},
            [
                kubernetes.Service(
                    apiversion="v1",
                    kind="Service",
                    metadata=Metadata(
                        name="test-project-test-repository-test-branch-my-service",
                        labels=make_labels(),
                    ),
                    spec=kubernetes.ServiceSpec(
                        ports=[
                            kubernetes.ServicePort(name="8080-8080", port=8080, targetPort=8080)
                        ],
                        selector=make_labels(),
                    ),
                )
            ],
            id="Service with ports",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py", ports=["8080"])},
            [
                kubernetes.Service(
                    apiversion="v1",
                    kind="Service",
                    metadata=Metadata(
                        name="test-project-test-repository-test-branch-my-service",
                        labels=make_labels(),
                    ),
                    spec=kubernetes.ServiceSpec(
                        ports=[kubernetes.ServicePort(name="8080", port=8080, targetPort=8080)],
                        selector=make_labels(),
                    ),
                )
            ],
            id="Service with single port",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py")},
            [],
            id="Service without port",
        ),
    ],
)
def test_generate_services(
    context: Context, services: docker_compose.Services, expected: list[kubernetes.Service]
) -> None:
    """
    GIVEN a Docker Compose services
    WHEN generating services
    THEN Kubernetes services are returned
    """
    # WHEN
    actual = generate_services(context, services)

    # THEN
    assert actual == expected
