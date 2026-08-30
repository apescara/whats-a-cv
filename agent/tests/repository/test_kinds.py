import pytest

from whats_a_cv.repository import RecordKind


def test_unknown_record_kind_is_rejected() -> None:
    with pytest.raises(ValueError):
        RecordKind("unknown")
