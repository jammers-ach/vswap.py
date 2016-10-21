from vswap.huffman import HuffmanTree


def test_basic_tree():
    tree = HuffmanTree.from_text('abcd')
    tree_tuple= tree.as_tuple()
    print(tree.root)
    assert tree_tuple == [['c','d'],['a','b']]

    tree = HuffmanTree.from_text('aaabbc')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b','c']]

    tree = HuffmanTree.from_text('aaaabbbccd')
    tree_tuple= tree.as_tuple()
    assert tree_tuple == ['a',['b',['c','d']]]

def test_dencode():

    tree = [['a', 'b'], ['c', 'd']]
    new_tree = HuffmanTree.from_tuple(tree)
    print(new_tree.root)
    assert tree == new_tree.as_tuple()

