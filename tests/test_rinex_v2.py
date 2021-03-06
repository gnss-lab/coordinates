import datetime
from io import StringIO
import pytest

from coordinates.broadcast import RinexNavFileV2
from coordinates.exceptions import RinexNavFileError


@pytest.fixture
def single_message():
    nav = '''\
 1 15  6 21  1 59 44.0-3.993976861238D-06 5.684341886081D-13 0.000000000000D+00
    1.400000000000D+01-4.700000000000D+01 4.392682972878D-09-2.839730993303D+00
   -2.508983016014D-06 4.379398305900D-03 1.055561006069D-05 5.153669719696D+03
    7.184000000000D+03-7.823109626770D-08-2.426429599721D+00-8.381903171539D-08
    9.624417937924D-01 1.785000000000D+02 3.916456197607D-01-7.789967340551D-09
    1.664355041354D-10 1.000000000000D+00 1.850000000000D+03 0.000000000000D+00
    2.000000000000D+00 0.000000000000D+00 5.587935447693D-09 1.400000000000D+01
    3.000000000000D+01 4.000000000000D+00
'''
    file_object = StringIO(nav)
    return file_object


def test_retrieve_ver_type(nav_file_v2):
    std = (2.0, 'N')
    with nav_file_v2 as filename:
        version, file_type = RinexNavFileV2.retrieve_ver_type(filename)
        assert std == (version, file_type)


def test_parse_epoch(single_message):
    # test message
    std = (
        1,
        datetime.datetime(2015, 6, 21, 1, 59, 44),
        (
            -3.993976861238e-06,
            5.684341886081e-13,
            0.000000000000e+00,
        ),
    )

    test = RinexNavFileV2.parse_epoch(single_message)

    assert std == test

    with pytest.raises(RinexNavFileError):
        RinexNavFileV2.parse_epoch(single_message)

    # EOF
    for _ in range(6):
        next(single_message)

    with pytest.raises(EOFError):
        RinexNavFileV2.parse_epoch(single_message)


def test_read_orbits(single_message):
    # Skip an epoch
    next(single_message)

    std = [
        '    1.400000000000D+01-4.700000000000D+01 4.392682972878D-09-2.839730993303D+00',
        '   -2.508983016014D-06 4.379398305900D-03 1.055561006069D-05 5.153669719696D+03',
        '    7.184000000000D+03-7.823109626770D-08-2.426429599721D+00-8.381903171539D-08',
        '    9.624417937924D-01 1.785000000000D+02 3.916456197607D-01-7.789967340551D-09',
        '    1.664355041354D-10 1.000000000000D+00 1.850000000000D+03 0.000000000000D+00',
        '    2.000000000000D+00 0.000000000000D+00 5.587935447693D-09 1.400000000000D+01',
        '    3.000000000000D+01 4.000000000000D+00',
    ]
    test = RinexNavFileV2.read_orbits(single_message, 7)
    assert std == test

    # EOF
    with pytest.raises(RinexNavFileError, match='Unexpected end of the file'):
        RinexNavFileV2.read_orbits(single_message, 7)


def test_parse_orbits(nav_file_v2):
    # GPS
    orbits = [
        '    0.350000000000D+02 0.222500000000D+02 0.482198656938D-08 0.368417754673D+00',
        '    0.121630728245D-05 0.527631223667D-02 0.668689608574D-05 0.515364252472D+04',
        '    0.864000000000D+05 0.391155481338D-07-0.140616900879D+01 0.106170773506D-06',
        '    0.963711739811D+00 0.247687500000D+03 0.450110393247D+00-0.827070165078D-08',
        '    0.284654714154D-09 0.100000000000D+01 0.189200000000D+04 0.000000000000D+00',
        '    0.200000000000D+01                    0.512227416039D-08 0.350000000000D+02',
        '    0.805020000000D+05 0.400000000000D+01 0.000000000000D+00 0.000000000000D+00',
    ]

    values_per_orbit = (4, 4, 4, 4, 4, 4, 2)

    std = (
        35.0, 22.25, 0.482198656938e-08, 0.368417754673e+00,
        0.121630728245e-05, 0.527631223667e-02, 0.668689608574e-05,
        0.515364252472e+04,
        86400.0, 0.391155481338e-07, -0.140616900879e+01, 0.106170773506e-06,
        0.963711739811e+00, 0.247687500000e+03, 0.450110393247e+00,
        -0.827070165078e-08,
        0.284654714154e-09, 1.0, 0.189200000000e+04, 0.0,
        2.0, 0.0, 0.512227416039e-08, 35.0,
        0.805020000000e+05, 4.0,
    )
    with nav_file_v2 as filename:
        nav = RinexNavFileV2(filename)
        test = nav.parse_orbits(orbits, values_per_orbit)

    assert test == std


def test_skip_header(nav_iter_v2):
    RinexNavFileV2.skip_header(nav_iter_v2)
    std = ' 1 16  4 11  0  0  0.0 0.169607810676D-04 0.113686837722D-11 0.000000000000D+00\n'
    test = next(nav_iter_v2)
    assert std == test


def test_iter(nav_file_v2):
    std = [
        (
            'G', 1, datetime.datetime(2016, 4, 11, 0, 0, 0),
            (0.169607810676e-04, 0.113686837722e-11, 0.0),
            (35.0, 22.25, 0.482198656938e-08, 0.368417754673e+00,
             0.121630728245e-05, 0.527631223667e-02, 0.668689608574e-05,
             0.515364252472e+04,
             86400, 0.391155481338e-07, -0.140616900879e+01, 0.106170773506e-06,
             0.963711739811e+00, 247.6875, 0.450110393247e+00,
             -0.827070165078e-08,
             0.284654714154e-09, 1, 1892.0, 0.0,
             2.0, 0.0, 0.512227416039e-08, 35.0,
             80502.0, 4.0,)
        ),
        (
            'G', 2, datetime.datetime(2016, 4, 11, 0, 0, 0),
            (0.597649253905e-03, -0.181898940355e-11, 0.0),
            (83.0, 18.59375, 0.527057686384e-08, 0.763017673126e+00,
             0.114180147648e-05, 0.156129685929e-01, 0.783614814282e-05,
             0.515374914742e+04,
             86400.0, -0.163912773132e-06, -0.145069785349e+01,
             0.100582838059e-06,
             0.942463959213e+00, 223.65625, -0.213318032835e+01,
             -0.861071569602e-08,
             0.216080431326e-09, 1.0, 1892.0, 0.0,
             2.0, 0.0, -0.200234353542e-07, 83.0,
             86400.0, 0.0)
        ),
    ]
    with nav_file_v2 as filename:
        nav = RinexNavFileV2(filename)
        for i, msg in enumerate(nav):
            assert std[i] == msg
