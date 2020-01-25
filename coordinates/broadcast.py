"""
Чтение навигационных файлов в формате RINEX
"""
import datetime
import logging
from abc import ABC, abstractmethod

from coordinates.exceptions import RinexNavFileError

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def validate_epoch(epoch):
    """Check epoch and convert into datetime.datetime

    Sometimes the seconds or minutes value >= 60, to return datetime.datetime
    we need to check this. Also converts YY to YYYY (datetime.datetime threats
     92 and 1992 in different ways).

    Parameters
    ----------
    epoch : list
        epoch = [year, month, day, hour, min, sec, microsec]

    Returns
    -------
    datetime : datetime.datetime
    """
    epoch = epoch[:]

    # YY -> YYYY
    if epoch[0] < 100:
        if epoch[0] >= 89:
            epoch[0] += 1900
        elif epoch[0] < 89:
            epoch[0] += 2000

    delta = datetime.timedelta(0)

    # epoch[-2] - seconds; epoch[-3] - minutes
    # we do all calculation in seconds so we use multiplier
    for i, ier in [(-2, 1), (-3, 60)]:
        if 60 <= epoch[i] <= 120:
            sec = (epoch[i] - 59) * ier
            delta += datetime.timedelta(seconds=sec)
            epoch[i] = 59

    epoch = datetime.datetime(*epoch) + delta

    return epoch


def sec2sec_ms(sec):
    """Converts float seconds into seconds and microseconds

    Parameters
    ----------
    sec : float

    Returns
    -------
    seconds : int
    microsec : int
    """
    microsec = (sec - int(sec)) * 1e+6
    microsec = float("%.1f" % microsec)

    return int(sec), int(microsec)


class RinexNavFile(ABC):
    item_len = 19

    orbit_start = None
    orbit_end = None

    values_per_orbit = dict(
        G=(4, 4, 4, 4, 4, 4, 2),  # GPS
        R=(4, 4, 4),  # GLONASS
        E=(4, 4, 4, 4, 4, 4, 2),  # Galileo
        S=(4, 4, 4),  # SBAS (GEO)
        J=(4, 4, 4, 4, 4, 4, 2),  # QZSS
        C=(4, 4, 4, 4, 4, 4, 2),  # BDS
        I=(4, 4, 4, 4, 4, 4, 2),  # IRNSS
    )

    @abstractmethod
    def __init__(self, filename):
        pass

    @staticmethod
    @abstractmethod
    def retrieve_ver_type(filename):
        pass

    @staticmethod
    @abstractmethod
    def parse_epoch(file_object):
        pass

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @staticmethod
    def skip_header(file_object):
        """
        Skip the header of the file.

        Parameters
        ----------
        file_object : file-like object

        Returns
        -------
        None

        Raises
        ------
        RinexNavFileError
            on unexpected end of the file.
        """
        line = ''
        while line[60:73] != 'END OF HEADER':
            try:
                line = next(file_object)
            except StopIteration:
                msg = 'Unexpected end of the file.'
                raise RinexNavFileError(msg)

    @staticmethod
    def read_orbits(file_object, num_of_orbits):
        """Return list of orbits read from the file.

        Parameters
        ----------
        file_object : iterable
            file-like object

        num_of_orbits : int

        Returns
        -------
        orbits : list

        Raises
        ------
        RinexNavFileError
            on unexpected end of the file.
        """
        orbits = [None] * num_of_orbits
        for i in range(num_of_orbits):
            try:
                line = next(file_object)
            except StopIteration:
                msg = 'Unexpected end of the file.'
                raise RinexNavFileError(msg)
            orbits[i] = line.rstrip()
        return orbits

    def parse_orbits(self, orbits, values_per_orbit):
        """Return navigation message. Message parsed from the orbits list
        according to values_per_orbit.

        Parameters
        ----------
        orbits : list
            list of 'broadcast orbit' records from coordinates file

        values_per_orbit : list


        Returns
        -------
        message : tuple

        Raises
        ------
        RinexNavFileError
            Can't parse the orbit record.

        """
        message = []

        # shortcuts
        ln = self.item_len
        start = self.orbit_start
        end = self.orbit_end

        for num, orbit in enumerate(orbits):
            values = []
            for i in range(start, end, ln):
                value = orbit[i:i + ln].rstrip().lower().replace('d', 'e')
                values.append(value)

            try:
                values = values[:values_per_orbit[num]]
                values = [s and float(s) or 0. for s in values]
            except ValueError:
                msg = "Can't parse the orbit: {}".format(orbit)
                raise RinexNavFileError(msg)

            message += values

        return tuple(message)


