import re
from pathlib import Path
from typing import Any, Optional

from pydantic import validator

from komposer.types.base import ImmutableBaseModel
from komposer.utils import load_yaml

lowercase_kebak_re = re.compile(r"^[a-z0-9][a-z\-0-9]*[a-z0-9]$")


def ensure_lowercase_kebab(string: str) -> None:
    if not lowercase_kebak_re.match(string):
        raise ValueError("Not a lowercase kebab string")


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
    branch_name: str
    repository_name: str
    default_image: str
    project_name: Optional[str] = None
    ingress_for_service: Optional[str] = None
    extra_manifest_paths: list[Path]
    deployment: DeploymentContext
    ingress: IngressContext

    @validator("project_name")
    def project_name_matches_kubernetes_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            ensure_lowercase_kebab(value)

        return value

    @validator("branch_name")
    def branch_name_matches_kubernetes_name(cls, value: str) -> str:
        ensure_lowercase_kebab(value)

        return value

    @validator("repository_name")
    def repository_name_matches_kubernetes_name(cls, value: str) -> str:
        ensure_lowercase_kebab(value)

        return value

    @property
    def manifest_prefix(self) -> str:
        fragments = [self.project_name, self.repository_name, self.branch_name]
        fragments_filtered = [fragment for fragment in fragments if fragment is not None]

        manifest_prefix = "-".join(fragments_filtered)

        return manifest_prefix
