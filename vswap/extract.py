import argparse
import os


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

    if not os.path.isdir(args.target):
        print("{} is not a directory".format(args.target))

if __name__ == '__main__':

    run()

