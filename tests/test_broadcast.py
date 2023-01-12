import pytest

from io import StringIO

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

def test_version_stringio_reading_v2(nav_iter_v2):
    info = RinexNavFileV2.retrieve_ver_type(nav_iter_v2)
    assert len(info) == 2
            
def test_version_stringio_reading_v3(nav_iter_v3):
    info = RinexNavFileV3.retrieve_ver_type(nav_iter_v3)
    assert len(info) == 3
