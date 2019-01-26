import datetime
from io import StringIO

import pytest

from coordinates.broadcast import RinexNavFileV3


@pytest.fixture
def single_geo_message():
    msg = '''\
S20 2017 09 08 00 16 32 0.000000000000e+00 0.000000000000e+00 4.330030000000e+05
     4.063672000000e+04 0.000000000000e+00 0.000000000000e+00 1.000000000000e+00
    -1.124591600000e+04 0.000000000000e+00 0.000000000000e+00 3.276700000000e+04
     0.000000000000e+00 0.000000000000e+00 0.000000000000e+00 2.150000000000e+02
'''
    return StringIO(msg)


def single_irnss_message():
    msg = '''\
I02 2017 09 08 00 00 00-1.946836709976e-05 5.002220859751e-11 0.000000000000e+00
     0.000000000000e+00-6.674375000000e+02 4.678766317969e-09-1.339956192520e+00
    -2.152472734451e-05 2.332962467335e-03-1.420080661774e-05 6.493272409439e+03
     4.320000000000e+05-1.378357410431e-07-8.484979733807e-01 1.750886440277e-07
     5.045885145484e-01 5.167500000000e+02-3.044988695841e+00-4.598762985509e-09
    -5.589518540169e-10                    1.965000000000e+03                   
     4.000000000000e+00 0.000000000000e+00-8.381903171539e-09                   
     4.320120000000e+05                                                             
'''


def retrieve_ver_type(nav_file_v3):
    std = (3.03, 'N', 'M')
    with nav_file_v3 as filename:
        ver, f_type, system = RinexNavFileV3.retrieve_ver_type(filename)
        assert std == (ver, f_type, system)


def test_defaults(nav_file_v3):
    with nav_file_v3 as filename:
        nav = RinexNavFileV3(filename)
        assert nav.version == 3.03
        assert nav.system == 'M'
        assert nav.file_type == 'N'
        assert nav.filename == filename


def test_parse_epoch(single_geo_message):
    std = (
        'S', 20, datetime.datetime(2017, 9, 8, 0, 16, 32),
        (0, 0, 433003),
    )
    test = RinexNavFileV3.parse_epoch(single_geo_message)
    assert std == test


def test_iter(nav_file_v3):
    std = (
        (
            'G', 1, datetime.datetime(2017, 9, 8, 0, 0, 0),
            (5.530333146453e-05, -4.547473508865e-13, 0.0),
            (7.200000000000e+01, -2.653125000000e+01, 4.883774857397e-09,
             -2.309091328065e-01,
             -1.233071088791e-06, 7.021094555967e-03, 2.788379788399e-06,
             5.153673307419e+03,
             4.320000000000e+05, 7.823109626770e-08, 2.011192878165e+00,
             4.284083843231e-08,
             9.681868691207e-01, 3.310000000000e+02, 6.192489497701e-01,
             -8.576071513516e-09,
             -2.500104139373e-11, 1.000000000000e+00, 1.965000000000e+03,
             0.000000000000e+00,
             2.000000000000e+00, 0.000000000000e+00, 5.587935447693e-09,
             7.200000000000e+01,
             4.248180000000e+05, 4.000000000000e+00),
        ),
        (
            'S', 20, datetime.datetime(2017, 9, 8, 0, 16, 32),
            (0.000000000000e+00, 0.000000000000e+00, 4.330030000000e+05),
            (4.063672000000e+04, 0.000000000000e+00, 0.000000000000e+00,
             1.000000000000e+00,
             -1.124591600000e+04, 0.000000000000e+00, 0.000000000000e+00,
             3.276700000000e+04,
             0.000000000000e+00, 0.000000000000e+00, 0.000000000000e+00,
             2.150000000000e+02),
        ),
    )
    with nav_file_v3 as filename:
        nav = RinexNavFileV3(filename)
        for i, msg in enumerate(nav):
            assert std[i] == msg
