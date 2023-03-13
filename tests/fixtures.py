from pathlib import Path
from typing import Optional

from komposer.cli import (
    DEFAULT_DOCKER_COMPOSE_FILENAME,
    DEFAULT_DOCKER_IMAGE,
    DEFAULT_INGRESS_DOMAIN,
)
from komposer.types.cli import Context, DeploymentContext, IngressContext

TEST_PROJECT_NAME = "test-project"
TEST_BRANCH_NAME = "test-branch"
TEST_REPOSITORY_NAME = "test-repository"


def make_labels() -> dict[str, Optional[str]]:
    return {"repository": TEST_REPOSITORY_NAME, "branch": TEST_BRANCH_NAME}


def make_context(
    temporary_path: Optional[Path] = None,
    docker_compose_path: Optional[Path] = None,
    project_name: Optional[str] = None,
    branch_name: str = TEST_BRANCH_NAME,
    repository_name: str = TEST_REPOSITORY_NAME,
    default_image: str = DEFAULT_DOCKER_IMAGE,
    ingress_for_service: Optional[str] = None,
    extra_manifest_paths: Optional[list[Path]] = None,
    ingress_tls_path: Optional[Path] = None,
    ingress_domain: Optional[str] = None,
    deployment_annotations_path: Optional[Path] = None,
    deployment_service_account_name: Optional[str] = None,
) -> Context:
    temporary_path = temporary_path or Path()
    docker_compose_path = docker_compose_path or (temporary_path / DEFAULT_DOCKER_COMPOSE_FILENAME)
    extra_manifest_paths = extra_manifest_paths or []
    ingress_domain = ingress_domain or DEFAULT_INGRESS_DOMAIN

    return Context(
        docker_compose_path=docker_compose_path,
        project_name=project_name,
        branch_name=branch_name,
        repository_name=repository_name,
        default_image=default_image,
        ingress_for_service=ingress_for_service,
        extra_manifest_paths=extra_manifest_paths,
        ingress=IngressContext(tls_path=ingress_tls_path, domain=ingress_domain),
        deployment=DeploymentContext(
            annotations_path=deployment_annotations_path,
            service_account_name=deployment_service_account_name,
        ),
    )
