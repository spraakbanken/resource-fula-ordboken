from pathlib import Path

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from resource_fula_ordboken.fula_ord_converter import FulaOrdTxt2JsonConverter


@pytest.fixture
def snapshot_json(snapshot):  # noqa: ANN001, ANN201
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)
    # or return snapshot.use_extension(JSONSnapshotExtension)


@pytest.mark.parametrize(
    "test_case", ["10-öres-brud.txt", "absa.txt", "ale.txt", "alträde.txt", "artontaggare.txt"]
)
def test_convert_cases(test_case: str, snapshot_json) -> None:  # noqa: ANN001
    filename = Path(f"test_data/{test_case}")

    converter = FulaOrdTxt2JsonConverter()
    with filename.open(encoding="utf-8") as fp:
        entries = list(converter.convert_entry(fp))

    assert entries == snapshot_json
