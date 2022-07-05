from enum import Enum, unique
from pathlib import Path
from typing import Optional, Union

from komposer.types.base import ImmutableBaseModel

EnvironmentMap = dict[str, Optional[str]]

EnvironmentArray = list[str]

Environment = Union[EnvironmentMap, EnvironmentArray]


@unique
class RestartPolicy(Enum):
    NO = "no"
    ALWAYS = "always"
    ON_FAILURE = "on-failure"
    UNLESS_STOPPED = "unless-stopped"


class Service(ImmutableBaseModel):
    image: Optional[str] = None
    restart: Optional[RestartPolicy] = None
    ports: list[str] = []
    command: Optional[Union[str, list[str]]] = None
    env_file: Optional[Path] = None
    environment: Optional[Environment] = None


Services = dict[str, Service]


class DockerCompose(ImmutableBaseModel):
    services: Services
