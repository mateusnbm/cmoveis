#
# code.py
#


import os
import csv
import smopy
import random
import datetime
import matplotlib.pyplot as plt


'''
Splits a single input file into a training and a testing file (90-10).
'''

def split_database(filename, output_path):

    # Open the csv file as a list dictionaries.

    csv_file = open(filename);
    csv_reader = csv.DictReader(csv_file)
    csv_data = list(csv_reader)
    csv_file.close()
    csv_headers = ','.join(csv_data[0].keys())

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

    # Write the first 90% of the items to the training file and the
    # remaining 10% to the testing file.

    testing_items = csv_data[0:testing_file_count]
    testing_data = [','.join(item.values()) + '\n' for item in testing_items]
    testing_string = ''.join(testing_data)

    training_items = csv_data[testing_file_count:]
    training_data = [','.join(item.values()) + '\n' for item in training_items]
    training_string = '\n'.join(training_data)

    testing_file.write(testing_string)
    training_file.write(training_string)

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
    bts_csv_file = open(bts_data_file_path);
    bts_csv_reader = csv.DictReader(bts_csv_file)
    bts_csv_data = list(bts_csv_reader)
    bts_csv_file.close()

    for bts in bts_csv_data:

        latitude = float(bts['lat'])
        longitude = float(bts['lon'])

        bts_points.append([latitude, longitude])

        lat_min = min(lat_min, latitude)
        lat_max = max(lat_max, latitude)
        lon_min = min(lon_min, longitude)
        lon_max = max(lon_max, longitude)

    bts_lat_min = lat_min
    bts_lat_max = lat_max
    bts_lon_min = lon_min
    bts_lon_max = lon_max

    for i in range(0, len(training_files)):

        lat_min = 180
        lat_max = -180
        lon_min = 180
        lon_max = -180

        set_points = []
        set_csv_file = open(training_files[i]);
        set_csv_reader = csv.DictReader(set_csv_file)
        set_csv_data = list(set_csv_reader)
        set_csv_file.close()

        map_file_name = '/inputs-map-' + str(i) + '.png'
        map_file_path = output_path + map_file_name

        statistics_file_name = '/inputs-statistics-' + str(i) + '.txt'
        statistics_file_path = output_path + statistics_file_name
        statistics_file = open(statistics_file_path, 'w+')

        for measurement in set_csv_data:

            latitude = float(measurement['lat'])
            longitude = float(measurement['lon'])

            set_points.append([latitude, longitude])

            lat_min = min(lat_min, latitude)
            lat_max = max(lat_max, latitude)
            lon_min = min(lon_min, longitude)
            lon_max = max(lon_max, longitude)

        lat_min = min(lat_min, bts_lat_min)
        lat_max = max(lat_max, bts_lat_max)
        lon_min = min(lon_min, bts_lon_min)
        lon_max = max(lon_max, bts_lon_max)

        zoomLevel = 15
        region = (lat_min, lon_min, lat_max, lon_max)
        smopyMap = smopy.Map(region, z=zoomLevel)
        matplotlibMap = smopyMap.show_mpl(figsize=(8, 8))

        for point in set_points:

            x, y = smopyMap.to_pixels(point[0], point[1])

            matplotlibMap.plot(x, y, 'og', ms=10, mew=2, alpha=0.2)

        for point in bts_points:

            x, y = smopyMap.to_pixels(point[0], point[1])

            matplotlibMap.plot(x, y, 'or', ms=10, mew=2)

        plt.savefig(map_file_path)
        statistics_file.close()

    return 0


'''
'''

bts_file_name = 'dados_BTSs.csv'
bts_file_path = '../' + bts_file_name

intput_file_name = 'LocTreino_Equipe_3.csv'
input_file_path = '../' + intput_file_name

output_folder_name = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
output_folder_path = 'outputs/' + output_folder_name

os.makedirs(output_folder_path)

training_files, testing_files = split_database(input_file_path, output_folder_path)

analyse_inputs(bts_file_path, training_files, output_folder_path)
