import numpy as np
import struct

readword = lambda d,p: struct.unpack('<H', d[p:p+2])[0]
readlong = lambda d,p: struct.unpack('<L', d[p:p+4])[0]

class Texture:
    size = (64, 64)

    def __init__(self, texture):
        assert texture.shape == self.size
        self.texture = texture

    def _print(self):
        '''Quick debug print of this wall'''
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                print("{:02X}".format(int(self.texture[i][j])), end='')

            print('')


class Wall(Texture):
    size = (64, 64)

    @classmethod
    def from_bytes(cls, data):
        # Check data right size
        assert len(data) == (cls.size[0] * cls.size[1]), "wall wrong size"

        # bytes to int
        data = np.array([int(i) for i in data])

        # reshape
        data = data.reshape(cls.size)
        data = np.rot90(data, 3)

        return cls(data)


class Sprite(Texture):

    @classmethod
    def from_bytes(cls, data):

        texture = np.zeros(cls.size)

        # First two words are the start and end column
        first_column = readword(data, 0)
        last_column = readword(data, 2)
        num_columns = last_column - first_column + 1

        post_offsets = [readword(data, (i*2) + 4) for i in range(num_columns)]

        # Location of the pixel pool
        pxpl = (num_columns * 2) + 4

        for col,post_offset in enumerate(post_offsets):
            post_stop = readword(data, post_offset) // 2
            post_start = readword(data, post_offset+4) // 2

            if(post_stop < post_start):
                continue

            for i in range(post_start, post_stop):
                texture[first_column + col, i] = data[pxpl]
                pxpl += 1


        texture = np.rot90(texture, 3)
        return cls(texture)
