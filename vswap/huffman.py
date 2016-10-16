'''
My own impelemntation of a huffman decoder and encoder
'''
import queue
from collections import Counter
from functools import partial
from io import StringIO
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

    def __init__(self, freq):
        ''':param freq: a dictionary'''
        self.freq = freq

        self.root = self._create_tree()
        self.code = self.walk_tree(self.root)

    def __repr__(self):
        return self.code.__repr__()

    def __getitem__(self, key):
        return self.code[key]

    def _create_tree(self):
        p = queue.PriorityQueue()
        for symbol, freq in self.freq.items():    # 1. Create a leaf node for each symbol
            p.put((freq, symbol))              #    and add it to the priority queue
        while p.qsize() > 1:         # 2. While there is more than one node
            l, r = p.get(), p.get()  # 2a. remove two highest nodes
            node = HuffmanNode(l, r) # 2b. create internal node with children
            p.put((l[0]+r[0], node)) # 2c. add new node to queue

        return p.get()               # 3. tree is complete - return root node

    # Recursively walk the tree down to the leaves,
    # assigning a code value to each symbol
    def walk_tree(self, node, prefix="", code={}):
        if isinstance(node[1].left[1], HuffmanNode):
            self.walk_tree(node[1].left,prefix+"0", code)
        else:
            code[node[1].left[1]]=prefix+"0"
        if isinstance(node[1].right[1],HuffmanNode):
            self.walk_tree(node[1].right,prefix+"1", code)
        else:
            code[node[1].right[1]]=prefix+"1"
        return(code)

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

def huffman_encode(text, pad=False):
    '''
    :param text: text to encode
    'param boolean pass: padds the text with 0 to make it fit into bytes
    '''
    freq = Counter(text)
    tree = HuffmanTree(freq)
    result = ''.join([tree[x] for x in text])

    if pad:
        if len(result) % 8 != 0:
            result += '0' * (8 - len(result)%8)
            assert len(result) % 8 == 0

    return tree, result

def huffman_encode_binary(text):
    tree, string = huffman_encode(text, pad=True)
    assert len(string) % 8 == 0

    # Split up int 8 character bytes, parse it as binary
    data = [l for l in iter(partial(StringIO(string).read, 8), '')]
    data = [int(l,2) for l in data]

    return tree, bytes(data)

# texts = [b'mississippi river',
#          b'James is super cool',
#          b'111222181717111',
#          b'9999999922222999999911199911999999999',
#          b'James James James James',
#          b'abcdefghijklmnop']
#
# for text in texts:
#     tree, result = huffman_encode_binary(text)
#
#     symbol_table = tree.as_bytes()
#
#     data = symbol_table + result
#     print("was {} bytes: now {}, symbol table {}".format(
#         len(text),
#         len(data),
#         len(symbol_table)))

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    print(fname)
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
        tree, result = huffman_encode_binary(data)

        symbol_table = tree.as_bytes()

        encoded = symbol_table + result
        print("was {} bytes: now {}, symbol table {}".format(
             len(data),
             len(encoded),
             len(symbol_table)))


