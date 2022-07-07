from pathlib import Path

import pytest

from komposer.types.cli import ensure_is_rfc_1123
from tests.fixtures import make_context


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
        pytest.param("a" * 63, id="Max length of the string"),
    ],
)
def test_ensure_is_kubernetes_name(value: str) -> None:
    """
    GIVEN a string
        AND the string is a valid RFC 1123
    WHEN calling ensure_is_kubernetes_name
    THEN no exception is raised
    """
    ensure_is_rfc_1123(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param("", "Not a valid RFC-1123 string", id="Empty string"),
        pytest.param("1string", "Not a valid RFC-1123 string", id="String with leading digit"),
        pytest.param("string1", "Not a valid RFC-1123 string", id="String with trailing digit"),
        pytest.param(
            "my/string", "Not a valid RFC-1123 string", id="String with unsupported symbol"
        ),
        pytest.param("a" * 64, "String is longer than 63 characters", id="String is too long"),
    ],
)
def test_ensure_is_kubernetes_name_fails_if_not_rfc_1123(value: str, expected: str) -> None:
    """
    GIVEN a string
        AND the string is not a valid RFC 1123
    WHEN calling ensure_is_kubernetes_name
    THEN an exception is raised
    """
    with pytest.raises(ValueError, match=expected):
        ensure_is_rfc_1123(value)
