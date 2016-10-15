# Quick demo of loading wolf3d map data
import sys
import pathlib
import struct
import os

def extract_map_offsets(gamedir):
    '''Gets from MAPHEAD the offsets of the map data'''
    maphead = gamedir / 'MAPHEAD.WL6'

    # mapHead contains the offsets of the map data
    # in the map file
    # the first two bytes are a magin number 0xABCD
    # After that it's a list of 4 byte unsigned long

    # We will use a python struct for this data.
    # But first we need to know the length of the file in bytes
    fsize = os.path.getsize(str(maphead))
    datasize = fsize - 2
    assert datasize % 4 == 0, "Filesize is not a multiple of 4"
    asset_count = int(datasize / 4)

    # Two bytes of 0xABCD, followed by 4 byte offsets
    fmt = '<H' + ('I' * asset_count)

    assert struct.calcsize(fmt) == fsize, "format string doesn't match length" \
        " of file, expected {}, file is {}".format(struct.calcsize(fmt), fsize)

    with maphead.open('rb') as f:
        data = struct.unpack_from(fmt, f.read())
        check1 = data[0]
        assert check1 == 0xabcd, "Check not valid"
        return data[1::]

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("maps.py GAMEDIR")
    else:
        offsets = extract_map_offsets(pathlib.Path(sys.argv[1]))
