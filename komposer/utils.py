import json
import shlex
from pathlib import Path
from typing import Any, Optional, Union, cast

import stringcase
import yaml
from dotenv import dotenv_values
from pydantic import BaseModel

from komposer.types import docker_compose


def to_kubernetes_name(string: str) -> str:
    name: str = stringcase.spinalcase(string.strip().lower().replace("/", "-").replace(":", "-"))

    if name.startswith("-"):
        name = name[1:]

    return name


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.open())


def parse_docker_compose_file(compose_path: Path) -> docker_compose.DockerCompose:
    content = load_yaml(compose_path)
    config = docker_compose.DockerCompose.parse_obj(content)

    return config


def parse_env_file(env_file: Path) -> dict[str, Optional[str]]:
    environment = dotenv_values(env_file)

    return environment


def command_to_args(command: Optional[Union[str, list[str]]]) -> Optional[list[str]]:
    if isinstance(command, str):
        return shlex.split(command)

    return command


def as_json_object(type_: BaseModel) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(type_.json(by_alias=True)))
