import itertools
from pathlib import Path
from typing import Iterable, Union

from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.utils import command_to_args, to_kubernetes_name


def generate_container_environment_from_environment(
    environment: docker_compose.Environment,
) -> Iterable[kubernetes.EnvironmentVariable]:
    env_vars_iter = (
        kubernetes.EnvironmentVariable.from_string(env_var) for env_var in environment
    )
    env_vars = itertools.chain(*env_vars_iter)

    return env_vars


def generate_container_environment_from_env_file(
    context: Context, env_file: Path
) -> Iterable[kubernetes.ConfigMapEnvironmentVariable]:
    env_vars = kubernetes.ConfigMapEnvironmentVariable.from_env_file(
        context.manifest_prefix, context.docker_compose_path.parent, env_file
    )

    return env_vars


def generate_container_environment(
    context: Context, service: docker_compose.Service
) -> Iterable[Union[kubernetes.EnvironmentVariable, kubernetes.ConfigMapEnvironmentVariable]]:
    if service.environment:
        return generate_container_environment_from_environment(service.environment)

    if service.env_file:
        return generate_container_environment_from_env_file(context, service.env_file)

    return []


def generate_containter_ports(ports: list[str]) -> list[kubernetes.ContainerPort]:
    return [kubernetes.ContainerPort.from_string(port) for port in ports]


def generate_container(
    context: Context, service_name: str, service: docker_compose.Service
) -> kubernetes.Container:
    return kubernetes.Container(
        image=service.image or context.default_image,
        name=to_kubernetes_name(service_name),
        args=command_to_args(service.command),
        env=list(generate_container_environment(context, service)),
        ports=generate_containter_ports(service.ports),
    )


def generate_containers(
    context: Context, services: docker_compose.Services
) -> list[kubernetes.Container]:
    return [
        generate_container(context, service_name, service)
        for service_name, service in services.items()
    ]
