import settings
import utils
from visualization.SizeTransport.SizeTransport_Animation import SizeTransport_Animation
from visualization.SizeTransport.SizeTransport_relative_concentrations import SizeTransport_relative_concentrations
from visualization.SizeTransport.SizeTransport_beach_timeseries import SizeTransport_beach_timeseries
from visualization.General import *
from visualization.SizeTransport.SizeTransport_CumulativeDistance import SizeTransport_CumulativeDistance
from visualization.SizeTransport.SizeTransport_SeparationDistance import SizeTransport_SeparationDistance
from visualization.SizeTransport.SizeTransport_VerticalProfile import SizeTransport_VerticalProfile
from visualization.SizeTransport.SizeTransport_lonlat_averages import SizeTransport_lonlat_averages
from visualization.SizeTransport.SizeTransport_reservoirs import SizeTransport_reservoirs
from visualization.SizeTransport.SizeTransport_rho_concentrations import SizeTransport_rho_concentrations
from visualization.SizeTransport.SizeTransport_full_concentrations import SizeTransport_full_concentrations
from visualization.SizeTransport.SizeTransport_MaxDistance import SizeTransport_MaxDistance
from visualization.SizeTransport.SizeTransport_concentration_subset import SizeTransport_concentration_subset
from visualization.SizeTransport.SizeTransport_concentration_OSM import SizeTransport_concentration_OSM
from visualization.SizeTransport.SizeTransport_vertical_OSM import SizeTransport_vertical_OSM
from visualization.SizeTransport.SizeTransport_concentration_seasons import SizeTransport_concentration_seasons
from visualization.SizeTransport.SizeTransport_peak_depth import SizeTransport_peak_depth
from visualization.SizeTransport.SizeTransport_vertical_time import SizeTransport_vertical_time
import Analysis
import os
import numpy as np


