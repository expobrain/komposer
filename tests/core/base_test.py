from typing import Optional, Sequence

import pytest
from pytest_mock import MockerFixture

from komposer.core.base import (
    ensure_deployment_annotations_is_valid_yaml,
    ensure_ingress_tls_is_valid_yaml,
    ensure_service_name_lowercase_RFC_1123,
    ensure_unique_ports_on_docker_compose,
    generate_manifest_from_docker_compose,
)
from komposer.exceptions import (
    ComposePortsNotUniqueError,
    DeploymentAnnotationsException,
    DeploymentAnnotationsInvaliYamlError,
    DeploymentAnnotationsNotAMappingError,
    IngressTlsException,
    IngressTlsInvalidYamlError,
    IngressTlsNotAListError,
    InvalidServiceNameError,
)
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.utils import as_json_object
from tests.fixtures import make_context, make_labels


def make_minimal_docker_compose() -> docker_compose.DockerCompose:
    return docker_compose.DockerCompose(services={"my-service": docker_compose.Service()})


def make_minimal_service() -> kubernetes.Service:
    return kubernetes.Service(
        apiVersion="v1",
        kind="Service",
        metadata=kubernetes.Metadata(
            name="test-project-test-repository-test-branch-my-service", labels=make_labels()
        ),
        spec=kubernetes.ServiceSpec(ports=[], selector=make_labels()),
    )


def make_minimal_deployment() -> kubernetes.Deployment:
    return kubernetes.Deployment(
        apiVersion="apps/v1",
        kind="Deployment",
        metadata=kubernetes.Metadata(
            name="test-project-test-repository-test-branch", labels=make_labels()
        ),
        spec=kubernetes.DeploymentSpec(
            hostAliases=[],
            selector=kubernetes.Selector(matchLabels=make_labels()),
            template=kubernetes.Template(
                metadata=kubernetes.UnnamedMetadata(labels=make_labels()),
                spec=kubernetes.TemplateSpec(),
            ),
        ),
    )


def make_minimal_ingress() -> kubernetes.Ingress:
    return kubernetes.Ingress(
        metadata=kubernetes.Metadata(
            name="test-project-test-repository-test-branch-my-service",
            labels=make_labels(),
            annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
        ),
        spec=kubernetes.IngressSpec(
            tls=[
                kubernetes.IngressTls(
                    hosts=[
                        (
                            "my-service"
                            ".test-project-test-repository-test-branch"
                            ".svc.cluster.local"
                        )
                    ],
                    secretName="plum-app-tls-cert",
                )
            ],
            rules=[
                kubernetes.IngressRule(
                    host=(
                        "my-service"
                        ".test-project-test-repository-test-branch"
                        ".svc.cluster.local"
                    ),
                    http=kubernetes.HttpPaths(
                        paths=[
                            kubernetes.HttpPath(
                                path="/",
                                pathType=kubernetes.PathType.PREFIX,
                                backend=kubernetes.Backend(
                                    service=kubernetes.ServiceRef(
                                        name="test-project-test-repository-test-branch-my-service",  # noqa: E501
                                        port=kubernetes.ServiceRefPort(number=8080),
                                    )
                                ),
                            )
                        ]
                    ),
                )
            ],
        ),
    )


