from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import pytest

from komposer.types.cli import Context
from tests.fixtures import make_context


@pytest.fixture
def temporary_path() -> Iterable[Path]:
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        yield temp_path


@pytest.fixture
def context(temporary_path: Path) -> Context:
    return make_context(temporary_path=temporary_path)
