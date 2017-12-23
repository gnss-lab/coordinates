===========
coordinates
===========

*****
Usage
*****

A short usage example::

    from datetime import datetime
    from coordinates import satellite_xyz

    filename = 'brdm2510.17p'
    epoch = datetime(2017, 9, 8, 1, 50, 0)

    xyz = satellite_xyz(filename, 'G', 1, epoch)

************
Installation
************

Install package from GitHub in "editable" mode.

    $ pip install -e git+https://github.com/gnss-lab/coordinates.git#egg=coordinates

*******
License
*******

Distributed under the terms of the
`MIT <https://github.com/gnss-lab/gnss-tec/blob/master/LICENSE.txt>`_
license, gnss-tec is free and open source software.

Copyright Ilya Zhivetiev, 2017.