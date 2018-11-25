#
# finferprinting.py
#


import csv
import math
import numpy
import pathloss

import smopy
import matplotlib.pyplot as plt

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

def compute_path_losses(bts_data, coordinates, algorithm):

    losses = []
    parameters = {}

    if algorithm == 'OkumuraHata':

        parameters['freq'] = 1800
        parameters['rxH'] = 1.5
        parameters['txH'] = 50.0
        parameters['area_kind'] = 'urban'
        parameters['city_kind'] = 'medium'

    elif algorithm == 'COST231':

        parameters['freq'] = 1800
        parameters['rxH'] = 1.5
        parameters['txH'] = 50.0
        parameters['ws'] = 15.0
        parameters['bs'] = 0.5
        parameters['hr'] = 3.0
        parameters['area_kind'] = 'urban'
        parameters['city_kind'] = 'medium'

    elif algorithm == 'ECC33':

        parameters['freq'] = 1800
        parameters['rxH'] = 1.5
        parameters['txH'] = 50.0
        parameters['area_kind'] = 'urban'
        parameters['city_kind'] = 'medium'

    for bts in bts_data:

        lat1, lon1 = float(bts['lat']), float(bts['lon'])
        lat2, lon2 = coordinates

        distance = coordinates_distance_km(lat1, lon1, lat2, lon2)
        loss = pathloss.pathloss(algorithm, parameters, distance)

        losses.append(loss)

    return losses


'''
'''

def create_grid(bts_data, test_data, tile_dimension_km, algorithm):

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

        lon = lon_min

        grid.append([])

        for j in range(0, lon_points):

            coordinates = (lat, lon)
            path_losses = compute_path_losses(bts_data, coordinates, algorithm)

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
            diff = [pow(losses[k]-values[k], 2) for k in range(0, len(losses))]
            norm = math.sqrt(sum(diff))

            if norm < distance:

                distance = norm
                position = (i, j)

    return position


'''
'''

def estimate(bts_file, training_files, testing_files, output_folder, algorithm):

    estimates = []

    # Open the csv file containing data about the base transceiver
    # stations (BTSs) as a list of dictionaries.

    bts_csv_file = open(bts_file);
    bts_csv_reader = csv.DictReader(bts_csv_file)
    bts_csv_data = list(bts_csv_reader)
    bts_csv_file.close()

    # Loop through each test file. Their results will be combined
    # in the list named 'estimates'.

    for test_file in testing_files:

        errors = []
        details = []

        # Open the csv file containing the test data as a list of dictionaries.

        testing_csv_file = open(test_file);
        testing_csv_reader = csv.DictReader(testing_csv_file)
        testing_csv_data = list(testing_csv_reader)
        testing_csv_file.close()

        # Create the fingerprinting grid. It will generate a set of 2D points
        # based on the given resolution and the test data coordinates minimums
        # and maximums.

        grid = create_grid(bts_csv_data, testing_csv_data, 0.01, algorithm)

        # Loop through each measurement in the test data.

        for item in testing_csv_data:

            # Below we look for point of the grid with the closest RSSI
            # signature to the measurement signature, using the Euclidean
            # distance.

            lat1 = float(item['lat'])
            lon1 = float(item['lon'])

            keys = [('pathBTS'+str(i)) for i in range(1, 7)]
            values = [float(item[key]) for key in keys]
            address = localize(values, grid)
            lat2, lon2 = grid[address[0]][address[1]][0]

            error_km = coordinates_distance_km(lat1, lon1, lat2, lon2)
            error_mt = error_km*1000

            # We record the real coordinates, the predicted coordinates and
            # the error in meters. Later, we will use this information to
            # plot the real coordinates agains the predicted one for every
            # measurement. The error will be used to compute the mean and
            # the standard deviation.

            info = {
                'point_id': item['pontoId'],
                'real_coordinates': (lat1, lon1),
                'predicted_coordinates': (lat2, lon2),
                'error_mt': error_mt
            }

            errors.append(error_mt)
            details.append(info)

        estimates.append({
            'coordinates_min': grid[0][0][0],
            'coordinates_max': grid[-1][-1][0],
            'error_min': numpy.amin(errors),
            'error_max': numpy.amax(errors),
            'error_mean': numpy.mean(errors),
            'error_stddev': numpy.std(errors),
            'data': details
        })

        # Now, let's draw the grid on a map. We cannot draw every line since
        # the resultant figure will, most likely, contain a filled square,
        # because the grid tile resolution is too low.

        file_index = testing_files.index(test_file)

        map_file_name = '/fingerprinting-'
        map_file_name += algorithm + '-grid-' + str(file_index) + '.png'
        map_file_path = output_folder + map_file_name

        grid_lat_min, grid_lon_min = grid[0][0][0]
        grid_lat_max, grid_lon_max = grid[-1][-1][0]

        zoomLevel = 15
        region = (grid_lat_min, grid_lon_min, grid_lat_max, grid_lon_max)
        smopyMap = smopy.Map(region, z=zoomLevel)
        matplotlibMap = smopyMap.show_mpl(figsize=(8, 8))

        for i in (range(0, len(grid), 8)+[len(grid)-1]):

            lat1, lon1 = grid[i][0][0]
            lat2, lon2 = grid[i][-1][0]

            x1, y1 = smopyMap.to_pixels(lat1, lon1)
            x2, y2 = smopyMap.to_pixels(lat2, lon2)

            matplotlibMap.plot((x1, x2), (y1, y2), 'k-', alpha=0.5)

        for j in (range(0, len(grid[0]), 8)+[len(grid[0])-1]):

            lat1, lon1 = grid[0][j][0]
            lat2, lon2 = grid[-1][j][0]

            x1, y1 = smopyMap.to_pixels(lat1, lon1)
            x2, y2 = smopyMap.to_pixels(lat2, lon2)

            matplotlibMap.plot((x1, x2), (y1, y2), 'k-', alpha=0.5)

        plt.savefig(map_file_path)

    return estimates
