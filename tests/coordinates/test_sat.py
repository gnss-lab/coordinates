import datetime

import pytest
from coordinates.sat import reference_time, get_week_sec, get_day_sec, read_nav_data, \
    nearest_message, get_dt, find_message, GPS_WAY, xyz_calculator, gps_sat_xyz, \
    glo_sat_xyz, GLO_WAY


def test_get_week_sec():
    epoch_start = datetime.datetime(1980, 1, 6, 0, 0, 0)
    epoch = datetime.datetime(1980, 1, 8, 0, 0, 30)

    std = 172830  # 2 days and 30 seconds
    test = get_week_sec(epoch, epoch_start)

    assert std == test


def test_get_day_sec():
    epoch = datetime.datetime(1980, 1, 6, 0, 2, 30)

    std = 150
    test = get_day_sec(epoch)

    assert std == test


def test_reference_time():
    with pytest.raises(ValueError):
        reference_time('Y', datetime.datetime.now())


def test_read_nav_data(nav_file_unsorted_v3):
    std = {
        ('S', 20): [
            {
                'epoch': datetime.datetime(2017, 9, 8, 0, 0, 32),
                'message': (40636.72, 0., 0., 1.0,
                            -11245.916, 0., 0., 32767.0,
                            0., 0., 0., 2.0)
            },
            {
                'epoch': datetime.datetime(2017, 9, 8, 0, 3, 12),
                'message': (40636.72, 0., 0., 1.0,
                            -11245.916, 0., 0., 32767.0,
                            0., 0., 0., 12.)
            },
            {
                'epoch': datetime.datetime(2017, 9, 8, 0, 5, 52),
                'message': (40636.72, 0., 0., 1.0,
                            -11245.916, 0., 0., 32767.0,
                            0., 0., 0., 22.)
            },
        ],

    }

    with nav_file_unsorted_v3 as filename:
        test = read_nav_data(filename)

    assert std == test


def test_nearest_message():
    messages = [
        {'epoch': datetime.datetime(2017, 9, 8, 2, 0), 'message': 1},
        {'epoch': datetime.datetime(2017, 9, 8, 4, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 6, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 8, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 10, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 12, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 14, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 15, 59, 44), 'message': 3},
        {'epoch': datetime.datetime(2017, 9, 8, 16, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 17, 59, 44), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 20, 0), 'message': None},
        {'epoch': datetime.datetime(2017, 9, 8, 22, 0), 'message': 2},
    ]

    epoch = datetime.datetime(2017, 9, 8, 2, 15)
    assert nearest_message(messages, epoch) == messages[0]

    epoch = datetime.datetime(2017, 9, 8, 0, 0)
    assert nearest_message(messages, epoch) == messages[0]

    epoch = datetime.datetime(2017, 9, 8, 23, 55)
    assert nearest_message(messages, epoch) == messages[-1]

    epoch = datetime.datetime(2017, 9, 8, 15, 59, 44)
    assert nearest_message(messages, epoch) == messages[7]

    with pytest.raises(ValueError):
        epoch = datetime.datetime(2017, 9, 7)
        nearest_message(messages, epoch)


def test_get_dt():
    obs_epoch = datetime.datetime(2017, 1, 1, 0, 0, 0)
    msg_epoch = datetime.datetime(2017, 1, 1, 0, 0, 30)

    std = -30
    test = get_dt(msg_epoch, obs_epoch)
    assert std == test

    obs_epoch = datetime.datetime(2017, 1, 1, 0, 5, 30)
    msg_epoch = datetime.datetime(2017, 1, 1, 0, 0, 0)

    std = 330
    test = get_dt(msg_epoch, obs_epoch)
    assert std == test


def test_find_message():
    nav_data = {
        ('S', 38): [
            {'epoch': datetime.datetime(2017, 9, 8, 0, 1, 4), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 5, 20), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 9, 36), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 13, 52), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 18, 8), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 22, 24), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 26, 40), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 30, 56), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 35, 12), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 39, 28),
             'message': ('SBAS')},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 43, 44), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 0, 48), 'message': ()},
        ],
        ('G', 23): [
            {'epoch': datetime.datetime(2017, 9, 8, 2, 0), 'message': ('GPS')},
            {'epoch': datetime.datetime(2017, 9, 8, 4, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 6, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 8, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 10, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 11, 59, 44), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 12, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 13, 59, 44), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 16, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 18, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 20, 0), 'message': ()},
            {'epoch': datetime.datetime(2017, 9, 8, 22, 0), 'message': ()},
        ],
    }

    # GLO-way
    satellite, number = 'S', 38
    epoch = datetime.datetime(2017, 9, 8, 0, 40)

    std = (32, 'SBAS')
    test = find_message(nav_data, satellite, number, epoch)

    assert std == test

    # GPS-way
    satellite, number = 'G', 23

    std = (434400.0000000393, 'GPS')
    test = find_message(nav_data, satellite, number, epoch)

    assert std == test

    with pytest.raises(ValueError):
        find_message(nav_data, 'R', 1, epoch)

    with pytest.raises(ValueError):
        find_message(nav_data, 'X', 1, epoch)


def test_xyz_calculator():
    for s in GPS_WAY:
        assert xyz_calculator(s) is gps_sat_xyz

    for s in GLO_WAY:
        assert xyz_calculator(s) is glo_sat_xyz

    with pytest.raises(ValueError):
        xyz_calculator('X')
