import re

from yaml.parser import ParserError

from komposer.core.config_map import generate_config_maps
from komposer.core.deployment import generate_deployment
from komposer.core.extra_manifest import load_extra_manifest
from komposer.core.ingress import generate_ingress_from_services
from komposer.core.service import generate_services
from komposer.exceptions import (
    ComposePortsNotUniqueError,
    DeploymentAnnotationsInvaliYamlError,
    DeploymentAnnotationsNotAMappingError,
    IngressTlsInvalidYamlError,
    IngressTlsNotAListError,
    InvalidServiceNameError,
)
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.types.ports import Ports
from komposer.utils import as_json_object, parse_docker_compose_file

rfc_1123_re = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$")


def ensure_service_name_lowercase_RFC_1123(compose: docker_compose.DockerCompose) -> None:
    invalid_service_names = [
        service_name
        for service_name in compose.services.keys()
        if not rfc_1123_re.match(service_name)
    ]

    if invalid_service_names:
        raise InvalidServiceNameError(
            f"Invalid lowercase RFC-4122 service names detected: {invalid_service_names}"
        )


def ensure_unique_ports_on_docker_compose(compose: docker_compose.DockerCompose) -> None:
    non_unique_ports: dict[int, list[str]] = {}

    for service_name, service in compose.services.items():
        for port_str in service.ports:
            port = Ports.from_string(port_str).container

            non_unique_ports.setdefault(port, []).append(service_name)

    non_unique_ports = {
        port: service_names
        for port, service_names in non_unique_ports.items()
        if len(service_names) > 1
    }

    if non_unique_ports:
        raise ComposePortsNotUniqueError(f"Non-unique ports detected: {non_unique_ports}")


def ensure_ingress_tls_is_valid_yaml(context: Context) -> None:
    try:
        ingress_tls = context.ingress.tls
    except ParserError:
        raise IngressTlsInvalidYamlError("The Ingress TLS value is not a valid YAML")

    if ingress_tls is None:
        return

    if not isinstance(ingress_tls, list):
        raise IngressTlsNotAListError("The Ingress TLS value is not a list")


def ensure_deployment_annotations_is_valid_yaml(context: Context) -> None:
    try:
        deployment_annotations = context.deployment.annotations
    except ParserError:
        raise DeploymentAnnotationsInvaliYamlError(
            "The Deployment annotations value is not a valid YAML"
        )

    if deployment_annotations is None:
        return

    if not isinstance(deployment_annotations, dict):
        raise DeploymentAnnotationsNotAMappingError(
            "The Deployment annotations value is not a mapping"
        )


def generate_manifest_from_docker_compose(context: Context) -> dict:
    # Parse docker compose file
    compose = parse_docker_compose_file(context.docker_compose_path)

    # Ensures Docker Compose is supported
    ensure_deployment_annotations_is_valid_yaml(context)
    ensure_ingress_tls_is_valid_yaml(context)
    ensure_unique_ports_on_docker_compose(compose)
    ensure_service_name_lowercase_RFC_1123(compose)

    # Generate configmaps
    config_maps = generate_config_maps(context, compose)

    # Generate pod
    deployment = generate_deployment(context, compose.services)

    # Generate services
    services = generate_services(context, compose.services)

    # Generate ingress
    ingress = generate_ingress_from_services(context, compose.services)

    # Load external manifest
    extra_manifest = load_extra_manifest(context)

    # Return manifest
    items = [*config_maps, deployment, *services]

    if ingress:
        items.append(ingress)

    manifest = kubernetes.List(items=items)

    # Convert to JSON object so that we can append the extra manifest as is
    manifest_dict = as_json_object(manifest)
    manifest_dict["items"].extend(extra_manifest)

    return manifest_dict
