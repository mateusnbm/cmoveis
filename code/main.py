# -*- coding: utf-8 -*-
#
# main.py
#


import os
import csv
import random
import datetime

import smopy
import numpy as np
import matplotlib.pyplot as plt

import knn
import regression
import pathloss
import conveniences
import fingerprinting


'''
Main implementation. Generate support files, splits the database,
compute statistics, run localization algorithms and generates the
required output files.
'''

# General definitions.

bts_file_name = 'dados_BTSs.csv'
bts_file_path = '../' + bts_file_name

intput_file_name = 'LocTreino_Equipe_3.csv'
input_file_path = '../' + intput_file_name

output_folder_name = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
output_folder_path = 'outputs/' + output_folder_name

# We create a new folder in each execution to store the program files.

os.makedirs(output_folder_path)

# Below we split the database in a training set and testing set,
# random records and drawn respecting the proportion 90-10, respectively.

training_files, testing_files = conveniences.split_database(input_file_path, output_folder_path)

# Call this convenience function to compute the mean and standard devitation
# of some database attributes. It will, also, plot the BTSs and measurement
# points on a OpenSteetMap tile.

conveniences.analyse_inputs(bts_file_path, training_files, output_folder_path)

# Localize the testing samples using the basic finferprinting algorithm.
'''
fingerprinting_okumura_results = (
    fingerprinting.estimate(
        bts_file_path,
        training_files,
        testing_files,
        output_folder_path,
        'OkumuraHata'
        )
    )

fingerprinting_cost231_results = (
    fingerprinting.estimate(
        bts_file_path,
        training_files,
        testing_files,
        output_folder_path,
        'COST231'
        )
    )

fingerprinting_ecc33_results = (
    fingerprinting.estimate(
        bts_file_path,
        training_files,
        testing_files,
        output_folder_path,
        'ECC33'
        )
    )
'''

knn_1_results = (
    knn.estimate(
        1,
        training_files,
        testing_files
        )
    )

knn_5_results = (
    knn.estimate(
        5,
        training_files,
        testing_files
        )
    )

regression_bayesian_results = (
    regression.estimate(
        'BayesianRidge',
        training_files,
        testing_files
        )
    )

regression_theil_results = (
    regression.estimate(
        'TheilSenRegressor',
        training_files,
        testing_files
        )
    )

# Pack the estimations in one list and generate the output artefacts in
# a single loop through the results. We generate the statistics files,
# results files, histograms, real-predicted coordinates maps and the boxplot.

boxplot_data = []
boxplot_file_name = output_folder_path + '/boxplot.png'
'''
results = [
    {
        'method': 'fingerprinting-OkumuraHata',
        'method_results': fingerprinting_okumura_results,
        'method_hist_title': u'Fingerprinting (Okumura Hata)'
    },
    {
        'method': 'fingerprinting-COST231',
        'method_results': fingerprinting_cost231_results,
        'method_hist_title': u'Fingerprinting (COST-231)'
    },
    {
        'method': 'fingerprinting-ECC33',
        'method_results': fingerprinting_ecc33_results,
        'method_hist_title': u'Fingerprinting (ECC-33)'
    },
    {
        'method': 'kNN-1',
        'method_results': knn_1_results,
        'method_hist_title': u'kNN (k=3)'
    },
    {
        'method': 'kNN-5',
        'method_results': knn_5_results,
        'method_hist_title': u'kNN (k=5)'
    }
]
'''

results = [
    {
        'method': 'kNN-1',
        'method_results': knn_1_results,
        'method_hist_title': u'kNN (k=1)'
    },
    {
        'method': 'kNN-5',
        'method_results': knn_5_results,
        'method_hist_title': u'kNN (k=5)'
    },
    {
        'method': 'Regression-BayesianRidge',
        'method_results': regression_bayesian_results,
        'method_hist_title': u'Regressão (BayesianRidge)'
    },
    {
        'method': 'Regression-TheilSenRegressor',
        'method_results': regression_theil_results,
        'method_hist_title': u'Regressão (TheilSenRegressor)'
    }
]

