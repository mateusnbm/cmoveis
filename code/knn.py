#
# knn.py
#


import csv
import math
import pathloss
import conveniences
import numpy as np


'''
'''

def knn(k, training_data, values):

    neighbors = []
    indexes = range(0, len(values))

    for item in training_data:

        distance = [pow((item[i]-values[i]), 2) for i in indexes]
        distance = math.sqrt(sum(distance))
        coordinates = item[len(values)]

        neighbors.append([distance, coordinates])

    neighbors.sort(key=lambda x: x[0])

    lats = []
    lons = []

    for neighbor in neighbors[:k]:

        lats.append(neighbor[1][0])
        lons.append(neighbor[1][1])

    return np.mean(lats), np.mean(lons)


'''
'''

def estimate(k, training_files, testing_files):

    estimates = []

    keys = [('pathBTS'+str(i)) for i in range(1, 7)]

    # Loop through each test file. Their results will be combined
    # in the list named 'estimates'.

    for test_file in testing_files:

        errors = []
        details = []
        file_index = testing_files.index(test_file)

        # Open the csv file containing the training data as a list
        # of dictionaries.

        training_csv_file = open(training_files[file_index]);
        training_csv_reader = csv.DictReader(training_csv_file)
        training_csv_data = list(training_csv_reader)
        training_csv_file.close()

        # Open the csv file containing the test data as a list of dictionaries.

        testing_csv_file = open(test_file);
        testing_csv_reader = csv.DictReader(testing_csv_file)
        testing_csv_data = list(testing_csv_reader)
        testing_csv_file.close()

        # We do some pre-processing to organize the RSSI columns order to
        # match the measurement ones. Also, normalize the data.

        testing_data = []
        training_data = []
        rssi_list = [[] for _ in range(0, 6)]

        for item in testing_csv_data:
            values = [float(item[key]) for key in keys]
            for i in range(0, 6):
                rssi_list[i].append(values[i])

        for item in training_csv_data:
            values = [float(item[key]) for key in keys]
            for i in range(0, 6):
                rssi_list[i].append(values[i])

        rssi_mins = [np.amin(w) for w in rssi_list]
        rssi_maxs = [np.amax(w) for w in rssi_list]

        for item in testing_csv_data:

            for i in range(0, 6):

                min = rssi_mins[i]
                max = rssi_maxs[i]
                val = float(item[keys[i]])

                item[keys[i]] = (val-min)/(max-min)

        for item in training_csv_data:

            for i in range(0, 6):

                min = rssi_mins[i]
                max = rssi_maxs[i]
                val = float(item[keys[i]])

                item[keys[i]] = (val-min)/(max-min)

            rssi_data = [float(item[key]) for key in keys]
            coordinates_data = (float(item['lat']), float(item['lon']))
            item_data = rssi_data + [coordinates_data]

            training_data.append(item_data)

        # Loop through each measurement in the test data.

        for item in testing_csv_data:

            # Below we compute the k nearest neighbors of the measurement
            # and average their coordinates to determine the resultant ones.

            lat1 = float(item['lat'])
            lon1 = float(item['lon'])

            values = [float(item[key]) for key in keys]
            lat2, lon2 = knn(k, training_data, values)
            error_km = conveniences.coordinates_distance_km(lat1, lon1, lat2, lon2)
            error_mt = error_km*1000

            # We record the real coordinates, the predicted coordinates and
            # the error in meters. Later, we will use this information to
            # plot the real coordinates agains the predicted ones for every
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

        lat_min, lon_min, lat_max, lon_max = (
            conveniences.coordinates_min_max(testing_csv_data)
            )

        estimates.append({
            'coordinates_min': (lat_min, lon_min),
            'coordinates_max': (lat_max, lon_max),
            'error_min': np.amin(errors),
            'error_max': np.amax(errors),
            'error_mean': np.mean(errors),
            'error_stddev': np.std(errors),
            'data': details
        })

    return estimates
