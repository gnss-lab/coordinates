import pytest

from coordinates.broadcast import rnx_nav
from coordinates.broadcast import RinexNavFileV3, RinexNavFileV2


def test_rnx_nav_v2(nav_file_v2):
    with nav_file_v2 as filename:
        nav = rnx_nav(filename)
        assert isinstance(nav, RinexNavFileV2)

def test_rnx_nav_v3(nav_file_v3):
    with nav_file_v3 as filename:
        nav = rnx_nav(filename)
        assert isinstance(nav, RinexNavFileV3)
