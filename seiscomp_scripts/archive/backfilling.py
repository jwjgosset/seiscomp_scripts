from datetime import datetime
from pathlib import Path
from typing import List
import obspy  # type: ignore


def get_source_dir(
    parent_dir: str,
    working_date: datetime
):
    '''
    Find the source directory to search for files, based on the given date


    '''
    subdir = working_date.strftime('/%Y/%m/%d/')

    return (parent_dir + subdir)


def find_files(
    directory: str,
    working_date: datetime
) -> List[Path]:
    dir_path = Path(directory)
    datepart = working_date.strftime("%Y.%j")

    found_files = list(dir_path.glob(f"*.{datepart}"))
    return found_files


def get_destination_file(
    parent_dir: str,
    working_date: datetime,
    net: str,
    sta: str,
    loc: str,
    chan: str
) -> str:
    subdir = f'/{working_date.strftime("%Y")}/{net}/{sta}/{chan}.D/'
    filename = f'{net}.{sta}.{loc}.{chan}.D.{working_date.strftime("%Y.%j")}'
    sdsfile = (parent_dir + subdir + filename)
    return sdsfile


def move_file(
    source_file: Path,
    destination_file: Path
):
    if destination_file.exists():
        # If the destination file exists, read both files and merge them
        source_stream: obspy.Stream = obspy.read(source_file)
        combined_stream: obspy.Stream = obspy.read(destination_file)
        combined_stream = combined_stream + source_stream
        # Merge the combined stream to get rid of any overlaps
        combined_stream.merge(method=1)
    else:
        # If the destination file doesn't exist, just move the source file to
        # it's location
        source_file.rename(destination_file)
    return
