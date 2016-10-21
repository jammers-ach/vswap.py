'''
My own impelemntation of a huffman decoder and encoder
'''
import queue
from collections import Counter
#Thanks to http://stackoverflow.com/questions/11587044/how-can-i-create-a-tree-for-huffman-encoding-and-decoding

class HuffmanNode(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return (self.left, self.right)

    def __lt__(self, other):
        return self

    def __gt__(self, other):
        return other

class HuffmanTree(object):

    def __init__(self):
        pass

    def __repr__(self):
        return self.as_tuple()

    def __getitem__(self, key):
        if not self.code:
            self.make_code()
        return self.code[key]

    def create_tree(self, freq):
        p = queue.PriorityQueue()
        for symbol, freq in sorted(freq.items()):    # 1. Create a leaf node for each symbol
            p.put((freq, symbol))              #    and add it to the priority queue
        while p.qsize() > 1:         # 2. While there is more than one node
            l, r = p.get(), p.get()  # 2a. remove two highest nodes
            node = HuffmanNode(l, r) # 2b. create internal node with children
            p.put((l[0]+r[0], node)) # 2c. add new node to queue

        self.root = p.get()


    def make_code(self):
        self._make_code(self.root)

    # Recursively walk the tree down to the leaves,
    # assigning a code value to each symbol
    def _make_code(self, node, prefix="", code={}):
        if isinstance(node[1].left[1], HuffmanNode):
            self._make_code(node[1].left,prefix+"0", code)
        else:
            code[node[1].left[1]]=prefix+"0"
        if isinstance(node[1].right[1],HuffmanNode):
            self._make_code(node[1].right,prefix+"1", code)
        else:
            code[node[1].right[1]]=prefix+"1"
        return code

    def as_bytes(self):
        '''The symbol table as bytes'''
        data = []
        for symbol, code in self.code.items():
            if isinstance(symbol, bytes):
                data.append(symbol)
            elif isinstance(symbol, str):
                data.append(ord(symbol))
            elif isinstance(symbol, int):
                data.append(symbol)
            else:
                raise ValueError("can't decode symbol %s", symbol)
            data.append(int(code, 2))
        return bytes(data)

    def as_tuple(self):
        '''
        represents this tree as a series of nested tuples,
        e.g.: (((1,(2,3))),(4,(5,6)))
        '''
        return self.walk_tree(self.root)

    def walk_tree(self, node, tree=[None, None]):
        if isinstance(node[1].left[1], HuffmanNode):
            tree[0] = self.walk_tree(node[1].left, [None, None])
        else:
            tree[0] = node[1].left[1]
        if isinstance(node[1].right[1],HuffmanNode):
            tree[1] = self.walk_tree(node[1].right, [None, None])
        else:
            tree[1] = node[1].right[1]

        return tree

    @classmethod
    def from_text(cls, data):
        freq = Counter(data)
        tree = cls()
        tree.create_tree(freq)

        return tree

    @classmethod
    def from_tuple(cls, tree_as_tuple):
        pass


def huffman_encode(text, pad=False):
    '''
    :param text: text to encode
    'param boolean pass: padds the text with 0 to make it fit into bytes
    '''
    tree = HuffmanTree.from_text(text)
    result = ''.join([tree[x] for x in text])

    return tree, result


