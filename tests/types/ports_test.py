import pytest

from komposer.types.ports import Ports


@pytest.mark.parametrize(
    "string, expected",
    [
        pytest.param("8080", Ports(container=8080, host=8080), id="Single port"),
        pytest.param(
            "8080:8080", Ports(container=8080, host=8080), id="host:container that matches"
        ),
        pytest.param(
            "5434:5432", Ports(container=5432, host=5434), id="Different host:container ports"
        ),
    ],
)
def test_ports_from_string(string: str, expected: Ports) -> None:
    """
    GIVEN a Docker port as a string
    WHEN parsing to a Kubernetes port
    THEN is the expected
    """
    # WHEN
    actual = Ports.from_string(string)

    # THEN
    assert actual == expected


@pytest.mark.parametrize(
    "ports, expected",
    [
        pytest.param(Ports(container=8080, host=8080), True, id="Same ports"),
        pytest.param(Ports(container=8080, host=9000), False, id="Different ports"),
    ],
)
def test_ports_same_ports(ports: Ports, expected: bool) -> None:
    """
    GIVEN two ports
    WHEN checking if they are the same
    THEN returns expected
    """
    # WHEN
    actual = ports.same_ports()

    # THEN
    assert actual == expected
