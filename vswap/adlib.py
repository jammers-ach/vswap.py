# with help from
# http://www.shikadi.net/moddingwiki/AudioT_Format
import struct
import logging

from vswap.sounds import Sound
from itertools import tee

logger = logging.getLogger(name=__name__)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def load_audio_head(gamedir, audiohead):
    audiohead = gamedir / audiohead

    offsets = []
    with audiohead.open('rb') as f:
        while True:
            data = f.read(4)
            if data == b'':
                break
            offset = struct.unpack('<L', data)[0]
            offsets.append(offset)

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
            else:
                audios.append(bytes())

    return audios

def convert_to_wav(audios, fx_chunks, music_chunks):
    logger.info("Converting soundfx")
    fx = []
    # TODO
    #for i in range(fx_chunks[0], fx_chunks[1]):
    #    print("reading fx {} ({} bytes)".format(i, len(audios[i])))
    #    fx.append(Sound.from_adlib(audios[i]))

    logger.info("Converting music")
    music = [Sound.from_imf(audios[i]) for i in range(music_chunks[0], music_chunks[1])]
    return [fx, music]

if __name__ == '__main__':
    import sys
    import pathlib

    if len(sys.argv) < 2:
        print("graphics.py GAMEDIR")
    else:
        gamedir = pathlib.Path(sys.argv[1])
        headfile = 'audiohed.bs6'
        audiofile = 'audiot.bs6'

        header = load_audio_head(gamedir, headfile)
        audios = load_audio(gamedir, audiofile, header)
        print(len(audios))

        for i, a in enumerate(audios):
            print("{:02d} {}".format(i, len(a)))

        fx, music= convert_to_wav(audios, [100,110], [300, 319])

        for i, m in enumerate(music):
            fname="out/music{:03d}.wav".format(i)
            m.output(fname)

        for i, f in enumerate(fx):
            fname="out/fx{:03d}.wav".format(i)
            f.output(fname)
