import pytest

from komposer.types.docker_compose import RestartPolicy, Service


@pytest.mark.parametrize("restart_policy", list(RestartPolicy))
def test_service_restart_policy(restart_policy: RestartPolicy) -> None:
    """
    GIVEN a restart policy
    WHEN parsing the service
    THEN matches the expected
    """
    # GIVEN
    service_dict = {"restart": restart_policy.value}

    # WHEN
    service = Service.parse_obj(service_dict)

    # THEN
    assert service.restart == restart_policy


def test_service_restart_policy_missing() -> None:
    """
    GIVEN no restart policy
    WHEN parsing the service
    THEN restart policy is null
    """
    # WHEN
    service = Service.parse_obj({})

    # THEN
    assert service.restart is None