def make_minimal_extra_manifest_items() -> list[dict]:
    return [
        {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "my-config-map",
            },
            "data": {
                "DEBUG": "1",
            },
        },
        {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": "my-job",
                "labels": {
                    "my-lable": "my-label-value",
                },
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "OnFailure",
                        "containers": [
                            {
                                "name": "my-container",
                                "imagePullPolicy": "IfNotPresent",
                                "image": "${IMAGE}",
                                "args": ["python", "run.py"],
                                "env": [
                                    {
                                        "name": "DEBUG",
                                        "valueFrom": {
                                            "configMapKeyRef": {
                                                "key": "DEBUG",
                                                "name": "my-config-map",
                                            }
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                },
            },
        },
    ]


@pytest.mark.parametrize(
    "services",
    [
        pytest.param(
            {
                "service1": docker_compose.Service(ports=["8080"]),
                "service2": docker_compose.Service(ports=["8080"]),
            },
            id="Same single ports",
        ),
        pytest.param(
            {
                "service1": docker_compose.Service(ports=["9000:8080"]),
                "service2": docker_compose.Service(ports=["8000:8080"]),
            },
            id="Same host:container ports",
        ),
    ],
)
def test_ensure_unique_ports_on_docker_compose_fails(services: docker_compose.Services) -> None:
    """
    GIVEN a Docker Compose file
        AND two services hvae the same internal port
    WHEN chekcing that all the service uses unique ports
    THEN raises an exception
    """
    # GIVEN
    compose = docker_compose.DockerCompose(services=services)

    # WHEN
    with pytest.raises(ComposePortsNotUniqueError):
        ensure_unique_ports_on_docker_compose(compose)


@pytest.mark.parametrize(
    "compose",
    [
        pytest.param(
            make_minimal_docker_compose(),
            id="Valid service name",
        ),
    ],
)
def test_ensure_service_name_lowercase_RFC_1123(compose: docker_compose.DockerCompose) -> None:
    """
    GIVEN a Docker Compose file
        AND a service name in lowercase RFC 1123 format
    WHEN checking all the service names
    THEN no exception is raised
    """
    # WHEN
    ensure_service_name_lowercase_RFC_1123(compose)


@pytest.mark.parametrize(
    "compose",
    [
        pytest.param(
            docker_compose.DockerCompose(services={"my_service": docker_compose.Service()}),
            id="Invalid service name",
        ),
        pytest.param(
            docker_compose.DockerCompose(services={"MY_SERVICE": docker_compose.Service()}),
            id="Invalid uppercase service name",
        ),
    ],
)
def test_ensure_service_name_lowercase_RFC_1123_fails(
    compose: docker_compose.DockerCompose,
) -> None:
    """
    GIVEN a Docker Compose file
        AND an invalid service name
    WHEN checking all the service names
    THEN an exception is raised
    """
    # WHEN
    with pytest.raises(InvalidServiceNameError):
        ensure_service_name_lowercase_RFC_1123(compose)


@pytest.mark.parametrize(
    "context, compose, config_maps, deployment, services, extra_manifest, expected",
    [
        pytest.param(
            make_context(),
            make_minimal_docker_compose(),
            [],
            make_minimal_deployment(),
            [make_minimal_service()],
            [],
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    as_json_object(make_minimal_deployment()),
                    as_json_object(make_minimal_service()),
                ],
            },
            id="Single service",
        ),
        pytest.param(
            make_context(ingress_for_service="my-service"),
            make_minimal_docker_compose(),
            [],
            make_minimal_deployment(),
            [make_minimal_service()],
            [],
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    as_json_object(make_minimal_deployment()),
                    as_json_object(make_minimal_service()),
                    as_json_object(make_minimal_ingress()),
                ],
            },
            id="Single service with ingress",
        ),
        pytest.param(
            make_context(extra_manifest_path="my-service"),
            make_minimal_docker_compose(),
            [],
            make_minimal_deployment(),
            [make_minimal_service()],
            make_minimal_extra_manifest_items(),
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    as_json_object(make_minimal_deployment()),
                    as_json_object(make_minimal_service()),
                    *make_minimal_extra_manifest_items(),
                ],
            },
            id="Single service with extra manifest",
        ),
    ],
)
def test_generate_manifest_from_docker_compose(
    mocker: MockerFixture,
    context: Context,
    compose: docker_compose.DockerCompose,
    config_maps: Sequence[kubernetes.ConfigMap],
    deployment: kubernetes.Deployment,
    services: Sequence[kubernetes.Service],
    extra_manifest: list[dict],
    expected: dict,
) -> None:
    """
    GIVEN a Docker Compose file
    WHEN generating a manifest
    THEN a manifest is returned
    """
    # GIVEN
    mocker.patch("komposer.core.base.parse_docker_compose_file", return_value=compose)
    mocker.patch("komposer.core.base.generate_config_maps", return_value=config_maps)
    mocker.patch("komposer.core.base.generate_deployment", return_value=deployment)
    mocker.patch("komposer.core.base.generate_services", return_value=services)
    mocker.patch("komposer.core.base.load_extra_manifest", return_value=extra_manifest)

    if context.ingress_for_service:
        mocker.patch(
            "komposer.core.base.generate_ingress_from_services",
            return_value=make_minimal_ingress(),
        )

    # WHEN
    actual = generate_manifest_from_docker_compose(context)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "ingress_tls_str",
    [
        pytest.param(None, id="No TLS"),
        pytest.param("[]", id="List"),
        pytest.param("", id="Empty string"),
        pytest.param("  ", id="Empty string with spaces"),
    ],
)
def test_ensure_ingress_tls_is_valid_yaml(ingress_tls_str: Optional[str]) -> None:
    """
    GIVEN a valid Ingress TLS string
    WHEN ensuring that it's a valid YAML
    THEN no exception is raised
    """
    # GIVEN
    context = make_context(ingress_tls_str=ingress_tls_str)

    # WHEN
    ensure_ingress_tls_is_valid_yaml(context)


