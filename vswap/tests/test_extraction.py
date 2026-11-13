import pytest
import os
import tempfile
import hashlib

from pathlib import Path
from vswap.games import detect_game, BstoneFull

def _md5file(fname):
    return hashlib.md5(open(fname,'rb').read()).hexdigest()

def test_detect_bstone(path="assets/bsa"):
    assert os.path.exists(path), "No bstone in assets"
    game = detect_game(path)
    assert game == BstoneFull

def test_load_bstone(path="assets/bsa"):
    assert os.path.exists(path), "No bstone in assets"
    game = detect_game(path)(path)
    game.load_maps()
    assert len(game.maps) == 90

    game.load_vswaps()
    assert len(game.walls) == 202
    assert len(game.sounds) == 59
    assert len(game.sprites) == 814

    game.load_graphics()
    assert len(game.images) == 159
    assert len(game.fonts) == 5

    game.load_adlib()
    assert len(game.fx) == 99
    assert len(game.music) == 19


def test_bstone_walls(path="assets/bsa"):
    assert os.path.exists(path), "No bstone in assets"
    game = detect_game(path)(path)
    game.load_vswaps()

    with tempfile.TemporaryDirectory() as dp:
        p = Path(dp)
        game._output_walls(p)
        assert _md5file(p/"wall0000.png") == "efbf552adc1df2c45d7542adac781ff1"
        assert _md5file(p/"wall0165.png") == "369e0e12b170f5d14e945501eed2e457"

def test_bstone_sprites(path="assets/bsa"):
    assert os.path.exists(path), "No bstone in assets"
    game = detect_game(path)(path)
    game.load_vswaps()

    with tempfile.TemporaryDirectory() as dp:
        p = Path(dp)
        game._output_sprites(p)
        assert _md5file(p/"sprite0594.png") == "6a76725b6ba0d289abbb50c2188a7506"
        assert _md5file(p/"sprite0109.png") == "61ec5f4df6718426d8361846638c0239"

