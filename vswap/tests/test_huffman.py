import pytest
from vswap.huffman import HuffmanTree


def test_basic_tree():
    tree = HuffmanTree.from_text('abcd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == [['c','d'],['a','b']]


@pytest.mark.xfail
def test_tree_unequal():
    tree = HuffmanTree.from_text('aaabbc')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b','c']]

    tree = HuffmanTree.from_text('aaaabbbccd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b',['c','d']]]

# TODO better names for these tests
def test_dencode_basic():
    tree = [['a', 'b'], ['c', 'd']]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    expected_code = {'a': '00',
                     'b': '01',
                     'c': '10',
                     'd': '11'}
    assert new_tree.symbol_table == expected_code


def test_dencode_basic2():
    tree = ['a', ['b', ['c', 'd']]]
    new_tree = HuffmanTree.from_tuple(tree)
    assert tree == new_tree.as_tuple()

    expected_code = {'a': '0',
                     'b': '10',
                     'c': '110',
                     'd': '111'}
    assert new_tree.symbol_table == expected_code

