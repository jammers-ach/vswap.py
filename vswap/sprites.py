
import sys
import pathlib
import struct

from vswap.textures import Wall, Sprite
# Made possible thanks to:
# http://gaarabis.free.fr/_sites/specs/files/wlspec_VSW.html


def load_swap_chunk_offsets(gamedir):
    '''Gets location and size and type of each sprite chunk,
    yeilds "wall"/"sprite"/"sound", chunk_size, chunk_offset'''
    vswap = gamedir / 'VSWAP.WL6'

    # first 3 words are: chunk
    header_fmt = '<HHH'

    with vswap.open('rb') as f:
        f.seek(0)
        data = f.read(struct.calcsize(header_fmt))
        nchunks, first_sprite, first_sound = \
            struct.unpack(header_fmt, data)

        chunk_list_fmt = '<' + 'L' * nchunks
        chunk_length_fmt = '<' + 'H' * nchunks
        data = f.read(struct.calcsize(chunk_list_fmt))
        chunk_offsets = struct.unpack(chunk_list_fmt, data)

        data = f.read(struct.calcsize(chunk_length_fmt))
        chunk_lengths = struct.unpack(chunk_length_fmt, data)

    chunks_info = zip(chunk_offsets, chunk_lengths)

    for i, d in enumerate(chunks_info):
        if i < first_sprite:
            c_type = 'wall'
        elif i < first_sound:
            c_type = 'sprite'
        else:
            c_type = 'sound'

        offset, length = d
        yield c_type, length, offset

def load_sprite_chunks(gamedir, chunk_offsets):
    vswap = gamedir / 'VSWAP.WL6'

    chunks = []
    with vswap.open('rb') as f:
        for c_type, length, offset in chunk_offsets:
            f.seek(offset)
            data = f.read(length)

            if c_type == 'wall':
                chunks.append(Wall.from_bytes(data))
            elif c_type == 'sprite':
                chunks.append(Sprite.from_bytes(data))
            else:
                chunks.append([c_type, data])
    return chunks

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("sprites.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        data_offsets = load_swap_chunk_offsets(gamedir)
        graphic_chunks = load_sprite_chunks(gamedir, data_offsets)

        # graphic_chunks[50]._print()
        c = 0
        for i in graphic_chunks:
            if isinstance(i, Sprite):
                i._print()
                print('----')
