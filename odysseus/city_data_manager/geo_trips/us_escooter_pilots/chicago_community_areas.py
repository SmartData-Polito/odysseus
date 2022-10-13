import os

import geopandas as gpd

from odysseus.city_data_manager.geo_trips.geo_data_source import GeoDataSource


class ChicagoCommunityAreas(GeoDataSource):

    def __init__(self):
        super().__init__("Chicago", "city_open_data")

    def load_raw(self):
        raw_geo_data_path = os.path.join(
            self.raw_data_path,
            [filename for filename in os.listdir(self.raw_data_path) if filename.endswith("dbf")][0]
        )
        self.gdf = gpd.read_file(raw_geo_data_path)
        return self.gdf

    def normalise(self):
        self.gdf_norm = self.gdf
        self.gdf_norm = self.gdf_norm.rename({
            "area_num_1": "community_area_number"
        }, axis=1)
        self.gdf_norm = self.gdf_norm[[
            "community_area_number", "geometry"
        ]]
        self.gdf_norm.community_area_number = self.gdf_norm.community_area_number.astype(int)

        self.gdf_norm.to_file(
            os.path.join(
                self.norm_data_path,
                "community_areas.shp"
            )
        )
        return self.gdf_norm
