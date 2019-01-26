from contextlib import contextmanager
from os import remove
from tempfile import NamedTemporaryFile


@contextmanager
def mktmp(tmp_str):
    tmp_file_name = None

    try:
        with NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.writelines(tmp_str)
            tmp_file_name = tmp_file.name

        yield tmp_file_name

    finally:
        if tmp_file_name:
            remove(tmp_file_name)
