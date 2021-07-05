import os

import geopandas as gpd

from odysseus.city_data_manager.city_data_source.geo_data_source.geo_data_source import GeoDataSource


class CalgaryHexagonalGrid(GeoDataSource):

    def __init__(self):
        super().__init__("Calgary", "city_of_calgary")

    def load_raw(self):
        raw_geo_data_path = os.path.join(
            self.raw_data_path,
            "geo_export_edc5528d-f07e-4fd8-9622-be91c874918c.dbf"
        )
        self.gdf = gpd.read_file(raw_geo_data_path)
        return self.gdf

    def normalise(self):
        self.gdf_norm = self.gdf
        self.gdf_norm = self.gdf_norm[[
            "grid_id", "geometry"
        ]]

        self.gdf_norm.to_file(
            os.path.join(
                self.norm_data_path,
                "hexagonal_grid.shp"
            )
        )
        return self.gdf_norm
