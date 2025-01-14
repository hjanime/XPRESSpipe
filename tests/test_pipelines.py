import os
import sys
import pandas as pd
import scipy.stats as stats

__path__  =  os.path.dirname(os.path.realpath(__file__)) + '/'
#__path__ = '/Users/jordan/scripts/XPRESSyourself/XPRESSpipe/tests/'

# Get source files
def get_source(path):

    os.system(
        'curl ftp://ftp.ensembl.org/pub/release-96/gtf/homo_sapiens/Homo_sapiens.GRCh38.96.gtf.gz -o ' + str(path) + 'transcripts_all.gtf.gz')
    os.system(
        'curl ftp://ftp.ensembl.org/pub/release-96/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.19.fa.gz -o ' + str(path) + 'chr19.fa.gz')
    os.system(
        'gzip -d ' + str(path) + '*')
    os.system(
        """awk -F $'\t' '$1 == "19"' """ + str(path) + 'transcripts_all.gtf > ' + str(path) + 'transcripts.gtf')
    os.system(
        'rm ' + str(path) + 'transcripts_all.gtf')

# Curate references
print('Creating riboseq reference for testing...')
rp_reference = str(__path__) + 'rp_reference/'
if os.path.exists(rp_reference):
    os.system(
        'rm -rf ' + str(rp_reference))

os.makedirs(rp_reference)
get_source(rp_reference)
os.system(
    'xpresspipe curateReference'
    + ' -o ' + str(rp_reference)
    + ' -f ' + str(rp_reference)
    + ' -g ' + str(rp_reference) + 'transcripts.gtf'
    + ' --sjdbOverhang 49'
    + ' --genome_size 11'
    + ' -l -p -t')

print('Creating single-end reference for testing...')
se_reference = str(__path__) + 'se_reference/'
if os.path.exists(se_reference):
    os.system(
        'rm -rf ' + str(se_reference))

os.makedirs(se_reference)
get_source(se_reference)
os.system(
    'xpresspipe curateReference'
    + ' -o ' + str(se_reference)
    + ' -f ' + str(se_reference)
    + ' -g ' + str(se_reference) + 'transcripts.gtf'
    + ' --sjdbOverhang 49'
    + ' --genome_size 11'
    + ' -l -p')

print('Creating paired-end reference for testing...')
pe_reference = str(__path__) + 'pe_reference/'
if os.path.exists(pe_reference):
    os.system(
        'rm -rf ' + str(pe_reference))

os.makedirs(pe_reference)
get_source(pe_reference)
os.system(
    'xpresspipe curateReference'
    + ' -o ' + str(pe_reference)
    + ' -f ' + str(pe_reference)
    + ' -g ' + str(pe_reference) + 'transcripts.gtf'
    + ' --genome_size 11'
    + ' -l -p')


# Test riboseq pipeline on test data
print('Running riboseq test pipeline...')
rp_input = str(__path__) + 'riboseq_test/'
rp_output = str(__path__) + 'riboseq_out/'
if os.path.exists(rp_output):
    os.system(
        'rm -rf ' + str(rp_output))

os.makedirs(rp_output)
rp_gtf = str(__path__) + 'rp_reference/transcripts_LCT.gtf'
os.system(
    'xpresspipe riboseq' \
    + ' -i ' + str(rp_input) \
    + ' -o ' + str(rp_output) \
    + ' -r ' + str(rp_reference) \
    + ' -g ' + str(rp_gtf) \
    + ' -e riboseq_test' \
    + ' -a CTGTAGGCACCATCAAT' \
    + ' --method RPM' \
    + ' --sjdbOverhang 49')

# Verify output by examining output count table with truth table and asserting on correlation
"""
# Need to smoothen this up or figure out a better way of doing things here
r_vals = []
rp_counts = str(rp_output) + 'counts/riboseq_test_count_table_rpmNormalized.tsv'
rp_truth = str(__path__) + 'other/riboseq_truth.tsv'
rp_test_table = pd.read_csv(rp_counts, sep='\t', index_col=0)
rp_truth_table = pd.read_csv(rp_truth, sep='\t', index_col=0)


rp_truth_table.shape
rp_test_table.shape

rp_truth_table.head()
rp_test_table.head()

r_vals.append(stats.pearsonr(rp_test_table.iloc[:,0].values.tolist(), rp_truth_table.iloc[:,0].values.tolist())[0])
r_vals.append(stats.pearsonr(rp_test_table.iloc[:,1].values, rp_truth_table.iloc[:,1].values)[0])
assert all(r >= 0.99 for r in r_vals), 'An error occured while testing the riboseq pipeline'"""

# Test single end pipeline on test data
print('Running single-end test pipeline...')
se_input = str(__path__) + 'se_test'
se_output = str(__path__) + 'se_out'
if os.path.exists(se_output):
    os.system(
        'rm -rf ' + str(se_output))

os.makedirs(se_output)
se_gtf = str(__path__) + 'se_reference/transcripts_LC.gtf'
os.system(
    'xpresspipe seRNAseq' \
    + ' -i ' + str(se_input) \
    + ' -o ' + str(se_output) \
    + ' -r ' + str(se_reference) \
    + ' -g ' + str(se_gtf) \
    + ' -e se_test' \
    + ' -a CTGTAGGCACCATCAAT' \
    + ' --method RPKM' \
    + ' --sjdbOverhang 49')

# Test paired end pipeline on test data
print('Running paired-end test pipeline...')
pe_input = str(__path__) + 'pe_test'
pe_output = str(__path__) + 'pe_out'
if os.path.exists(pe_output):
    os.system(
        'rm -rf ' + str(pe_output))

os.makedirs(pe_output)
pe_gtf = str(__path__) + 'pe_reference/transcripts_LC.gtf'
os.system(
    'xpresspipe peRNAseq' \
    + ' -i ' + str(pe_input) \
    + ' -o ' + str(pe_output) \
    + ' -r ' + str(pe_reference) \
    + ' -g ' + str(pe_gtf) \
    + ' -e pe_test' \
    + ' -a AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC' \
    + ' --method RPKM' \
    + ' --sjdbOverhang 100')
