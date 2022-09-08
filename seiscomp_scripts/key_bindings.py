import logging
from subprocess import Popen, PIPE
from pathlib import Path
from typing import List


class SeiscompStatusError(Exception):
    def __init__(self, e: str):
        super().__init__(e)


class MaskedStations(List):
    maskfile_path: Path

    def __init__(self, maskfile_path: Path):
        self.maskfile_path = maskfile_path
        with open(maskfile_path, mode='r') as f:
            lines = f.read().split('\n')
            self.extend(lines)

    def write_to_file(self):
        contents = "\n".join(self)
        logging.debug(f'Writing to {str(self.maskfile_path)}:\n{contents}')
        with open(self.maskfile_path, mode='w') as f:
            f.write(contents)


def update_key_files(
    station_list: List[str],
    slarchive_process: str,
    masked_stations: List[str]
):
    '''
    Create new key binding files for any station that doesn't have one, and
    isn't in the list on masked stations

    Parameters
    ----------
    station_list: List[str]
        List of station codes in the NN_SSSSS format

    slarchive_process: str
        The name of the slarchive process to assign to the station key bindings

    masked_stations: List[str]
        List of stations to ignore to avoid crashing of slarchive process
    '''
    # Create a key file for each station if one doesn't exist
    for station in station_list:
        if station not in masked_stations:
            success = create_key_file(
                slarchive_process=slarchive_process,
                station_name=station)

            # If the slarchive process crashed after adding a station, add it
            # to the list of masked stations
            if not success:
                masked_stations.append(station)


def create_key_file(
    slarchive_process: str,
    station_name: str
) -> bool:
    '''
    Create a key file for a specific station

    Parameters
    ----------
    slarchive_process: str
        The name of the slarchive_process for the key file to point to

    station_name: str
        The station's name in NN_SSSS format

    Returns
    -------
        Bool: Returns True on success, False on failure
    '''
    stationfile = Path(
        f'/home/sysop/seiscomp/etc/key/station_{station_name}')

    # Check if the key file already exists
    if not stationfile.exists():

        logging.debug(f'Writing key binding file {str(stationfile)}')
        # Write the key file
        lines = [f'{slarchive_process}:local\n']
        with open(stationfile, mode='w') as f:
            f.writelines(lines)

        # Try reconfiguring slarchive process
        try:
            reconfigure_slarchive_process(slarchive_process=slarchive_process)
        except SeiscompStatusError as e:
            logging.warning((f'Adding key binding for stream {station_name} ' +
                             f'caused {slarchive_process} to crash'))
            logging.warning(e)
            # Roll back changes
            stationfile.unlink()
            reconfigure_slarchive_process(slarchive_process=slarchive_process)

            # Return False if the key binding could not be added
            return False
    else:
        logging.debug(f'Key binding {str(stationfile)} already exists')
    return True


def get_station_list(
    ip_address: str
) -> List[str]:
    '''
    Uses slinktool to get a list of stations an acquisition server can serve

    Parameters
    ----------
    ip_address: str
        IP address of the acquisition server

    Returns
    -------
    List: list of station names in NN_SSSSS format
    '''
    # Use slinktool to get a list of streams the acquisition server can serve
    process = Popen(["slinktool", "-L", ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # If slinktool caused an error, log it
    if stderr.decode() != '':
        logging.error("Slinktool error: " + stderr.decode())

    lines = stdout.decode().split('\n')

    stations: List[str] = []

    # Parse the output of slinktool for station codes
    for line in lines:
        splitline = line.split(' ')
        # invalid lines are skipped
        if len(splitline) < 2:
            continue

        # Reformat line into NN_SSSSS format
        station = splitline[0] + '_' + splitline[1]
        stations.append(station)

    return stations


def reconfigure_slarchive_process(
    slarchive_process: str
):
    '''
    Update and restart an slarchive process

    Parameters
    ----------
    slarchive_process: str
        The name of the slarchive process

    Raises
    ------
    SeiscompStatusError: Raised if the process is not running after an update
    and restart
    '''
    # Update config
    cmd = ['seiscomp', 'update-config', slarchive_process]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    logging.debug(stdout.decode())

    if stderr.decode() != '':
        logging.error("Seiscomp update-config error: " + stderr.decode())

    # Restart process
    cmd[1] = 'restart'

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    logging.debug(stdout.decode())

    if stderr.decode() != '':
        logging.error("Seiscomp restart error: " + stderr.decode())

    # Check status
    cmd[1] = 'status'

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    logging.debug(stdout.decode())

    if stderr.decode() != '':
        logging.error("Seiscomp status error: " + stderr.decode())

    # Raise an exception if the slarchive process isn't running
    if 'is running' not in stdout.decode():
        raise SeiscompStatusError(f'{slarchive_process} is not running.')
