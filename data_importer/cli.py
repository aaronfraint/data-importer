import click

import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
DB_NAME = os.getenv("DB_NAME")


@click.group()
def main():
    "The command 'DB-IMPORT' is used to import data into PostgreSQL."
    pass


@click.command()
def test():
    print(DB_NAME)
    # print(os.getcwd())


@click.command()
def import_data():
    """Import RideScore data into the SQL database"""
    ridescore_inputs = GDRIVE_ROOT / "inputs"
    import_shapefiles(ridescore_inputs, db)


all_commands = [test, import_data]

for cmd in all_commands:
    main.add_command(cmd)
