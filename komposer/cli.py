from pathlib import Path
from typing import Optional

import click
import yaml

from komposer.core.base import generate_manifest_from_docker_compose
from komposer.types import kubernetes
from komposer.types.cli import Context

DEFAULT_DOCKER_COMPOSE_FILENAME = Path("docker-compose.yml")
DEFAULT_PROJECT_NAME = "default"
DEFAULT_DOCKER_IMAGE = "${IMAGE}"


def output_manifest(manifest: kubernetes.List) -> None:
    content = yaml.safe_load(manifest.json(by_alias=True))
    output = yaml.safe_dump(content)

    print(output)


@click.command()
@click.option(
    "--compose-file",
    "-f",
    default=DEFAULT_DOCKER_COMPOSE_FILENAME,
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
    help=f"Path to the Docker compose file. Default is {DEFAULT_DOCKER_COMPOSE_FILENAME}.",
)
@click.option(
    "--project-name",
    "-p",
    default=DEFAULT_PROJECT_NAME,
    help=f"Name of the project. Default value is `{DEFAULT_PROJECT_NAME}`",
)
@click.option(
    "--repository-name", "-r", required=True, help="Name of the repository of this project"
)
@click.option("--branch-name", "-b", required=True, help="Name of the branch going to be deployed")
@click.option(
    "--ingress-for-service", "-i", help="Name of the service to have an ingress associated to it"
)
@click.option(
    "--extra-manifest",
    "-e",
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True, path_type=Path),
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
    "--ingress-tls",
    help=(
        "Specify the Ingress' TLS configuration as a JSON object. "
        "It's your responsibility to make sure that it's a valid Kubernetes config."
    ),
)
def main(
    compose_file: Path,
    project_name: str,
    repository_name: str,
    branch_name: str,
    default_image: str,
    ingress_for_service: Optional[str] = None,
    extra_manifest: Optional[Path] = None,
    ingress_tls: Optional[str] = None,
) -> None:
    context = Context(
        docker_compose_path=compose_file,
        project_name=project_name,
        branch_name=branch_name,
        repository_name=repository_name,
        default_image=default_image,
        ingress_for_service=ingress_for_service,
        extra_manifest_path=extra_manifest,
        ingress_tls_str=ingress_tls,
    )

    manifest_data = generate_manifest_from_docker_compose(context)

    output_manifest(manifest_data)


if __name__ == "__main__":
    main()
