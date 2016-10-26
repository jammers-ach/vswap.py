import pytest
from vswap.huffman import HuffmanTree, huffman_encode


def _binary_string_to_bytes(text):
    '''
    Utility function, pads short bytes with trailing 0s
    and returns a byte
    '11110101' => [0xaf]
    '1' => [0x01] (intermedate 0000001)
    '''
    if len(text) % 8 != 0:
        text += '0' * (8 - len(text) % 8)
        assert len(text) % 8 == 0

    data = []
    for i in range(int(len(text)/8)):
        offset = i*8
        byte = text[offset:offset+8]
        data.append(int(byte[::-1], 2))

    return bytes(data)

def test_utility_function():
    assert _binary_string_to_bytes('10101111'[::-1]) == bytes([0xaf])
    assert _binary_string_to_bytes('1'[::-1]) == bytes([0x01])
    assert _binary_string_to_bytes('1111111111110101') == bytes([0xff, 0xaf])

def test_tree_from_text():
    tree = HuffmanTree.from_text('abcd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == [['c','d'],['a','b']]


@pytest.mark.xfail
def test_tree_from_unequal_text():
    tree = HuffmanTree.from_text('aaabbc')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b','c']]

    tree = HuffmanTree.from_text('aaaabbbccd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b',['c','d']]]

def test_tree_from_tuple():
    tree = [['a', 'b'], ['c', 'd']]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    expected_code = {'a': '00',
                     'b': '01',
                     'c': '10',
                     'd': '11'}
    assert new_tree.symbol_table == expected_code

    result = huffman_encode("abcd", new_tree)
    assert result == '00011011'


def test_tree_from_tuple2():
    tree = ['a', ['b', ['c', 'd']]]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    expected_code = {'a': '0',
                     'b': '10',
                     'c': '110',
                     'd': '111'}
    assert new_tree.symbol_table == expected_code

    result = huffman_encode("abcd", new_tree)
    assert result == '010110111'


@pytest.mark.parametrize("value, expected", [
    ('0', 'a'),
    ('10', 'b'),
    ('110', 'c'),
    ('111', 'd'),
    ('1110', 'da'),
    ('010100110111', 'abbacd'),
])
def test_decode_from_tree(value, expected):
    tree = ['a', ['b', ['c', 'd']]]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    new_encoded = huffman_encode(expected, new_tree)
    assert new_encoded == value

    value_bytes = _binary_string_to_bytes(value)
    decoded = ''.join(new_tree.decode_bytes(value_bytes, decode_count=len(expected)))
    assert decoded == expected



@pytest.mark.xfail(reason="Running on wolf3d data always raises this, disabling for now")
def test_failing_decode_from_tree():

    tree = ['a', ['b', ['c', 'd']]]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    # These cases contain patterns that leave the decoding
    # Not on a leaf node
    failing_tests = [
        ('11111111', 'dda'),
        ('01010011', 'abbacd'),
    ]
    for value, expected in failing_tests:
        value_bytes = _binary_string_to_bytes(value)
        with pytest.raises(ValueError):
            data = new_tree.decode_bytes(value_bytes, decode_count=len(expected))
