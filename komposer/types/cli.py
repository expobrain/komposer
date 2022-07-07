import re
from pathlib import Path
from typing import Any, Optional

from pydantic import validator

from komposer.types.base import ImmutableBaseModel
from komposer.utils import load_yaml

RFC_1123_MAX_LENGTH = 63

rfc_1123_re = re.compile(r"^[a-z][a-z\-0-9]*[a-z]$")


def ensure_is_rfc_1123(string: str) -> None:
    if not rfc_1123_re.match(string):
        raise ValueError("Not a valid RFC-1123 string")

    if len(string) > RFC_1123_MAX_LENGTH:
        raise ValueError("String is longer than 63 characters")


class DeploymentContext(ImmutableBaseModel):
    annotations_path: Optional[Path] = None
    service_account_name: Optional[str] = None

    @property
    def annotations(self) -> Optional[Any]:
        return None if self.annotations_path is None else load_yaml(self.annotations_path)


class IngressContext(ImmutableBaseModel):
    tls_path: Optional[Path] = None

    @property
    def tls(self) -> Optional[Any]:
        return None if self.tls_path is None else load_yaml(self.tls_path)


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

    @validator("project_name")
    def project_name_matches_kubernetes_name(cls, value: str) -> str:
        ensure_is_rfc_1123(value)

        return value

    @validator("branch_name")
    def branch_name_matches_kubernetes_name(cls, value: str) -> str:
        ensure_is_rfc_1123(value)

        return value

    @validator("repository_name")
    def repository_name_matches_kubernetes_name(cls, value: str) -> str:
        ensure_is_rfc_1123(value)

        return value

    @property
    def manifest_prefix(self) -> str:
        return "-".join([self.project_name, self.repository_name, self.branch_name])
