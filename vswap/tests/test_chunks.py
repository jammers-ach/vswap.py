from vswap.chunk_types import PictTable
import pytest


def test_picttable_basic_fail():
    with pytest.raises(ValueError):
        c = PictTable.from_chunk(1, bytes([1,0]))
        c = PictTable.from_chunk(1, bytes([1,0,0,0,0,0]))

def test_picttable_basic():
    c = PictTable.from_chunk(1, bytes([1, 2, 3, 4]))
    assert c.width == 513
    assert c.height == 1027
    assert c.chunk_id == 1
