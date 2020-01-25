from tempfile import NamedTemporaryFile

import pytest

from coordinates.broadcast import RinexNavFileV2, RinexNavFileV3
from coordinates.broadcast import rnx_nav
from coordinates.exceptions import RinexNavFileError


@pytest.mark.parametrize('content, expected_type', [
    ('''\
     2              NAVIGATION DATA                         RINEX VERSION / TYPE
''', RinexNavFileV2),
    ('''\
     2.01           GLONASS NAV DATA                        RINEX VERSION / TYPE
''', RinexNavFileV2),
    ('''\
     2.10           GLONASS NAV DATA                        RINEX VERSION / TYPE
''', RinexNavFileV2),
    ('''\
     2.10           N: GPS NAV DATA                         RINEX VERSION / TYPE
''', RinexNavFileV2),
    ('''\
     2.11           H: GEO NAV MSG DATA                     RINEX VERSION / TYPE
''', RinexNavFileV2),
    ('''\
     3.00           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''', RinexNavFileV3),
    ('''\
     3.01           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''', RinexNavFileV3),
    ('''\
     3.02           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''', RinexNavFileV3),
    ('''\
     3.03           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''', RinexNavFileV3),
], ids=[
    '2', '2.01', '2.10 R', '2.10 G', '2.11', '3.00', '3.01', '3.02', '3.03'
])
def test_rnx_nav(content, expected_type):
    with NamedTemporaryFile(mode='w') as tmp_file:
        tmp_file.writelines(content)
        tmp_file.seek(0)
        obj = rnx_nav(filename=tmp_file.name)
        assert isinstance(obj, expected_type)


@pytest.mark.parametrize('content', [
    '''\
     3.04           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''',
    '''\
     2.12           N: GNSS NAV DATA    G: GPS              RINEX VERSION / TYPE
''',
], ids=[
    '3.04', '2.12',
])
def test_rnx_nav_unknown_version(content):
    with NamedTemporaryFile(mode='w') as tmp_file:
        tmp_file.writelines(content)
        tmp_file.seek(0)
        with pytest.raises(RinexNavFileError, match=r'Version \S+ is not supported.'):
            rnx_nav(filename=tmp_file.name)
