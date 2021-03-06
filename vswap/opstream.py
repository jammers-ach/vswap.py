import pyopl
import wave
import sys

from io import BytesIO
from struct import unpack


class OPLStream:
    # Playback frequency.  Try a different value if the output sounds stuttery.
    freq = 44100

    # How many bytes per sample (2 == 16-bit samples).  This is the only value
    # currently implemented.
    sample_size = 2

    # How many channels to output (2 == stereo).  The OPL2 is mono, so in stereo
    # mode the mono samples are copied to both channels.  Enabling OPL3 mode will
    # switch the synth to true stereo (and in this case setting num_channels=1
    # will just drop the right channel.)  It is done this way so that you can set
    # num_channels=2 and output stereo data, and it doesn't matter whether the
    # synth is in OPL2 or OPL3 mode - it will always work.
    num_channels = 2

    # How many samples to synthesise at a time.  Higher values will reduce CPU
    # usage but increase lag.
    synth_size = 512

    def __init__(self, ticksPerSecond):
        self.opl = pyopl.opl(self.freq, sampleSize=self.sample_size, channels=self.num_channels)
        self.ticksPerSecond = ticksPerSecond
        self.buf = bytearray(self.synth_size * self.sample_size * self.num_channels)
        self.delay = 0
        self.stream = BytesIO()

    def writeReg(self, reg, value):
        self.opl.writeReg(reg, value)

    def wait(self, ticks):
        # Rather than calculating the exact number of samples we need to generate,
        # we just keep generating 512 samples at a time until we've waited as close
        # as possible to the requested delay.
        # This does mean we might wait for up to 511/freq samples too little (at
        # 48kHz that's a worst-case of 10.6ms too short) but nobody should notice
        # and it saves enough CPU time and complexity to be worthwhile.
        self.delay += ticks * self.freq / self.ticksPerSecond
        while self.delay > self.synth_size:
            self.opl.getSamples(self.buf)
            self.stream.write(self.buf)
            self.delay -= self.synth_size

    def get_pcm(self):
        return self.stream.getvalue()

    def save(self, fname):
        with wave.open("{}".format(fname), 'w') as f:
            f.setnchannels(self.num_channels)
            f.setsampwidth(self.sample_size)
            f.setframerate(self.freq)
            f.writeframes(self.get_pcm())

    @classmethod
    def from_file(cls, fname, ticksPerSecond=700):
        with open(fname, 'rb') as f:
            return cls.from_stream(f, ticksPerSecond)

    @classmethod
    def from_stream(cls, f, ticksPerSecond=700):
        chunk = f.read(2)
        lenData, = unpack('H', chunk)
        if lenData == 0:
            f.seek(0)

        # Set up the OPL synth
        oplStream = cls(ticksPerSecond)

        # Enable Wavesel on OPL2
        oplStream.writeReg(1, 32)

        lenRead = 0
        while lenRead < lenData or lenData == 0:
            # Read the next OPL bytes from the file
            chunk = f.read(4)
            lenRead += 4
            if not chunk:
                break

            reg, val, delay = unpack('BBH', chunk)

            # Send them to the synth
            oplStream.writeReg(reg, val)

            # Wait for the given number of ticks
            if delay:
                oplStream.wait(delay)

        return oplStream


    @classmethod
    def from_adlibfx(cls, f):
        # All made possible thanks to
        # http://www.shikadi.net/moddingwiki/Adlib_sound_effect
        length, = unpack('<L', f[0:4])
        assert len(f) - length == 33, "FX chunk is not valid"
        priority, = unpack('<H', f[4:6])
        instrument_settings = f[6:6+16]
        octave = f[6+16]
        sound = f[6+17:6+17+length]

        oplStream = cls(140)
        oplStream.writeReg(0x20, instrument_settings[0])
        oplStream.writeReg(0x23, instrument_settings[1])
        oplStream.writeReg(0x40, instrument_settings[2])
        oplStream.writeReg(0x43, instrument_settings[3])
        oplStream.writeReg(0x60, instrument_settings[4])
        oplStream.writeReg(0x63, instrument_settings[5])
        oplStream.writeReg(0x80, instrument_settings[6])
        oplStream.writeReg(0x83, instrument_settings[7])
        oplStream.writeReg(0xE0, instrument_settings[8])
        oplStream.writeReg(0xE3, instrument_settings[9])
        oplStream.writeReg(0xC0, instrument_settings[10])

        block = (octave & 7) << 2
        note = False
        for b in sound:
            if b == 0:
                oplStream.writeReg(0xb0, block)
                note = False
            else:
                oplStream.writeReg(0xA0, b)
                if not note:
                    oplStream.writeReg(0xb0, block | 0x20)
                    note = True
            oplStream.wait(1)

        return oplStream


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please specify one IMF filename.")
    oplStream = OPLStream.from_file(sys.argv[1])
    oplStream.save("test.wav")

