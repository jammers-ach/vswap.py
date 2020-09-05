import sys
import pathlib
import struct
import os
from collections import namedtuple
from vswap.huffman import HuffmanTree
from itertools import tee, chain

from vswap.textures import Graphic

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

readword = lambda d,p: struct.unpack('<H', d[p:p+2])[0]

# All made possible with the help of:
# http://gaarabis.free.fr/_sites/specs/files/wlspec_VGA.html
# http://gaarabis.free.fr/_sites/specs/wlspec_index.html
def load_head(gamedir):
    vgadict = gamedir / 'VGAHEAD.WL6'

    fmt = '<BBB'
    datasize = struct.calcsize(fmt)
    HeaderNode = namedtuple('HeaderNode', ['b1','b2','b3'])
    offsets = []

    with vgadict.open('rb') as f:
        read_bytes = f.read(datasize)
        while read_bytes:
            data = struct.unpack(fmt, read_bytes)
            offset = data[0] + (data[1] << 8) + (data[2] << 16)
            offsets.append(offset)

            read_bytes = f.read(datasize)

    for a, b in pairwise(offsets):
        assert b > a, 'Offsets are decreasing'

    return offsets

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


def load_chunks(gamedir, tree, offsets):
    vgagraph = gamedir / 'VGAGRAPH.WL6'

    # Loop through the offsets pairwise and
    # calculate the size of the compressed data
    read_loc = []
    for a, b in pairwise(offsets):
        data_size = b-a
        read_loc.append((a, data_size))

    fmt = '<L'
    datasize = struct.calcsize(fmt)

    chunks = []

    with vgagraph.open('rb') as f:
        for offset, compressed_size in read_loc:
            f.seek(offset)
            decompressed_size = struct.unpack(fmt, f.read(datasize))[0]
            data = f.read(compressed_size)

            data = tree.decode_bytes(data, decompressed_size)
            chunks.append(data)
    return chunks

def extract_images(chunk):
    # chunk 0 contains info about the image chunks
    total_images = len(chunk[0])/4
    print(total_images)
    images = []
    for i in range(0, len(chunk[0]), 4):
        chunk_id = int(i/4)
        x = readword(chunk[0], i)
        y = readword(chunk[0], i+2)
        print("chunk {} is {}x{}".format(i, x, y))
        images.append(Graphic.from_chunk(chunk[chunk_id+3], x,y))

    return images

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("graphics.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        tree = load_dict(gamedir)
        header = load_head(gamedir)
        chunks = load_chunks(gamedir, tree, header)
        images = extract_images(chunks)
        from vswap.pallets import wolf3d_pallet
        for i, image in enumerate(images):
            image.output("out/graphics{}.png".format(i), wolf3d_pallet)



