# coding=utf8
"""Test suite for gpss.coordinates."""
from io import StringIO
from os import remove

from contextlib import contextmanager
from tempfile import NamedTemporaryFile

from coordinates import retrieve_xyz, xyz2lbh

RNX = '''\
     2.11           OBSERVATION DATA    M (MIXED)           RINEX VERSION / TYPE
teqc  2016Nov7      NOAA/NOS/NGS/CORS   20170707 04:06:33UTCPGM / RUN BY / DATE
ASPA                                                        MARKER NAME
50503S006                                                   MARKER NUMBER
Giovanni Sella      NGS                                     OBSERVER / AGENCY
4733K06635          TRIMBLE NETR5       4.85                REC # / TYPE / VERS
30517456            TRM55971.00     NONE                    ANT # / TYPE
 -6100258.8690  -996506.1670 -1567978.8630                  APPROX POSITION XYZ
        0.0000        0.0000        0.0000                  ANTENNA: DELTA H/E/N
     1     1                                                WAVELENGTH FACT L1/2
    11    L1    L2    L5    C1    P1    C2    P2    C5    S1# / TYPES OF OBSERV
          S2    S5                                          # / TYPES OF OBSERV
    30.0000                                                 INTERVAL
    18                                                      LEAP SECONDS
  2017     7     6     0     0    0.0000000     GPS         TIME OF FIRST OBS
                                                            END OF HEADER
'''


@contextmanager
def mktmp(tmp_str):
    """Returns the name of the file which holds tmp_str inside, and removes
    the file after all.

    """
    tmp_file_name = None

    try:
        with NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.writelines(tmp_str)
            tmp_file.close()
            tmp_file_name = tmp_file.name

        yield tmp_file_name

    finally:
        if tmp_file_name:
            remove(tmp_file_name)


def test_retrieve_xyz():
    std_xyz = (-6100258.8690, -996506.1670, -1567978.8630)

    managers = [
        mktmp,
        StringIO,
    ]

    for manager in managers:
        with manager(RNX) as tmp_rinex:
            xyz = retrieve_xyz(tmp_rinex)
        assert xyz == std_xyz


def test_xyz2lbh():
    xyz = (4121967.5664, 2652172.1378, 4069036.5926)
    std_lbh = (32.75819444508266, 39.88741666437168, 989.9998747808859)
    lbh = xyz2lbh(*xyz)
    assert std_lbh == lbh
