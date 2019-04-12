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
import pandas as pd

"""Scan first exons recursively by chromosome position and truncate"""
def scan_forward(
    gtf,
    index,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    _5prime,
    _3prime,
    penalty=0):

    # Forward scan for first exon
    n = 0 + penalty
    item = gtf.at[index, 2]
    while item != str(search_string):

        n += 1
        if (index + n) <= (len(gtf.index) - 1): # Make sure next record won't run out of bounds
            item = gtf.at[index + n, 2]
        else:
            return gtf, bad_exons

        if item == str(stop_string): # Make sure didn't run into next transcript
            return gtf, bad_exons

        # Sanity check that we are at an exon record
        if gtf.at[index + n, 2] == str(search_string) \
        and str(annotation) in gtf.at[index + n, 8]:
            # Exon 1 will be first exon
            if gtf.at[index + n, 6] == '+':
                gtf, bad_exons = plus_5prime(
                                    gtf,
                                    index,
                                    n,
                                    _5prime,
                                    _3prime,
                                    bad_exons,
                                    search_string,
                                    stop_string,
                                    annotation,
                                    penalty)
                return gtf, bad_exons

            # Exon 1 will be last exon
            elif gtf.at[index + n, 6] == '-':
                gtf, bad_exons = minus_3prime(
                                    gtf,
                                    index,
                                    n,
                                    _5prime,
                                    _3prime,
                                    bad_exons,
                                    search_string,
                                    stop_string,
                                    annotation,
                                    penalty)
                return gtf, bad_exons

            # Exon 1 does not have a strandedness annotation
            else:
                raise Exception('Unstranded transcript record present')

"""Truncate 5' amount from the first listed positive stranded exon"""
def plus_5prime(
    gtf,
    index,
    counter,
    _5prime,
    _3prime,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    penalty):

    # Edit location and exit the recursive loop
    if gtf.at[index + counter, 3] + _5prime <= gtf.at[index + counter, 4]:
        gtf.at[index + counter, 3] = gtf.at[index + counter, 3] \
                                    + _5prime
        return gtf, bad_exons

    # Add current exon to list of exons too short and enter recursive loop
    else:
        bad_exons.append(index + counter) # Remove short exon from record
        remainder = _5prime \
                    - abs(gtf.at[index + counter, 4] - gtf.at[index + counter, 3]) # Take what's left over
        return scan_forward( # Recursive scan to next exon until no remainder
                gtf,
                index,
                bad_exons,
                search_string,
                stop_string,
                annotation,
                remainder,
                _3prime,
                penalty + 1)

"""Truncate 3' amount from the first listed minus stranded exon"""
def minus_3prime(
    gtf,
    index,
    counter,
    _5prime,
    _3prime,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    penalty):

    # Edit location and exit the recursive loop
    if gtf.at[index + counter, 3] + _3prime <= gtf.at[index + counter, 4]:
        gtf.at[index + counter, 3] = gtf.at[index + counter, 3] \
                                        + _3prime
        return gtf, bad_exons

    # Add current exon to list of exons too short and enter recursive loop
    else:
        bad_exons.append(index + counter) # Remove short exon from record
        remainder = _3prime \
                    - abs(gtf.at[index + counter, 4] - gtf.at[index + counter, 3]) # Take what's left over
        return scan_forward( # Recursive scan to next exon until no remainder
                gtf,
                index,
                bad_exons,
                search_string,
                stop_string,
                annotation,
                _5prime,
                remainder,
                penalty + 1)

