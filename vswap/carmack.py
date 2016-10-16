'''
Implementation of carmack decompression

It's kinda similar to Run Length Encoding but with a bit more
http://www.shikadi.net/moddingwiki/Carmack_compression
'''
import logging
import struct

logger = logging.getLogger(__name__)


def hexdump(data, newline=True):
    for b in data:
        print("{:02X}".format(b), end=' ')
    if newline:
        print('')

def carmack_decompress(data):
    marker_bits = len([x for x in data if x in (0xA7, 0xA8, 0xFE)])

    # if not marker_bits:
        # logger.warn("Trying to decompress data that has no marker bits. "\
                    # "Probably not Carmack encoded")

    # First word (2 bytes) tell us the size of
    # The uncompressed data in bytes
    hexdump(data[0:2])
    size = struct.unpack('<H', data[0:2])[0]
    print("Should dcompress", size, "data is:", len(data))

    data_pointer = 2
    done = False
    hexdump(data[data_pointer: data_pointer+8])


    while not done and data_pointer < len(data):
        data_pointer += 1

    # assert False, "bailing out for developing"
    print("--")
    return data
