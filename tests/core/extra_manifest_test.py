import textwrap
from collections.abc import Mapping, Sequence
from pathlib import Path
from tempfile import mkstemp

import pytest

from komposer.core.extra_manifest import load_extra_manifests
from komposer.exceptions import (
    ExtraManifestException,
    ExtraManifestMissingMetadataError,
    ExtraManifestMissingNameError,
)
from tests.fixtures import make_context


def write_content_to_path(base_path: Path, content: str) -> Path:
    _, filename_str = mkstemp(dir=base_path, suffix=".yml")

    filename = Path(filename_str)
    filename.write_text(content)

    return filename


@pytest.mark.parametrize(
    "extra_manifests, expected",
    [
        pytest.param([""], [], id="No content"),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiversion: v1
                kind: List
                items: []
                """
                )
            ],
            [],
            id="Empty list",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: Service
                metadata:
                    name: service-1
                    labels:
                        app: service-1
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                }
            ],
            id="List with single item",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: List
                items:
                - apiVersion: v1
                  kind: Service
                  metadata:
                    name: service-1
                    labels:
                      app: service-1
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                }
            ],
            id="Kubernetes list with single item",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: List
                items:
                - apiVersion: v1
                  kind: Service
                  metadata:
                    name: service-1
                    labels:
                      app: service-1
                  spec:
                    template:
                      spec:
                        containers:
                          - env:
                            - name: MY_ENV
                              valueFrom:
                                configMapKeyRef:
                                  key: MY_ENV
                                  name: service-1
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "env": [
                                            {
                                                "name": "MY_ENV",
                                                "valueFrom": {
                                                    "configMapKeyRef": {
                                                        "key": "MY_ENV",
                                                        "name": "test-repository-test-branch-service-1",  # noqa: E501
                                                    }
                                                },
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                }
            ],
            id="List with single item with env from config map",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: List
                items:
                - apiVersion: v1
                  kind: Service
                  metadata:
                    name: service-1
                    labels:
                      app: service-1
                  spec:
                    template:
                      spec:
                        containers:
                          - env:
                            - name: MY_ENV
                              value: my-value
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "env": [
                                            {
                                                "name": "MY_ENV",
                                                "value": "my-value",
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                }
            ],
            id="List with single item with env from literals",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: Service
                metadata:
                    name: service-1
                    labels:
                        app: service-1
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                }
            ],
            id="Single item",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                ---
                apiVersion: v1
                kind: Service
                metadata:
                    name: service-1
                    labels:
                        app: service-1
                """
                )
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                }
            ],
            id="Document with single item",
        ),
        pytest.param(
            [
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: Service
                metadata:
                    name: service-1
                    labels:
                        app: service-1
                """
                ),
                textwrap.dedent(
                    """
                apiVersion: v1
                kind: Service
                metadata:
                    name: service-2
                    labels:
                        app: service-2
                """
                ),
            ],
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-1",
                        "labels": {
                            "app": "service-1",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                },
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": "test-repository-test-branch-service-2",
                        "labels": {
                            "app": "service-2",
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                },
            ],
            id="Multiple extra manifest files",
        ),
    ],
)
def test_load_external_manifests(
    temporary_path: Path, extra_manifests: Sequence[str], expected: Sequence[Mapping]
) -> None:
    """
    GIVEN an extra manifest's content
    WHEN we load the extra manifest
    THEN we get the expected manifest
    """
    # GIVEN
    extra_manifest_paths = [
        write_content_to_path(temporary_path, extra_manifest) for extra_manifest in extra_manifests
    ]

    context = make_context(extra_manifest_paths=extra_manifest_paths)

    # WHEN
    extra_items = load_extra_manifests(context)

    # THEN
    assert extra_items == expected


@pytest.mark.parametrize(
    "extra_manifest, expected",
    [
        pytest.param("{}", ExtraManifestMissingMetadataError, id="No content"),
        pytest.param(
            textwrap.dedent(
                """
                apiVersion: v1
                kind: List
                items:
                - apiVersion: v1
                  kind: Service
                """
            ),
            ExtraManifestMissingMetadataError,
            id="Item in Kubernetes List without metadata",
        ),
        pytest.param(
            textwrap.dedent(
                """
                ---
                apiVersion: v1
                kind: Service
                """
            ),
            ExtraManifestMissingMetadataError,
            id="Item in list without metadata",
        ),
        pytest.param(
            textwrap.dedent(
                """
                apiVersion: v1
                kind: Service
                """
            ),
            ExtraManifestMissingMetadataError,
            id="Item without metadata",
        ),
        pytest.param(
            textwrap.dedent(
                """
                apiVersion: v1
                kind: List
                items:
                - apiVersion: v1
                  kind: Service
                  metadata: {}
                """
            ),
            ExtraManifestMissingNameError,
            id="Item in Kubernetes List without name",
        ),
        pytest.param(
            textwrap.dedent(
                """
                apiVersion: v1
                kind: Service
                metadata: {}
                """
            ),
            ExtraManifestMissingNameError,
            id="Item without name",
        ),
    ],
)
def test_load_external_manifests_fails(
    temporary_path: Path, extra_manifest: str, expected: type[ExtraManifestException]
) -> None:
    """
    GIVEN a context with an extra manifest
        AND an extra manifest's content
        AND the extra manifest's content is invalid
    WHEN we load the extra manifest
    THEN raises an exception
    """
    # GIVEN
    extra_manifest_path = temporary_path / "extra-manifest.yaml"
    extra_manifest_path.write_text(extra_manifest)

    context = make_context(
        temporary_path=temporary_path, extra_manifest_paths=[extra_manifest_path]
    )

    # WHEN
    with pytest.raises(expected):
        load_extra_manifests(context)