"""Scan last exons recursively by chromosome position and truncate"""
def scan_backward(
    gtf,
    index,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    _5prime,
    _3prime,
    penalty=0):

    n = 0
    item = ''
    while item != str(stop_string):

        n += 1
        if (index + n) <= (len(gtf.index) - 1): # Make sure next selection not out of bounds
            item = gtf.at[index + n, 2]
        else:
            return gtf, bad_exons

        if item == str(stop_string) \
        or (index + n) == (len(gtf.index) - 1): # Check next selection
            # If next selection is last index and exon, modify coordinates
            y = 0
            item = gtf.at[index + n + y, 2]
            if (index + n) == (len(gtf.index) - 1) \
            and gtf.at[index + n + y, 2] == str(search_string) \
            and str(annotation) in gtf.at[index + n + y, 8]:
                # Exon 1 will be first exon
                if gtf.at[index + n + y, 6] == '+':
                    gtf, bad_exons = plus_3prime(
                                        gtf,
                                        index,
                                        n,
                                        y,
                                        _5prime,
                                        _3prime,
                                        bad_exons,
                                        search_string,
                                        stop_string,
                                        annotation,
                                        penalty)
                    return gtf, bad_exons
                # Exon 1 will be last exon
                elif gtf.at[index + n + y, 6] == '-':
                    gtf, bad_exons = minus_5prime(
                                        gtf,
                                        index,
                                        n,
                                        y,
                                        _5prime,
                                        _3prime,
                                        bad_exons,
                                        search_string,
                                        stop_string,
                                        annotation,
                                        penalty)
                    return gtf, bad_exons
                else:
                    raise Exception('Unstranded transcript record present')

            # Otherwise start tracking back to last exon for transcript
            else:
                y = 0 - penalty
                while item != str(search_string):
                    y -= 1
                    if (index + n + y) > 0: # Check that step back will be valid
                        item = gtf.at[index + n + y, 2]
                    else:
                        return gtf, bad_exons

                    if item == str(stop_string): # Make sure didn't run back into last transcript
                        return gtf, bad_exons

                    # Sanity check that we are at an exon record
                    if gtf.at[index + n + y, 2] == str(search_string) \
                    and str(annotation) in gtf.at[index + n + y, 8]:

                        # Exon last will be last exon
                        if gtf.at[index + n + y, 6] == '+':
                            gtf, bad_exons = plus_3prime(
                                                gtf,
                                                index,
                                                n,
                                                y,
                                                _5prime,
                                                _3prime,
                                                bad_exons,
                                                search_string,
                                                stop_string,
                                                annotation,
                                                penalty)
                            return gtf, bad_exons
                        # Exon last will be first exon
                        elif gtf.at[index + n + y, 6] == '-':
                            gtf, bad_exons = minus_5prime(
                                                gtf,
                                                index,
                                                n,
                                                y,
                                                _5prime,
                                                _3prime,
                                                bad_exons,
                                                search_string,
                                                stop_string,
                                                annotation,
                                                penalty)
                            return gtf, bad_exons
                        else:
                            raise Exception('Unstranded transcript record present')
                    else:
                        pass

"""Truncate 3' amount from the first listed positive stranded exon"""
def plus_3prime(
    gtf,
    index,
    counter,
    inner_counter,
    _5prime,
    _3prime,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    penalty):

    # Edit location and exit the recursive loop
    if gtf.at[index + counter + inner_counter, 4] - _3prime >= gtf.at[index + counter + inner_counter, 3]:
        gtf.at[index + counter + inner_counter, 4] = gtf.at[index + counter + inner_counter, 4] \
                                                    - _3prime
        return gtf, bad_exons

    # Add current exon to list of exons too short and enter recursive loop
    else:
        bad_exons.append(index + counter + inner_counter) # Remove short exon from record
        remainder = _3prime \
                    - abs(gtf.at[index + counter + inner_counter, 4] - gtf.at[index + counter + inner_counter, 3]) # Take what's left over
        return scan_backward( # Recursive scan to next exon until no remainder
                gtf,
                index + counter + inner_counter,
                bad_exons,
                search_string,
                stop_string,
                annotation,
                _5prime,
                remainder,
                penalty + 1)

"""Truncate 5' amount from the first listed minus stranded exon"""
def minus_5prime(
    gtf,
    index,
    counter,
    inner_counter,
    _5prime,
    _3prime,
    bad_exons,
    search_string,
    stop_string,
    annotation,
    penalty):

    # Edit location and exit the recursive loop
    if gtf.at[index + counter + inner_counter, 4] - _5prime >= gtf.at[index + counter + inner_counter, 3]:
        gtf.at[index + counter + inner_counter, 4] = gtf.at[index + counter + inner_counter, 4] \
                                                    - _5prime
        return gtf, bad_exons

    # Add current exon to list of exons too short and enter recursive loop
    else:
        bad_exons.append(index + counter + inner_counter) # Remove short exon from record
        remainder = _5prime \
                    - abs(gtf.at[index + counter + inner_counter, 4] - gtf.at[index + counter + inner_counter, 3]) # Take what's left over
        return scan_backward( # Recursive scan to next exon until no remainder
                gtf,
                index + counter + inner_counter,
                bad_exons,
                search_string,
                stop_string,
                annotation,
                remainder,
                _3prime,
                penalty + 1)

"""Run MAIN function for GTF truncation"""
def truncate_gtf(
    gtf,
    _5prime=45,
    _3prime=15):

    # Initialize
    gtf_c = gtf.copy() # Make copy in order to edit dataframe

    bad_exons = [] # Make list of indicies with bad exons (too short)

    for index, row in gtf.iterrows():

        # Find records for transcripts
        if row[2] == 'transcript':

            # Recursively scan forward in the transcript to truncate n nucleotides
            gtf_c, bad_exons = scan_forward(gtf_c, index, bad_exons, 'exon', 'transcript', 'exon_number \"', _5prime, _3prime)

            # Forward scan for next transcript, then backtrack to last exon record for transcript
            gtf_c, bad_exons = scan_backward(gtf_c, index, bad_exons, 'exon', 'transcript', 'exon_number \"', _5prime, _3prime)

    # Drop exons that are completely truncated
    print(str(len(bad_exons)) + ' exons records removed from reference chunk for being too short.')

    gtf_c = gtf_c.drop(gtf_c.index[bad_exons])

    return gtf_c