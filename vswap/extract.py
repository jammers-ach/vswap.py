import argparse
import os
import pathlib
import logging

from games import Wolf3dFull

def extract(gamedir, target):
    game = Wolf3dFull(gamedir)
    game.load_all()
    game.output(target)

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
        return

    if not os.path.isdir(args.target):
        print("{} is not a directory".format(args.target))
        return

    extract(args.gamedir, args.target)

if __name__ == '__main__':
    logging.basicConfig()
    run()

