


class Sound():

    @classmethod
    def from_bytes(cls, data):
        sound = cls()
        cls.data = data
        return sound

