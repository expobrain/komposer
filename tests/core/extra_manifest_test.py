from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Optional

import pytest
import yaml
from pydantic import ValidationError

from komposer.core.extra_manifest import load_extra_manifest
from komposer.types.cli import Context
from tests.fixtures import make_context


@pytest.fixture
def context_with_extra_manifest(temporary_path: Path) -> Context:
    return make_context(
        temporary_path=temporary_path, extra_manifest_path=temporary_path / "extra_manifest.yaml"
    )


@pytest.mark.parametrize(
    "extra_manifest, expected",
    [
        pytest.param({}, [], id="No content"),
        pytest.param({"apiVersion": "v1", "kind": "List", "items": []}, [], id="Empty list"),
        pytest.param(
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    {
                        "apiVersion": "v1",
                        "kind": "Service",
                        "metadata": {
                            "name": "service-1",
                            "labels": {
                                "app": "service-1",
                            },
                        },
                    }
                ],
            },
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
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    {
                        "apiVersion": "v1",
                        "kind": "Job",
                        "metadata": {"name": "job-1"},
                        "spec": {
                            "template": {
                                "spec": {
                                    "containers": [
                                        {
                                            "args": [
                                                "ping",
                                                "${KOMPOSER_SERVICE_PREFIX}-service=1}",
                                            ],
                                        }
                                    ]
                                }
                            }
                        },
                    }
                ],
            },
            [
                {
                    "apiVersion": "v1",
                    "kind": "Job",
                    "metadata": {
                        "name": "test-repository-test-branch-job-1",
                        "labels": {
                            "repository": "test-repository",
                            "branch": "test-branch",
                        },
                    },
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "args": [
                                            "ping",
                                            "test-repository-test-branch-service=1}",
                                        ],
                                    }
                                ]
                            }
                        }
                    },
                }
            ],
            id="Single item with ${KOMPOSER_SERVICE_PREFIX} env var",
        ),
        pytest.param(
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [
                    {
                        "apiVersion": "v1",
                        "kind": "Service",
                        "metadata": {
                            "name": "service-1",
                            "labels": {"app": "service-1"},
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
                                                            "name": "service-1",
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
            },
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
            id="Single item with env from config map",
        ),
    ],
)
def test_load_external_manifest(
    context_with_extra_manifest: Context, extra_manifest: Mapping, expected: Sequence[Mapping]
) -> None:
    """
    GIVEN a context with an extra manifest
        AND an extra manifest's content
    WHEN we load the extra manifest
    THEN we get the expected manifest
    """
    # GIVEN
    assert isinstance(context_with_extra_manifest.extra_manifest_path, Path)

    context_with_extra_manifest.extra_manifest_path.write_text(yaml.dump(extra_manifest))

    # WHEN
    extra_items = load_extra_manifest(context_with_extra_manifest)

    # THEN
    assert extra_items == expected


@pytest.mark.parametrize(
    "extra_manifest",
    [
        pytest.param(None, id="No content"),
        pytest.param({"apiVersion": "v1", "kind": "Kind"}, id="Not a List kind"),
        pytest.param(
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [{"apiVersion": "v1", "kind": "Service"}],
            },
            id="Item without metadata",
        ),
        pytest.param(
            {
                "apiVersion": "v1",
                "kind": "List",
                "items": [{"apiVersion": "v1", "kind": "Service", "metadata": {}}],
            },
            id="Item without labels nor name",
        ),
    ],
)
def test_load_external_manifest_fails_not_a_list_kind(
    context_with_extra_manifest: Context, extra_manifest: Optional[dict]
) -> None:
    """
    GIVEN a context with an extra manifest
        AND an extra manifest's content
        AND the root item is not a List kind
    WHEN we load the extra manifest
    THEN raises an exception
    """
    # GIVEN
    assert isinstance(context_with_extra_manifest.extra_manifest_path, Path)

    content = "" if extra_manifest is None else yaml.dump(extra_manifest)
    context_with_extra_manifest.extra_manifest_path.write_text(content)

    # WHEN
    with pytest.raises(ValidationError):
        load_extra_manifest(context_with_extra_manifest)
