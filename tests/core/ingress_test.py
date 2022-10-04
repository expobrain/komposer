from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Optional

import pytest
import yaml

from komposer.cli import DEFAULT_INGRESS_DOMAIN
from komposer.core.ingress import generate_ingress_from_services
from komposer.exceptions import ServiceNotFoundError
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.types.kubernetes import IngressRule, Metadata
from tests.fixtures import make_context, make_labels


@pytest.mark.parametrize(
    "services, ingress_domain, ingress_tls, expected",
    [
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py")},
            None,
            None,
            kubernetes.Ingress(
                metadata=Metadata(
                    name="test-repository-test-branch-my-service",
                    labels=make_labels(),
                    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
                ),
                spec=kubernetes.IngressSpec(
                    tls=None,
                    rules=[
                        IngressRule(
                            host=(
                                f"my-service.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"
                            ),
                            http=kubernetes.HttpPaths(paths=[]),
                        )
                    ],
                ),
            ),
            id="Service without ingress TLS",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py")},
            None,
            [
                {
                    "hosts": [f"api.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"],
                    "secretName": "app-tls-cert",
                }
            ],
            kubernetes.Ingress(
                metadata=Metadata(
                    name="test-repository-test-branch-my-service",
                    labels=make_labels(),
                    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
                ),
                spec=kubernetes.IngressSpec(
                    tls=[
                        {
                            "hosts": [f"api.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"],
                            "secretName": "app-tls-cert",
                        }
                    ],
                    rules=[
                        IngressRule(
                            host=(
                                f"my-service.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"
                            ),
                            http=kubernetes.HttpPaths(paths=[]),
                        )
                    ],
                ),
            ),
            id="Service with ingress TLS",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py", ports=["8080"])},
            None,
            None,
            kubernetes.Ingress(
                metadata=Metadata(
                    name="test-repository-test-branch-my-service",
                    labels=make_labels(),
                    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
                ),
                spec=kubernetes.IngressSpec(
                    tls=None,
                    rules=[
                        IngressRule(
                            host=(
                                f"my-service.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"
                            ),
                            http=kubernetes.HttpPaths(
                                paths=[
                                    kubernetes.HttpPath(
                                        path="/",
                                        pathType=kubernetes.PathType.PREFIX,
                                        backend=kubernetes.Backend(
                                            service=kubernetes.ServiceRef(
                                                name="test-repository-test-branch-my-service",  # noqa: E501
                                                port=kubernetes.ServiceRefPort(number=8080),
                                            )
                                        ),
                                    )
                                ]
                            ),
                        )
                    ],
                ),
            ),
            id="Service with single port",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py", ports=["8080:9000"])},
            None,
            None,
            kubernetes.Ingress(
                metadata=Metadata(
                    name="test-repository-test-branch-my-service",
                    labels=make_labels(),
                    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
                ),
                spec=kubernetes.IngressSpec(
                    tls=None,
                    rules=[
                        IngressRule(
                            host=(
                                f"my-service.test-repository-test-branch.{DEFAULT_INGRESS_DOMAIN}"
                            ),
                            http=kubernetes.HttpPaths(
                                paths=[
                                    kubernetes.HttpPath(
                                        path="/",
                                        pathType=kubernetes.PathType.PREFIX,
                                        backend=kubernetes.Backend(
                                            service=kubernetes.ServiceRef(
                                                name="test-repository-test-branch-my-service",  # noqa: E501
                                                port=kubernetes.ServiceRefPort(number=8080),
                                            )
                                        ),
                                    )
                                ]
                            ),
                        )
                    ],
                ),
            ),
            id="Service with double ports",
        ),
        pytest.param(
            {"my_service": docker_compose.Service(command="python run.py")},
            "dev.mydomain.com",
            None,
            kubernetes.Ingress(
                metadata=Metadata(
                    name="test-repository-test-branch-my-service",
                    labels=make_labels(),
                    annotations={"cert-manager.io/cluster-issuer": "letsencrypt-prod"},
                ),
                spec=kubernetes.IngressSpec(
                    tls=None,
                    rules=[
                        IngressRule(
                            host=("my-service.test-repository-test-branch.dev.mydomain.com"),
                            http=kubernetes.HttpPaths(paths=[]),
                        )
                    ],
                ),
            ),
            id="Service with custom ingress domain",
        ),
    ],
)
def test_generate_ingress_from_service(
    temporary_path: Path,
    services: docker_compose.Services,
    ingress_domain: Optional[str],
    ingress_tls: Optional[Sequence[Mapping[str, Any]]],
    expected: kubernetes.Ingress,
) -> None:
    """
    GIVEN a Docker Compose services
        AND an ingress is required
    WHEN generating the ingress
    THEN Kubernetes ingress is returned
    """
    # GIVEN
    if ingress_tls is not None:
        ingress_tls_path = temporary_path / "ingress_tls.yaml"
        ingress_tls_path.write_text(yaml.safe_dump(ingress_tls))
    else:
        ingress_tls_path = None

    context = make_context(
        ingress_for_service="my_service",
        ingress_domain=ingress_domain,
        ingress_tls_path=ingress_tls_path,
    )

    # WHEN
    actual = generate_ingress_from_services(context, services)

    # THEN
    assert actual == expected


@pytest.mark.parametrize("context_with_ingress", [make_context(ingress_for_service="my_service")])
@pytest.mark.parametrize(
    "services",
    [
        pytest.param({}, id="No services"),
        pytest.param(
            {"not_found": docker_compose.Service(command="python run.py")},
            id="one service but not the required one",
        ),
    ],
)
def test_generate_ingress_from_service_raises_if_service_not_found(
    context_with_ingress: Context, services: docker_compose.Services
) -> None:
    """
    GIVEN a Docker Compose services
        AND an ingress is required
        AND the service is not found
    WHEN generating the ingress
    THEN an exception is raised
    """
    # WHEN
    with pytest.raises(ServiceNotFoundError):
        generate_ingress_from_services(context_with_ingress, services)
