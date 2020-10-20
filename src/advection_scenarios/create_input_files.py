import settings
import utils

import numpy as np
import glob
import os
import xarray
from netCDF4 import Dataset
import pandas as pd
import geopy.distance
from datetime import datetime, timedelta
import fiona
from collections import Iterable
from matplotlib import colors
import cartopy.crs as ccrs
import cartopy.feature as cpf
from copy import deepcopy
from progressbar import ProgressBar
import math


def create_input_files(prefix: str, grid: np.array, lon: np.array, lat: np.array):
    # Create the output prefix and then check if any files with such prefixes exist
    if settings.INPUT in ['Jambeck', 'Lebreton']:
        output_prefix = settings.INPUT_DIREC + settings.INPUT + '_' + prefix + '_2010_'
    else:
        os.system('echo "Perhaps take another look at what input you are using?"')

    # Check existence
    if len(glob.glob(output_prefix + '*')) > 0:
        os.system('echo "The input files {} are already present"'.format(output_prefix))
    else:
        os.system('echo "We need to create the input files {}"'.format(output_prefix))
        if settings.INPUT == 'Jambeck':
            # Get the population data
            dataset = Dataset(settings.INPUT_DIREC + 'gpw_v4_population_count_adjusted_rev11_2pt5_min.nc')
            population = np.array(dataset.variables[
                                      'UN WPP-Adjusted Population Count, v4.11 (2000, 2005, 2010, 2015, 2020): 2.5 arc-minutes'][
                                  2, :, :])
            lon_population = dataset.variables['longitude'][:]
            lat_population = dataset.variables['latitude'][:]
            # Get the mismanaged plastic fraction
            mismanaged = get_mismanaged_fraction_Jambeck(grid=grid, lon=lon, lat=lat, prefix=prefix)
            # Get the distance from land to shore
        elif settings.INPUT == 'Lebreton':
            lebData = pd.read_csv(settings.INPUT_DIREC + 'PlasticRiverInputs.csv')
            lon_inputs, lat_inputs = np.array(lebData['X']), np.array(lebData['Y'])
            plastic_inputs = np.array(lebData['i_low'])
        # Only keep the particles that are within the domain
        lon_inputs, lat_inputs, plastic_inputs = within_domain(lon=lon, lat=lat, lon_inputs=lon_inputs,
                                                               lat_inputs=lat_inputs, plastic_inputs=plastic_inputs)
        # Get the inputs onto the grid of the advection data
        inputs_grid = utils.histogram(lon_data=lon_inputs, lat_data=lat_inputs, bins_Lon=lon, bins_Lat=lat,
                                      weight_data=plastic_inputs, area_correc=False)
        # Get the ocean cells adjacent to coastal ocean cells, as these are the ones in which the particles will
        # be placed. For brevity, we will refer to these cells as coastal in the code here
        coastal = get_coastal_extended(grid=grid, coastal=get_coastal_cells(grid=grid))
        # Getting the inputs onto the coastal cells
        inputs_coastal_grid = input_to_nearest_coastal(coastal=coastal, inputs_grid=inputs_grid, lon=lon, lat=lat)
        # The inputs so far are annual, how many particle releases will occur per year
        releases = math.floor(timedelta(days=365) / settings.REPEAT_DT_R0) + 1
        inputs_coastal_grid /= releases
        # How many particles will be released per cell, and what are the assigned weights
        particle_number, particle_weight, particle_remain_num, particle_remain = number_weights_releases(
            input_grid=inputs_coastal_grid)
        # Get arrays of all particles release points and associated weights
        particle_lat, particle_lon, particle_weight = particle_grid_to_list(particle_number=particle_number,
                                                                            particle_weight=particle_weight,
                                                                            particle_remain_num=particle_remain_num,
                                                                            particle_remain=particle_remain,
                                                                            lon=lon, lat=lat)
        # How much of the plastic is being accounted for
        missing_percent = np.divide(np.sum(inputs_coastal_grid) - np.sum(particle_weight),
                                    np.sum(inputs_coastal_grid)) * 100
        os.system('echo "The particles account for {}% of the total inputs"'.format(100 - missing_percent))
        os.system('echo "We release {} particles per release step, so {} per year"'.format(len(particle_lat),
                                                                                           len(particle_lat)*releases))


def get_mismanaged_fraction_Jambeck(grid: np.array, lon: np.array, lat: np.array, prefix: str):
    mismanaged_file = settings.INPUT_DIREC + 'Jambeck_mismanaged_fraction_2010.nc'
    if utils._check_file_exist(mismanaged_file):
        dataset = Dataset(mismanaged_file)
        return dataset.variables['mismanaged fraction'][:]
    else:
        os.system('echo "I can not find the original code that was used to generate this so I will fill this in '
                  'later..."')


def within_domain(lon: np.array, lat: np.array, lon_inputs: np.array, lat_inputs: np.array, plastic_inputs: np.array):
    lon_max, lon_min = np.max(lon), np.min(lon)
    lat_max, lat_min = np.max(lat), np.min(lon)
    # Check which cells are within the domain
    domain = (lon_inputs <= lon_max) & (lon_inputs >= lon_min) & (lat_inputs >= lat_min) & (lat_inputs <= lat_max)
    os.system('echo "Of the original {} particles in the {} scenario, {} are within the domain"'.format(len(lon_inputs),
                                                                                                        settings.INPUT,
                                                                                                        np.sum(
                                                                                                            domain * 1)))
    return lon_inputs[domain], lat_inputs[domain], plastic_inputs[domain]


