#
# finferprinting.py
#


import csv
import math
import numpy
import pathloss

from geographiclib.geodesic import Geodesic, Math


'''
'''

def coordinates_distance_km(lat1, lon1, lat2, lon2):

    extract = lambda g:g['s12']/1000
    mask = Geodesic.DISTANCE | Geodesic.AZIMUTH | Geodesic.REDUCEDLENGTH
    gab = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2, mask)

    return extract(gab)


'''
'''

def coordinates_min_max(data):

    lat_min = 180
    lat_max = -180
    lon_min = 180
    lon_max = -180

    for item in data:

        latitude = float(item['lat'])
        longitude = float(item['lon'])

        lat_min = min(lat_min, latitude)
        lat_max = max(lat_max, latitude)
        lon_min = min(lon_min, longitude)
        lon_max = max(lon_max, longitude)

    return lat_min, lon_min, lat_max, lon_max


'''
'''

def compute_path_losses(bts_data, coordinates):

    losses = []

    for bts in bts_data:

        parameters = {}
        parameters['freq'] = 1800
        parameters['rxH'] = 1.5
        parameters['txH'] = 50
        parameters['area_kind'] = 'Urban'
        parameters['city_kind'] = 'Medium'

        lat1, lon1 = float(bts['lat']), float(bts['lon'])
        lat2, lon2 = coordinates

        distance = coordinates_distance_km(lat1, lon1, lat2, lon2)
        loss = pathloss.pathloss("OkumuraHata", parameters, distance)

        losses.append(loss)

    return losses


'''
'''

def create_grid(bts_data, test_data, tile_dimension_km):

    grid = []

    lat_min, lon_min, lat_max, lon_max = coordinates_min_max(test_data)

    lat_distance = coordinates_distance_km(lat_min, lon_min, lat_max, lon_min)
    lon_distance = coordinates_distance_km(lat_min, lon_min, lat_min, lon_max)

    lat_points = int(math.ceil(lat_distance/tile_dimension_km))
    lon_points = int(math.ceil(lon_distance/tile_dimension_km))

    lat_step_size = abs(lat_min-lat_max)/lat_points
    lon_step_size = abs(lon_min-lon_max)/lon_points

    lat = lat_min
    lon = lon_min

    for i in range(0, lat_points):

        grid.append([])

        for j in range(0, lon_points):

            coordinates = (lat, lon)
            path_losses = compute_path_losses(bts_data, coordinates)

            grid[i].append([coordinates, path_losses])

            lon = lon + lon_step_size

        lat = lat + lat_step_size

    return grid


'''
'''

def localize(values, grid):

    distance = 100000
    position = (0, 0)

    for i in range(0, len(grid)):

        for j in range(0, len(grid[0])):

            losses = grid[i][j][1]
            diff = [pow(values[k]-losses[k], 2) for k in range(0, len(losses))]
            norm = math.sqrt(sum(diff))

            if norm < distance:

                distance = norm
                position = (i, j)

    return position


'''
'''

def estimate(bts_file, training_files, testing_files, output_folder):

    estimates = []

    bts_csv_file = open(bts_file);
    bts_csv_reader = csv.DictReader(bts_csv_file)
    bts_csv_data = list(bts_csv_reader)
    bts_csv_file.close()

    for test_file in testing_files:

        errors = []

        testing_csv_file = open(test_file);
        testing_csv_reader = csv.DictReader(testing_csv_file)
        testing_csv_data = list(testing_csv_reader)
        testing_csv_file.close()

        grid = create_grid(bts_csv_data, testing_csv_data, 0.01)

        for item in testing_csv_data:

            lat1 = float(item['lat'])
            lon1 = float(item['lon'])

            keys = [('pathBTS'+str(i)) for i in range(1, 7)]
            values = [float(item[key]) for key in keys]
            address = localize(values, grid)
            lat2, lon2 = grid[address[0]][address[1]][0]

            error_km = coordinates_distance_km(lat1, lon1, lat2, lon2)
            error_mt = error_km*1000

            errors.append(error_mt)

        print('mean: ' + str(numpy.mean(errors)))
        print('standard deviation: ' + str(numpy.std(errors)))

        estimates.append(errors)

    return estimates
