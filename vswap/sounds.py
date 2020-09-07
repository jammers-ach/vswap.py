import logging

import wave

logger = logging.getLogger(name=__name__)

# thanks to wolfcore_pm.c from wolfextractor
class Sound():
    samplerate = 7000 #Hz

    def output(self, filename):
        #wav_write( tempFileName, soundBuffer, totallength, 1, SAMPLERATE, 1 );
        # 1 channel
        # 7000hz sample rate
        # bytes per sample = 1
        logger.info("writing %s", filename)
        with wave.open("{}".format(filename), 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(1)
            f.setframerate(self.samplerate)
            f.writeframes(self.data)

    @classmethod
    def from_bytes(cls, data):
        sound = cls()
        sound.data = data
        return sound

