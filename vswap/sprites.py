import struct

from vswap.textures import Wall, Sprite
# Made possible thanks to:
# http://gaarabis.free.fr/_sites/specs/files/wlspec_VSW.html


def load_swap_chunk_offsets(gamedir, vswapfile):
    '''Gets location and size and type of each sprite chunk,
    yeilds "wall"/"sprite"/"sound", chunk_size, chunk_offset'''
    vswap = gamedir / vswapfile

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

def load_sprite_chunks(gamedir, swapfile, chunk_offsets):
    vswap = gamedir / swapfile

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

