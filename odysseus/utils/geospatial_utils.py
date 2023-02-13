import math

import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd
from math import radians, cos, sin, asin, sqrt
from haversine import haversine, Unit
from scipy.spatial.distance import euclidean


def get_width_height_from_wgs84_bounds(x_min, y_min, bin_side_length):

    # this has to be pretty much the same long all the longitudes
    # cause paralles are equidistant, so equal for every city

    p1 = (y_min, x_min)
    p2 = (y_min + 0.01, x_min)
    height_001 = haversine(p1, p2, unit=Unit.METERS)
    height = (0.01 * bin_side_length) / height_001

    # width changes depending on the city, cause longitude distances vary depending on the latitude.
    p1 = (y_min, x_min)
    p2 = (y_min, x_min + 0.01)
    width_001 = haversine(p1, p2, unit=Unit.METERS)
    width = (0.01 * bin_side_length) / width_001

    return width, height


def get_city_grid_as_gdf(total_bounds, bin_side_length, crs="epsg:4326"):

    x_min, y_min, x_max, y_max = total_bounds
    if crs == "epsg:4326":
        width, height = get_width_height_from_wgs84_bounds(x_min, y_min, bin_side_length)
        step_x = width
        step_y = height
    elif crs == "dummy_crs":
        step_x = step_y = bin_side_length
    else:
        raise Exception("Geospatial Grid non properly configured!")

    y_top = y_max
    y_bottom = y_max - step_y
    polygons = []
    while y_bottom >= y_min:
        x_left = x_min
        x_right = x_min + step_x
        while x_right <= x_max:
            polygons.append(Polygon([(x_left, y_top), (x_right, y_top), (x_right, y_bottom), (x_left, y_bottom)]))
            x_left = x_left + step_x
            x_right = x_right + step_x
        y_top = y_top - step_y
        y_bottom = y_bottom - step_y

    grid = gpd.GeoDataFrame({"geometry": polygons})

    grid["zone_id"] = range(len(grid))
    if crs == "epsg:4326":
        grid.crs = crs
    if crs == "dummy_crs":
        grid.crs = "epsg:3857"

    return grid


def get_city_grid_as_matrix(total_bounds, bin_side_length, crs="epsg:4326"):
    x_min, y_min, x_max, y_max = total_bounds
    if crs == "epsg:4326":
        width, height = get_width_height_from_wgs84_bounds(x_min, y_min, bin_side_length)
        step_x = width
        step_y = height
    elif crs == "dummy_crs":
        step_x = step_y = bin_side_length
    else:
        raise Exception("Grid Matrix non properly configured!")

    grid_matrix = []
    zone_id = 0
    i = 0
    y_top = y_max
    y_bottom = y_max - step_y
    while y_bottom >= y_min:
        x_left = x_min
        x_right = x_min + step_x
        grid_matrix.append(list())
        while x_right <= x_max:
            grid_matrix[i].append(zone_id)
            zone_id += 1
            x_left = x_left + step_x
            x_right = x_right + step_x
        y_top = y_top - step_y
        y_bottom = y_bottom - step_y
        i += 1

    return pd.DataFrame(grid_matrix)


def get_grid_matrix_from_config(grid_config):
    grid_matrix = get_city_grid_as_matrix(
        (0, 0, grid_config["n_cols"] * grid_config["bin_side_length"],
         grid_config["n_rows"] * grid_config["bin_side_length"]),
        grid_config["bin_side_length"],
        "dummy_crs"
    )
    return grid_matrix


def get_random_point_from_linestring (linestring):
    if linestring.geom_type == 'MultiLineString':
        coords = []
        for line in linestring:
            coords += list(line.coords)
        linestring = LineString(coords)
    linestring_coords = linestring.coords
    segment_index = np.random.randint(0, len(linestring_coords)-1)
    random_segment = LineString([
        Point(linestring_coords[segment_index]),
        Point(linestring_coords[(segment_index+1)])
    ])
    u = np.random.rand()
    x1, x2 = random_segment.coords[0][0], random_segment.coords[1][0]
    y1, y2 = random_segment.coords[0][1], random_segment.coords[1][1]
    random_x = (1-u)*x1 + u*x2
    random_y = (1-u)*y1 + u*y2
    random_point = Point(random_x, random_y)
    return random_point


def get_random_point_from_shape(shape):
    within = False
    while not within:
        x = np.random.uniform(shape.bounds[0], shape.bounds[2])
        y = np.random.uniform(shape.bounds[1], shape.bounds[3])
        within = shape.contains(Point(x, y))
    return Point(x, y)


def add_grouped_count_to_grid(grid, trips_locations, group_col, od_key, aggfunc="count"):
    for group, group_df in trips_locations.groupby(group_col):
        grid["_".join([od_key, aggfunc, str(group)])] = \
            group_df.groupby("index_right").geometry.count()
    return grid


def get_haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r * 1000


def get_od_distance(grid_centroids, origin_id, destination_id, crs="epsg:3857"):
    x1 = grid_centroids.loc[origin_id, "centroid_x"]
    y1 = grid_centroids.loc[origin_id, "centroid_y"]
    x2 = grid_centroids.loc[destination_id, "centroid_x"]
    y2 = grid_centroids.loc[destination_id, "centroid_y"]
    if crs == "epsg:4326":
        return get_haversine_distance(x1, y1, x2, y2)
    elif crs == "epsg:3857":
        return euclidean((x1, y1), (x2, y2))


def miles_to_meters(miles):
    return miles * 1609.34


def get_in_flow_count(trips_destinations):

    in_flow_count = trips_destinations[["zone_id", "year", "month", "day", "end_hour", "end_time"]].groupby(
        ["zone_id", "year", "month", "day", "end_hour"], as_index=False
    ).count().rename(columns={"end_time": "in_flow_count"})

    return in_flow_count


def get_out_flow_count(trips_origins):

    out_flow_count = trips_origins[["zone_id", "year", "month", "day", "start_hour", "start_time"]].groupby(
        ["zone_id", "year", "month", "day", "start_hour"], as_index=False
    ).count().rename(columns={"start_time": "out_flow_count"})

    return out_flow_count


def get_grid_indexes_dict(grid_matrix):
    grid_indexes_dict = {}
    for j in grid_matrix.columns:
        for i in grid_matrix.index:
            grid_indexes_dict[grid_matrix.iloc[i, j]] = (i, j)
    return grid_indexes_dict


def get_distance_matrix(
        grid_indexes_dict, origin_zones, destination_zones, bin_side_length
):

    distance_matrix = dict()
    for o_id in origin_zones:
        distance_matrix[o_id] = dict()
        for d_id in destination_zones:
            o_i, o_j = grid_indexes_dict[o_id]
            d_i, d_j = grid_indexes_dict[d_id]
            distance_matrix[o_id][d_id] = euclidean((o_j, o_i), (d_j, d_i)) * bin_side_length

    return pd.DataFrame(distance_matrix).T


def get_closest_zone_from_grid_matrix(grid_indexes_dict, origin_zones, destination_zones):
    closest_zones = dict()
    for o_id in origin_zones:
        min_od_dist = 10e12
        min_dist_zone = -1
        for d_id in destination_zones:
            o_i, o_j = grid_indexes_dict[o_id]
            d_i, d_j = grid_indexes_dict[d_id]
            od_dist = euclidean((o_j, o_i), (d_j, d_i))
            if od_dist < min_od_dist:
                min_od_dist = od_dist
                min_dist_zone = d_id
            closest_zones[o_id] = min_dist_zone
    return closest_zones
