#!/usr/bin/env Rscript

# Control batch effects for prep, chips, etc
if (!requireNamespace("BiocManager", quietly = TRUE)) {install.packages("BiocManager", repos = "http://cran.us.r-project.org")}

if ("DESeq2" %in% rownames(installed.packages()) == FALSE) {
  BiocManager::install("DESeq2", dependencies=TRUE)
} else {
  print("DESeq2 package already installed")
}

library(DESeq2)

# Get arguments
# args[1] = dataframe
# args[2] = sample info
# args[3] = output file name
# args[4] = DE equation
args = commandArgs(trailingOnly=TRUE)

# Set parameters
DATAFRAME <- args[1] # Directory containing
INFO <- args[2]
OUTPUT <- args[3] # Path and filename with .txt extension
EQUATION <- args[4]

# Import counts_data
count_table <- read.table(DATAFRAME, sep = '\t', header = TRUE, row.names = 1)

# Create conditions dataframe
sample_table <- read.table(text = readLines(INFO, warn = FALSE), header = TRUE, sep = '\t')
names(sample_table) <- tolower(names(sample_table))

# Run DESeq2 analysis on data
dds <- DESeqDataSetFromMatrix(
  countData = count_table,
  colData = sample_table,
  design = as.formula(paste('~', tolower(toString(EQUATION)))))
dds <- DESeq(dds)
res <- results(dds)
resOrdered <- res[order(res$padj),]

# Write output to new file
write.table(as.data.frame(resOrdered), file = OUTPUT, sep = '\t', col.names = T, row.names = T)