# некоторые значения WGS84 и ПЗ-90

from math import sqrt

# semiaxis of the ellipse
a = 6378137.00
b = 6356752.314245

# eccentricity of the ellipse
e = sqrt(1 - pow(b, 2)/pow(a, 2))
# e = 0.081819199

# radius of the Earth
r_e = 6371e3

# m^3/s^2 - Earth's gravitational field constant
mu = 398600.44e+9

# equatorial radius of the Earth
ae = 6378136  # ПЗ-90 (ICD GLONASS)

# second zonal harmonic of the spherical harmonic
J0sqd = 1082625.7e-9

# second zonal harmonic coefficient
C20 = -1082.63e-6

# angular velocity of the Earth, rad/sec
omega = 7.2921151467e-5
