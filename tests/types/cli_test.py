from pathlib import Path

import pytest

from komposer.types.cli import Context
from tests.fixtures import TEST_IMAGE_NAME


@pytest.mark.parametrize(
    "project_name, repository_name, branch_name, expected",
    [
        pytest.param(
            "my-project",
            "my-repository",
            "my-branch",
            "my-project-my-repository-my-branch",
            id="Simple repository and branch names",
        ),
        pytest.param(
            "MY-PROJECT",
            "MY-REPOSITORY",
            "MY-BRANCH",
            "my-project-my-repository-my-branch",
            id="Uppercase repository and branch names",
        ),
        pytest.param(
            "my/project",
            "my/repository",
            "my/branch",
            "my-project-my-repository-my-branch",
            id="Symbols in repository and branch names",
        ),
    ],
)
def test_context_manifest_prefix(
    temporary_path: Path, project_name: str, repository_name: str, branch_name: str, expected: str
) -> None:
    """
    GIVEN a project, repository and branch names
    WHEN creating a context
        AND accessging the manifest_prefix attribute
    THEN is the expected
    """
    # WHEN
    context = Context(
        docker_compose_path=temporary_path,
        project_name=project_name,
        branch_name=branch_name,
        repository_name=repository_name,
        default_image=TEST_IMAGE_NAME,
    )

    # THEN
    assert context.manifest_prefix == expected
