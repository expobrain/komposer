from pathlib import Path
from typing import Any, Optional

import yaml

from komposer.types.base import ImmutableBaseModel
from komposer.utils import to_kubernetes_name


class Context(ImmutableBaseModel):
    docker_compose_path: Path
    project_name: str
    branch_name: str
    repository_name: str
    default_image: str
    ingress_for_service: Optional[str] = None
    extra_manifest_path: Optional[Path] = None
    ingress_tls_str: Optional[str] = None
    deployment_annotations_str: Optional[str] = None

    @staticmethod
    def __parse_str_as_yaml(value_str: Optional[str]) -> Any:
        if value_str is None:
            return None

        value = yaml.safe_load(value_str)

        return value

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

    @property
    def ingress_tls(self) -> Optional[Any]:
        return self.__parse_str_as_yaml(self.ingress_tls_str)

    @property
    def deployment_annotations(self) -> Optional[Any]:
        return self.__parse_str_as_yaml(self.deployment_annotations_str)
