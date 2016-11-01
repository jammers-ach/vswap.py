import struct

class PictTable(Chunk):
    '''defines the width and height of the pictures'''
    fmt = '<HH'
    fields = ['width', 'height']


class Chunk:
    '''Generic data chunk
    subclass this with a fmt and fields'''

    def __init__(self, *args, **kwargs):
        assert len(args) == len(self.fields)
        for attr, val in zip(self.fields, args):
            setattr(self, attr, val)

    @classmethod
    def from_chunk(cls, chunk_id, data):
        '''Decode this chunk type from this data'''
        datasize = struct.calcsize(cls.fmt)

        if len(data) != datasize:
            raise ValueError("{} expects {} bytes of data, {} given".format(
                cls.__name__,
                datasize,
                len(data)
            ))

        data = struct.unpack(cls.fmt, data)
        ret = cls(*data)
        ret.chunk_id = chunk_id
        return ret


