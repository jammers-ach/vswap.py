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

    def __repr__(self):
        return "({},{})".format(self.left, self.right)

class HuffmanTree(object):

    def __init__(self):
        self._code = None

    def __repr__(self):
        return self.as_tuple()

    def __getitem__(self, key):
        return self.symbol_table[key]

    def create_tree(self, freq):
        p = queue.PriorityQueue()
        for symbol, freq in sorted(freq.items()):    # 1. Create a leaf node for each symbol
            p.put((freq, symbol))              #    and add it to the priority queue
        while p.qsize() > 1:         # 2. While there is more than one node
            l, r = p.get(), p.get()  # 2a. remove two highest nodes
            node = HuffmanNode(l, r) # 2b. create internal node with children
            p.put((l[0]+r[0], node)) # 2c. add new node to queue

        self.root = p.get()


    @property
    def symbol_table(self):
        if not self._code:
            self._code = self._make_code(self.root)
        return self._code


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
        root = cls._from_tuple(tree_as_tuple)
        tree = cls()
        tree.root = (0, root)

        return tree

    @classmethod
    def _from_tuple(cls, tree_as_tuple):
        l, r = tree_as_tuple

        if isinstance(l,list) or isinstance(l,tuple):
            l = cls._from_tuple(l)

        if isinstance(r,list) or isinstance(r,tuple):
            r = cls._from_tuple(r)


        node = HuffmanNode((0,l), (0,r))
        return node

    #TODO binary as a string, srysly??
    def decode_text(self, text):
        '''
        decodes a binary text string
        :param string text: a string to decode e.g. '010101110'
        '''
        data_pointer = 0
        symbols = ''
        tree_node = self.root[1]
        while data_pointer < len(text):
            if text[data_pointer] == '0':
                tree_node = tree_node.left[1]
            elif text[data_pointer] == '1':
                tree_node = tree_node.right[1]
            else:
                raise ValueError('Only expected "0" or "1" in data, got {}'.format(
                    text[data_pointer]
                ))

            if not isinstance(tree_node,HuffmanNode):
                symbols += tree_node
                tree_node = self.root[1]

            data_pointer += 1



        return symbols



def huffman_encode(text, tree=None):
    '''
    :param text: text to encode
    '''
    if tree == None:
        tree = HuffmanTree.from_text(text)

    result = ''.join([tree[x] for x in text])

    return result


