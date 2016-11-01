import numpy as np

class Wall:
    size = (64, 64)

    def __init__(self, texture):
        assert texture.shape == self.size
        self.texture = texture


    def _print(self):
        '''Quick debug print of this wall'''
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                print("{:02X}".format(self.texture[i][j]), end='')

            print('')


    @classmethod
    def from_bytes(cls, data):
        # Check data right size
        assert len(data) == (cls.size[0] * cls.size[1]), "wall wrong size"

        # bytes to int
        data = np.array([int(i) for i in data])

        # reshape
        data = data.reshape(cls.size)

        wall = cls(data)
        return wall
