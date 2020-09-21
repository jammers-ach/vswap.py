# Quick demo of loading wolf3d map data
import sys
import pathlib
import struct
import os
import numpy as np
import json
import logging

from collections import namedtuple
from vswap.carmack import carmack_decompress, rlew_decompress

# All made possible with the help of:
# http://web.archive.org/web/20160625002331/http://devinsmith.net/backups/bruce/wolf3d.html

logger = logging.getLogger(__name__)

LevelHeader = namedtuple("LevelHeader", ["map_pointer",
                            "object_pointer",
                            "other_pointer",
                            "map_size",
                            "object_size",
                            "other_size",
                            "width",
                            "height",
                            "name"])
class Wolf3dMap():
    def __init__(self, map_header, object_data, map_data, other_data):
        self.map_header = map_header
        self._build_matrix(map_data)
        self._build_object_list(object_data, other_data)



    def _build_matrix(self, map_data):
        self.level = np.zeros((self.width, self.height), dtype=int)
        for i in range(self.width):
            for j in range(self.height):
                index = (i*self.width) + j
                self.level[i,j] = map_data[index]

    def _build_object_list(self, object_data, other_data):
        self.object_list = []
        for i in range(self.width):
            for j in range(self.height):
                index = (i*self.width) + j
                if object_data and object_data[index]:
                    self.object_list.append(((i,j), object_data[index]))
                if other_data and other_data[index]:
                    self.object_list.append(((i,j), "Other-{}".format(other_data[index])))

    @property
    def width(self):
        return self.map_header.width

    @property
    def height(self):
        return self.map_header.height

    @property
    def name(self):
        return str(self.map_header.name, 'ascii')

    def print_map(self):
        for i in range(self.width):
            for j in range(self.height):
                print("{:02X}".format(self.level[i,j]), end='')
            print('')

        for loc, obj in self.object_list:
            print(loc, obj)

    @property
    def json(self):
        data = {}
        data['level'] = self.level.tolist()
        data['object_list'] = self.object_list
        data['name'] = self.name
        data['size'] = (self.width, self.height)
        return data


    def output(self, fname):
        with open(fname, 'w') as f:
            json.dump(self.json, f)


def extract_map_offsets(gamedir, maphead):
    '''Gets from MAPHEAD the offsets of the map data
    :param pathlib.Path gamedir: location of the game wiht a MAPHEAD
    :returns list: ints each one representing the offset of a map'''

    maphead = gamedir / maphead

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


def extract_maps(gamedir, gamemaps, offsets):
    '''
    :param pathlib.Path gamedir: location of the game wiht a MAPHEAD
    :param offsets: a list of integers where the
    '''
    # see http://www.shikadi.net/moddingwiki/TED5
    uncompressed = gamemaps.lower().startswith('maptemp')
    gamemaps = gamedir / gamemaps

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

    maps = []
    with gamemaps.open('rb') as f:
        for offset in offsets:
            #Get the level header
            if offset == 0xffffffff:
                continue
            data = struct.unpack_from(fmt, seek_and_read(f, offset, datasize))
            header = LevelHeader(*data)

            #Now get the data
            object_data = seek_and_read(f, header.object_pointer, header.object_size)
            map_data = seek_and_read(f, header.map_pointer, header.map_size)
            other_data = seek_and_read(f, header.other_pointer, header.other_size)

            if not uncompressed:
                object_data = carmack_decompress(object_data)
                map_data = carmack_decompress(map_data)
                other_data = carmack_decompress(other_data)

            if len(map_data) == 0:
                logger.info("Map {} has no map data, skipping".format(str(header.name)))
                continue

            map_data = rlew_decompress(map_data)
            if len(object_data):
                object_data = rlew_decompress(object_data)
                object_data = convert_to_shorts(object_data, header.width* header.height)
            else:
                object_data = None

            if len(other_data):
                other_data = rlew_decompress(other_data)
                other_data = convert_to_shorts(other_data, header.width * header.height)
            else:
                other_data = None

            level = Wolf3dMap(header,
                              object_data,
                              convert_to_shorts(map_data, header.width * header.height),
                              other_data
                              )
            maps.append(level)

    return maps

def convert_to_shorts(data, new_size):
    '''converts an array of bytres to arrays of shorts'''
    fmt = '<{}H'.format(new_size)
    return struct.unpack(fmt, data)

def seek_and_read(f, pointer, size):
    f.seek(pointer, 0)
    data = f.read(size)
    return data

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("maps.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        offsets = extract_map_offsets(gamedir, 'MAPHEAD.WL6')
        maps = extract_maps(gamedir, 'GAMEMAPS.WL6', offsets)
        maps[0].print_map()
