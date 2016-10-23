# Quick demo of loading wolf3d map data
import sys
import pathlib
import struct
import os
from collections import namedtuple
from vswap.huffman import HuffmanTree

# All made possible with the help of:
# http://gaarabis.free.fr/_sites/specs/files/wlspec_VGA.html


def load_dict(gamedir):
    vgadict = gamedir / 'VGADICT.WL6'

    fmt = '<BBBB'
    datasize = struct.calcsize(fmt)
    DictNode = namedtuple('DictNode', ['ref_l', 'type_l', 'ref_r', 'type_r'])

    # Read in all the nodes
    nodes = []
    node_index = 0
    with vgadict.open('rb') as f:
        read_bytes = f.read(datasize)
        while read_bytes:
            data = struct.unpack(fmt, read_bytes)
            node = DictNode(*data)
            nodes.append(node)
            node_index += 1
            read_bytes = f.read(datasize)

    # Make huffman tree
    tree = HuffmanTree.from_vgadict(nodes)

    return tree

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("sprites.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        tree = load_dict(gamedir)

        print(tree)
