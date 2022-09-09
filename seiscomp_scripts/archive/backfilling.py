from datetime import datetime
from pathlib import Path
from typing import List
from dataclasses import dataclass
import obspy  # type: ignore
import shutil


@dataclass
class SNCL:
    network: str
    station: str
    location: str
    channel: str

    def __init__(self, sncl: str):
        split_sncl = sncl.split('.')
        self.network = split_sncl[0]
        self.station = split_sncl[1]
        self.location = split_sncl[2]
        self.channel = split_sncl[3]

    def __str__(self) -> str:
        return f"{self.network}.{self.station}.{self.location}.{self.channel}"


def get_source_dir(
    parent_dir: str,
    working_date: datetime
) -> str:
    '''
    Find the source directory to search for files, based on the given date

    Parameters
    ----------
    parent_dir: str
        The parent directory of the source archive

    workind_date: datetime
        The date to search for files for

    Returns
    -------
    str: The path to the subdirectory for the specified date in the source
    archive
    '''

    subdir = working_date.strftime('/%Y/%m/%d/')

    return (parent_dir + subdir)


def find_files(
    directory: str,
    working_date: datetime
) -> List[Path]:
    '''
    Get a list of miniseed files for a specific date inside a directory

    Parameters
    ----------
    directory: str
        The directory to search for miniseed files

    working_date: datetime
        The date to search for corresponding miniseed files

    Returns
    -------
    List[Path]: List of path objects pointing to the found miniseed files
    '''
    dir_path = Path(directory)
    datepart = working_date.strftime("%Y.%j")

    found_files = list(dir_path.glob(f"*.{datepart}"))
    return found_files


def get_destination_file(
    parent_dir: str,
    working_date: datetime,
    sncl: SNCL
) -> str:
    '''
    Determine the path a miniseed file should have in the SDS archive

    Parameters
    ----------
    parent_dir: str
        The parent directory of the SDS archive

    working_date: datetime
        The date to use in the filename

    sncl: SNCL
        Object containing the station, network, location and channel of the
        stream in the miniseed file

    Returns
    -------
    str: The path to the destination file in the sds archive
    '''
    subdir = (f'/{working_date.strftime("%Y")}/{sncl.network}/'
              f'{sncl.station}/{sncl.channel}.D/')
    filename = f'{sncl}.D.{working_date.strftime("%Y.%j")}'
    sdsfile = (parent_dir + subdir + filename)
    return sdsfile


def get_sncl(
    file_path: Path
) -> SNCL:
    '''
    Gets the SNCL of a miniseed file based on the filename given

    Parameters
    ----------
    file_path: Path
        Path to the file to extract the SNCL from

    Returns
    -------
    SNCL: Object containing the network, station, location and channel
    '''
    return SNCL('.'.join(file_path.name.split('.')[0:4]))


def move_file(
    source_file: Path,
    destination_file: Path
):
    '''
    Copies the sourcefile to the sdsarchive, if there is no corresponding file
    in the sdsarchive already. If a file already exists in the sdsarchive,
    uses obspy to read and merge both files before writing it to the sds
    archive to ensure the file is as complete as possible.

    Parameters
    ----------
    source_file: Path
        Path to the source file

    destination_file: Path
        Path to the destination in the sds archive
    '''
    if destination_file.exists():
        # If the destination file exists, read both files and merge them
        source_stream: obspy.Stream = obspy.read(source_file)
        combined_stream: obspy.Stream = obspy.read(destination_file)
        combined_stream = combined_stream + source_stream
        # Merge the combined stream to get rid of any overlaps
        combined_stream.merge(
            method=1,
            interpolation_samples=-1,
            fill_value=None)
        combined_stream.write(str(destination_file), format='MSEED')
    else:
        # If the destination file doesn't exist, just copy the source file to
        # it's location
        shutil.copy(str(source_file), str(destination_file))


def move_files(
    files: List[Path],
    working_date: datetime,
    sds_archive: str
):
    '''
    Move a list of miniseed files to their intended destination in the
    sdsarchive

    Parameters
    ----------
    files: List[Path]
        List of Path objects pointing at the files to be moved

    working_date: datetime
        The date for the miniseed file
    sds_archive: str
        path to the sds archive parent directory
    '''
    for file in files:
        sncl = get_sncl(file)
        destination_path = get_destination_file(
            parent_dir=sds_archive,
            working_date=working_date,
            sncl=sncl
        )
        move_file(
            source_file=file,
            destination_file=Path(destination_path)
        )
