import numpy as np

from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd

def get_bookings_gdf (bookings, coord_cols):    
    gdf = gpd.GeoDataFrame\
        (bookings, geometry=bookings.loc[:, [coord_cols[0], coord_cols[1]]]\
        .apply(lambda p: Point(p[0], p[1]), axis=1))
    gdf.crs = {"init": "epsg:4326"}
    gdf = gdf.to_crs({"init": "epsg:3857"})
    gdf.loc[:, coord_cols[0]] = gdf.geometry.apply(lambda p: p.x)
    gdf.loc[:, coord_cols[1]] = gdf.geometry.apply(lambda p: p.y)
    return gdf

def get_parkings_gdf (parkings):    
    gdf = gpd.GeoDataFrame\
        (parkings, geometry=parkings.loc[:, ["longitude", "latitude"]]\
        .apply(lambda p: Point(p[0], p[1]), axis=1)) 
    gdf.crs = {"init": "epsg:4326"}
    gdf = gdf.to_crs({"init": "epsg:3857"})
    gdf.loc[:, "longitude"] = gdf.geometry.apply(lambda p: p.x)
    gdf.loc[:, "latitude"] = gdf.geometry.apply(lambda p: p.y)
    return gdf

def get_parking_gs (parking):
    parking.loc["geometry"] = Point(parking.longitude, parking.latitude)
    gs = gpd.GeoSeries(parking)
    gs.crs = {"init": "epsg:3857"}
    return gs
    
def get_city_grid (locations, bin_side_length):
        
    x_min, y_min, x_max, y_max = locations.total_bounds
    width = bin_side_length
    height = bin_side_length
    rows = int(np.ceil((y_max-y_min) / height))
    cols = int(np.ceil((x_max-x_min) / width))
    x_left = x_min
    x_right = x_min + width
    polygons = []
    for i in range(cols):
        y_top = y_max
        y_bottom = y_max - height
        for j in range(rows):
            polygons.append(Polygon([(x_left, y_top), 
                                     (x_right, y_top), 
                                     (x_right, y_bottom),
                                     (x_left, y_bottom)])) 
            y_top = y_top - height
            y_bottom = y_bottom - height
        x_left = x_left + width
        x_right = x_right + width
    grid = gpd.GeoDataFrame({"geometry":polygons})

    grid["zone_id"] = range(len(grid))
    grid.crs = {"init": "epsg:3857"}

    return grid

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r