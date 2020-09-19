import logging
import wave

from io import BytesIO
from opstream import OPLStream

logger = logging.getLogger(name=__name__)

# thanks to wolfcore_pm.c from wolfextractor
class Sound():
    samplerate = 7000 #Hz
    nchannels = 1
    samplewidth = 1

    def output(self, filename):
        #wav_write( tempFileName, soundBuffer, totallength, 1, SAMPLERATE, 1 );
        # 1 channel
        # 7000hz sample rate
        # bytes per sample = 1
        logger.info("writing %s", filename)
        with wave.open("{}".format(filename), 'w') as f:
            f.setnchannels(self.nchannels)
            f.setsampwidth(self.samplewidth)
            f.setframerate(self.samplerate)
            f.writeframes(self.data)

    @classmethod
    def from_bytes(cls, data):
        sound = cls()
        sound.data = data
        return sound

    @classmethod
    def from_imf(cls, data):
        '''make a sound from adlib music'''
        stream = BytesIO(data)
        oplstream = OPLStream.from_stream(stream)
        sound = cls()
        sound.nchannels = oplstream.num_channels
        sound.samplewidth = oplstream.sample_size
        sound.samplerate = oplstream.freq
        sound.data = oplstream.get_pcm()
        return sound

    @classmethod
    def from_adlibfx(cls, data):
        '''make a sound from adlib music'''
        stream = BytesIO(data)
        oplstream = OPLStream.from_adlibfx(stream)
        sound = cls()
        sound.nchannels = oplstream.num_channels
        sound.samplewidth = oplstream.sample_size
        sound.samplerate = oplstream.freq
        sound.data = oplstream.get_pcm()
        return sound
