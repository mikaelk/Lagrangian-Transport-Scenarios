import settings
import factories.scenario_factory as scenario_factory
import utils
from netCDF4 import Dataset
import visualization.visualization_utils as vUtils
import matplotlib.pyplot as plt
import numpy as np
import string
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from advection_scenarios import advection_files
from copy import deepcopy


def SizeTransport_CumulativeDistance(scenario, figure_direc, size_list, rho_list, figsize=(12, 8), fontsize=14):
    # Getting the size of the domain that we want to plot for
    advection_scenario = advection_files.AdvectionFiles(server=settings.SERVER, stokes=settings.STOKES,
                                                        advection_scenario='CMEMS_MEDITERRANEAN',
                                                        repeat_dt=None)
    adv_file_dict = advection_scenario.file_names

    # Setting the folder within which we have the output, and where we have the saved timeslices
    output_direc = figure_direc + 'mix/'
    data_direc = utils.get_output_directory(server=settings.SERVER) + 'statistics/{}/'.format('SizeTransport')
    utils.check_direc_exist(output_direc)

    # Loading in the data
    date = datetime(2012, 12, 31, 12, 0, 0).strftime("%Y-%m-%d-%H-%M-%S")
    prefix = 'timeslices_{}'.format(date)

    variable_list = ['z', 'distance_vertical', 'distance_horizontal']
    variable_domain = [np.arange(0, np.nanmax(adv_file_dict['DEPTH']), 1.0),
                       np.logspace(0, 4, num=100),
                       np.logspace(0, 4, num=100)]
    variable_dict = dict.fromkeys(variable_list, None)
    timeseries_dict = dict.fromkeys(size_list, deepcopy(variable_dict))
    for index_size, size in enumerate(size_list):
        data_dict = vUtils.SizeTransport_load_data(scenario=scenario, prefix=prefix, data_direc=data_direc,
                                                   size=size, rho=rho_list[index_size])
        for index_var, variable in enumerate(variable_list):
            var_data = data_dict[variable]
            timeseries_dict[size][variable] = np.zeros(shape=variable_domain[index_var].shape)
            for step in range(timeseries_dict[size][variable]):
                timeseries_dict[size][variable][step] += np.nansum(var_data < variable_domain[index_var][step])

    # Creating the figure structure
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(nrows=1, ncols=3)
    ax_list = []
    for column in range(gs.ncols):
        ax = fig.add_subplot(gs[0, column])
        if column == 0:
            ax.set_ylabel(r'Fraction of Total (%)', fontsize=fontsize)
        ax.tick_params(axis='both', labelsize=fontsize)
        ax.set_ylim([0, 105])
        ax_list.append(ax)
    # First, we will plot the max depth
    ax_list[0].set_xlabel('Max depth (m)', fontsize=fontsize)
    ax_list[1].set_xscale('log')
    ax_list[1].set_xlim([1e0, 1e3])
    # Next it will be the cumulative vertical distance
    ax_list[1].set_xlabel('Cumulative vertical distance (m)', fontsize=fontsize)
    ax_list[1].set_xscale('log')
    ax_list[1].set_xlim([1e0, 1e4])
    # Finally, the cumulative horizontal distance
    ax_list[2].set_xlabel('Cumulative horizontal distance (km)', fontsize=fontsize)
    ax_list[2].set_xscale('log')
    ax_list[2].set_xlim([1e0, 1e4])

    # Plotting the data
    for index_size, size in enumerate(size_list):
        for index_var, variable in enumerate(variable_list):
            ax_list[index_var].plot(variable_domain[index_var], timeseries_dict[size][variable], linestyle='-',
                                    color=vUtils.discrete_color_from_cmap(index_size, subdivisions=len(size_list)),
                                    label=size_label(size, index_var))

    # Saving the figure
    file_name = output_direc + 'Vertical_Horizontal_Distance_cumulative.png'
    plt.savefig(file_name, bbox_inches='tight')


def size_label(size, index):
    alphabet = string.ascii_lowercase
    return r'({}) r = {:.2f} mm'.format(alphabet[index], size * 1e3)