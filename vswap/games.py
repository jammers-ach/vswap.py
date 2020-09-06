import logging
import os

from pathlib import Path

from vswap.sprites import load_swap_chunk_offsets, load_sprite_chunks
from vswap.pallets import wolf3d_pallet
from vswap.textures import Wall, Sprite
from vswap.graphics import load_dict, load_head, load_chunks, extract_images

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
        for chunk in vswap_chunks:
            if type(chunk) == Sprite:
                self.sprites.append(chunk)
            if type(chunk) == Wall:
                self.walls.append(chunk)


    def load_graphics(self):
        logger.info("Loading %s", self.graphfile)
        tree = load_dict(self.gamedir, self.dictfile)
        header = load_head(self.gamedir, self.headfile)
        chunks = load_chunks(self.gamedir, self.graphfile, tree, header)
        self.images = extract_images(chunks)


    def output(self, target):
        '''output all our assests to a target directory'''
        target = Path(target)

        for i, sprite in enumerate(self.sprites):
            fname = "sprite{:04d}.png".format(i)
            logger.info("Writing {}".format(fname))
            sprite.output(target / fname, self.pallet)

        for i, wall in enumerate(self.walls):
            fname = "wall{:04d}.png".format(i)
            logger.info("Writing {}".format(fname))
            wall.output(target / fname, self.pallet)

        for i, image in enumerate(self.images):
            fname = "image{:04d}.png".format(i)
            logger.info("Writing {}".format(fname))
            image.output(target / fname, self.pallet)


class Wolf3dFull(Wolf3dGame):
    pallet = wolf3d_pallet
    swapfile = 'VSWAP.WL6'
    dictfile = 'VGADICT.WL6'
    headfile = 'VGAHEAD.WL6'
    graphfile = 'VGAGRAPH.WL6'

