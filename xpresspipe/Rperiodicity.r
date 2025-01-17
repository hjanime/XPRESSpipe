#!/usr/bin/env Rscript
license <- function() {
  "
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
  "
  }

# Measure library complexity of RNA-seq sample

# Install dependencies
if (!requireNamespace("BiocManager", quietly = TRUE)) {install.packages("BiocManager", repos = "http://cran.us.r-project.org")}

if ("devtools" %in% rownames(installed.packages()) == FALSE) {
  print("Installing devtools...")
  install.packages("devtools", repos = "http://cran.us.r-project.org")
} else {
  print("devtools package already installed")
}
library(devtools)

# note: conda-build may screw with this install, remove from conda environment to get this to work
if ("riboWaltz" %in% rownames(as.data.frame(installed.packages()[,c(1,3:4)]))) {
  print("riboWaltz package already installed")
} else {
  print("Installing riboWaltz...")
  install_github("LabTranslationalArchitectomics/riboWaltz", dependencies = TRUE)
}

library(riboWaltz)

# Get arguments
# args[1] = BAMtranscriptome directory
# args[2] = GTF reference file (full)
# args[3] = output directory for metrics
args = commandArgs(trailingOnly=TRUE)

# Set parameters
BAM_LIST <- args[1] # Directory containing
GTF <- args[2]
OUTPUT <- args[3] # Path and filename with .txt extension

# Get p-site offsets
#annotation_dt <- read.table(
#  INDEX,
#  header = TRUE,
#  sep = '\t')
#annotation_dt <- subset(annotation_dt, select = c('transcript','l_tr','l_utr5','l_cds','l_utr3'))

annotation_dt <- create_annotation(gtfpath=GTF)

reads_list <- bamtolist(bamfolder = BAM_LIST, annotation = annotation_dt)
p_sites <- psite(reads_list) # This will fail if the input files are too small and don't have good representation across genes
p_info <- psite_info(reads_list, p_sites)

# Get list of unique elements in 'sample' column in p_sites
# Generate tables for each sample
for (SAMPLE in as.list(unique(p_sites$sample))) {
  SAMPLE_NAME = vapply(strsplit(SAMPLE, "[.]"), `[`, 1, FUN.VALUE=character(1)) # Get sample name
  OUTPUT_NAME = paste(OUTPUT, SAMPLE_NAME, "_metrics.txt", sep="")
  meta_prof <- metaprofile_psite(p_info, annotation_dt, SAMPLE, cdsl = 75)
  write.table(as.data.frame(meta_prof$dt), file=OUTPUT_NAME, sep='\t', col.names=NA)
}
