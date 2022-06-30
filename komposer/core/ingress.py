from typing import Optional

from komposer.exceptions import ServiceNotFoundError
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context
from komposer.utils import to_kubernetes_name

DEFAULT_INGRESS_ANNOTATIONS: kubernetes.Annotations = {
    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
}
DEFAULT_CLUSTER_NAME = "svc.cluster.local"


def generate_ingress_path(
    context: Context, service_name: str, service_port: str
) -> kubernetes.HttpPath:
    service_ref_port = kubernetes.ServiceRefPort.from_string(service_port)
    service_name_kubernetes = to_kubernetes_name(service_name)

    http_path = kubernetes.HttpPath(
        path="/",
        pathType=kubernetes.PathType.PREFIX,
        backend=kubernetes.Backend(
            service=kubernetes.ServiceRef(
                name=f"{context.manifest_prefix}-{service_name_kubernetes}",
                port=service_ref_port,
            )
        ),
    )

    return http_path


def generate_ingress_host(context: Context) -> str:
    if context.ingress_for_service is None:
        raise ValueError("Context.ingress_for_service is None")

    return ".".join(
        [
            to_kubernetes_name(context.ingress_for_service),
            context.manifest_prefix,
            DEFAULT_CLUSTER_NAME,
        ]
    )


def generate_ingress_from_services(
    context: Context, services: docker_compose.Services
) -> Optional[kubernetes.Ingress]:
    if context.ingress_for_service is None:
        return None

    if context.ingress_for_service not in services:
        raise ServiceNotFoundError(f"Service {context.ingress_for_service} not found")

    service = services[context.ingress_for_service]
    metadata = kubernetes.Metadata.from_context_with_suffix(
        context, context.ingress_for_service, annotations=DEFAULT_INGRESS_ANNOTATIONS
    )
    host = generate_ingress_host(context)
    paths = [
        generate_ingress_path(context, context.ingress_for_service, port) for port in service.ports
    ]

    ingress = kubernetes.Ingress(
        metadata=metadata,
        spec=kubernetes.IngressSpec(
            rules=[kubernetes.IngressRule(host=host, http=kubernetes.HttpPaths(paths=paths))],
            tls=context.ingress.tls,
        ),
    )

    return ingress
