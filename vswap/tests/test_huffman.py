import pytest
from vswap.huffman import HuffmanTree, huffman_encode


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


def test_decode_from_tree():
    tree = ['a', ['b', ['c', 'd']]]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    #Check the decode_text doesn't work with crappy data
    with pytest.raises(ValueError):
        new_tree.decode_text('0101AA')

    tests = [
        ('0', 'a'),
        ('10', 'b'),
        ('110', 'c'),
        ('111', 'd'),
        ('1110', 'da'),
        ('010100110111', 'abbacd')
    ]

    for value, expected in tests:
        assert new_tree.decode_text(value) == expected
