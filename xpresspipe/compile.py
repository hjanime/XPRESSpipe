"""
XPRESSpipe
An alignment and analysis pipeline for RNAseq data
alias: xpresspipe

Copyright (C) 2019  Jordan A. Berg
jordan <dot> berg <at> biochem <dot> utah <dot> edu

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""IMPORT DEPENDENCIES"""
import os
import sys
import pandas as pd
import numpy as np
from math import ceil
from scipy.stats import gaussian_kde
import matplotlib
#matplotlib.use('agg') #remove need for -X server connect
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = 'Arial'

"""IMPORT INTERNAL DEPENDENCIES"""
from .utils import add_directory

"""Compile images from a list of metrics files using start and stop keys"""
def compile_file_metrics(
        args_dict,
        path,
        file_list,
        line2find,
        line2stop,
        lab_x,
        lab_y,
        plot_type,
        experiment,
        plot_output,
        individual_output,
        dpi=600):

    # Keep axes happy to avoid 'IndexError: too many indices for array' error
    # Auto formats figure summary size based on number of plots
    if (len(file_list) / 2) < 2:
        plot_rows = 2
        fig_size = (15, 16)
    else:
        plot_rows = ceil(len(file_list) / 2)
        fig_size = (15, (8 * (int(len(file_list) / 2))))

    # Set up figure space
    fig, axes = plt.subplots(
        nrows = plot_rows,
        ncols = 2,
        figsize = fig_size,
        subplot_kw = {'facecolor':'none'})
    plt.subplots_adjust(
        bottom = 0.3)

    # Initialize file and axis counters for formatting summary figure
    file_number = 0
    ax_y = 0

    # Parse files for relevant data
    for file in file_list:
        x = 0
        df = pd.DataFrame(
            pd.DataFrame(
                columns = [lab_x,lab_y])) # Initialize dataframe for relevant data

        with open(path + file, 'r') as f:
            for line in f: # Find first line of dataframe
                if str(line2find) in line:
                    for line in f: # Now you are at the lines you want
                        if plot_type == 'fastqc' and line2stop in line: # Catch line to stop for fastqc plot
                            break

                        data = line.split("\t") # Start parsing in the line

                        if plot_type == 'periodicity' and data[0] == line2stop: # Catch line to stop for periodicity plot
                            break

                        if data[1].endswith('\n'): # Get rid of trailing new line in data
                            data[1] = data[1].strip()

                        if data[1] != 'nan': # Handle cases where data is 'nan'
                            df.loc[x] = [int(data[0]),float(data[1])]
                        else: # Read in the data
                            df.loc[x] = [int(data[0]),0]

                        if plot_type == 'metagene' and data[0] == '100': # Additional break point for fastqc summaries
                            break

                        x += 1

        # Prepare subplots
        if (file_number % 2) == 0:
            ax_x = 0
        else:
            ax_x = 1

        if file_number != 0:
            if (file_number % 2) == 0:
                ax_y += 1

        # Plot figure
        df.plot.line(
            x = lab_x,
            y = lab_y,
            title = file[:-4],
            ax = axes[ax_y, ax_x],
            grid = None)

        axes[ax_y, ax_x].axhline(
            0,
            xmin = 0.048,
            ls = '-',
            color = 'black')
        axes[ax_y, ax_x].axvline(
            0,
            ymin = 0.048,
            ls = '-',
            color = 'black')

        fig.savefig(
            str(individual_output) + str(file[:-16]) + '_' + str(plot_type) + '.pdf',
            dpi = dpi,
            bbox_inches = 'tight')

        file_number += 1
        del df

    # Save catenated figure
    plot_title = str(experiment) + '_' + str(plot_type) # Make figure title to save as from experiment name and plot type
    fig.savefig(
        str(plot_output) + plot_title + '_summary.pdf',
        dpi = dpi,
        bbox_inches = 'tight')

