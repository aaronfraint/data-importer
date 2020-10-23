from philly_transit_data import TransitData
from postgis_helpers import PostgreSQL


def import_transit_data(db: PostgreSQL):
    """
        Import SEPTA, NJT, and PATCO stops & lines.
        This code lives in another repo:
            https://github.com/aaronfraint/philly-transit-data
    """

    transit_data = TransitData()
    stops, lines = transit_data.all_spatial_data()

    # Import transit stops
    db.import_geodataframe(stops, "regional_transit_stops")

    # Massage the lines before importing
    # - reset index and then explode so all are singlepart lines
    line_gdf = lines.reset_index()
    line_gdf = line_gdf.explode()
    line_gdf["explode_idx"] = line_gdf.index
    line_gdf = line_gdf.reset_index()

    db.import_geodataframe(line_gdf, "regional_transit_lines")

    # Reproject from 4326 to 26918
    db.table_reproject_spatial_data("regional_transit_lines", 4326, 26918, "LINESTRING")
    db.table_reproject_spatial_data("regional_transit_stops", 4326, 26918, "POINT")
