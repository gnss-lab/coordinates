class CoordinatesException(Exception):
    """
    The base class for all exceptions related to the package.
    """


class RinexNavFileError(CoordinatesException):
    """
    Raised by methods of the ``coordinates.broadcast.RinexNavFile``
    object when parsing the navigation file fails.
    """


class SatSystemError(CoordinatesException):
    """
    Raised by ``coordinates.sat`` functions
    when the satellite system is unknown.
    """


class NavMessageNotFoundError(CoordinatesException):
    """
    Raised by ``coordinates.sat`` functions
    when the navigation message not found.
    """


class XYZNotFoundError(CoordinatesException):
    """
    Raised by coordinates.retrieve_xyz when nothing found.
    """
