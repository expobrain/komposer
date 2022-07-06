from pathlib import Path
from typing import Optional, Union

from komposer.types.base import ImmutableBaseModel

EnvironmentMap = dict[str, Optional[str]]

EnvironmentArray = list[str]

Environment = Union[EnvironmentMap, EnvironmentArray]


class Service(ImmutableBaseModel):
    image: Optional[str] = None
    ports: list[str] = []
    command: Optional[Union[str, list[str]]] = None
    env_file: Optional[Path] = None
    environment: Optional[Environment] = None


Services = dict[str, Service]


class DockerCompose(ImmutableBaseModel):
    services: Services
