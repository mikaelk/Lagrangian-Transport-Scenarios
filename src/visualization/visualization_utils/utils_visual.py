import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cpf
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

import utils


def SizeTransport_linestyle_SEABED_CRIT(tau):
    """
    Returning the linestyle for line-based figures depending on the
    :param tau:
    :return:
    """
    return {0.14: '--', 0.025: '-'}[tau]


def cartopy_standard_map(fig, gridspec, row, column, domain, resolution='50m', add_gridlines=True, add_gridlabels=True,
                         lat_grid_step=20, lon_grid_step=30, label_size=14, land_zorder=1, ocean_zorder=1,
                         line_zorder=101):
    """
    A nice basic function that can be used to create standardized maps
    :param fig:
    :param gridspec:
    :param row:
    :param column:
    :param domain:
    :param resolution:
    :param add_gridlines:
    :param add_gridlabels:
    :param lat_grid_step:
    :param lon_grid_step:
    :param label_size:
    :param land_zorder:
    :param ocean_zorder:
    :param line_zorder:
    :return:
    """
    axis = fig.add_subplot(gridspec[row, column], projection=ccrs.PlateCarree())
    # Setting the domain of the map
    lon_min, lon_max, lat_min, lat_max = domain
    axis.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # Adding coastlines, borders, land and ocean shapefiles
    axis.coastlines(resolution=resolution)
    axis.add_feature(cpf.BORDERS.with_scale(resolution), edgecolor='black', zorder=line_zorder)
    axis.add_feature(cpf.LAND.with_scale(resolution), facecolor='lightgray', zorder=land_zorder)
    axis.add_feature(cpf.OCEAN.with_scale(resolution), facecolor='white', zorder=ocean_zorder)

    # Adding gridlines and axis labels
    if add_gridlines:
        grid = axis.gridlines(crs=ccrs.PlateCarree(),  # specify the projection being used
                              draw_labels=add_gridlabels,  # Add labels
                              linestyle='-',  # style
                              color='black',
                              zorder=line_zorder
                              )
        # Here we can choose along which axes we want to have the labels included
        grid.top_labels = False
        grid.right_labels = False
        if column == 0:
            grid.left_labels = True
        else:
            grid.left_labels = False
        if row == (gridspec.nrows - 1):
            grid.bottom_labels = True
        else:
            grid.bottom_labels = False
        # Formatting of the labels, since that they include N/S or E/W
        grid.xformatter = LONGITUDE_FORMATTER
        grid.yformatter = LATITUDE_FORMATTER

        # Determine where we want labels
        grid.xlocator = mticker.FixedLocator(np.arange(int(lon_min), int(lon_max) + lon_grid_step, lon_grid_step))
        grid.ylocator = mticker.FixedLocator(np.arange(int(lat_min), int(lat_max) + lat_grid_step, lat_grid_step))
        # Here we can change the appearances of the labels
        grid.xlabel_style = {'size': label_size, 'color': 'black', 'weight': 'normal'}
        grid.ylabel_style = {'size': label_size, 'color': 'black', 'weight': 'normal'}

    # Setting the axis
    axis.set_aspect('auto', adjustable=None)
    return axis


def discrete_color_from_cmap(index, subdivisions, cmap='viridis_r'):
    cmap_steps = plt.cm.get_cmap(cmap, subdivisions)
    return cmap_steps(index)


def base_figure(fig_size, ax_range, y_label, x_label, ax_label_size, ax_ticklabel_size,
                shape=(1, 1), plot_num=1, all_x_labels=False, legend_axis=False, log_yscale=False, log_xscale=False,
                x_time_axis=False, width_ratios=None, height_ratios=None):
    """
    Function creating the base figure that we use as a foundation for almost all figures
    :param log_yscale: if True, the y axis has a log scale
    :param log_xscale: if True, the x axis has a log scale
    :param x_time_axis: if True, the x axis is a time axis
    :param height_ratios:
    :param width_ratios:
    :param fig_size: size of the figure
    :param ax_range: the limits of the x and y axes
    :param y_label: the y label
    :param x_label: the x label
    :param ax_label_size: the fontsize of the axis labels
    :param shape: the shape of the array (rows, columns)
    :param plot_num: how many subplots we want to create (e.g. in case we have a 2x3 figure but only want 5 panels)
    :param all_x_labels: if True, all subplots in the bottom row of teh figure will have x labels, otherwise just the
                         middle one
    :param legend_axis: if true, we add an additional column in which we can add the legend (in case it is too big to
                        fit within a subplot)
    :return:
    """
    # Loading the axis limits
    xmax, xmin, ymax, ymin = ax_range
    utils.print_statement('{} {}'.format(xmax, xmin), to_print=True)
    if log_xscale:
        assert xmax > 0 and xmin > 0, "Must have positive x limits for log scales"
    if log_yscale:
        assert ymax > 0 and ymin > 0, "Must have positive y limits for log scales"
    # Creating the figure
    fig = plt.figure(figsize=fig_size)
    if legend_axis:
        grid = GridSpec(nrows=shape[0], ncols=shape[1] + 1, figure=fig, width_ratios=width_ratios,
                        height_ratios=height_ratios)
    else:
        grid = GridSpec(nrows=shape[0], ncols=shape[1], figure=fig, width_ratios=width_ratios,
                        height_ratios=height_ratios)
    ax, fig_index = [], 1
    for row in range(shape[0]):
        for column in range(shape[1]):
            ax_sub = fig.add_subplot(grid[row, column])
            # Setting the axis limits
            ax_sub.set_ylim((ymin, ymax))
            ax_sub.set_xlim((xmin, xmax))
            # Setting the tick parameters and setting the axis scale
            ax_sub.tick_params(axis='both', labelsize=ax_ticklabel_size)
            if log_xscale:
                ax_sub.set_xscale('log')
            if log_yscale:
                ax_sub.set_yscale('log')
            if x_time_axis:
                years = mdates.YearLocator()
                months = mdates.MonthLocator()
                yearsFmt = mdates.DateFormatter('%Y')
                ax_sub.xaxis.set_major_locator(years)
                ax_sub.xaxis.set_minor_locator(months)
                ax_sub.xaxis.set_major_formatter(yearsFmt)
            # Labeling the x and y axes
            # Only add y labels if we are in the first column
            if column == 0:
                ax_sub.set_ylabel(y_label, fontsize=ax_label_size)
            else:
                ax_sub.tick_params(labelleft=False)
            # Only add x labels if we are in the bottom row, and only to the middle one unless all_x_labels == True
            if row == (shape[0] - 1):
                if not all_x_labels and column % 2 is 1:
                    ax_sub.set_xlabel(x_label, fontsize=ax_label_size)
                elif all_x_labels:
                    ax_sub.set_xlabel(x_label, fontsize=ax_label_size)
                else:
                    ax_sub.tick_params(labelbottom=False)
            else:
                ax_sub.tick_params(labelbottom=False)
            # Adding the axis to the list and continuiing to the next plot
            ax.append(ax_sub)
            fig_index += 1
            if fig_index > plot_num:
                break
    if legend_axis:
        # Adding a legend axis
        ax_legend = fig.add_subplot(grid[:, -1])
        ax_legend.set_axis_off()
        ax.append(ax_legend)
    return tuple(ax)

