import struct

from vswap.textures import Wall, Sprite
from vswap.sounds import Sound
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
    sound_chunks = []
    with vswap.open('rb') as f:
        for c_type, length, offset in chunk_offsets:
            f.seek(offset)
            data = f.read(length)

            if c_type == 'wall':
                chunks.append(Wall.from_bytes(data))
            elif c_type == 'sprite':
                chunks.append(Sprite.from_bytes(data))
            else:
                sound_chunks.append(data)

    for data in group_sound_chunks(sound_chunks):
        chunks.append(Sound.from_bytes(data))
    return chunks

def group_sound_chunks(chunks):
    """sounds are stored in chunks
    a chunk's max size is 4096, if a sound
    chunk is equal to this then it's part of the next chunk
    """
    new_chunks = []
    last_chunk = bytes()
    for chunk in chunks:
        last_chunk += chunk
        if len(chunk) < 4096:
            new_chunks.append(last_chunk)
            last_chunk = bytes()
    return new_chunks


# This was used when debugging sprite extraction
# left if needed
# if __name__ == '__main__':
    # from vswap.pallets import wolf3d_pallet
    # from vswap.textures import Sprite
    # import pathlib
    # gamedir = 'assets/wolf3d'
    # swapfile = 'VSWAP.WL6'
    # pallet = wolf3d_pallet
    # gamedir = pathlib.Path(gamedir)

    # data_offsets = load_swap_chunk_offsets(gamedir, swapfile)

    # vswap = gamedir / swapfile

    # target = 4
    # count = 0
    # with vswap.open('rb') as f:
        # for c_type, length, offset in data_offsets:
            # f.seek(offset)
            # data = f.read(length)
            # print(c_type)
            # if c_type == 'sprite':
                # count += 1
                # if count == target:
                    # result = Sprite.from_bytes(data)
                    # print(result)
                    # result.output("./tmp.png", pallet)
                    # break