"""Compile images from a list of metrics matrices"""
def compile_matrix_metrics(
        args_dict,
        path,
        file_list,
        lab_x,
        lab_y,
        plot_type,
        experiment,
        plot_output,
        individual_output,
        dpi=600):

    # Keep axes happy to avoid 'IndexError: too many indices for array' error
    # Auto formats figure summary size based on number of plots
    if (len(file_list) / 2) < 2:
        plot_rows = 2
        fig_size = (15, 16)
    else:
        plot_rows = ceil(len(file_list) / 2)
        fig_size = (15, (8 * (int(len(file_list) / 2))))

    # Set up figure space
    fig, axes = plt.subplots(
        nrows = plot_rows,
        ncols = 2,
        figsize = fig_size,
        subplot_kw = {'facecolor':'none'})
    plt.subplots_adjust(
        bottom = 0.3)

    # Initialize file and axis counters for formatting summary figure
    file_number = 0
    ax_y = 0

    for file in file_list:
        x = 0
        df = pd.read_csv(
            str(path + file),
            sep = '\t') # Initialize dataframe for relevant data
        df = df.dropna(
            axis = 0,
            subset = [str(lab_x), str(lab_y)]) # Remove rows where pertinent information is missing

        # Prepare subplots
        if (file_number % 2) == 0:
            ax_x = 0
        else:
            ax_x = 1

        if file_number != 0:
            if (file_number % 2) == 0:
                ax_y += 1

        # Plot figure
        df.plot.line(
            x = lab_x,
            y = lab_y,
            title = file[:-4],
            ax = axes[ax_y, ax_x],
            grid = None)

        axes[ax_y, ax_x].axhline(
            0,
            xmin = 0.048,
            ls = '-',
            color = 'black')
        axes[ax_y, ax_x].axvline(
            0,
            ymin = 0.048,
            ls = '-',
            color = 'black')

        fig.savefig(
            str(individual_output) + str(file[:-4]) + '_' + str(plot_type) + '.pdf',
            dpi = dpi,
            bbox_inches = 'tight')

        file_number += 1
        del df

    # Save catenated figure
    plot_title = str(experiment) + '_' + str(plot_type) # Make figure title to save as from experiment name and plot type
    fig.savefig(
        str(plot_output) + plot_title + '_summary.pdf',
        dpi = dpi,
        bbox_inches = 'tight')

""""""
def compile_complexity_metrics(
        args_dict,
        path,
        file_list,
        column_x,
        column_y,
        plot_type,
        experiment,
        plot_output,
        individual_output,
        dpi=600):

    # Keep axes happy to avoid 'IndexError: too many indices for array' error
    # Auto formats figure summary size based on number of plots
    if (len(file_list) / 2) < 2:
        plot_rows = 2
        fig_size = (15, 16)
    else:
        plot_rows = ceil(len(file_list) / 2)
        fig_size = (15, (8 * (int(len(file_list) / 2))))

    # Set up figure space
    fig, axes = plt.subplots(
        nrows = plot_rows,
        ncols = 2,
        figsize = fig_size,
        subplot_kw = {'facecolor':'none'})
    plt.subplots_adjust(
        bottom = 0.3)

    # Initialize file and axis counters for formatting summary figure
    file_number = 0
    ax_y = 0

    for file in file_list:
        x = 0
        df = pd.read_csv(
            str(path + file),
            sep = '\t') # Initialize dataframe for relevant data
        df = df[[column_x, column_y]]
        df = df.dropna(axis = 0) # Remove rows where pertinent information is missing
        df[column_x] = np.log10(df[column_x] + 1)
        df[column_y] = df[column_y] * 100

        # Prepare subplots
        if (file_number % 2) == 0:
            ax_x = 0
        else:
            ax_x = 1

        if file_number != 0:
            if (file_number % 2) == 0:
                ax_y += 1

        # Calculate the point density (adapted from: Joe Kington, https://stackoverflow.com/a/20107592/9571488)
        x = df[str(column_x)].values
        y = df[str(column_y)].values

        xy = np.vstack([x,y])
        z = gaussian_kde(xy)(xy)

        idx = z.argsort() # Sort points by density
        x, y, z = x[idx], y[idx], z[idx]

        axes[ax_y, ax_x].axhline(
            -2,
            xmin = 0.048,
            ls = '-',
            color = 'black')
        axes[ax_y, ax_x].axvline(
            0,
            ymin = 0.060,
            ls = '-',
            color = 'black')
        axes[ax_y, ax_x].scatter(
            x,
            y,
            c = z,
            s = 3,
            alpha = 0.7)

        axes[ax_y, ax_x].set_xlabel('log$_1$$_0$expression (reads/kb)')
        axes[ax_y, ax_x].set_ylabel('% duplicate reads')
        axes[ax_y, ax_x].set_title(str(file[:-4]))
        axes[ax_y, ax_x].grid(False)

        # Output individual plot
        fig.savefig(
            str(individual_output) + str(file[:-4]) + '_' + str(plot_type) + '.pdf',
            dpi = dpi,
            bbox_inches = 'tight')

        file_number += 1
        del df

    # Save catenated figure
    plot_title = str(experiment) + '_' + str(plot_type) # Make figure title to save as from experiment name and plot type
    fig.savefig(
        str(plot_output) + plot_title + '_summary.pdf',
        dpi = dpi,
        bbox_inches = 'tight')
