# Quick demo of loading wolf3d map data
import sys
import pathlib
import struct
import os
from collections import namedtuple
from carmack import carmack_decompress, rlew_decompress

# All made possible with the help of:
# http://web.archive.org/web/20160625002331/http://devinsmith.net/backups/bruce/wolf3d.html

def extract_map_offsets(gamedir):
    '''Gets from MAPHEAD the offsets of the map data
    :param pathlib.Path gamedir: location of the game wiht a MAPHEAD
    :returns list: ints each one representing the offset of a map'''
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
        return [d for d in data[1::] if d > 0]


def extract_level_headers(gamedir, offsets):
    '''
    :param pathlib.Path gamedir: location of the game wiht a MAPHEAD
    :param offsets: a list of integers where the
    '''
    gamemaps = gamedir / 'GAMEMAPS.WL6'

    #  {
        #unsigned long  map_pointer;    // 32 bits
        #unsigned long  object_pointer; // 32 bits
        #unsigned long  other_pointer;  // 32 bits
        #short          map_size;       // 16 bits
        #short          object_size;    // 16 bits
        #short          other_size;     // 16 bits
        #short          width;          // 16 bits
        #short          height;         // 16 bits
        #unsigned char  name[16]
    #}
    fmt = '<IIIHHHHH16s'
    datasize = struct.calcsize(fmt)
    LevelHeader = namedtuple("LevelHeader", ["map_pointer",
                             "object_pointer",
                             "other_pointer",
                             "map_size",
                             "object_size",
                             "other_size",
                             "width",
                             "height",
                             "name"])

    MapData = namedtuple("MapData", ["header", "object_data", "map_data", "other_data"])

    maps = []
    with gamemaps.open('rb') as f:
        for offset in offsets:
            #Get the level header
            data = struct.unpack_from(fmt, seek_and_read(f, offset, datasize))
            header = LevelHeader(*data)

            #Now get the data
            object_data = seek_and_read(f, header.object_pointer, header.object_size)
            map_data = seek_and_read(f, header.map_pointer, header.map_size)
            other_data = seek_and_read(f, header.other_pointer, header.other_size)

            # object_data = rlew_decompress(carmack_decompress(object_data))
            map_data = rlew_decompress(carmack_decompress(map_data))
            other_data = carmack_decompress(other_data)


            b = MapData(header, object_data, map_data, other_data)
            maps.append(b)

    return maps

def seek_and_read(f, pointer, size):
    f.seek(pointer, 0)
    data = f.read(size)
    return data

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("maps.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        offsets = extract_map_offsets(gamedir)
        headers = extract_level_headers(gamedir, offsets)
        print("READ {} maps".format(len(headers)))
