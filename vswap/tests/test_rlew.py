import pytest

from vswap.carmack import rlew_decompress

def _assert_same_after(data_in, func, data_expected):
    data_in = bytes(data_in)
    data_expected = bytes(data_expected)

    result = func(data_in)

    assert result == data_expected

def test_testing_assert():
    increment = lambda x: bytes([i+1 for i in x])

    _assert_same_after(
        [ 0x11, 0x12, 0x13],
        lambda x: x,
        [ 0x11, 0x12, 0x13]
    )

    _assert_same_after(
        [ 0x11, 0x12, 0x13],
        increment,
        [ 0x12, 0x13, 0x14]
    )

    with pytest.raises(AssertionError):
        _assert_same_after(
            [ 0x11, 0x12, 0x13],
            increment,
            [ 0x12, 0x11, 0x14]
        )


def test_rlew_basic():
    _assert_same_after(
        # two bytes, first word is 0x0100
        [ 0x02, 0x00, 0x00, 0x01],
        rlew_decompress,
        [ 0x00, 0x01]
    )
    _assert_same_after(
        # four bytes, first word is 0x0100 second is 0xff10
        [ 0x04, 0x00, 0x00, 0x01, 0x10, 0xff],
        rlew_decompress,
        [ 0x00, 0x01, 0x10, 0xff]
    )

def test_rlew_runs():
    _assert_same_after(
        # 10 bytes, a 5 run of 0x0100
        [ 0x0A, 0x00, 0xCD, 0xAB, 0x05, 0x00, 0x00, 0x01],
        rlew_decompress,
        [ 0x00, 0x01, 0x00, 0x01, 0x00, 0x01,0x00, 0x01,  0x00, 0x01, ]
    )

    _assert_same_after(
        # 10 bytes, a 5 run of 0x0100
        # There is some extra, but there's an extra two bytes in the data
        [ 0x0A, 0x00, 0xCD, 0xAB, 0x05, 0x00, 0x00, 0x01, 0xFF, 0xAB],
        rlew_decompress,
        [ 0x00, 0x01, 0x00, 0x01, 0x00, 0x01,0x00, 0x01,  0x00, 0x01]
    )

    _assert_same_after(
        # 12 bytes, a 5 run of 0x0100
        # There is some extra, but there's an extra two bytes in the data
        [ 0x0C, 0x00, 0xCD, 0xAB, 0x05, 0x00, 0x00, 0x01, 0xFF, 0xAB],
        rlew_decompress,
        [ 0x00, 0x01, 0x00, 0x01, 0x00, 0x01,0x00, 0x01,  0x00, 0x01, 0xFF, 0xAB]
    )

def test_rlew_bad_data():

    with pytest.raises(IndexError):
        _assert_same_after(
            # 10 bytes, a 6 run of 0x0100
            [ 0x0A, 0x00, 0xCD, 0xAB, 0x06, 0x00, 0x00, 0x01, 0xFF, 0xAB],
            rlew_decompress,
            [ ]
        )
