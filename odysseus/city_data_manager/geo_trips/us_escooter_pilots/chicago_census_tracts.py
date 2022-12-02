import os

import geopandas as gpd

from odysseus.city_data_manager.geo_trips.geo_data_source import GeoDataSource


class ChicagoCensusTracts(GeoDataSource):

    def __init__(self):
        super().__init__("Chicago", "us_census_bureau")

    def load_raw(self):
        raw_geo_data_path = os.path.join(
            self.raw_data_path,
            [filename for filename in os.listdir(self.raw_data_path) if filename.endswith("dbf")][0]
        )
        self.gdf = gpd.read_file(raw_geo_data_path)
        return self.gdf

    def normalise(self):
        self.gdf_norm = self.gdf
        print(list(self.gdf_norm.columns))
        self.gdf_norm = self.gdf_norm.rename({
            "geoid10": "census_tract_id"
        }, axis=1)
        self.gdf_norm = self.gdf_norm[[
            "census_tract_id", "geometry"
        ]]
        self.gdf_norm.census_tract_id = self.gdf_norm.census_tract_id.astype(int)

        self.gdf_norm.to_file(
            os.path.join(
                self.norm_data_path,
                "census_tracts.shp"
            )
        )
        return self.gdf_norm