import click
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv, find_dotenv

import postgis_helpers as pGIS

from .openstreetmap import import_osm_for_dvrpc_region
from .shapefiles import import_shapefiles


load_dotenv(find_dotenv(usecwd=True))
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
GDRIVE_ROOT = os.getenv("GDRIVE_ROOT")

credentials = pGIS.configurations()


@click.group()
def main():
    "The command 'DB-IMPORT' is used to import data into PostgreSQL."
    pass


# OPEN STREET MAP
# --------------

@click.command()
@click.option(
    "--networktype", "-n",
    help="Network type to download (see osmnx docs)",
    default="drive",
)
def osm(networktype):
    """Download OpenStreetMap data for the DVRPC region.
       Defaults to the 'drive' network
    """
    db = pGIS.PostgreSQL(DB_NAME, **credentials[DB_HOST])
    import_osm_for_dvrpc_region(db, network_type=networktype)


# COPY FROM ANOTHER DATABASE
# --------------------------
@click.command()
@click.argument('src_db')
@click.argument('src_host')
@click.argument('table_to_copy')
@click.option(
    "--srcschema", "-ss",
    help="Table's schema name in source database",
    default="public",
)
@click.option(
    "--targetschema", "-ts",
    help="Schema where new table should go",
    default="public",
)
def copy(src_db, src_host, table_to_copy, srcschema, targetschema):
    """Copy a table from the specified source db/host"""

    src_db = pGIS.PostgreSQL(
        src_db,
        active_schema=srcschema,
        **credentials[src_host]
    )

    target_db = pGIS.PostgreSQL(
        DB_NAME,
        **credentials[DB_HOST]
    )

    src_db.transfer_data_to_another_db(
        table_to_copy,
        target_db,
        schema=targetschema
    )


# IMPORT A FOLDER FULL OF SHAPEFILES
# ----------------------------------
@click.command()
@click.argument('folder_subpath')
def shapefile_folder_on_gdrive(folder_subpath):
    """Import all .shp files in a given subfolder under GDRIVE_ROOT """

    folder_path = Path(GDRIVE_ROOT) / Path(folder_subpath)

    db = pGIS.PostgreSQL(DB_NAME, **credentials[DB_HOST])
    import_shapefiles(folder_path, db)


# LOAD UP AN ALREADY-CREATED DATABASE
# -----------------------------------
@click.command()
@click.argument("database")
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
def from_dumpfile(folder: str, database: str, host: str):
    """ Load up a .SQL file created by 'pg_dump'.
        NOTE!!! This will overwrite the database if you already
        have a db on your host with the same name.
    """

    folder = Path(folder) / database

    # Find the one with the highest version tag
    all_db_files = [x for x in folder.rglob("*.sql")]

    latest_datetime = datetime(1969, 8, 18, 9, 0, 0)
    latest_file = None

    for db_file in all_db_files:
        year, month, date, _, hour, minute, second = db_file.name[:-4].split("_d_")[-1].split("_")

        this_dt = datetime(*[int(x) for x in [year, month, date, hour, minute, second]])

        if this_dt > latest_datetime:
            latest_datetime = this_dt
            latest_file = db_file

    print(f"Loading db frozen on {latest_datetime} from \n\t-> {latest_file}")

    db = pGIS.PostgreSQL(database, **credentials[host])
    db.db_load_pgdump_file(latest_file)


# Wire up all the commands
# ------------------------

all_commands = [
    osm,
    copy,
    shapefile_folder_on_gdrive,
    from_dumpfile,
]

for cmd in all_commands:
    main.add_command(cmd)
