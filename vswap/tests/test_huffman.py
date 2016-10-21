from vswap.huffman import HuffmanTree


def test_basic_tree():
    tree = HuffmanTree.from_text('abcd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == [['a','b'],['c','d']]

    tree = HuffmanTree.from_text('aaabbc')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b','c']]

    tree = HuffmanTree.from_text('aaaabbbccd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b',['c','d']]]