for result in results:

    method = result['method']
    method_results = result['method_results']
    method_hist_title = result['method_hist_title']

    statistics_file_name = '/'+method+'-statistics.txt'
    statistics_file_path = output_folder_path + statistics_file_name
    statistics_file = open(statistics_file_path, 'w+')

    for result in method_results:

        file_index = method_results.index(result)

        # Generate histogram.

        hist_file_name = '/' + method + '-hist-' + str(file_index) + '.png'
        hist_file_name = output_folder_path + hist_file_name

        data = [foo['error_mt'] for foo in result['data']]

        plt.figure()
        plt.grid(zorder=0)
        plt.hist(data, bins=50, zorder=3)
        plt.xlabel(u'Erro (metros)')
        plt.ylabel(u'Número de Itens')
        plt.title(method_hist_title)
        plt.savefig(hist_file_name, bbox_inches='tight')

        # Generate statistics.

        min = result['error_min']
        max = result['error_max']
        mean = result['error_mean']
        stddev = result['error_stddev']

        content = '\nTraining File ' + str(file_index) + ' Statistics:\n\n'
        content = content + 'Error Min: ' + str(min) + '\n'
        content = content + 'Error Max: ' + str(max) + '\n'
        content = content + 'Error mean: ' + str(mean) + '\n'
        content = content + 'Error Standard Deviation: ' + str(stddev) + '\n'
        content = content + '\n'

        statistics_file.write(content)

        # Generate real-prediction coordinates map.

        map_file_name = '/' + method + '-map-' + str(file_index) + '.png'
        map_file_path = output_folder_path + map_file_name

        lat_min, lon_min = result['coordinates_min']
        lat_max, lon_max = result['coordinates_max']

        zoomLevel = 15
        region = (lat_min, lon_min, lat_max, lon_max)
        smopyMap = smopy.Map(region, z=zoomLevel)
        matplotlibMap = smopyMap.show_mpl(figsize=(8, 8))

        for prediction in result['data']:

            real_lat, real_lon = prediction['real_coordinates']
            pred_lat, pred_lon = prediction['predicted_coordinates']

            x1, y1 = smopyMap.to_pixels(real_lat, real_lon)
            x2, y2 = smopyMap.to_pixels(pred_lat, pred_lon)

            matplotlibMap.plot(x1, y1, 'og', ms=5, mew=2, alpha=0.5)
            matplotlibMap.plot(x2, y2, 'or', ms=5, mew=2, alpha=0.5)

        plt.savefig(map_file_path)

        # Generate the 'results.csv' file.

        results_file_content = ''
        results_file_name = '/'+method+'-results-' + str(file_index) + '.csv'
        results_file_path = output_folder_path + results_file_name
        results_file = open(results_file_path, 'w+')

        for prediction in result['data']:

            pointId = prediction['point_id']
            real_lat, real_lon = prediction['real_coordinates']
            pred_lat, pred_lon = prediction['predicted_coordinates']
            error_mt = prediction['error_mt']

            results_file_content += pointId + ','
            results_file_content += str(real_lat) + ','
            results_file_content += str(real_lon) + ','
            results_file_content += str(pred_lat) + ','
            results_file_content += str(pred_lon) + ','
            results_file_content += str(error_mt)
            results_file_content += '\n'

        results_file.write('pontoId,lat,lon,lat_pred,lon_pred,erro_loc\n')
        results_file.write(results_file_content)
        results_file.close()

        # Pack the necessary data to generate the boxplot.

        boxplot_data.append([foo['error_mt'] for foo in result['data']])

    statistics_file.close()

plt.figure()
plt.boxplot(boxplot_data)
plt.xticks([1, 2, 3], ['FP OH', 'FP COST-231', 'FP ECC-33', 'kNN OH'])
plt.xlabel(u'Método')
plt.ylabel(u'Erro (metros)')
plt.title(u'Comparando Métodos')
plt.savefig(boxplot_file_name, bbox_inches='tight')
