import click
from pathlib import Path

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


# Wire up all the commands
# ------------------------

all_commands = [osm, copy, shapefile_folder_on_gdrive]

for cmd in all_commands:
    main.add_command(cmd)
