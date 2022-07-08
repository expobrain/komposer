import json
import shlex
from pathlib import Path
from typing import Any, Optional, Union, cast

import stringcase
import yaml
from dotenv import dotenv_values
from pydantic import BaseModel

from komposer.types import docker_compose


def str_presenter(dumper: yaml.representer.SafeRepresenter, data: Any) -> yaml.nodes.Node:
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


def to_kubernetes_name(string: str) -> str:
    name: str = stringcase.spinalcase(string.strip().lower().replace("/", "-").replace(":", "-"))

    if name.startswith("-"):
        name = name[1:]

    return name


def load_yaml(source: Union[Path, str]) -> Any:
    if isinstance(source, Path):
        source = source.read_text()

    content = yaml.safe_load(source)

    return content


def dump_yaml(data: Any) -> str:
    output: str = yaml.safe_dump(data)

    return output


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
