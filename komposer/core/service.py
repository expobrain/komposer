from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context


def generate_service_ports(ports: list[str]) -> list[kubernetes.ServicePort]:
    return [kubernetes.ServicePort.from_string(port) for port in ports]


def generate_service(
    context: Context, service_name: str, service: docker_compose.Service
) -> kubernetes.Service:
    metadata = kubernetes.Metadata.from_context_with_suffix(context, service_name)
    k8s_service = kubernetes.Service(
        metadata=metadata,
        spec=kubernetes.ServiceSpec(
            ports=generate_service_ports(service.ports), selector=metadata.labels
        ),
    )

    return k8s_service


def generate_services(
    context: Context, services: docker_compose.Services
) -> list[kubernetes.Service]:
    return [
        generate_service(context, service_name, service)
        for service_name, service in services.items()
        if service.ports
    ]
