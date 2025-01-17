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
from __future__ import print_function

"""IMPORT DEPENDENCIES"""
import os
import sys

"""IMPORT INTERNAL DEPENDENCIES"""
from .utils import get_files, add_directory
from .parallel import parallelize

"""Convert sorted sam files in directory to bed files"""
def bed_convert(
        args):

    file, args_dict = args[0], args[1] # Parse args

    # Convert BAM to BED
    os.system(
        'bedtools bamtobed'
        + ' -i ' + str(args_dict['input']) + str(file).rsplit('.',1)[0] + '.bam'
        + ' > ' + str(args_dict['bed_files']) + str(file).rsplit('.',1)[0] + '.bed')

"""Run BED creation manager"""
def create_bed(
        args_dict):

    # Add output directories
    args_dict = add_directory(
        args_dict,
        'output',
        'bed_files')

    # Get list of files to convert based on acceptable file types
    files = get_files(
        args_dict['input'],
        ['.bam'])

    # Convert aligned RNAseq reads to BED files
    parallelize(
        bed_convert,
        files,
        args_dict)

    return args_dict
