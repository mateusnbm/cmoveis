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

output_folder_name = '23-11-2018 01-23-51'#datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
output_folder_path = 'outputs/' + output_folder_name

# We create a new folder in each execution to store the program files.

#os.makedirs(output_folder_path)

# Below we split the database in a training set and testing set,
# random records and drawn respecting the proportion 90-10, respectively.

#training_files, testing_files = conveniences.split_database(input_file_path, output_folder_path)

training_files, testing_files = (
    [output_folder_path+'/training-0.csv'], [output_folder_path+'/testing-0.csv']
)

# Call this convenience function to compute the mean and standard devitation
# of some database attributes. It will, also, plot the BTSs and measurement
# points on a OpenSteetMap tile.

#conveniences.analyse_inputs(bts_file_path, training_files, output_folder_path)

# Localize the testing samples using the basic finferprinting algorithm.

fingerprinting_estimates = (
    fingerprinting.estimate(
        bts_file_path,
        training_files,
        testing_files,
        output_folder_path,
        'OkumuraHata'
        )
)

# Generate histograms.

for estimate in fingerprinting_estimates:

    file_index = fingerprinting_estimates.index(estimate)
    hist_file_name = '/fingerprinting-OkumuraHata-hist-'+str(file_index)+'.png'
    hist_file_name = output_folder_path + hist_file_name

    data = [foo['error_mt'] for foo in estimate['data']]

    plt.figure()
    plt.hist(data, bins=50)
    plt.xlabel(u'Erro Médio (m)')
    plt.ylabel(u'Número de Medidas')
    plt.title(u'Fingerprinting Básico (Okumura Hata)')
    plt.grid(True)
    plt.savefig(hist_file_name, bbox_inches='tight')

# ... (generate box plot)

# ... (generate final report, statistics)
