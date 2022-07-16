from collections.abc import Sequence
from pathlib import Path

import pytest

from komposer.core.config_map import generate_config_maps
from komposer.types import docker_compose
from komposer.types.cli import Context
from komposer.types.kubernetes import ConfigMap, Metadata
from tests.fixtures import make_labels


@pytest.mark.parametrize(
    "compose",
    [
        pytest.param(
            docker_compose.DockerCompose(
                services={"my_service": docker_compose.Service(env_file=".env")}
            )
        )
    ],
)
@pytest.mark.parametrize(
    "dotfile_content, expected",
    [
        pytest.param(
            "MY_VARIABLE=my-value",
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-env", labels=make_labels()
                    ),
                    data={"MY_VARIABLE": "my-value"},
                )
            ],
            id="Single variable",
        ),
        pytest.param(
            "MY_VARIABLE",
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-env", labels=make_labels()
                    ),
                    data={"MY_VARIABLE": None},
                )
            ],
            id="Single variable null",
        ),
        pytest.param(
            "MY_VARIABLE=",
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-env", labels=make_labels()
                    ),
                    data={"MY_VARIABLE": ""},
                )
            ],
            id="Single variable not set",
        ),
        pytest.param("", [], id="No variables"),
    ],
)
def test_generate_config_map_from_file(
    context: Context,
    temporary_path: Path,
    compose: docker_compose.DockerCompose,
    dotfile_content: str,
    expected: list[ConfigMap],
) -> None:
    """
    GIVEN a file with env variables
    WHEN generating a config map from the file
    THEN a ConfigMap is returned
    """
    # GIVEN
    dotfile_path = temporary_path / ".env"
    dotfile_path.write_text(dotfile_content)

    # WHEN
    actual = list(generate_config_maps(context, compose))

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "compose, expected",
    [
        pytest.param(
            docker_compose.DockerCompose(
                services={
                    "my_service": docker_compose.Service(environment=["MY_VARIABLE=my-value"])
                }
            ),
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-my-service",
                        labels=make_labels(),
                        annotations=None,
                    ),
                    data={"MY_VARIABLE": "my-value"},
                )
            ],
            id="Single variable",
        ),
        pytest.param(
            docker_compose.DockerCompose(
                services={
                    "my_service": docker_compose.Service(
                        environment=["MY_VARIABLE_1=my-value-1", "MY_VARIABLE_2=my-value-2"]
                    )
                }
            ),
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-my-service",
                        labels=make_labels(),
                        annotations=None,
                    ),
                    data={"MY_VARIABLE_1": "my-value-1", "MY_VARIABLE_2": "my-value-2"},
                )
            ],
            id="Multiple variables",
        ),
        pytest.param(
            docker_compose.DockerCompose(
                services={"my_service": docker_compose.Service(environment=["MY_VARIABLE"])}
            ),
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-my-service",
                        labels=make_labels(),
                        annotations=None,
                    ),
                    data={"MY_VARIABLE": None},
                )
            ],
            id="Single variable not set",
        ),
        pytest.param(
            docker_compose.DockerCompose(
                services={"my_service": docker_compose.Service(environment=["MY_VARIABLE="])}
            ),
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-my-service",
                        labels=make_labels(),
                        annotations=None,
                    ),
                    data={"MY_VARIABLE": ""},
                )
            ],
            id="Single variable empty",
        ),
        pytest.param(
            docker_compose.DockerCompose(
                services={"my_service": docker_compose.Service(environment=["MY_VARIABLE"])}
            ),
            [
                ConfigMap(
                    metadata=Metadata(
                        name="test-repository-test-branch-my-service",
                        labels=make_labels(),
                        annotations=None,
                    ),
                    data={"MY_VARIABLE": None},
                )
            ],
            id="Single variable null",
        ),
        pytest.param(
            docker_compose.DockerCompose(services={"my_service": docker_compose.Service()}),
            [],
            id="No variables",
        ),
    ],
)
def test_generate_config_map_from_list_of_envs(
    context: Context, compose: docker_compose.DockerCompose, expected: Sequence[ConfigMap]
) -> None:
    """
    GIVEN a list of environments variable
    WHEN generating a config map from the list
    THEN a ConfigMap is returned
    """
    # WHEN
    actual = list(generate_config_maps(context, compose))

    # THEN
    assert actual == expected
