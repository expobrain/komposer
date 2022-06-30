from pathlib import Path
from typing import Any, Optional

import yaml

from komposer.types.base import ImmutableBaseModel
from komposer.utils import to_kubernetes_name


def parse_str_as_yaml(value_str: Optional[str]) -> Any:
    if value_str is None:
        return None

    value = yaml.safe_load(value_str)

    return value


class DeploymentContext(ImmutableBaseModel):
    annotations_str: Optional[str] = None
    service_account_name: Optional[str] = None

    @property
    def annotations(self) -> Optional[Any]:
        return parse_str_as_yaml(self.annotations_str)


class IngressContext(ImmutableBaseModel):
    tls_str: Optional[str] = None

    @property
    def tls(self) -> Optional[Any]:
        return parse_str_as_yaml(self.tls_str)


class Context(ImmutableBaseModel):
    docker_compose_path: Path
    project_name: str
    branch_name: str
    repository_name: str
    default_image: str
    ingress_for_service: Optional[str] = None
    extra_manifest_path: Optional[Path] = None
    deployment: DeploymentContext
    ingress: IngressContext

    @property
    def project_name_kubernetes(self) -> str:
        return to_kubernetes_name(self.project_name)

    @property
    def branch_name_kubernetes(self) -> str:
        return to_kubernetes_name(self.branch_name)

    @property
    def repository_name_kubernetes(self) -> str:
        return to_kubernetes_name(self.repository_name)

    @property
    def manifest_prefix(self) -> str:
        return "-".join(
            [
                self.project_name_kubernetes,
                self.repository_name_kubernetes,
                self.branch_name_kubernetes,
            ]
        )