def get_coastal_cells(grid: np.array):
    mask = grid.mask
    coastal = np.zeros(mask.shape, dtype=bool)
    for lat_index in range(mask.shape[0]):
        for lon_index in range(mask.shape[1]):
            if not mask[lat_index, lon_index]:
                for lat_step in [-1, 0, 1]:
                    for lon_step in [-1, 0, 1]:
                        if mask[(lat_index + lat_step) % mask.shape[0], (lon_index + lon_step) % mask.shape[1]]:
                            coastal[lat_index, lon_index] = True
    return coastal


def get_coastal_extended(grid: np.array, coastal: np.array):
    mask = grid.mask
    # We want the next layer of ocean cells after the coastal cells
    coastal_extended = np.zeros(mask.shape, dtype=bool)
    for lat_index in range(mask.shape[0]):
        for lon_index in range(mask.shape[1]):
            if not mask[lat_index, lon_index] and coastal[lat_index, lon_index]:
                for lat_step in [-1, 0, 1]:
                    for lon_step in [-1, 0, 1]:
                        if coastal[(lat_index + lat_step) % mask.shape[0], (lon_index + lon_step) % mask.shape[1]]:
                            coastal_extended[lat_index, lon_index] = True
    return coastal_extended


def input_to_nearest_coastal(coastal: np.array, inputs_grid: np.array, lon: np.array, lat: np.array):
    # Find the positions with non-zero inputs
    non_zero_inputs = np.where(inputs_grid > 0)
    inputs_coastal_grid = np.zeros(coastal.shape)
    # Looping through the non-zero points to find the nearest one with
    for point in range(len(non_zero_inputs[0])):
        lat_point, lon_point = non_zero_inputs[0][point], non_zero_inputs[1][point]
        # If the input is already in the coastal cell
        if coastal[lat_point, lon_point]:
            inputs_coastal_grid[lat_point, lon_point] += inputs_grid[lat_point, lon_point]
        # Else find the nearest coastal cell
        else:
            step = 1
            coastal_lon, coastal_lat, coastal_distance = [], [], []
            while len(coastal_lon) < 1:
                for lat_step in [-step, step]:
                    for lon_step in range(-step, step + 1):
                        if coastal[(lat_point + lat_step) % coastal.shape[0], (lon_point + lon_step) % coastal.shape[1]]:
                            coastal_lat.append((lat_point + lat_step) % coastal.shape[0])
                            coastal_lon.append((lon_point + lon_step) % coastal.shape[1])
                step += 1
        # Now find the coastal cell that is geographically the closest to the input
        nearest_dist = geopy.distance.distance((lat[lat_point], lon[lon_point]),
                                               (lat[coastal_lat[0]], lon[coastal_lon[0]]))
        nearest_lat, nearest_lon = coastal_lat[0], coastal_lon[0]
        if len(coastal_lon) > 0:
            for candidate in range(len(coastal_lon)):
                distance = geopy.distance.distance((lat[lat_point], lon[lon_point]),
                                                   (lat[coastal_lat[candidate]], lon[coastal_lon[candidate]]))
                if distance < nearest_dist:
                    nearest_dist = distance
                    nearest_lat, nearest_lon = coastal_lat[candidate], coastal_lon[candidate]
        inputs_coastal_grid[nearest_lat, nearest_lon] += inputs_grid[lat_point, lon_point]
    return inputs_coastal_grid


def number_weights_releases(input_grid: np.array):
    particle_number = np.zeros(input_grid.shape)
    particle_weight = np.zeros(input_grid.shape)
    particle_remain = np.zeros(input_grid.shape)
    particle_remain_num = np.zeros(input_grid.shape)
    # First all the inputs lower than the cutoff and greater than minimum
    selection = (input_grid < settings.INPUT_MAX) & (input_grid >= settings.INPUT_MIN)
    particle_number[selection] += 1
    particle_weight[selection] += input_grid[selection]
    # Next we consider the cells where we have inputs greater than the cutoff
    selection = input_grid >= settings.INPUT_MAX
    particle_number[selection] += np.floor(input_grid[selection] / settings.INPUT_MAX)
    particle_weight[selection] += settings.INPUT_MAX
    # Finally, we have the remainder for when inputs are not multiples of the cutoff, and so we have a remainder
    selection = (np.multiply(particle_number, particle_weight) - input_grid) > settings.INPUT_MIN
    particle_remain_num[selection] += 1
    particle_remain[selection] += (np.multiply(particle_number, particle_weight)[selection] - input_grid[selection])
    return particle_number.astype('int'), particle_weight, particle_remain_num.astype('int'), particle_remain


def particle_grid_to_list(particle_number: np.array, particle_weight: np.array, particle_remain_num: np.array,
                          particle_remain: np.array, lon: np.array, lat: np.array):
    particle_lat, particle_lon, particle_mass = [], [], []
    for lat_index in range(particle_number.shape[0]):
        for lon_index in range(particle_number.shape[1]):
            if particle_number[lat_index, lon_index] > 0:
                for reps in range(particle_number[lat_index, lon_index]):
                    particle_lat.append(lat[lat_index])
                    particle_lon.append(lon[lon_index])
                    particle_mass.append(particle_weight[lat_index, lon_index])
            if particle_remain_num[lat_index, lon_index] > 0:
                for reps in range(particle_remain_num[lat_index, lon_index]):
                    particle_lat.append(lat[lat_index])
                    particle_lon.append(lon[lon_index])
                    particle_mass.append(particle_remain[lat_index, lon_index])
    return np.array(particle_lat), np.array(particle_lon), np.array(particle_mass)
