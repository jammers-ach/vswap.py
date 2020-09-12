import logging
import os

from pathlib import Path

from vswap.sprites import load_swap_chunk_offsets, load_sprite_chunks, group_sound_chunks
from vswap.pallets import wolf3d_pallet, bstone_pallet
from vswap.textures import Wall, Sprite
from vswap.sounds import Sound
from vswap.graphics import load_dict, load_head, load_chunks, extract_images, load_fonts

logger = logging.getLogger(name=__name__)

class Wolf3dGame():

    def __init__(self, gamedir):
        self.gamedir = Path(gamedir)
        assert self.swapfile
        assert self.dictfile
        assert self.headfile
        assert self.graphfile
        self._scan_gamedir()

    def _scan_gamedir(self):
        # Scan gamedir to see if we're in upper or lowercase
        self.swapfile = self._correct_case(self.swapfile)
        self.dictfile = self._correct_case(self.dictfile)
        self.headfile = self._correct_case(self.headfile)
        self.graphfile = self._correct_case(self.graphfile)


    def _correct_case(self, fname):
        '''checks if a file exists in upper or lower case
        errors if it doesn't exist'''
        if os.path.isfile(self.gamedir / fname.upper()):
            return fname.upper()
        elif os.path.isfile(self.gamedir / fname.lower()):
            return fname.lower()
        else:
            raise Exception("{} or {} not found".format(self.gamedir / fname.upper(),
                                                        self.gamedir / fname.lower()))



    def load_all(self):
        self.load_vswaps()
        self.load_graphics()

    def load_vswaps(self):
        logger.info("Loading %s", self.swapfile)
        data_offsets = load_swap_chunk_offsets(self.gamedir, self.swapfile)
        vswap_chunks = load_sprite_chunks(self.gamedir, self.swapfile, data_offsets)
        self.walls= []
        self.sprites = []
        self.sounds = []
        for chunk in vswap_chunks:
            if type(chunk) == Sprite:
                self.sprites.append(chunk)
            if type(chunk) == Wall:
                self.walls.append(chunk)
            if type(chunk) == Sound:
                self.sounds.append(chunk)


    def load_graphics(self):
        logger.info("Loading %s", self.graphfile)
        tree = load_dict(self.gamedir, self.dictfile)
        header = load_head(self.gamedir, self.headfile)
        chunks = load_chunks(self.gamedir, self.graphfile, tree, header)
        self.images = extract_images(chunks, self.graphics_offset)
        self.fonts = load_fonts(chunks, self.font_chunks)



    def output(self, target):
        '''output all our assests to a target directory'''
        target = Path(target)

        for i, sound in enumerate(self.sounds):
            fname = "sound{:04d}.wav".format(i)
            sound.output(target / fname)

        for i, sprite in enumerate(self.sprites):
            fname = "sprite{:04d}.png".format(i)
            sprite.output(target / fname, self.pallet)

        for i, wall in enumerate(self.walls):
            fname = "wall{:04d}.png".format(i)
            wall.output(target / fname, self.pallet)

        for i, image in enumerate(self.images):
            fname = "image{:04d}.png".format(i)
            image.output(target / fname, self.pallet)

        for i, font in enumerate(self.fonts):
            for j, glyph in enumerate(font):
                fname = "font-{}-{:03d}.png".format(i+1,j)
                glyph.output(target / fname, self.pallet)





class Wolf3dFull(Wolf3dGame):
    pallet = wolf3d_pallet
    swapfile = 'VSWAP.WL6'
    dictfile = 'VGADICT.WL6'
    headfile = 'VGAHEAD.WL6'
    graphfile = 'VGAGRAPH.WL6'
    graphics_offset = 3
    font_chunks = [1,2]


class BstoneFull(Wolf3dGame):
    pallet = bstone_pallet
    swapfile = 'VSWAP.BS6'
    dictfile = 'VGADICT.BS6'
    headfile = 'VGAHEAD.BS6'
    graphfile = 'VGAGRAPH.BS6'
    graphics_offset = 6
    font_chunks = [1,2,3,4,5]

class BstonePlanet(Wolf3dGame):
    pallet = bstone_pallet
    swapfile = 'VSWAP.VSI'
    dictfile = 'VGADICT.VSI'
    headfile = 'VGAHEAD.VSI'
    graphfile = 'VGAGRAPH.VSI'
    graphics_offset = 6
    font_chunks = [1,2,3,4,5]

def detect_game(gamedir):
    gamedir = Path(gamedir)
    games = [Wolf3dFull, BstoneFull, BstonePlanet]
    for game in games:
        fname = game.swapfile
        if os.path.isfile(gamedir / fname.upper()) or \
            os.path.isfile(gamedir / fname.lower()):
            logger.info("Detected {}".format(game))
            return game
    raise Exception("No game found in {}".format(gamedir))

