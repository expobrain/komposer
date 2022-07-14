from __future__ import annotations

from collections.abc import Iterable
from enum import Enum, unique
from io import StringIO
from ipaddress import IPv4Address
from pathlib import Path
from typing import Literal, Optional, Union

from dotenv import dotenv_values
from pydantic import Field

from komposer.types.base import CamelCaseImmutableBaseModel
from komposer.types.cli import Context
from komposer.types.ports import Ports
from komposer.utils import to_kubernetes_name

Labels = dict[str, Optional[str]]
Annotations = dict[str, Optional[str]]


@unique
class ImagePullPolicy(Enum):
    IF_NOT_PRESENT = "IfNotPresent"
    ALWAYS = "Always"
    NEVER = "Never"


@unique
class PathType(Enum):
    IMPLEMENTATION_SPECIFIC = "ImplementationSpecific"
    EXACT = "Exact"
    PREFIX = "Prefix"


class UnnamedMetadata(CamelCaseImmutableBaseModel):
    labels: Labels = {}
    annotations: Optional[Annotations] = None


class Metadata(UnnamedMetadata):
    name: str

    @staticmethod
    def labels_from_context(context: Context) -> Labels:
        return {
            "repository": context.repository_name,
            "branch": context.branch_name,
        }

    @staticmethod
    def from_context(context: Context, annotations: Optional[Annotations] = None) -> Metadata:
        return Metadata(labels=Metadata.labels_from_context(context), annotations=annotations)

    @staticmethod
    def from_context_with_suffix(
        context: Context, suffix: str, annotations: Optional[Annotations] = None
    ) -> Metadata:
        name = f"{context.manifest_prefix}-{to_kubernetes_name(suffix)}"
        labels = Metadata.labels_from_context(context)

        return Metadata(name=name, labels=labels, annotations=annotations)

    @staticmethod
    def from_context_with_name(
        context: Context, annotations: Optional[Annotations] = None
    ) -> Metadata:
        return Metadata(
            name=context.manifest_prefix,
            labels=Metadata.labels_from_context(context),
            annotations=annotations,
        )


class Item(CamelCaseImmutableBaseModel):
    api_version: str
    kind: str
    metadata: Metadata


class ConfigMap(Item):
    api_version: Literal["v1"] = "v1"
    kind: Literal["ConfigMap"] = "ConfigMap"
    metadata: Metadata
    data: dict[str, Optional[str]]


class Selector(CamelCaseImmutableBaseModel):
    match_labels: Labels = {}


class HostAlias(CamelCaseImmutableBaseModel):
    ip: IPv4Address
    hostnames: list[str] = []


class ConfigMapKeyRef(CamelCaseImmutableBaseModel):
    key: str
    name: str


class ConfigMapEnvironmentVariable(CamelCaseImmutableBaseModel):
    name: str
    value_from: ConfigMapKeyRef

    @staticmethod
    def from_env_file(
        prefix: str, docker_compose_path: Path, relative_env_file_path: Path
    ) -> Iterable[ConfigMapEnvironmentVariable]:
        env_file = docker_compose_path / relative_env_file_path
        env_vars = dotenv_values(env_file)
        config_map_name = f"{prefix}-{to_kubernetes_name(str(relative_env_file_path))}"
        keys = sorted(env_vars.keys())

        for key in keys:
            yield ConfigMapEnvironmentVariable(
                name=key, valueFrom=ConfigMapKeyRef(key=key, name=config_map_name)
            )


class EnvironmentVariable(CamelCaseImmutableBaseModel):
    name: str
    value: Optional[str]

    @staticmethod
    def from_string(string: str) -> Iterable[EnvironmentVariable]:
        env_vars = dotenv_values(stream=StringIO(string))
        items = sorted(env_vars.items())

        for key, value in items:
            yield EnvironmentVariable(name=key, value=value)


class ContainerPort(CamelCaseImmutableBaseModel):
    container_port: int
    host_port: Optional[int] = None

    @staticmethod
    def from_string(string: str) -> ContainerPort:
        ports = Ports.from_string(string)

        if ports.same_ports():
            return ContainerPort(containerPort=ports.container)

        return ContainerPort(containerPort=ports.container, hostPort=ports.host)


class Container(CamelCaseImmutableBaseModel):
    image_pull_policy: ImagePullPolicy = ImagePullPolicy.IF_NOT_PRESENT
    image: str
    name: str
    args: Optional[list[str]] = None
    env: list[Union[EnvironmentVariable, ConfigMapEnvironmentVariable]] = []
    ports: Optional[list[ContainerPort]] = []


class TemplateSpec(CamelCaseImmutableBaseModel):
    service_account_name: Optional[str] = None
    host_aliases: list[HostAlias] = []
    containers: list[Container] = []


class Template(CamelCaseImmutableBaseModel):
    metadata: UnnamedMetadata
    spec: TemplateSpec


class DeploymentSpec(CamelCaseImmutableBaseModel):
    replicas: int = Field(1, ge=1)
    selector: Selector
    template: Template


class Deployment(Item):
    api_version: Literal["apps/v1"] = "apps/v1"
    kind: Literal["Deployment"] = "Deployment"
    metadata: Metadata
    spec: DeploymentSpec


class ServicePort(CamelCaseImmutableBaseModel):
    name: str
    port: int
    target_port: int

    @staticmethod
    def from_string(string: str) -> ServicePort:
        ports = Ports.from_string(string)
        name = to_kubernetes_name(string)

        return ServicePort(name=name, targetPort=ports.container, port=ports.host)


class ServiceSpec(CamelCaseImmutableBaseModel):
    ports: list[ServicePort] = []
    selector: Labels


class Service(Item):
    api_version: Literal["v1"] = "v1"
    kind: Literal["Service"] = "Service"
    metadata: Metadata
    spec: ServiceSpec


class IngressTls(CamelCaseImmutableBaseModel):
    hosts: list[str]
    secret_name: str


class ServiceRefPort(CamelCaseImmutableBaseModel):
    number: int

    @staticmethod
    def from_string(string: str) -> ServiceRefPort:
        ports = Ports.from_string(string)

        return ServiceRefPort(number=ports.host)


class ServiceRef(CamelCaseImmutableBaseModel):
    name: str
    port: ServiceRefPort


class Backend(CamelCaseImmutableBaseModel):
    service: ServiceRef


class HttpPath(CamelCaseImmutableBaseModel):
    path: Path
    path_type: PathType
    backend: Backend


class HttpPaths(CamelCaseImmutableBaseModel):
    paths: list[HttpPath]


class IngressRule(CamelCaseImmutableBaseModel):
    host: str
    http: HttpPaths


class IngressSpec(CamelCaseImmutableBaseModel):
    ingress_class_name: str = "nginx-internal"
    tls: Optional[list[IngressTls]] = None
    rules: list[IngressRule] = []


class Ingress(Item):
    api_version: Literal["networking.k8s.io/v1"] = "networking.k8s.io/v1"
    kind: Literal["Ingress"] = "Ingress"
    metadata: Metadata
    spec: IngressSpec


class List(CamelCaseImmutableBaseModel):
    api_version: Literal["v1"] = "v1"
    kind: Literal["List"] = "List"
    # We should be able to use Field(..., discriminator="kind") here
    items: list[Item] = []
