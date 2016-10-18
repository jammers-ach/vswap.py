'''
Implementation of carmack decompression

It's kinda similar to Run Length Encoding but with a bit more
http://www.shikadi.net/moddingwiki/Carmack_compression
'''
import logging
import struct

logger = logging.getLogger(__name__)

readword = lambda d,p: struct.unpack('<H', d[p:p+2])[0]
readbyte = lambda d,p: struct.unpack('<B', d[p:p+1])[0]

def hexdump(data, newline=True):
    for b in data:
        print("{:02X}".format(b), end=' ')
    if newline:
        print('')

def carmack_decompress(data):
    # First word (2 bytes) tell us the size of
    # The uncompressed data in bytes
    size = readword(data,0)
    print("cmrk Should dcompress", size, "data is:", len(data))
    new_data = [0] * (size)

    src_pointer = 2
    dest_pointer = 0
    while src_pointer < len(data):
        cpy_cnt = data[src_pointer] # How many bytes to copy
        cpy_type = data[src_pointer+1] # carmac tag
        src_pointer += 2

        if cpy_type == 0xA7 or cpy_type == 0xA8:
            if cpy_cnt == 0x00: # a copy count of 0x00 is an exepction
                new_data[dest_pointer] = cpy_type
                new_data[dest_pointer+1] = data[src_pointer]
                dest_pointer +=2

            else:
                # we copy the last n bytes we wrote
                if cpy_type == 0xA7:
                    rel_oss = readbyte(data, src_pointer)
                    src_pointer += 1
                    copy_oss = dest_pointer - (2*rel_oss)
                else:
                    oss = readword(data, src_pointer)
                    src_pointer += 2
                    copy_oss = oss * 2

                for i in range(cpy_cnt):
                    new_data[dest_pointer] = new_data[copy_oss + i]
                    dest_pointer += 1

        else:
            new_data[dest_pointer] = cpy_cnt
            new_data[dest_pointer+1] = cpy_type
            dest_pointer +=2


    hexdump(new_data)

    return bytes(new_data)


def rlew_decompress(data):
    size = int(readword(data,0) / 2)
    print("rlew Should dcompress", size, " words data is:", len(data), "btes")
    new_data = []

    src_pointer = 2
    words_read = 0
    while words_read < size:
        w1 = readword(data, src_pointer) # Magic word
        src_pointer += 2


        if w1 == 0xABCD:
            w2 = readword(data, src_pointer) # Copy count
            w3 = readword(data, src_pointer+2) # Copy datao
            src_pointer += 6

            print("Decompressing {} words, currently read {}, {} in total".format(
                w2,
                words_read,
                size
            ))

            if w2 + words_read > size:
                raise IndexError("Trying to decompress {} words, when {} read, and {} in total".format(
                    w2,
                    words_read,
                    size
                ))

            for i in range(w2):
                new_data.append(w3)

            words_read += w2
        else:
            new_data.append(w1)
            words_read += 1

    assert False, "bailing out for developing"

    return bytes(new_data)
