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
import math
import pandas as pd
import matplotlib
#matplotlib.use('agg') #remove need for -X server connect
import matplotlib.pyplot as plt
matplotlib.rcParams['font.sans-serif'] = 'Arial'

"""Compile images from a list of metrics files using start and stop keys"""
def compile_size_distribution(
    args_dict, path, file_list,
    line2find, line2stop,
    lab_x, lab_y,
    plot_type, experiment,
    plot_output, dpi=600):

    # Keep axes happy to avoid 'IndexError: too many indices for array' error
    # Auto formats figure summary size based on number of plots
    if (len(file_list) / 2) < 2:
        plot_rows = 2
        fig_size = (15, 16)
    else:
        plot_rows = ceil(len(file_list) / 2)
        fig_size = (15, (8 * (int(len(file_list) / 2))))

    # Set up figure space
    fig, axes = plt.subplots(nrows=plot_rows, ncols=2, figsize=fig_size)
    plt.subplots_adjust(bottom = 0.3)

    # Initialize file and axis counters for formatting summary figure
    file_number = 0
    ax_y = 0

    # Parse files for relevant data
    for file in file_list:
        with open(path + file, 'r') as f:
            x = 0
            df = pd.DataFrame(pd.DataFrame(columns=[lab_x,lab_y])) # Initialize dataframe for relevant data

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
        df.plot.line(x=lab_x, y=lab_y, title=file[:-4], ax=axes[ax_y, ax_x])
        file_number += 1
        del df

    # Save catenated figure
    plot_title = str(experiment) + '_' + str(plot_type) # Make figure title to save as from experiment name and plot type
    fig.savefig(str(plot_output) + plot_title + '_summary.pdf', dpi=dpi)
