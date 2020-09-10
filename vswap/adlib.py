# with help from
# http://www.shikadi.net/moddingwiki/AudioT_Format
import struct
import os
from itertools import tee, chain

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def load_head(gamedir, audiohead):
    audiohead = gamedir / audiohead

    offsets = []
    with audiohead.open('rb') as f:
        while True:
            data = f.read(4)
            if data == b'':
                break
            offset = struct.unpack('<L', data)[0]
            offsets.append(offset)

    print(offsets)
    return offsets

def load_audio(gamedir, audiofile, offsets):
    audio = gamedir / audiofile

    audios = []

    with audio.open('rb') as f:
        for o1, o2 in pairwise(offsets):
            size = o2-o1
            if size != 0:
                data = f.read(size)
                audios.append(data)
    return audios

if __name__ == '__main__':
    import sys
    import pathlib

    if len(sys.argv) < 2:
        print("graphics.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        headfile = 'audiohed.bs6'
        audiofile = 'audiot.bs6'

        header = load_head(gamedir, headfile)
        audios = load_audio(gamedir, audiofile, header)

        for i, audio in enumerate(audios):
            fname = 'out/audio{:03d}.imf'.format(i)
            with open(fname, 'wb') as f:
                f.write(audio)
