import settings
import utils
import visualization.visualization_utils as vUtils
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import string
import numpy as np


class FragmentationKaandorpPartial_boxmodelcomparison:
    def __init__(self, figure_direc, scenario, shore_time, lambda_frag, rho, sink=True):
        # Data parameters
        self.output_direc = figure_direc + 'size_distribution/'
        self.data_direc = utils.get_output_directory(server=settings.SERVER) + 'size_distribution/FragmentationKaandorpPartial/'
        utils.check_direc_exist(self.output_direc)
        self.prefix = 'size_distribution'
        self.beach_state_list = ['adrift', 'beach']
        # Simulation parameters
        self.scenario = scenario
        self.shore_time = shore_time
        self.lambda_frag = lambda_frag
        self.rho = rho
        self.class_num = settings.SIZE_CLASS_NUMBER
        self.sink = sink
        if self.sink:
            self.count, self.mass = 'particle_number', 'particle_mass'
        else:
            self.count, self.mass = 'particle_number_sink', 'particle_mass_sink'
        # Figure parameters
        self.fig_size = (14, 14)
        self.fig_shape = (1, 2)
        self.x_label = 'Size (mm)'
        self.y_label = r'Particle Number (n)'
        self.twiny_label = r'Particle Mass (g)'
        self.ax_ticklabel_size = 12
        self.ax_label_size = 14
        self.legend_size = 12
        self.xmin, self.xmax = 1e-3, 2e2
        self.ymin, self.ymax = 1e-3, 1e8
        self.ax_range = self.xmax, self.xmin, self.ymax, self.ymin
        self.twin_ymin, self.twin_ymax = 1e-3, 1e8
        self.twin_ax_range = self.xmax, self.xmin, self.twin_ymax, self.twin_ymin
        self.number_of_plots = self.fig_shape[0] * self.fig_shape[1]

    def plot(self):
        # Getting the sizes of the size classes, and we convert from meters to mm
        size_classes = utils.size_range(size_class_number=self.class_num, units='mm')

        # Loading the data
        data_dict = {}
        data = vUtils.FragmentationKaandorpPartial_load_data(scenario=self.scenario, prefix=self.prefix,
                                                             data_direc=self.data_direc, shore_time=self.shore_time,
                                                             lambda_frag=self.lambda_frag, rho=self.rho,
                                                             postprocess=True)
        data_dict[self.count] = data[self.beach_state_list[0]][self.count] + data[self.beach_state_list[1]][self.count]
        data_dict[self.mass] = data[self.beach_state_list[0]][self.mass] + data[self.beach_state_list[1]][self.mass]
        time_indices = data[self.mass].keys()

        # Creating the figure
        ax, twin_ax = vUtils.base_figure(fig_size=self.fig_size, ax_range=self.ax_range, x_label=self.x_label,
                                         y_label=self.y_label, ax_ticklabel_size=self.ax_ticklabel_size,
                                         ax_label_size=self.ax_label_size, shape=self.fig_shape,
                                         plot_num=self.number_of_plots, log_yscale=True, log_xscale=True,
                                         all_x_labels=True, all_y_labels=True, add_twinx=True,
                                         twinx_y_label=self.twiny_label, twinx_ax_range=self.twin_ax_range,
                                         log_twinxscale=True)

        # Labelling the subfigures
        for index_ax in range(self.number_of_plots):
            ax[index_ax].set_title(subfigure_title(index_ax),
                                   fontsize=self.ax_label_size)

        # Saving the figure
        str_format = self.shore_time, self.rho, self.lambda_frag
        file_name = self.output_direc + 'boxmodel_comparison-ST={}-rho={}-lambda_f={}.png'.format(*str_format)
        plt.savefig(file_name, bbox_inches='tight')


def subfigure_title(index, beach_state):
    alphabet = string.ascii_lowercase
    subtitle_list = ['Counts', 'Mass']
    return '({}) {}'.format(alphabet[index], subtitle_list[beach_state])



