# Tests carmack encoding and RLEW ecoding


def _assert_decompress(data_in, func, data_expected):
    data_in = bytes(data_in)
    data_expected = bytes(data_expected)

    result = func(data_in)

    assert data_in == data_expected


def test_rlew_basic():
    assert False