@pytest.mark.parametrize(
    "ingress_tls_str, exception",
    [
        pytest.param("aaa", IngressTlsNotAListError, id="Single string"),
        pytest.param("{", IngressTlsInvalidYamlError, id="Broken YAML"),
        pytest.param("{}", IngressTlsNotAListError, id="Empty object"),
        pytest.param('{"key":"value"}', IngressTlsNotAListError, id="Empty object"),
    ],
)
def test_ensure_ingress_tls_is_valid_yaml_fails(
    ingress_tls_str: str, exception: type[IngressTlsException]
) -> None:
    """
    GIVEN an invalid Ingress TLS string
    WHEN ensuring that it's a valid YAML
    THEN raise an exception
    """
    # GIVEN
    context = make_context(ingress_tls_str=ingress_tls_str)

    # WHEN
    with pytest.raises(exception):
        ensure_ingress_tls_is_valid_yaml(context)


@pytest.mark.parametrize(
    "deployment_annotations_str",
    [
        pytest.param(None, id="No annotations"),
        pytest.param("", id="Empty string"),
        pytest.param("  ", id="Empty string with spaces"),
        pytest.param("{}", id="Empty mapping"),
        pytest.param('{"key": "value"}', id="Mapping"),
    ],
)
def test_ensure_deployment_annotations_is_valid_yaml(
    deployment_annotations_str: Optional[str],
) -> None:
    """
    GIVEN a valid Deployment annotations string
    WHEN ensuring that it's a valid YAML
    THEN no exception is raised
    """
    # GIVEN
    context = make_context(deployment_annotations_str=deployment_annotations_str)

    # WHEN
    ensure_deployment_annotations_is_valid_yaml(context)


@pytest.mark.parametrize(
    "deployment_annotations_str, exception",
    [
        pytest.param("aaa", DeploymentAnnotationsNotAMappingError, id="Single string"),
        pytest.param("{", DeploymentAnnotationsInvaliYamlError, id="Broken YAML"),
        pytest.param("[]", DeploymentAnnotationsNotAMappingError, id="List"),
    ],
)
def test_ensure_deployment_annotations_is_valid_yaml_fails(
    deployment_annotations_str: str, exception: type[DeploymentAnnotationsException]
) -> None:
    """
    GIVEN an invalid Deployment annotations string
    WHEN ensuring that it's a valid YAML
    THEN raise an exception
    """
    # GIVEN
    context = make_context(deployment_annotations_str=deployment_annotations_str)

    # WHEN
    with pytest.raises(exception):
        ensure_deployment_annotations_is_valid_yaml(context)
