from pathlib import Path
from typing import Optional

from komposer.cli import DEFAULT_DOCKER_COMPOSE_FILENAME
from komposer.types.cli import Context

TEST_IMAGE_NAME = "test-image"
TEST_PROJECT_NAME = "test-project"
TEST_BRANCH_NAME = "test-branch"
TEST_REPOSITORY_NAME = "test-repository"


def make_labels() -> dict[str, str]:
    return {"repository": TEST_REPOSITORY_NAME, "branch": TEST_BRANCH_NAME}


def make_context(
    temporary_path: Optional[Path] = None,
    ingress_for_service: Optional[str] = None,
    extra_manifest_path: Optional[Path] = None,
    ingress_tls_str: Optional[str] = None,
) -> Context:
    temporary_path = temporary_path or Path()
    extra_manifest_path = extra_manifest_path or Path()

    return Context(
        docker_compose_path=temporary_path / DEFAULT_DOCKER_COMPOSE_FILENAME,
        kubernetes_manifest_path=temporary_path / "manifest.yaml",
        project_name=TEST_PROJECT_NAME,
        branch_name=TEST_BRANCH_NAME,
        repository_name=TEST_REPOSITORY_NAME,
        default_image=TEST_IMAGE_NAME,
        ingress_for_service=ingress_for_service,
        extra_manifest_path=extra_manifest_path,
        ingress_tls_str=ingress_tls_str,
    )
