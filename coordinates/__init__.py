# coding=utf-8
"""
Tools for manipulating coordinates for gnss-lab project.

"""
from math import pi, sin, cos, atan2, sqrt
from coordinates.sat import satellite_xyz

__version__ = '1.0.1.dev1'
__author__ = __maintainer__ = 'Ilya Zhivetiev'
__email__ = 'i.zhivetiev@gnss-lab.org'


def retrieve_xyz(rnx_file):
    """Retrieve and return geocentric approximate marker position from the
    rnx_file. ValueError is raised if nothing is found.

    Parameters
    ----------
    rnx_file : str or file
        File or filename. The file must be a plain RINEX observation file, e.g.
        guniped and crx2rnx-ed. Note that the position will be seek to the start
        of the file.

    Returns
    -------
    xyz : tuple
        X, Y, and Z values
    """
    xyz_label = 'APPROX POSITION XYZ'
    end_label = 'END OF HEADER'

    xyz = None
    is_string = True

    try:
        rnx_file + ''
    except (TypeError, ValueError):
        is_string = False

    if is_string:
        rnx = open(rnx_file)
    else:
        rnx = iter(rnx_file)

    for line in rnx:
        label = line[60:].rstrip().upper()
        if label == xyz_label:
            xyz = [float(line[i:i + 14]) for i in range(0, 42, 14)]
            break
        if label == end_label:
            break

    if is_string:
        rnx.close()
    else:
        rnx.seek(0)

    if xyz:
        return tuple(xyz)
    else:
        raise ValueError


def xyz2lbh(x, y, z, deg=True):
    """Converts cartesian coordinates to geodetic coordinates.

    Parameters
    ----------
    x, y, z : float
        meters

    deg : bool, optional
        If True, l and b values will be converted into grad. Default is True.

    Returns
    -------
    l, b : float
        longitude and latitude

    h : float
        height, meters

    Note
    ----
    К.Ф. Афонин Высшая геодезия. Системы координат и преобразования
        между ними // Новосибирск. СГГА. 2011 г. 55 с.
    """

    # semiaxis and eccentricity of the ellipse
    datum_a = 6378137.00
    datum_b = 6356752.314245
    datum_e = sqrt(1 - pow(datum_b, 2) / pow(datum_a, 2))

    # threshold
    e_B = 1e-12

    Q = sqrt(x ** 2 + y ** 2)

    # L - longitude
    if x == 0:
        if y > 0:
            L = pi / 2
        else:
            L = 3 * pi / 2
    else:
        L = atan2(y, x)

    # B - latitude
    # initial values
    Bi1 = z / Q * 1 / (1 - datum_e ** 2)
    Bi = Bi1
    N = 0

    while 1:
        W = sqrt(1 - datum_e ** 2 * sin(Bi) ** 2)
        N = datum_a / W
        T = z + N * datum_e ** 2 * sin(Bi)

        Bi1 = atan2(T, Q)

        if abs(Bi1 - Bi) <= e_B:
            break

        Bi = Bi1

    B = Bi1

    # H - height
    H = Q * cos(B) + z * sin(B) - N * (1 - datum_e ** 2 * sin(B) ** 2)

    if deg:
        L, B = L * 180 / pi, B * 180 / pi

        if L < 0:
            L += 360

    return L, B, H