def run(scenario, figure_direc: str):
    """
    So, this is the function where I call all the functions for creating the figures. The figures that I don't want to
    run will just be commented out.
    :param scenario:
    :return:
    """
    size_list = np.array([5000, 2500, 1250, 625, 313, 156, 78, 39, 20, 10, 5, 2]) * settings.SIZE_FACTOR

    # Creating a figure of the basin bathymetry
    # General_bathymetry(scenario=scenario, figure_direc=figure_direc).plot()

    # Figure of the mean wind speed over the full simulation period
    # General_average_wind_speed(scenario=scenario, figure_direc=figure_direc).plot()

    # Figure of the input scenario
    # General_input_scenario(scenario=scenario, figure_direc=figure_direc).plot()

    # Figure of the seasonal average MLD and wind speed
    # General_season_average(scenario=scenario, figure_direc=figure_direc, variable='MLD').plot()
    # General_season_average(scenario=scenario, figure_direc=figure_direc, variable='wind').plot()

    # Figure of the distance to shore for each cell in the Mediterranean
    # General_distance2coast(scenario=scenario, figure_direc=figure_direc).plot()

    # Plotting the mean vertical profile of Tidal Kz
    # General_mean_tidal_Kz(scenario=scenario, figure_direc=figure_direc).plot()

    # Figure showing a histogram of all depth levels in the Mediterranean
    # for region in ['all', 'nearshore', 'offshore', 'coastal']:
    #     General_bathymetry_histogram(scenario=scenario, figure_direc=figure_direc, depth_selection=region).plot()

    # Creating an animation of the horizonal/vertical transport of particles for the particles specified within
    # size_list
    # SizeTransport_Animation(scenario=scenario, figure_direc=figure_direc, size_list=size_list,
    #                         simulation_years=3).animate()

    # Creating figures showing the relative distribution averaged for each simulation year
    # for time_select in [0, 1, 2]:
    #     for rho in [30, 920, 980, 1020]:
    #         SizeTransport_relative_concentrations(scenario=scenario, figure_direc=figure_direc, size_list=size_list,
    #                                               beach_state='adrift', time_selection=time_select, rho=rho).plot()
    #         SizeTransport_relative_concentrations(scenario=scenario, figure_direc=figure_direc, size_list=size_list,
    #                                               beach_state='beach', time_selection=time_select, rho=rho).plot()

    # Plotting the relative distributions for fixed particle sizes, but with different particle densities
    # for time_select in [0, 1, 2]:
    #     for size in np.array([78]) * settings.SIZE_FACTOR:
    #         for depth_level in ['surface_5m']:
    #             SizeTransport_rho_concentrations(scenario=scenario, figure_direc=figure_direc, size=size,
    #                                              beach_state='adrift', time_selection=time_select,
    #                                              rho_list=[30, 920, 980, 1020], depth_level=depth_level).plot()
    #             SizeTransport_concentration_seasons(scenario=scenario, figure_direc=figure_direc, size=size,
    #                                                 beach_state='adrift', time_selection=time_select,
    #                                                 depth_level=depth_level).plot()

    # Plotting all horizontal concentrations for a given density (so all 12 of them)
    # for rho in [920]:
    #     for time_select in [0, 2]:
    #         for depth_level in ['surface_1m', 'column']:
    #             SizeTransport_full_concentrations(scenario=scenario, figure_direc=figure_direc, beach_state='adrift',
    #                                               time_selection=time_select, rho=rho, depth_level=depth_level).plot()
    #             SizeTransport_full_concentrations(scenario=scenario, figure_direc=figure_direc, beach_state='adrift',
    #                                               time_selection=time_select, rho=rho, depth_level=depth_level,
    #                                               fixed_resus=True, resus_time=7).plot()
    #             SizeTransport_full_concentrations(scenario=scenario, figure_direc=figure_direc, beach_state='adrift',
    #                                               time_selection=time_select, rho=rho, depth_level=depth_level,
    #                                               fixed_resus=True, resus_time=50).plot()

    # For direct comparison between full column and 1m concentrations for a specific simulation year
    # for rho in [920, 980]:
    #     for time_select in [0]:
    #         for size_list in [np.array([5000, 2]) * settings.SIZE_FACTOR]:
    #             SizeTransport_concentration_subset(scenario=scenario, figure_direc=figure_direc,
    #                                                time_selection=time_select, rho=rho, size_list=size_list).plot()
    #             SizeTransport_concentration_subset(scenario=scenario, figure_direc=figure_direc,
    #                                                time_selection=time_select, rho=rho, size_list=size_list,
    #                                                fixed_resus=True, resus_time=7).plot()
    #             SizeTransport_concentration_subset(scenario=scenario, figure_direc=figure_direc,
    #                                                time_selection=time_select, rho=rho, size_list=size_list,
    #                                                fixed_resus=True, resus_time=50).plot()

    # Plot the maximum distance from shore for a given density, where subselection indicates if we want a plot with all
    # particle sizes or just 2 (the largest and smallest)
    # for rho in [920]:
    #     for subselection in [False]:
    #         SizeTransport_MaxDistance(scenario=scenario, figure_direc=figure_direc, rho=rho,
    #                                   subselection=subselection).plot()
    #         SizeTransport_MaxDistance(scenario=scenario, figure_direc=figure_direc, rho=rho, fixed_resus=True,
    #                                   resus_time=7, subselection=subselection).plot()
    #         SizeTransport_MaxDistance(scenario=scenario, figure_direc=figure_direc, rho=rho, fixed_resus=True,
    #                                   resus_time=50, subselection=subselection).plot()

    # Creating figures of the timeseries of the number of particles that are beached/adrift/seabed
    # SizeTransport_beach_timeseries(scenario=scenario, figure_direc=figure_direc, size_list=size_list,
    #                                simulation_years=3, rho_list=[30, 920, 980, 1020]).plot()

    # Figure showing the beached/adrift fractions of each size class
    # SizeTransport_reservoirs(scenario=scenario, figure_direc=figure_direc, resus_time=7).plot()
    # SizeTransport_reservoirs(scenario=scenario, figure_direc=figure_direc, resus_time=50).plot()
    # for rho in [30, 920, 980, 1020]:
    #     SizeTransport_reservoirs(scenario=scenario, figure_direc=figure_direc,
    #                              rho_list=[rho], resus_time=7).plot()
    #     SizeTransport_reservoirs(scenario=scenario, figure_direc=figure_direc,
    #                              rho_list=[rho], resus_time=50).plot()

    # Plotting the seasonal averaged vertical profiles
    # for rho in [[920, 980], [30, 1020]]:
    #     for shore in ['all', 'nearshore', 'offshore']:
    #         for time_selection in [0, 1, 2, 'all']:
    #             SizeTransport_VerticalProfile(scenario=scenario, figure_direc=figure_direc, size_list=size_list,
    #                                           time_selection=time_selection, rho_list=rho, shore=shore).plot()

    # Plotting the monthly average vertical profiles
    # size_list = np.array([5000, 2500, 1250, 625, 313, 156, 78, 39, 20, 10, 5, 2]) * settings.SIZE_FACTOR
    # for size in size_list:
    #     for time_selection in [0, 1, 2]:
    #         for shore in ['all', 'nearshore', 'offshore']:
    #             SizeTransport_vertical_time(scenario=scenario, figure_direc=figure_direc, size=size,
    #                                         time_selection=time_selection, shore=shore,
    #                                         rho_list=[30, 920, 980, 1020]).plot()

    # Figures for OSM 2022
    # for depth in ['column', 'surface_1m']:
    #     SizeTransport_concentration_OSM(scenario=scenario, figure_direc=figure_direc, depth=depth).plot()
    # for season in ['Winter', 'Summer']:
    #     for year in [0, 1, 2]:
    #         SizeTransport_vertical_OSM(scenario=scenario, figure_direc=figure_direc, time_selection=year,
    #                                    season=season).plot()

    # Calculate basic statistics
    # for size in np.array([5000, 2]) * settings.SIZE_FACTOR:
    #     for rho in [30, 920, 980, 1020]:
    #         base_statistic = Analysis.SizeTransport_Statistics(scenario=scenario, size=size, rho=rho)
    #         base_statistic.fraction_below_depth(reference_depth=10)
    #         base_statistic.fraction_per_reservoir()

    utils.print_statement("That is all folks!", to_print=True)
