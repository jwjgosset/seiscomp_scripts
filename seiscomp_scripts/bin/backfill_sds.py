from datetime import datetime
import click

from seiscomp_scripts.archive.backfilling import find_files, get_source_dir, \
    move_files


@click.command()
@click.option(
    '--source-dir',
    help="The parent directory of the archive to copy files from."
)
@click.option(
    '--sdsarchive',
    help="The parent directory for the sds archive to move files to."
)
@click.option(
    '--date',
    help="The date to move files for."
)
def main(
    source_dir: str,
    sdsarchive: str,
    date: datetime
):
    date_dir = get_source_dir(
        parent_dir=source_dir,
        working_date=date
    )
    source_files = find_files(
        directory=date_dir,
        working_date=date
    )
    move_files(
        files=source_files,
        working_date=date,
        sds_archive=sdsarchive
    )


if __name__ == '__main__':
    main()
