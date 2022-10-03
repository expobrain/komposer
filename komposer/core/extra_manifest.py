import itertools
from collections.abc import Mapping, Sequence
from typing import Any, Union

from komposer.exceptions import (
    ExtraManifestInvalidYamlError,
    ExtraManifestMissingMetadataError,
    ExtraManifestMissingNameError,
)
from komposer.types import kubernetes
from komposer.types.cli import Context
from komposer.utils import load_yaml


def update_item_metadata_labels(item: Mapping, labels: Mapping) -> None:
    item["metadata"].setdefault("labels", {}).update(labels)


def update_item_metadata_name(item: Mapping, manifest_prefix: str) -> None:
    item["metadata"]["name"] = f"{manifest_prefix}-{item['metadata']['name']}"


def update_item_env_configmapkeyref_name(item: Mapping, manifest_prefix: str) -> None:
    containers = item.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    envs = itertools.chain(*(container.get("env", []) for container in containers))
    config_map_key_refs = (env.get("valueFrom", {}).get("configMapKeyRef") for env in envs)
    config_map_key_refs = (
        config_map_key_ref for config_map_key_ref in config_map_key_refs if config_map_key_ref
    )

    for config_map_key_ref in config_map_key_refs:
        config_map_key_ref["name"] = f"{manifest_prefix}-{config_map_key_ref['name']}"


def get_items_from_extra_manifest(extra_manifest_raw: Union[Mapping, Sequence]) -> list[dict]:
    # Returns empty list if null
    if extra_manifest_raw is None:
        return []

    # Returns if it's a list
    if isinstance(extra_manifest_raw, list):
        return extra_manifest_raw

    # Returns if it's a object
    if isinstance(extra_manifest_raw, dict):
        if extra_manifest_raw.get("kind") == "List":
            return extra_manifest_raw.get("items", [])

        return [extra_manifest_raw]

    # Not uspported
    raise ExtraManifestInvalidYamlError(
        f"Unsupported extra manifest type: {type(extra_manifest_raw)}"
    )


def ensure_metadata_is_present(extra_manifest_items: Sequence[Mapping[str, Any]]) -> None:
    for extra_manifest_item in extra_manifest_items:
        metadata = extra_manifest_item.get("metadata")
        if metadata is None:
            raise ExtraManifestMissingMetadataError(
                f"Missing metadata in extra manifest item: {extra_manifest_item}"
            )

        if "name" not in metadata:
            raise ExtraManifestMissingNameError(
                f"Missing metadata.name in extra manifest item: {extra_manifest_item}"
            )


def load_extra_manifests(context: Context) -> list[dict]:
    # Skip if no extra manifest
    if context.extra_manifest_paths is None:
        return []

    # Load manifest
    extra_manifests_str = (
        extra_manifest_path.read_text() for extra_manifest_path in context.extra_manifest_paths
    )

    # Parse manifest
    extra_manifests_raw = (
        load_yaml(extra_manifest_str) for extra_manifest_str in extra_manifests_str
    )

    # Just validate that the format of the file
    extra_manifest_items = list(
        itertools.chain(
            *(
                get_items_from_extra_manifest(extra_manifest_raw)
                for extra_manifest_raw in extra_manifests_raw
            )
        )
    )

    ensure_metadata_is_present(extra_manifest_items)

    # Update metadata labels and names and env's configmap names
    labels = kubernetes.Metadata.labels_from_context(context)
    manifest_prefix = context.manifest_prefix

    for item in extra_manifest_items:
        update_item_metadata_labels(item, labels)
        update_item_metadata_name(item, manifest_prefix)
        update_item_env_configmapkeyref_name(item, manifest_prefix)

    return extra_manifest_items
