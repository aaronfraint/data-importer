import click

import os
from dotenv import load_dotenv, find_dotenv

import postgis_helpers as pGIS

from .openstreetmap import import_osm_for_dvrpc_region

load_dotenv(find_dotenv(usecwd=True))
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

credentials = pGIS.configurations()


@click.group()
def main():
    "The command 'DB-IMPORT' is used to import data into PostgreSQL."
    pass


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


all_commands = [osm]

for cmd in all_commands:
    main.add_command(cmd)
