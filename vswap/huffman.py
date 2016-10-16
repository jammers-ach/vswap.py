'''
My own impelemntation of a huffman decoder and encoder
'''
import queue
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

freq = {
    'a': 8,
    'b': 1,
    'c': 2,
    'd': 4,
    'e': 12,
    'f': 2,
    'k': 2,
    'g': 5}


tree = HuffmanTree(freq)

for symbol, freq in sorted(freq.items()):
    print(symbol, '{:6.2f}'.format(freq), tree[symbol])
