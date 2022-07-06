import itertools
from typing import Literal

from pydantic import parse_obj_as

from komposer.types import kubernetes
from komposer.types.base import CamelCaseImmutableBaseModel
from komposer.types.cli import Context
from komposer.utils import load_yaml


def _komposer_service_prefix_value(context: Context) -> str:
    return context.manifest_prefix


komposer_env_variables_map = {"${KOMPOSER_SERVICE_PREFIX}": _komposer_service_prefix_value}


class ExtraManifest(CamelCaseImmutableBaseModel):
    api_version: Literal["v1"] = "v1"
    kind: Literal["List"] = "List"
    items: list[kubernetes.Item] = []


def update_item_metadata_labels(item: dict, labels: dict) -> None:
    item["metadata"].setdefault("labels", {}).update(labels)


def update_item_metadata_name(item: dict, manifest_prefix: str) -> None:
    item["metadata"]["name"] = f"{manifest_prefix}-{item['metadata']['name']}"


def update_item_env_configmapkeyref_name(item: dict, manifest_prefix: str) -> None:
    containers = item.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    envs = itertools.chain(*(container.get("env", []) for container in containers))
    config_map_key_refs = (env.get("valueFrom", {}).get("configMapKeyRef", {}) for env in envs)

    for config_map_key_ref in config_map_key_refs:
        config_map_key_ref["name"] = f"{manifest_prefix}-{config_map_key_ref['name']}"


def replace_env_variables(context: Context, extra_manifest_str: str) -> str:
    for env_name, env_fn in komposer_env_variables_map.items():
        env_value = env_fn(context)
        extra_manifest_str = extra_manifest_str.replace(env_name, env_value)

    return extra_manifest_str


def load_extra_manifest(context: Context) -> list[dict]:
    # Skip if no extra manifest
    if context.extra_manifest_path is None:
        return []

    # Load manifest
    extra_manifest_str = context.extra_manifest_path.read_text()

    # Replace KOMPOSER_* env variables
    extra_manifest_str = replace_env_variables(context, extra_manifest_str)

    # Parse manifest
    extra_manifest_raw = load_yaml(extra_manifest_str)

    # just validate that the format of the file
    parse_obj_as(ExtraManifest, extra_manifest_raw)

    # this is necessary because we need to manipulate the original item
    # and the item can be undefined in our list of types
    extra_manifest_items: list[dict] = extra_manifest_raw.get("items", [])

    # Update metadate labels and names and env's configmap names
    labels = kubernetes.Metadata.labels_from_context(context)
    manifest_prefix = context.manifest_prefix

    for item in extra_manifest_items:
        update_item_metadata_labels(item, labels)
        update_item_metadata_name(item, manifest_prefix)
        update_item_env_configmapkeyref_name(item, manifest_prefix)

    return extra_manifest_items
