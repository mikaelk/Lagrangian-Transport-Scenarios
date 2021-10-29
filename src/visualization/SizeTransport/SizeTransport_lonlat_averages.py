import settings
import utils
import visualization.visualization_utils as vUtils
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from advection_scenarios import advection_files
import numpy as np
import string
import cmocean.cm as cmo


class SizeTransport_lonlat_averages:
    def __init__(self, scenario, figure_direc, size_list, time_selection, rho=920, tau=0):
        # Simulation parameters
        self.scenario = scenario
        self.rho = rho
        self.time_selection = time_selection
        self.size_list = size_list
        self.tau = tau
        self.beach_state_list = ['beach', 'adrift']
        self.dimension_list = ["lon_counts", "lat_counts"]
        # Data parameters
        self.output_direc = figure_direc + 'concentrations/'
        self.data_direc = utils.get_output_directory(server=settings.SERVER) + 'concentrations/SizeTransport/'
        utils.check_direc_exist(self.output_direc)
        self.prefix = 'lonlat_concentration'
        # Figure parameters
        self.figure_size = (20, 10)
        self.figure_shape = (2, 2)
        self.ax_label_size = 14
        self.ax_ticklabel_size = 14
        self.number_of_plots = self.size_list.__len__()
        self.adv_file_dict = advection_files.AdvectionFiles(server=settings.SERVER, stokes=settings.STOKES,
                                                            advection_scenario='CMEMS_MEDITERRANEAN',
                                                            repeat_dt=None).file_names
        self.spatial_domain = np.nanmin(self.adv_file_dict['LON']), np.nanmax(self.adv_file_dict['LON']), \
                              np.nanmin(self.adv_file_dict['LAT']), np.nanmax(self.adv_file_dict['LAT'])
        self.cmap = 'viridis_r'

    def plot(self):
        # Loading the data
        concentration_dict = {}
        key_concentration = utils.analysis_simulation_year_key(self.time_selection)
        for index, size in enumerate(self.size_list):
            data_dict = vUtils.SizeTransport_load_data(scenario=self.scenario, prefix=self.prefix,
                                                       data_direc=self.data_direc,
                                                       size=size, rho=self.rho, tau=self.tau)
            concentration_dict[index] = data_dict[key_concentration]
        lon, lat = data_dict['lon'], data_dict['lat']

        # Normalizing the concentrations by the total number of particles in the simulation
        for size in concentration_dict.keys():
            for beach_state in self.beach_state_list:
                for lonlat in self.dimension_list:
                    concentration_dict[size][beach_state][lonlat] /= np.nansum(
                        concentration_dict[size][beach_state][lonlat])

        # Setting zero values to NAN
        for size in concentration_dict.keys():
            for beach_state in self.beach_state_list:
                for lonlat in self.dimension_list:
                    zero = concentration_dict[size][beach_state][lonlat] == 0
                    concentration_dict[size][beach_state][lonlat][zero] = np.nan

        # Creating the base figure
        fig = plt.figure(figsize=self.figure_size)
        gs = fig.add_gridspec(nrows=self.figure_shape[0], ncols=self.figure_shape[1], width_ratios=[1, 0.5],
                              height_ratios=[1, 0.5])

        ax_map = vUtils.cartopy_standard_map(fig=fig, gridspec=gs, row=0, column=0, add_gridlabels=False,
                                             domain=self.spatial_domain, label_size=self.ax_label_size,
                                             lat_grid_step=5, lon_grid_step=10, resolution='10m', land_color='grey',
                                             border_color='white')
        # Creating the axis for the longitudes
        ax_lon = fig.add_subplot(gs[1, 0])
        ax_lon.set_ylim((0, 1))
        ax_lon.set_xlim((self.spatial_domain[0], self.spatial_domain[1]))
        # Creating the axis for the latitudes
        ax_lat = fig.add_subplot(gs[0, 1])
        ax_lat.set_ylim((self.spatial_domain[2], self.spatial_domain[3]))
        ax_lat.set_xlim((0, 1))

        # Saving the figure
        str_format = self.time_selection, self.rho
        fig_name = self.output_direc + "lon_lat_year={}__rho={}.png".format(*str_format)
        plt.savefig(fig_name, bbox_inches='tight')


