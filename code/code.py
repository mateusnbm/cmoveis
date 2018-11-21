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
'''

def split_database(filename, output_path):

    csv_file = open(filename);
    csv_reader = csv.DictReader(csv_file)
    csv_data = list(csv_reader)
    csv_file.close()
    csv_headers = ','.join(csv_data[0].keys())

    random.shuffle(csv_data)

    training_file_path = output_path + "/training-0.csv"
    training_file = open(training_file_path, 'w+')
    training_file.write(csv_headers + '\n')

    testing_file_count = int(0.1*len(csv_data))
    testing_file_path = output_path + '/testing-0.csv'
    testing_file = open(testing_file_path, 'w+')
    testing_file.write(csv_headers + '\n')

    for i in range(0, len(csv_data)):
        data = ','.join(csv_data[i].values()) + '\n'
        if i < testing_file_count:
            testing_file.write(data)
        else:
            training_file.write(data)

    training_file.close()
    testing_file.close()

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

    for filepath in training_files:

        lat_min = 180
        lat_max = -180
        lon_min = 180
        lon_max = -180

        set_points = []
        set_csv_file = open(filepath);
        set_csv_reader = csv.DictReader(set_csv_file)
        set_csv_data = list(set_csv_reader)
        set_csv_file.close()

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

        plt.savefig('map.png')

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
