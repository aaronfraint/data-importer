import click
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

import postgis_helpers as pGIS

load_dotenv(find_dotenv(usecwd=True))
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
GDRIVE_ROOT = os.getenv("GDRIVE_ROOT")

credentials = pGIS.configurations()


@click.group()
def main():
    "The command 'DB-EXPORT' is used to export data out of PostgreSQL."
    pass


# FREEZE A DATABASE
# -----------------

@click.command()
@click.option(
    "--folder", "-f",
    help="Folder where database backups are stored",
    default=Path(GDRIVE_ROOT) / "SQL databases",
)
@click.option(
    "--database", "-d",
    help="Name of db, if not using 'DB_NAME'",
    default=DB_NAME,
)
@click.option(
    "--host", "-h",
    help="Name of host, if not using 'DB_HOST'",
    default=DB_HOST,
)
def freeze(folder: str, database: str, host: str):
    """ Export a .SQL file of the database.
        Use without optional arguments to leverage your
        environment variables. Or, manually specify
        any of the following:

            - FOLDER

            - DATABASE (name)

            - HOST
    """

    folder = Path(folder) / database

    if not folder.exists():
        print("\n!!! The folder below does not exist yet. Create the folder and run again.")
        print("\t->", folder)
        return

    db = pGIS.PostgreSQL(database, **credentials[host])

    db.db_export_pgdump_file(folder)


# Wire up all the commands
# ------------------------

all_commands = [freeze]

for cmd in all_commands:
    main.add_command(cmd)
