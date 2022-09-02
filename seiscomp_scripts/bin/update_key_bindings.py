import logging
from subprocess import Popen, PIPE
from pathlib import Path
from typing import List
import click


class SeiscompStatusError(Exception):
    def __init__(self, e: str):
        super().__init__(e)


def create_key_file(
    slarchive_process: str,
    station_name: str
):
    stationfile = Path(f'/home/sysop/seiscomp/etc/key/station_{station_name}')

    # Check if the key file already exists
    if not stationfile.exists():

        # Write the key file
        lines = [f'{slarchive_process}:local']
        with open(stationfile, mode='w') as f:
            f.writelines(lines)

        # Return boolean to tell if a change was made, indicating that the
        # process needs a reconfigure
        changed = True
    else:
        changed = False

    return changed


def get_station_list(
    ip_address: str
) -> List[str]:
    process = Popen(["slinktool", "-L", ip_address], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    lines = stdout.decode().split('\n')

    stations: List[str] = []

    for line in lines:
        splitline = line.split(' ')
        # invalid lines are skipped
        if len(splitline) < 2:
            continue

        # Reformat line into station name
        station = splitline[0] + '_' + splitline[1]
        stations.append(station)

    return stations


def reconfigure_slarchive_process(
    slarchive_process: str
):
    # Update config
    cmd = ['seiscomp', 'update-config', slarchive_process]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    # Restart process
    cmd[1] = 'restart'

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    # Check status
    cmd[1] = 'status'

    process = Popen(cmd, stdout=PIPE, stderr=PIPE)

    stdout, stderr = process.communicate()

    # Raise an exception if the slarchive process isn't running
    if 'is running' not in stdout.decode():
        raise SeiscompStatusError(f'{slarchive_process} is not running.')


@click.command()
@click.option(
    '--ip-address',
    help='IP Address of acquisition server.'
)
@click.option(
    '--slarchive-process',
    help='Name of slarchive process'
)
def main(
    ip_address: str,
    slarchive_process: str
):

    # Flag for reconfiguring slarchive process if changes are made
    reconfigure = False

    # Get a list of stations
    station_list = get_station_list(ip_address=ip_address)

    # Create a key file for each station if one doesn't exist
    for station in station_list:
        changed = create_key_file(
            slarchive_process=slarchive_process,
            station_name=station)
        # If a new keyfile was made, flag it
        if changed:
            reconfigure = True

    # Try to reconfigure the slarchive process if anything changed
    if reconfigure:
        try:
            reconfigure_slarchive_process(slarchive_process=slarchive_process)
        except SeiscompStatusError as e:
            logging.error(e)

    return


if __name__ == '__main__':
    main()
