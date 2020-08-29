import argparse
import os
import pathlib
import logging

from vswap.sprites import load_swap_chunk_offsets, load_sprite_chunks
from vswap.pallets import wolf3d_pallet


def extract(gamedir, target):
    # TODO fornow assume wolf3d
    swapfile = 'VSWAP.WL6'
    pallet = wolf3d_pallet
    gamedir = pathlib.Path(gamedir)
    target = pathlib.Path(target)

    data_offsets = load_swap_chunk_offsets(gamedir, swapfile)
    graphic_chunks = load_sprite_chunks(gamedir, swapfile, data_offsets)
    for i, chunk in enumerate(graphic_chunks):
        filename = "target{:04d}.png".format(i)
        chunk.output(target / filename, pallet)

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

