from komposer.core.container import generate_containers
from komposer.types import docker_compose, kubernetes
from komposer.types.cli import Context

LOCALHOST = "127.0.0.1"


def generate_host_aliases(services: docker_compose.Services) -> list[kubernetes.HostAlias]:
    if not services:
        return []

    host_names = [service_name for service_name in services.keys()]
    host_aliases = kubernetes.HostAlias(hostnames=host_names, ip=LOCALHOST)

    return [host_aliases]


def generate_deployment(
    context: Context, services: docker_compose.Services
) -> kubernetes.Deployment:
    host_aliases = generate_host_aliases(services)
    containers = generate_containers(context, services)
    metadata = kubernetes.Metadata.from_context_with_name(context, context.deployment.annotations)

    deployment = kubernetes.Deployment(
        metadata=metadata,
        spec=kubernetes.DeploymentSpec(
            selector=kubernetes.Selector(matchLabels=dict(metadata.labels)),
            template=kubernetes.Template(
                metadata=kubernetes.UnnamedMetadata(labels=dict(metadata.labels)),
                spec=kubernetes.TemplateSpec(
                    hostAliases=host_aliases,
                    containers=containers,
                    serviceAccountName=context.deployment.service_account_name,
                ),
            ),
        ),
    )

    return deployment
