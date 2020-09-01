import pytest

from vswap.carmack import carmack_decompress

def _assert_same_bytes(data_in, func, data_expected):
    '''Apply func to data_in and compare it to data_expected'''
    data_in = bytes(data_in)
    data_expected = bytes(data_expected)

    result = func(data_in)

    assert result == data_expected



def test_carmack_basic():
    # Basic tests with no special encoding
    _assert_same_bytes(
        #Nothing to decompress
        [0x00, 0x00],
        carmack_decompress,
        []
    )

    _assert_same_bytes(
        #Decompress 2 bytes
        [0x02, 0x00, 0x01,0x02],
        carmack_decompress,
        [0x01, 0x02]
    )

    _assert_same_bytes(
        #Decompress 3 bytes of 0x00
        [0x04, 0x00, 0x01, 0x02, 0x03, 0x04],
        carmack_decompress,
        [0x01, 0x02, 0x03, 0x04]
    )

def test_carmack_basic():
    _assert_same_bytes(
        # 4 byte sequence, repeted 3 times with a near pointer
        [0x08, 0x00, # length
         0x01, 0x02, 0x03, 0x04, # Two word run
         0x02, 0xA7, 0x02 # Repeat the last 2 words starting 2 words ago
         ],
        carmack_decompress,
        [0x01, 0x02, 0x03, 0x04,
         0x01, 0x02, 0x03, 0x04]
    )

