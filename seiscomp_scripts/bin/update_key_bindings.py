from pathlib import Path
import click
from seiscomp_scripts.key_bindings import MaskedStations, \
    get_station_list, update_key_files  # type: ignore


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
def main(
    ip_address: str,
    slarchive_process: str,
    mask_file: str
):
    # Get a list of stations
    station_list = get_station_list(ip_address=ip_address)

    # Load the list of masked stations

    masked_stations = MaskedStations(Path(mask_file))

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
