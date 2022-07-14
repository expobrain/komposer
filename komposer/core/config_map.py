from collections.abc import Iterable
from io import StringIO
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values

from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.utils import parse_env_file, to_kubernetes_name


def _generate_config_map_from_environment(
    context: Context, service_name: str, environment: docker_compose.Environment
) -> kubernetes.ConfigMap:
    if isinstance(environment, list):
        stream = StringIO("\n".join(environment))
        environment = dotenv_values(stream=stream)

    name = to_kubernetes_name(service_name)

    config_map = kubernetes.ConfigMap(
        metadata=kubernetes.Metadata.from_context_with_suffix(context, name), data=environment
    )

    return config_map


def _generate_config_map_from_env_file(
    context: Context, env_file: Path
) -> Optional[kubernetes.ConfigMap]:
    env_file_full_path = (context.docker_compose_path.parent / env_file).resolve()
    env_vars = parse_env_file(env_file_full_path)

    if not env_vars:
        return None

    name = to_kubernetes_name(env_file.name)

    config_map = kubernetes.ConfigMap(
        metadata=kubernetes.Metadata.from_context_with_suffix(context, name), data=env_vars
    )

    return config_map


def generate_config_maps(
    context: Context, compose: docker_compose.DockerCompose
) -> Iterable[kubernetes.ConfigMap]:
    config_maps = {}

    for service_name, service in compose.services.items():
        if service.env_file:
            config_map = _generate_config_map_from_env_file(context, service.env_file)
        elif service.environment:
            config_map = _generate_config_map_from_environment(
                context, service_name, service.environment
            )
        else:
            config_map = None

        if config_map:
            config_maps[config_map.metadata.name] = config_map

    return config_maps.values()
