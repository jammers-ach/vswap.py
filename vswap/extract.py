import argparse
import os
import pathlib
import logging

from vswap.sprites import load_swap_chunk_offsets, load_sprite_chunks
from vswap.pallets import wolf3d_pallet
from vswap.textures import Wall, Sprite
from vswap.sounds import Sound


def extract(gamedir, target):
    # TODO fornow assume wolf3d
    swapfile = 'VSWAP.WL6'
    pallet = wolf3d_pallet
    gamedir = pathlib.Path(gamedir)
    target = pathlib.Path(target)

    data_offsets = load_swap_chunk_offsets(gamedir, swapfile)
    vswap_chunks = load_sprite_chunks(gamedir, swapfile, data_offsets)
    wall_count = 0
    sprite_count = 0
    sound_count = 0

    for chunk in vswap_chunks:
        if type(chunk) == Sprite:
            sprite_count += 1
            fname = "sprite{:04d}.png".format(sprite_count)
            chunk.output(target / fname, pallet)
        if type(chunk) == Wall:
            wall_count += 1
            fname = "wall{:04d}.png".format(wall_count)
            chunk.output(target / fname, pallet)

def run():
    parser = argparse.ArgumentParser(description='Extracts')
    parser.add_argument('gamedir', metavar='ASSET_DIR',
                        help='Directory of game assets')

    parser.add_argument('--target', metavar='TARGET_DIR', default="./",
                        help='Target extraction path')

    args = parser.parse_args()

    # check valid dir
    if not os.path.isdir(args.gamedir):
        print("{} is not a directory".format(args.gamedir))
        retu

    if not os.path.isdir(args.target):
        print("{} is not a directory".format(args.target))
        return

    extract(args.gamedir, args.target)

if __name__ == '__main__':
    logging.basicConfig()
    run()

