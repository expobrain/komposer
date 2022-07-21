from collections.abc import Sequence
from pathlib import Path
from typing import Optional

import click

from komposer.core.base import generate_manifest_from_docker_compose
from komposer.types.cli import Context, DeploymentContext, IngressContext
from komposer.utils import dump_yaml

DEFAULT_DOCKER_COMPOSE_FILENAME = Path("docker-compose.yml")
DEFAULT_DOCKER_IMAGE = "${IMAGE}"


def output_raw_manifest(manifest: dict) -> None:
    output = dump_yaml(manifest)

    print(output)


@click.command()
@click.option(
    "--compose-file",
    "-f",
    default=DEFAULT_DOCKER_COMPOSE_FILENAME,
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help=f"Path to the Docker compose file. Default is {DEFAULT_DOCKER_COMPOSE_FILENAME}.",
)
@click.option("--project-name", "-p", help="Name of the project")
@click.option(
    "--repository-name", "-r", required=True, help="Name of the repository of this project"
)
@click.option("--branch-name", "-b", required=True, help="Name of the branch going to be deployed")
@click.option(
    "--ingress-for-service", "-i", help="Name of the service to have an ingress associated to it"
)
@click.option(
    "--extra-manifest",
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    multiple=True,
    help=(
        "Path to an extra manifest file with custom items to be merged. "
        "The manifest must be in a format where the root element is a Kubernetes List node. "
        "The branch and repository labels will be added to each item; "
        "each item's name will be prefixed with the computed prefix of the generated manifest"
    ),
)
@click.option(
    "--default-image",
    default=DEFAULT_DOCKER_IMAGE,
    help=(
        "Default image to be used for those Docker Compose services whom don't have the image set. "  # noqa: E501
        f"Default is {DEFAULT_DOCKER_IMAGE}"
    ),
)
@click.option(
    "--ingress-tls-file",
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help=(
        "Specify the filename containing the Ingress' TLS configuration as a YAML list. "
        "It's your responsibility to make sure that it's a valid Kubernetes config fragment. "
    ),
)
@click.option(
    "--deployment-annotations-file",
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help=(
        "Specify the filename containing the extra Deployment's annotaions as a YAML object. "
        "It's your responsibility to make sure that it's a valid Kubernetes config fragment. "
    ),
)
@click.option(
    "--deployment-service-account-name", help="Service account name to be used for the Deployment."
)
def main(
    compose_file: Path,
    project_name: str,
    repository_name: str,
    branch_name: str,
    default_image: str,
    extra_manifest: Sequence[Path],
    ingress_for_service: Optional[str] = None,
    ingress_tls_file: Optional[Path] = None,
    deployment_annotations_file: Optional[Path] = None,
    deployment_service_account_name: Optional[Path] = None,
) -> None:
    context = Context(
        docker_compose_path=compose_file,
        project_name=project_name,
        branch_name=branch_name,
        repository_name=repository_name,
        default_image=default_image,
        ingress_for_service=ingress_for_service,
        extra_manifest_paths=extra_manifest,
        ingress=IngressContext(tls_path=ingress_tls_file),
        deployment=DeploymentContext(
            annotations_path=deployment_annotations_file,
            service_account_name=deployment_service_account_name,
        ),
    )

    manifest_data = generate_manifest_from_docker_compose(context)

    output_raw_manifest(manifest_data)


if __name__ == "__main__":
    main()
