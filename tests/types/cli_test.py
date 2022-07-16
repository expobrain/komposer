from pathlib import Path
from typing import Optional

import pytest

from komposer.types.cli import ensure_lowercase_kebab
from tests.fixtures import make_context


@pytest.mark.parametrize(
    "repository_name, branch_name, project_name, expected",
    [
        pytest.param(
            "my-repository",
            "my-branch",
            None,
            "my-repository-my-branch",
            id="Simple repository and branch names",
        ),
        pytest.param(
            "my-repository",
            "my-branch",
            "my-project",
            "my-project-my-repository-my-branch",
            id="With project name",
        ),
    ],
)
def test_context_manifest_prefix(
    temporary_path: Path,
    repository_name: str,
    branch_name: str,
    project_name: Optional[str],
    expected: str,
) -> None:
    """
    GIVEN a project, repository and branch names
    WHEN creating a context
        AND accessging the manifest_prefix attribute
    THEN is the expected
    """
    # WHEN
    context = make_context(
        docker_compose_path=temporary_path,
        project_name=project_name,
        branch_name=branch_name,
        repository_name=repository_name,
    )

    # THEN
    assert context.manifest_prefix == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("string", id="Simple string"),
        pytest.param("my-string", id="String with hyphens"),
        pytest.param("my-1-string", id="String with digits"),
        pytest.param("1-string", id="String with leading digits"),
        pytest.param("string-1", id="String with trailing digits"),
    ],
)
def test_ensure_is_kubernetes_name(value: str) -> None:
    """
    GIVEN a string
        AND the string is in lowercase kebab format
    WHEN calling ensure_is_kubernetes_name
    THEN no exception is raised
    """
    ensure_lowercase_kebab(value)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="Empty string"),
        pytest.param("my/string", id="String with unsupported symbol /"),
        pytest.param("my_string", id="String with unsupported symbol _"),
    ],
)
def test_ensure_is_kubernetes_name_fails_if_not_lowercase_kebak(value: str) -> None:
    """
    GIVEN a string
        AND the string is not in lowercase kebab format
    WHEN calling ensure_is_kubernetes_name
    THEN an exception is raised
    """
    with pytest.raises(ValueError, match="Not a lowercase kebab string"):
        ensure_lowercase_kebab(value)
