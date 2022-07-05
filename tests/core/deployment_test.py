import textwrap
from pathlib import Path
from typing import Optional

import pytest

from komposer.cli import DEFAULT_DOCKER_IMAGE
from komposer.core.deployment import generate_deployment
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.types.kubernetes import Annotations, Metadata, UnnamedMetadata
from tests.fixtures import make_context, make_labels


@pytest.mark.parametrize(
    "services, expected",
    [
        pytest.param(
            {},
            kubernetes.Deployment(
                apiversion="v1",
                kind="Deployment",
                metadata=Metadata(
                    name="test-project-test-repository-test-branch", labels=make_labels()
                ),
                spec=kubernetes.DeploymentSpec(
                    hostAliases=[],
                    selector=kubernetes.Selector(matchLabels=make_labels()),
                    template=kubernetes.Template(
                        metadata=UnnamedMetadata(labels=make_labels()),
                        spec=kubernetes.TemplateSpec(),
                    ),
                ),
            ),
            id="No services",
        ),
        pytest.param(
            {
                "my_service": docker_compose.Service(
                    command="python run.py",
                    environment=["MY_ENV=my-value"],
                    ports=["8080:8080"],
                    image="my_image:latest",
                )
            },
            kubernetes.Deployment(
                apiversion="v1",
                kind="Deployment",
                metadata=Metadata(
                    name="test-project-test-repository-test-branch", labels=make_labels()
                ),
                spec=kubernetes.DeploymentSpec(
                    selector=kubernetes.Selector(matchLabels=make_labels()),
                    template=kubernetes.Template(
                        metadata=UnnamedMetadata(labels=make_labels()),
                        spec=kubernetes.TemplateSpec(
                            hostAliases=[
                                kubernetes.HostAlias(ip="127.0.0.1", hostnames=["my_service"])
                            ],
                            containers=[
                                kubernetes.Container(
                                    image="my_image:latest",
                                    name="my-service",
                                    args=["python", "run.py"],
                                    env=[
                                        kubernetes.EnvironmentVariable(
                                            name="MY_ENV", value="my-value"
                                        )
                                    ],
                                    ports=[kubernetes.ContainerPort(containerPort=8080)],
                                )
                            ],
                        ),
                    ),
                ),
            ),
            id="Service with image+string command+port+image",
        ),
        pytest.param(
            {
                "my_service": docker_compose.Service(
                    command=["python", "run.py"],
                    environment=["MY_ENV=my-value"],
                    ports=["8080:8080"],
                    image="my_image:latest",
                )
            },
            kubernetes.Deployment(
                apiversion="v1",
                kind="Deployment",
                metadata=Metadata(
                    name="test-project-test-repository-test-branch", labels=make_labels()
                ),
                spec=kubernetes.DeploymentSpec(
                    selector=kubernetes.Selector(matchLabels=make_labels()),
                    template=kubernetes.Template(
                        metadata=UnnamedMetadata(labels=make_labels()),
                        spec=kubernetes.TemplateSpec(
                            hostAliases=[
                                kubernetes.HostAlias(ip="127.0.0.1", hostnames=["my_service"])
                            ],
                            containers=[
                                kubernetes.Container(
                                    image="my_image:latest",
                                    name="my-service",
                                    args=["python", "run.py"],
                                    env=[
                                        kubernetes.EnvironmentVariable(
                                            name="MY_ENV", value="my-value"
                                        )
                                    ],
                                    ports=[kubernetes.ContainerPort(containerPort=8080)],
                                )
                            ],
                        ),
                    ),
                ),
            ),
            id="Service with image+list command+port+image",
        ),
    ],
)
def test_generate_deployment_environment(
    context: Context, services: docker_compose.Services, expected: kubernetes.Deployment
) -> None:
    """
    GIVEN a Docker Compose services
        AND a list of environment variables
    WHEN generating a deployment
    THEN a Deployment is returned
    """
    # WHEN
    actual = generate_deployment(context, services)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "services, env_file_content, env_file_filename, expected",
    [
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py", env_file=".env")},
            textwrap.dedent(
                """
                MY_ENV=my-value
                """
            ),
            Path(".env"),
            kubernetes.Deployment(
                apiversion="apps/v1",
                kind="Deployment",
                metadata=Metadata(
                    name="test-project-test-repository-test-branch", labels=make_labels()
                ),
                spec=kubernetes.DeploymentSpec(
                    selector=kubernetes.Selector(matchLabels=make_labels()),
                    template=kubernetes.Template(
                        metadata=UnnamedMetadata(labels=make_labels()),
                        spec=kubernetes.TemplateSpec(
                            hostAliases=[
                                kubernetes.HostAlias(ip="127.0.0.1", hostnames=["my_service"])
                            ],
                            containers=[
                                kubernetes.Container(
                                    image=DEFAULT_DOCKER_IMAGE,
                                    name="my-service",
                                    args=["python", "run.py"],
                                    env=[
                                        kubernetes.ConfigMapEnvironmentVariable(
                                            name="MY_ENV",
                                            valueFrom=kubernetes.ConfigMapKeyRef(
                                                key="MY_ENV",
                                                name="test-project-test-repository-test-branch-env",  # noqa: E501
                                            ),
                                        )
                                    ],
                                )
                            ],
                        ),
                    ),
                ),
            ),
            id="Service with env_file .env",
        ),
        pytest.param(
            {
                "my_service": docker_compose.Service(
                    command="python run.py", env_file=".env.docker"
                )
            },
            textwrap.dedent(
                """
                MY_ENV=my-value
                """
            ),
            Path(".env.docker"),
            kubernetes.Deployment(
                apiversion="apps/v1",
                kind="Deployment",
                metadata=Metadata(
                    name="test-project-test-repository-test-branch", labels=make_labels()
                ),
                spec=kubernetes.DeploymentSpec(
                    selector=kubernetes.Selector(matchLabels=make_labels()),
                    template=kubernetes.Template(
                        metadata=UnnamedMetadata(labels=make_labels()),
                        spec=kubernetes.TemplateSpec(
                            hostAliases=[
                                kubernetes.HostAlias(ip="127.0.0.1", hostnames=["my_service"])
                            ],
                            containers=[
                                kubernetes.Container(
                                    image=DEFAULT_DOCKER_IMAGE,
                                    name="my-service",
                                    args=["python", "run.py"],
                                    env=[
                                        kubernetes.ConfigMapEnvironmentVariable(
                                            name="MY_ENV",
                                            valueFrom=kubernetes.ConfigMapKeyRef(
                                                key="MY_ENV",
                                                name="test-project-test-repository-test-branch-env-docker",  # noqa: E501
                                            ),
                                        )
                                    ],
                                )
                            ],
                        ),
                    ),
                ),
            ),
            id="Service with env_file .env.docker",
        ),
    ],
)
def test_generate_deployment_env_file(
    context: Context,
    temporary_path: Path,
    env_file_content: str,
    env_file_filename: Path,
    services: docker_compose.Services,
    expected: kubernetes.Deployment,
) -> None:
    """
    GIVEN a Docker Compose services
        AND a env_file content is provided
    WHEN generating a deployment
    THEN a Deployment is returned
    """
    # GIVEN
    env_file_path = temporary_path / env_file_filename
    env_file_path.write_text(env_file_content)

    # WHEN
    actual = generate_deployment(context, services)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "services",
    [{"my_service": docker_compose.Service(command="python run.py")}],
)
@pytest.mark.parametrize(
    "deployment_annotations_str, expected",
    [
        pytest.param(None, None, id="No annotations"),
        pytest.param('{"key": "value"}', {"key": "value"}, id="Mapping"),
    ],
)
def test_generate_deployment_with_extra_annotations(
    deployment_annotations_str: Optional[str],
    services: docker_compose.Services,
    expected: Annotations,
) -> None:
    """
    GIVEN a Docker Compose services
        AND a list of extra annotations
    WHEN generating a deployment
    THEN a Deployment is returned
        AND the annotations matches the expected
    """
    # GIVEN
    context = make_context(deployment_annotations_str=deployment_annotations_str)

    # WHEN
    actual = generate_deployment(context, services)

    # THEN
    assert actual.metadata.annotations == expected


@pytest.mark.parametrize(
    "services",
    [{"my_service": docker_compose.Service(command="python run.py")}],
)
@pytest.mark.parametrize(
    "service_account_name",
    [None, "my-service-account"],
)
def test_generate_deployment_with_service_account_name(
    service_account_name: Optional[str], services: docker_compose.Services
) -> None:
    """
    GIVEN a Docker Compose services
        AND a service account name
    WHEN generating a deployment
    THEN a Deployment is returned
        AND the service account name matches the expected
    """
    # GIVEN
    context = make_context(deployment_service_account_name=service_account_name)

    # WHEN
    actual = generate_deployment(context, services)

    # THEN
    assert actual.spec.template.spec.service_account_name == service_account_name
