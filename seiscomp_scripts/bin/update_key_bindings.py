from pathlib import Path
import click
from seiscomp_scripts.key_bindings import MaskedStations, \
    get_station_list, update_key_files  # type: ignore
from seiscomp_scripts.config import LogLevels
import logging


@click.command()
@click.option(
    '--ip-address',
    help='IP Address of acquisition server.'
)
@click.option(
    '--slarchive-process',
    help='Name of slarchive process'
)
@click.option(
    '--mask-file',
    help='Path to file containing list of stations to mask'
)
@click.option(
    '--log-level',
    type=click.Choice([v.value for v in LogLevels]),
    help='Log level for debugging',
    default='WARNING'
)
def main(
    ip_address: str,
    slarchive_process: str,
    mask_file: str,
    log_level: str
):

    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level)

    # Get a list of stations
    station_list = get_station_list(ip_address=ip_address)

    logging.debug(f'Station list: {station_list}')

    # Load the list of masked stations

    masked_stations = MaskedStations(Path(mask_file))

    logging.debug(f'List of masked stations: {masked_stations}')

    # Create key files for any missing stations
    update_key_files(
        station_list=station_list,
        slarchive_process=slarchive_process,
        masked_stations=masked_stations)

    # Update the list of masked stations
    masked_stations.write_to_file()

    return


if __name__ == '__main__':
    main()
