#
# regression.py
#


import csv
import math
import pathloss
import conveniences
import numpy as np

from sklearn import svm
from sklearn import linear_model
from sklearn.linear_model import LinearRegression

'''
'''

def regressor_model(name):

    if name == 'SVR': return svm.SVR()
    if name == 'SGDRegressor': return linear_model.SGDRegressor()
    if name == 'BayesianRidge': return linear_model.BayesianRidge()
    if name == 'LassoLars': return linear_model.LassoLars()
    if name == 'ARDRegression': return linear_model.ARDRegression()
    if name == 'PassiveAggressiveRegressor': return linear_model.PassiveAggressiveRegressor()
    if name == 'TheilSenRegressor': return linear_model.TheilSenRegressor()
    if name == 'LinearRegression': return linear_model.LinearRegression()

    return linear_model.LinearRegression()


'''
'''

def estimate(regressor, training_files, testing_files):

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

        # Setup the support vector machine.

        training_attributes = []
        training_targets_lat = []
        training_targets_lon = []

        for item in training_csv_data:

            lat = float(item['lat'])
            lon = float(item['lon'])

            training_attributes.append([float(item[key]) for key in keys])
            training_targets_lat.append(lat)
            training_targets_lon.append(lon)

        model_lat = regressor_model(regressor)
        model_lat.fit(training_attributes, training_targets_lat)

        model_lon = regressor_model(regressor)
        model_lon.fit(training_attributes, training_targets_lon)

        # Loop through each measurement in the test data.

        for item in testing_csv_data:

            # Below we compute the k nearest neighbors of the measurement
            # and average their coordinates to determine the resultant ones.

            lat1 = float(item['lat'])
            lon1 = float(item['lon'])

            values = [float(item[key]) for key in keys]
            lat2 = model_lat.predict([values])[0]
            lon2 = model_lon.predict([values])[0]

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
