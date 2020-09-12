import sys
import pathlib
import struct
import os
from collections import namedtuple
from vswap.huffman import HuffmanTree
from itertools import tee, chain

from vswap.textures import Graphic, Font

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

readword = lambda d,p: struct.unpack('<H', d[p:p+2])[0]
readsignedword = lambda d,p: struct.unpack('<h', d[p:p+2])[0]
readbyte = lambda d,p: struct.unpack('<B', d[p:p+1])[0]

# All made possible with the help of:
# http://gaarabis.free.fr/_sites/specs/files/wlspec_VGA.html
# http://gaarabis.free.fr/_sites/specs/wlspec_index.html
def load_head(gamedir, vgahead):

    vgadict = gamedir / vgahead

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

def load_dict(gamedir, vgadict_file):
    vgadict = gamedir / vgadict_file

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


def load_chunks(gamedir, graphfile, tree, offsets):
    vgagraph = gamedir / graphfile

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

def extract_images(chunk, graphics_offset=3):
    # chunk 0 contains info about the image chunks
    total_images = len(chunk[0])/4
    images = []
    for i in range(0, len(chunk[0]), 4):
        chunk_id = int(i/4)
        x = readword(chunk[0], i)
        y = readword(chunk[0], i+2)
        images.append(Graphic.from_chunk(chunk[chunk_id+graphics_offset], x,y))

    return images


def load_fonts(chunks, font_offsets):
    return [load_font(chunks[i]) for i in font_offsets]

def load_font(chunk, num_fonts=256):
    height = readword(chunk, 0)
    offsets = [readsignedword(chunk, 2+(2*i)) for i in range(num_fonts)]
    widths = [readbyte(chunk, 2+(2*256)+i) for i in range(num_fonts)]
    glyphs = []
    for off, width in zip(offsets, widths):
        if width == 0:
            continue
        data = bytes([readbyte(chunk, off + i) for i in range(width*height)])
        font = Font.from_chunk(data, width, height)
        glyphs.append(font)
    return glyphs

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("graphics.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        swapfile = 'vswap.bs6'
        dictfile = 'vgadict.bs6'
        headfile = 'vgahead.bs6'
        graphfile = 'vgagraph.bs6'
        tree = load_dict(gamedir, dictfile)
        header = load_head(gamedir, headfile)
        chunks = load_chunks(gamedir, graphfile, tree, header)
        fonts = load_fonts(chunks, [1,2,3,4,5])

        from vswap.pallets import wolf3d_pallet

        for f, font in enumerate(fonts):
            for g, glyph in enumerate(font):
                fname = "out/{}-{:03d}.png".format(f,g)
                glyph.output(fname,wolf3d_pallet)



