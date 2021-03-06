import numpy as np
import struct
import logging

from PIL import Image


logger = logging.getLogger(name=__name__)


readword = lambda d,p: struct.unpack('<H', d[p:p+2])[0]
readsignedword = lambda d,p: struct.unpack('<h', d[p:p+2])[0]
readlong = lambda d,p: struct.unpack('<L', d[p:p+4])[0]

class Texture:
    size = (64, 64)

    def __init__(self, texture):
        assert texture.shape == self.size, "{} expected {}".format(texture.shape, self.size)
        self.texture = texture

    def __str__(self):
        '''Quick debug print of this Texture'''
        render = ''
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                render += "{:02X}".format(int(self.texture[i][j]))
            render += "\n"
        return render

    def _pallet_convert(self, pallet):
        new_texture = np.empty((self.size[0], self.size[1], 4), dtype='uint8')
        t = lambda x: pallet[int(x)]
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                r,g,b = t(self.texture[i][j])
                new_texture[i][j][0] = r
                new_texture[i][j][1] = g
                new_texture[i][j][2] = b
                new_texture[i][j][3] = 0 if self.texture[i][j] == -1 else 255
        return new_texture

    def output(self, filename, pallet):
        '''Write this'''
        logger.info("writing %s", filename)
        result = Image.fromarray(self._pallet_convert(pallet), mode='RGBA')
        result.save(filename)


class Font(Texture):
    def __init__(self, texture):
        self.size = texture.shape
        self.texture = texture

    @classmethod
    def from_chunk(cls, data, w, h):
        assert len(data) == (w * h), "wrong image size, expected {} bytes got {}".format((w*h), len(data) )

        conv = lambda x: -1 if x == 0x00 else 0
        data = np.array([conv(i) for i in data])
        # reshape
        data = data.reshape((h,w))

        return cls(data)




class Graphic(Texture):

    def __init__(self, texture):
        self.size = texture.shape
        self.texture = texture

    @classmethod
    def from_chunk(cls, data, w, h):
        assert len(data) == (w * h), "wrong image size, expected {} bytes got {}".format((w*h), len(data) )

        # new texture
        new_texture = np.empty((w,h,1), dtype='uint8')

        #http://gaarabis.free.fr/_sites/specs/files/wlspec_VGA.html#GUI5
        for plane in range(4):
            for y in range(h):
                for x in range(int(w/4)):
                    dst_x = (x*4) + plane
                    src_pxl = x + (int((w*h)/4) * plane)
                    src_pxl += (y * int(w/4))

                    new_texture[dst_x][y] = data[int(src_pxl)]
        texture = np.rot90(new_texture, 3)
        texture = np.flip(texture, 1)
        return cls(texture)



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
        data = np.flip(data, 1)

        return cls(data)


class Sprite(Texture):

    @classmethod
    def from_bytes(cls, data):

        # -1 indicates transparrent
        texture = np.full(cls.size, -1)

        # First two words are the start and end column
        first_column = readword(data, 0)
        last_column = readword(data, 2)
        num_columns = last_column - first_column + 1
        post_offsets = [readword(data, (i*2) + 4) for i in range(num_columns)]

        for col,post_offset in enumerate(post_offsets):

            while True:
                line_cmd1 = readword(data, post_offset)
                if line_cmd1 == 0:
                    break
                line_cmd2 = readsignedword(data, post_offset+2)
                line_cmd3 = readword(data, post_offset+4)
                post_offset += 6

                post_stop = line_cmd1 // 2
                post_start = line_cmd3 // 2

                pxpl_offset = post_start + (line_cmd2)
                pxpl = pxpl_offset

                for i in range(post_start, post_stop):
                    texture[first_column + col, i] = data[pxpl]
                    pxpl += 1

        texture = np.rot90(texture, 3)
        texture = np.flip(texture, 1)
        return cls(texture)
