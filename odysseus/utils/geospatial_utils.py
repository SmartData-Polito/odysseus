import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd
from math import radians, cos, sin, asin, sqrt
from haversine import haversine, Unit


def get_city_grid_as_gdf(total_bounds, crs, bin_side_length):
    x_min, y_min, x_max, y_max = total_bounds

    # this has to be pretty much the same long all the longitudes, cause paralles are equidistant, so equal for every city
    p1 = (y_min, x_min)
    p2 = (y_min + 0.01, x_min)
    height_001 = haversine(p1, p2, unit=Unit.METERS)
    height = (0.01 * bin_side_length) / height_001

    # width changes depending on the city, casuse longitude distances vary depending on the latitude.
    p1 = (y_min, x_min)
    p2 = (y_min, x_min + 0.01)
    width_001 = haversine(p1, p2, unit=Unit.METERS)
    width = (0.01 * bin_side_length) / width_001

    rows = int(np.ceil((y_max - y_min) / height))
    cols = int(np.ceil((x_max - x_min) / width))
    x_left = x_min
    x_right = x_min + width
    polygons = []
    for i in range(cols):
        y_top = y_max
        y_bottom = y_max - height
        for j in range(rows):
            polygons.append(Polygon([(x_left, y_top), (x_right, y_top), (x_right, y_bottom), (x_left, y_bottom)]))
            y_top = y_top - height
            y_bottom = y_bottom - height
        x_left = x_left + width
        x_right = x_right + width
    grid = gpd.GeoDataFrame({"geometry": polygons})
    grid["zone_id"] = range(len(grid))
    grid.crs = crs
    return grid


def get_city_grid_as_matrix(total_bounds, bin_side_length):
    x_min, y_min, x_max, y_max = total_bounds

    # this has to be pretty much the same long all the longitudes, cause paralles are equidistant, so equal for every city
    p1 = (y_min, x_min)
    p2 = (y_min + 0.01, x_min)
    height_001 = haversine(p1, p2, unit=Unit.METERS)
    height = (0.01 * bin_side_length) / height_001

    # width changes depending on the city, casuse longitude distances vary depending on the latitude.
    p1 = (y_min, x_min)
    p2 = (y_min, x_min + 0.01)
    width_001 = haversine(p1, p2, unit=Unit.METERS)
    width = (0.01 * bin_side_length) / width_001

    rows = int(np.ceil((y_max - y_min) / height))
    cols = int(np.ceil((x_max - x_min) / width))
    grid_matrix = []
    row = 0
    for i in range(rows):
        grid_matrix.append([])
        col = 0
        for j in range(cols):
            grid_matrix[i].append(col * rows + row)
            col += 1
        row += 1
    return pd.DataFrame(grid_matrix)


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


def get_od_distance(grid, origin_id, destination_id):
    lon1 = grid.loc[origin_id, "geometry"].centroid.x
    lat1 = grid.loc[origin_id, "geometry"].centroid.y
    lon2 = grid.loc[destination_id, "geometry"].centroid.x
    lat2 = grid.loc[destination_id, "geometry"].centroid.y
    return get_haversine_distance(lon1, lat1, lon2, lat2)


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
