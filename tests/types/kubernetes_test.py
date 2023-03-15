import pytest

from komposer.types.cli import Context
from komposer.types.kubernetes import (
    ContainerPort,
    EnvironmentVariable,
    Labels,
    Metadata,
    ServicePort,
    ServiceRefPort,
)
from komposer.utils import to_kubernetes_name
from tests.fixtures import TEST_BRANCH_NAME, TEST_REPOSITORY_NAME, make_context


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param(
            "8080",
            ContainerPort(containerPort=8080),
            id="Single port",
        ),
        pytest.param(
            "8080:8080",
            ContainerPort(containerPort=8080),
            id="host:container that matches",
        ),
        pytest.param(
            "5434:5432",
            ContainerPort(containerPort=5432, hostPort=5434),
            id="Different host:container ports",
        ),
    ],
)
def test_container_port_from_string(string: str, expected: ContainerPort) -> None:
    """
    GIVEN a Docker port as a string
    WHEN parsing to a Kubernetes port
    THEN is the expected
    """
    # WHEN
    actual = ContainerPort.from_string(string)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param(
            "8080",
            ServicePort(name="8080", port=8080, targetPort=8080),
            id="Single port",
        ),
        pytest.param(
            "8080:8080",
            ServicePort(name="8080-8080", port=8080, targetPort=8080),
            id="host:container that matches",
        ),
        pytest.param(
            "5434:5432",
            ServicePort(name="5434-5432", port=5434, targetPort=5432),
            id="Different host:container ports",
        ),
    ],
)
def test_service_port_from_string(string: str, expected: ServicePort) -> None:
    """
    GIVEN a Docker port as a string
    WHEN parsing to a Kubernetes port
    THEN is the expected
    """
    # WHEN
    actual = ServicePort.from_string(string)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param("", []),
        pytest.param("MY_VAR=my-value", [EnvironmentVariable(name="MY_VAR", value="my-value")]),
        pytest.param("MY_VAR", [EnvironmentVariable(name="MY_VAR", value=None)]),
    ],
)
def test_environment_variable_from_string(
    string: str, expected: list[EnvironmentVariable]
) -> None:
    """
    GIVEN a string representing a env variable
    WHEN parsing the string
    THEN return a list of EnvironmentVariable
    """
    # WHEN
    actual = list(EnvironmentVariable.from_string(string))

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param("8080", ServiceRefPort(number=8080), id="Single port"),
        pytest.param("8080:8080", ServiceRefPort(number=8080), id="host:container that matches"),
    ],
)
def test_service_ref_port_from_string(string: str, expected: ServiceRefPort) -> None:
    """
    GIVEN a Docker port as a string
    WHEN parsing to a Kubernetes port
    THEN is the expected
    """
    # WHEN
    actual = ServiceRefPort.from_string(string)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "context, expected",
    [
        pytest.param(
            make_context(),
            {
                "repository": to_kubernetes_name(TEST_REPOSITORY_NAME),
                "branch": to_kubernetes_name(TEST_BRANCH_NAME),
            },
            id="Default values",
        ),
    ],
)
def test_metadata_labels_from_context(context: Context, expected: Labels) -> None:
    """
    GIVEN a context
    WHEN returning the Metadata labels
    THEN matches the expected
    """
    # WHEN
    actual = Metadata.labels_from_context(context)

    # THEN
    assert actual == expected
