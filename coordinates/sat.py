import datetime
from collections import defaultdict
from functools import lru_cache
from math import sqrt, sin, cos, atan2
from operator import itemgetter

from coordinates import datum
from coordinates.broadcast import rnx_nav
from coordinates.exceptions import SatSystemError, NavMessageNotFoundError

# GPS, BDS, Galileo, and IRNSS
GPS_WAY = {'G', 'C', 'E', 'I'}

# GLONASS, SBAS, and QZSS
GLO_WAY = {'R', 'S', 'J'}

KNOWN_SYSTEMS = GPS_WAY | GLO_WAY

EPOCH_START = dict(
    G=datetime.datetime(1980, 1, 6, 0, 0, 0),  # GPS
    C=datetime.datetime(2006, 1, 1, 0, 0, 0),  # BDS
    E=datetime.datetime(1999, 8, 22, 0, 0, 13),  # Galileo
    I=datetime.datetime(1999, 8, 21, 23, 59, 47),  # IRNSS
)


def get_week_sec(epoch, epoch_start):
    """Returns seconds since the beginning of the week

    Parameters
    ----------
    epoch : datetime.datetime
    epoch_start : datetime.datetime

    Returns
    -------
    seconds : float

    """
    current_epoch = epoch - epoch_start
    week = current_epoch.days / 7.

    seconds = (week - int(week)) * (7 * 24 * 60 * 60)
    seconds += current_epoch.seconds

    return seconds


def get_day_sec(epoch):
    """Returns seconds since the beginning of the day

    """
    time = epoch.time()
    seconds = datetime.timedelta(0, (time.hour * 60 ** 2 +
                                     time.minute * 60 +
                                     time.second)).seconds
    return seconds


def get_dt(msg_epoch, obs_epoch):
    """Returns delta between msg_epoch and obs_epoch in seconds.

    """
    if obs_epoch >= msg_epoch:
        return (obs_epoch - msg_epoch).seconds
    else:
        return (msg_epoch - obs_epoch).seconds * -1


def reference_time(satellite, epoch):
    """Returns reference time of the epoch according to satellite system in
    seconds.

    """
    if satellite not in EPOCH_START:
        raise SatSystemError(satellite)
    return get_week_sec(epoch, EPOCH_START[satellite])


def nearest_message(messages, obs_epoch):
    """Returns the nearest navigation message.

    """
    first_date = messages[0]['epoch'].date()
    if not obs_epoch.date() == first_date:
        raise NavMessageNotFoundError(
            'The dates of the nav message and observation must be the same.'
        )

    left = -1
    right = len(messages)

    while right - left > 1:
        pivot = (left + right) // 2
        if obs_epoch >= messages[pivot]['epoch']:
            left = pivot
        else:
            right = pivot

    if left == -1:
        return messages[0]

    return messages[left]


def find_message(nav_data, satellite, number, epoch):
    """Returns a navigation message and timedelta between the message
    time and the epoch.

    """
    if satellite not in KNOWN_SYSTEMS:
        raise SatSystemError(satellite)

    try:
        satellite_messages = nav_data[(satellite, number)]
    except KeyError:
        msg = 'No such satellite: {sat}{num}'.format(
            sat=satellite,
            num=number,
        )
        raise NavMessageNotFoundError(msg)

    # Returns the first for GPS, BDS, Galileo, and IRNSS
    if satellite in GPS_WAY:
        message = satellite_messages[0]
        # время с начала недели
        dt = reference_time(satellite, epoch)

    # Returns the nearest for GLONASS, SBAS, and QZSS
    elif satellite in GLO_WAY:
        message = nearest_message(satellite_messages, epoch)
        # разница между сообщением и набл
        dt = get_dt(message['epoch'], epoch)
    else:
        raise NavMessageNotFoundError(
            'Navigation message not found: {sat}{num} {epoch}'.format(
                sat=satellite,
                num=number,
                epoch=epoch,
            )
        )

    return dt, message['message']


def gps_sat_xyz(ephemeris, sec):
    """Returns geocentric coordinates XYZ of the GPS (GPS-way) satellite

    Parameters
    ----------
    ephemeris : list
        list with ephemeris

    sec : float
        amount of seconds since the start of the week, seconds

    Returns
    -------
    x : float
        X, meters
    y : float
        Y, meters
    z : float
        Z, meters

    """
    # threshold
    # e_ps = 2e-15

    crs = ephemeris[1]
    dn = ephemeris[2]
    m0 = ephemeris[3]
    cuc = ephemeris[4]
    e0 = ephemeris[5]
    cus = ephemeris[6]
    a0 = ephemeris[7] ** 2
    toe = ephemeris[8]
    cic = ephemeris[9]
    omega_0 = ephemeris[10]
    cis = ephemeris[11]
    i0 = ephemeris[12]
    crc = ephemeris[13]
    w0 = ephemeris[14]
    omega_dot = ephemeris[15]
    i_dot = ephemeris[16]

    tk = sec - toe

    if tk > 302400:
        tk -= 604800
    elif tk < -302400:
        tk += 604800

    n = sqrt(datum.mu / a0 ** 3) + dn
    mk = m0 + n * tk

    ek = mk
    ek_1 = ek + 1

    prv_d_ek = 0
    cur_d_ek = 1
    #   while ( abs(ek-ek_1) > e_ps ):
    while prv_d_ek != cur_d_ek:
        prv_d_ek = abs(ek - ek_1)
        ek_1 = ek
        ek = ek_1 - (ek_1 - e0 * sin(ek_1) - mk) / (1 - e0 * cos(ek_1))
        cur_d_ek = abs(ek - ek_1)
        # print prv_d_ek, cur_d_ek

    fs = (sqrt(1 - e0 ** 2) * sin(ek)) / (1 - e0 * cos(ek))
    fc = (cos(ek) - e0) / (1 - e0 * cos(ek))
    tettak = atan2(fs, fc)

    u0k = tettak + w0
    uk = u0k + cuc * cos(2 * u0k) + cus * sin(2 * u0k)

    rk = a0 * (1 - e0 * cos(ek)) + crc * cos(2 * u0k) + crs * sin(2 * u0k)

    ik = i0 + (cic * cos(2 * u0k) + cis * sin(2 * u0k)) + i_dot * tk

    omega_k = omega_0 + (omega_dot - datum.omega) * tk - datum.omega * toe

    x = rk * (cos(uk) * cos(omega_k) - sin(uk) * sin(omega_k) * cos(ik))
    y = rk * (cos(uk) * sin(omega_k) + sin(uk) * cos(omega_k) * cos(ik))
    z = rk * sin(uk) * sin(ik)

    return x, y, z


