#
# conveniences.py
#


import csv
import random
import smopy
import numpy as np
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
Splits a single input file into a training and a testing file (90-10).
'''

def split_database(filename, output_path):

    # Open the csv file as a list of dictionaries.

    csv_file = open(filename);
    csv_reader = csv.DictReader(csv_file)
    csv_data = list(csv_reader)
    csv_file.close()
    csv_headers = ','.join(csv_data[0].keys())

    # Remove lines that contain an unknown attribute value.

    indexes = []

    for i in range(0, len(csv_data)):

        if 'NA' in csv_data[i].values():

            indexes.append(i)

    csv_data = [i for j, i in enumerate(csv_data) if j not in indexes]

    # We shuffle the list to simplify the process of extracting
    # random items from it. The training and test sets must contain
    # completely random items.

    random.shuffle(csv_data)

    # Create a file for the training set and one for the testing
    # set. We, also, write the csv headers to them.

    training_file_path = output_path + "/training-0.csv"
    training_file = open(training_file_path, 'w+')
    training_file.write(csv_headers + '\n')

    testing_file_count = int(0.1*len(csv_data))
    testing_file_path = output_path + '/testing-0.csv'
    testing_file = open(testing_file_path, 'w+')
    testing_file.write(csv_headers + '\n')

    # Write the first 10% of the items to the training file and the
    # remaining 10% to the testing file.

    training_items = csv_data[testing_file_count:]
    training_data = [','.join(item.values()) + '\n' for item in training_items]
    training_string = ''.join(training_data)

    testing_items = csv_data[0:testing_file_count]
    testing_data = [','.join(item.values()) + '\n' for item in testing_items]
    testing_string = ''.join(testing_data)

    training_file.write(training_string)
    testing_file.write(testing_string)

    # Close the files and return their paths. We return each path inside
    # a list for compatibility reasons. In the future we might want
    # to implement a better cross validation mechanism that generates
    # more than one pair files, this will help simplify other parts of the
    # implementation.

    testing_file.close()
    training_file.close()

    return [training_file_path], [testing_file_path]


'''
'''

def analyse_inputs(bts_data_file_path, training_files, output_path):

    lat_min = 180
    lat_max = -180
    lon_min = 180
    lon_max = -180

    bts_points = []
    bts_features = [[], []]

    # Open the csv file containing data about the base transceiver
    # stations (BTSs) as a list of dictionaries.

    bts_csv_file = open(bts_data_file_path);
    bts_csv_reader = csv.DictReader(bts_csv_file)
    bts_csv_data = list(bts_csv_reader)
    bts_csv_file.close()

    # Loop through the stations looking for the coordinates that are
    # further away from the origin. We'll use them to determine the area
    # that should be presented on the map.

    # We also use the loop below to compute two vectors listing all latitudes
    # and longitudes. We'll use them to compute the mean and standard deviation.

    for bts in bts_csv_data:

        latitude = float(bts['lat'])
        longitude = float(bts['lon'])

        bts_points.append([latitude, longitude])
        bts_features[0].append(latitude)
        bts_features[1].append(longitude)

        lat_min = min(lat_min, latitude)
        lat_max = max(lat_max, latitude)
        lon_min = min(lon_min, longitude)
        lon_max = max(lon_max, longitude)

    bts_lat_min = lat_min
    bts_lat_max = lat_max
    bts_lon_min = lon_min
    bts_lon_max = lon_max

    bts_lat_mean = np.mean(bts_features[0])
    bts_lat_stddev = np.std(bts_features[0])
    bts_lon_mean = np.mean(bts_features[1])
    bts_lon_stddev = np.std(bts_features[1])

    # Write the BTSs mean positino and standard deviation to a file.
    # We'll use the same file later to write some more statistics for each
    # training and testing file.

    statistics_file_name = '/inputs-statistics.txt'
    statistics_file_path = output_path + statistics_file_name
    statistics_file = open(statistics_file_path, 'w+')

    content = '\nBTS Statistics:\n\n'
    content = content + 'Latitude mean: ' + str(bts_lat_mean) + ' '
    content = content + 'stddev: ' + str(bts_lat_stddev) + '\n'
    content = content + 'Longitude mean: ' + str(bts_lon_mean) + ' '
    content = content + 'stddev: ' + str(bts_lon_stddev) + '\n\n'

    statistics_file.write(content)

    # ...

    for i in range(0, len(training_files)):

        lat_min = 180
        lat_max = -180
        lon_min = 180
        lon_max = -180

        map_file_name = '/inputs-map-' + str(i) + '.png'
        map_file_path = output_path + map_file_name

        # ...

        set_points = []
        set_features = [[] for _ in range(0, 8)]
        set_csv_file = open(training_files[i]);
        set_csv_reader = csv.DictReader(set_csv_file)
        set_csv_data = list(set_csv_reader)
        set_csv_file.close()

        # ...

        for measurement in set_csv_data:

            latitude = float(measurement['lat'])
            longitude = float(measurement['lon'])

            set_points.append([latitude, longitude])

            features = [
                'lat', 'lon',
                'pathBTS1', 'pathBTS2', 'pathBTS3',
                'pathBTS4', 'pathBTS5', 'pathBTS6'
                ]

            for k in range(0, len(features)):

                feature = features[k]

                if measurement[feature] != 'NA':

                    set_features[k].append(float(measurement[feature]))

            lat_min = min(lat_min, latitude)
            lat_max = max(lat_max, latitude)
            lon_min = min(lon_min, longitude)
            lon_max = max(lon_max, longitude)

        lat_min = min(lat_min, bts_lat_min)
        lat_max = max(lat_max, bts_lat_max)
        lon_min = min(lon_min, bts_lon_min)
        lon_max = max(lon_max, bts_lon_max)

        lat_mean = np.mean(set_features[0])
        lat_stddev = np.std(set_features[0])
        lon_mean = np.mean(set_features[1])
        lon_stddev = np.std(set_features[1])
        path_bts_1_mean = np.mean(set_features[2])
        path_bts_1_stddev = np.std(set_features[2])
        path_bts_2_mean = np.mean(set_features[3])
        path_bts_2_stddev = np.std(set_features[3])
        path_bts_3_mean = np.mean(set_features[4])
        path_bts_3_stddev = np.std(set_features[4])
        path_bts_4_mean = np.mean(set_features[5])
        path_bts_4_stddev = np.std(set_features[5])
        path_bts_5_mean = np.mean(set_features[6])
        path_bts_5_stddev = np.std(set_features[6])
        path_bts_6_mean = np.mean(set_features[7])
        path_bts_6_stddev = np.std(set_features[7])

        # ...

        content = 'Training File '+str(i)+' Statistics:\n\n'
        content = content + 'Latitude mean: ' + str(lat_mean) + ' '
        content = content + 'stddev: ' + str(lat_stddev) + '\n'
        content = content + 'Longitude mean: ' + str(lon_mean) + ' '
        content = content + 'stddev: ' + str(lon_stddev) + '\n'
        content = content + 'PathBTS1 mean: ' + str(path_bts_1_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_1_stddev) + '\n'
        content = content + 'PathBTS2 mean: ' + str(path_bts_2_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_2_stddev) + '\n'
        content = content + 'PathBTS3 mean: ' + str(path_bts_3_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_3_stddev) + '\n'
        content = content + 'PathBTS4 mean: ' + str(path_bts_4_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_4_stddev) + '\n'
        content = content + 'PathBTS5 mean: ' + str(path_bts_5_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_5_stddev) + '\n'
        content = content + 'PathBTS6 mean: ' + str(path_bts_6_mean) + ' '
        content = content + 'stddev: ' + str(path_bts_6_stddev) + '\n\n'

        statistics_file.write(content)

        # ...

        zoomLevel = 15
        region = (lat_min, lon_min, lat_max, lon_max)
        smopyMap = smopy.Map(region, z=zoomLevel)
        matplotlibMap = smopyMap.show_mpl(figsize=(8, 8))

        for point in set_points:

            x, y = smopyMap.to_pixels(point[0], point[1])

            matplotlibMap.plot(x, y, 'og', ms=5, mew=2, alpha=0.2)

        for point in bts_points:

            x, y = smopyMap.to_pixels(point[0], point[1])

            matplotlibMap.plot(x, y, 'or', ms=10, mew=2)

        plt.savefig(map_file_path)

    statistics_file.close()

    return 0
