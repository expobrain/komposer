from collections.abc import Sequence
from pathlib import Path

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from komposer import cli
from komposer.types.cli import Context
from tests.fixtures import (
    TEST_BRANCH_NAME,
    TEST_PROJECT_NAME,
    TEST_REPOSITORY_NAME,
    make_context,
)


def make_mandatory_long_args() -> list[str]:
    return [
        "--project-name",
        TEST_PROJECT_NAME,
        "--repository-name",
        TEST_REPOSITORY_NAME,
        "--branch-name",
        TEST_BRANCH_NAME,
    ]


def make_mandatory_short_args() -> list[str]:
    return ["-p", TEST_PROJECT_NAME, "-r", TEST_REPOSITORY_NAME, "-b", TEST_BRANCH_NAME]


@pytest.mark.parametrize(
    "cli_args, expected",
    [
        pytest.param(
            make_mandatory_long_args(),
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
            ),
            id="Mandatory args, long form",
        ),
        pytest.param(
            make_mandatory_short_args(),
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
            ),
            id="Mandatory args, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--compose-file", "test-compose.yml"],
            make_context(
                docker_compose_path=Path("test-compose.yml").resolve(),
            ),
            id="Different compose file, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "-f", "test-compose.yml"],
            make_context(
                docker_compose_path=Path("test-compose.yml").resolve(),
            ),
            id="Different compose file, short form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--ingress-for-service", "my-service"],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                ingress_for_service="my-service",
            ),
            id="Ingress for service, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "-i", "my-service"],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                ingress_for_service="my-service",
            ),
            id="Ingress for service, short form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--extra-manifest", Path("extra-manifest.yml")],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                extra_manifest_path=Path("extra-manifest.yml").resolve(),
            ),
            id="Extra manifest, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--default-image", "my-image"],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                default_image="my-image",
            ),
            id="Default image, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--ingress-tls-file", Path("tls.yml")],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                ingress_tls_path=Path("tls.yml").resolve(),
            ),
            id="Ingress TLS file, long form",
        ),
        pytest.param(
            [
                *make_mandatory_long_args(),
                "--deployment-annotations-file",
                Path("annotations.yml"),
            ],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                deployment_annotations_path=Path("annotations.yml").resolve(),
            ),
            id="Deployment annotations file, long form",
        ),
        pytest.param(
            [*make_mandatory_long_args(), "--deployment-service-account-name", "my-account"],
            make_context(
                docker_compose_path=cli.DEFAULT_DOCKER_COMPOSE_FILENAME.resolve(),
                deployment_service_account_name="my-account",
            ),
            id="Deployment annotations file, long form",
        ),
    ],
)
def test_main(mocker: MockerFixture, cli_args: Sequence[str], expected: Context) -> None:
    """
    GIVEN CLI args
    WHEN parsing to a Context
    THEN is the expected
    """
    # GIVEN
    m_generate_manifest_from_docker_compose = mocker.patch(
        "komposer.cli.generate_manifest_from_docker_compose", return_value={}
    )

    runner = CliRunner()

    # WHEN
    actual = runner.invoke(cli.main, cli_args)

    # THEN
    print(actual.output)
    assert actual.exit_code == 0

    m_generate_manifest_from_docker_compose.assert_called_once_with(expected)