class RinexNavFileV2(RinexNavFile):
    orbit_start = 3
    orbit_end = 75

    system = dict(
        N='G',
        G='R',
        H='S',
    )

    def __init__(self, filename):
        super().__init__(filename)
        self.filename = filename
        self.version, self.file_type = self.retrieve_ver_type(filename)

    @staticmethod
    def retrieve_ver_type(filename):
        """Returns RINEX version and type

        Returns
        -------
        tuple
            (float, str) -- RINEX version and type.

        Raises
        ------
        RinexNavFileError
            on empty file.

        """
        with open(filename) as rinex:
            try:
                header_line = next(rinex)
            except StopIteration:
                raise RinexNavFileError('Unexpected end of the file.')
            else:
                version = float(header_line[:9])
                file_type = header_line[20]
        return version, file_type

    @staticmethod
    def parse_epoch(file_object):
        """Return satellite number, epoch and sv_clock

        Raises
        ------
        EOFError
            on the end of the file.

        RinexNavFileError
            when it can't parse the epoch record.
        """
        try:
            line = next(file_object)
        except StopIteration:
            raise EOFError

        number = line[0:2]

        # year, month, day, hour, min; +sec
        epoch = [line[i:i + 3] for i in range(2, 17, 3)]
        sec = line[17:22]

        sv_clock = [line[i:i + 19] for i in (22, 41, 60)]
        sv_clock = [i.lower().replace('d', 'e') for i in sv_clock]

        try:
            number = int(number)

            sec = sec2sec_ms(float(sec))

            epoch = [int(i) for i in epoch] + list(sec)
            epoch = validate_epoch(epoch)

            sv_clock = [float(f) for f in sv_clock]

        except ValueError:
            msg = "Can't read epoch: {}.".format(line)
            raise RinexNavFileError(msg)

        return number, epoch, tuple(sv_clock)

    def __iter__(self):
        system = self.system[self.file_type]
        values_per_orbit = self.values_per_orbit[system]
        num_of_orbits = len(values_per_orbit)

        with open(self.filename, 'r') as file_object:
            self.skip_header(file_object)

            while True:
                try:
                    satellite, epoch, sv_clock = self.parse_epoch(file_object)
                except EOFError:
                    break
                orbits = self.read_orbits(file_object, num_of_orbits)
                message = self.parse_orbits(orbits, values_per_orbit)
                yield system, satellite, epoch, sv_clock, message


class RinexNavFileV3(RinexNavFile):
    orbit_start = 4
    orbit_end = 76

    def __init__(self, filename):
        super().__init__(filename)
        self.filename = filename

        version, file_type, system = self.retrieve_ver_type(filename)

        self.version = version
        self.file_type = file_type
        self.system = system

    @staticmethod
    def retrieve_ver_type(filename):
        """Возвращает версию, тип файла и спутниковую систему

        """
        with open(filename) as rinex:
            header_line = next(rinex)
            version = float(header_line[:9])
            file_type = header_line[20]
            system = header_line[40]

        return version, file_type, system

    @staticmethod
    def parse_epoch(file_object):
        """Returns epoch components

        Parameters
        ----------
        file_object : file-like object

        Returns
        -------
        epoch_components : tuple
            (satellite_system, satellite_number, epoch, sv_clock)

        Raises
        ------
        EOFError
            on the end of the file.

        RinexNavFileError
            when it can't parse the epoch record.
        """
        try:
            line = next(file_object)
        except StopIteration:
            raise EOFError

        system = line[0]
        number = line[1:3]

        # month, day, hour, min, sec; year + ...
        epoch = [line[i:i + 3] for i in range(8, 23, 3)]
        epoch = [line[4:9]] + epoch

        sv_clock = [line[i:i + 19] for i in (23, 42, 61)]
        sv_clock = [i.lower().replace('d', 'e') for i in sv_clock]

        try:
            number = int(number)

            epoch = [int(i) for i in epoch]
            epoch = validate_epoch(epoch)

            sv_clock = [float(f) for f in sv_clock]

        except ValueError:
            msg = "Can't read epoch: {}.".format(line)
            raise RinexNavFileError(msg)

        return system, number, epoch, tuple(sv_clock)

    def __iter__(self):
        with open(self.filename, 'r') as file_object:
            self.skip_header(file_object)

            while True:
                try:
                    (system, satellite,
                     epoch, sv_clock) = self.parse_epoch(file_object)
                except EOFError:
                    break

                values_per_orbit = self.values_per_orbit[system]
                num_of_orbits = len(values_per_orbit)

                orbits = self.read_orbits(file_object, num_of_orbits)
                message = self.parse_orbits(orbits, values_per_orbit)

                yield system, satellite, epoch, sv_clock, message


def rnx_nav(filename):
    """Возвращает объект RinexNavFile в зависимости от версии в файле.

    """
    version, file_type = RinexNavFileV2.retrieve_ver_type(filename)

    if version in {2.0, 2.01, 2.1, 2.11}:
        return RinexNavFileV2(filename)
    elif version in {3.0, 3.01, 3.02, 3.03}:
        return RinexNavFileV3(filename)
    else:
        msg = 'Version {} is not supported.'.format(version)
        raise RinexNavFileError(msg)