def glo_sat_xyz(ephemeris, dt):
    """Returns geocentric coordinates XYZ of the GLONASS (GLO-way) satellite

    Parameters
    ----------
    ephemeris : list
        list with ephemeris

    dt : float
        difference between time of the ephemeris and observation time, seconds

    Returns
    -------
    x : float
        X, meters
    y : float
        Y, meters
    z : float
        Z, meters
    """

    # meters
    x0 = ephemeris[0] * 1000
    vX = ephemeris[1] * 1000
    aX = ephemeris[2] * 1000

    y0 = ephemeris[4] * 1000
    vY = ephemeris[5] * 1000
    aY = ephemeris[6] * 1000

    z0 = ephemeris[8] * 1000
    vZ = ephemeris[9] * 1000
    aZ = ephemeris[10] * 1000

    if dt == 0:
        return x0, y0, z0

    r = sqrt(x0 ** 2 + y0 ** 2 + z0 ** 2)

    # - GLONASS ICD ver 5.1, 2008.
    first_sd = -(datum.mu / r ** 3)
    second_sd = 3 / 2. * datum.J0sqd * datum.mu * datum.ae ** 2 / r ** 5

    # - x, y, z
    fx = lambda x, z: (first_sd * x - second_sd * x *
                       (1 - 5 * z ** 2 / r ** 2) +
                       datum.omega ** 2 * x + 2 * datum.omega * vY + aX)

    fy = lambda y, z: (first_sd * y - second_sd * y *
                       (1 - 5 * z ** 2 / r ** 2) +
                       datum.omega ** 2 * y - 2 * datum.omega * vX + aY)

    fz = lambda z: (first_sd * z - second_sd * z *
                    (3 - 5 * z ** 2 / r ** 2) + aZ)

    x = dict()
    kx = dict()

    y = dict()
    ky = dict()

    z = dict()
    kz = dict()

    # 1
    kx[1] = fx(x0, z0) * dt
    ky[1] = fy(y0, z0) * dt
    kz[1] = fz(z0) * dt

    x[1] = x0 + vX * dt / 2. + kx[1] * dt / 8.
    y[1] = y0 + vY * dt / 2. + ky[1] * dt / 8.
    z[1] = z0 + vZ * dt / 2. + kz[1] * dt / 8.

    # 2
    kx[2] = fx(x[1], z[1]) * dt
    ky[2] = fy(y[1], z[1]) * dt
    kz[2] = fz(z[1]) * dt

    x[2] = x0 + vX * dt / 2. + kx[2] * dt / 8.
    y[2] = y0 + vY * dt / 2. + ky[2] * dt / 8.
    z[2] = z0 + vZ * dt / 2. + kz[2] * dt / 8.

    # 3
    kx[3] = fx(x[2], z[2]) * dt
    ky[3] = fy(y[2], z[2]) * dt
    kz[3] = fz(z[2]) * dt

    # result
    xyz = (
        x0 + vX * dt + (kx[1] + kx[2] + kx[3]) * dt / 6,
        y0 + vY * dt + (ky[1] + ky[2] + ky[3]) * dt / 6,
        z0 + vZ * dt + (kz[1] + kz[2] + kz[3]) * dt / 6
    )

    return xyz


def xyz_calculator(satellite):
    """Возвращает калькулятор XYZ в зависимости от спутниковой системы.

    """
    if satellite in GPS_WAY:
        return gps_sat_xyz
    elif satellite in GLO_WAY:
        return glo_sat_xyz
    else:
        raise SatSystemError(satellite)


@lru_cache(maxsize=8)
def read_nav_data(filename):
    """Returns dictionary which contains navigation data from the file.
    Navigation records are sorted by epoch.

    """
    nav_data = defaultdict(list)
    for row in rnx_nav(filename):
        satellite, number, epoch, sv_clock, message = row
        record = {'epoch': epoch, 'message': message}
        nav_data[(satellite, number)].append(record)

    for sat in nav_data:
        nav_data[sat].sort(key=itemgetter('epoch'))

    return nav_data


@lru_cache(maxsize=None)
def satellite_xyz(filename, satellite, number, epoch):
    """Returns XYZ coordinates of the satellite with number

    """
    calculate = xyz_calculator(satellite)
    data = read_nav_data(filename)
    dt, message = find_message(
        data,
        satellite,
        number,
        epoch,
    )
    xyz = calculate(message, dt)
    return xyz
