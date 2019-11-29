r"""
Finding homologs of short sequences in a genome
===============================================

In this example we use a local alignment (dynamic programming) for
identification of homologs of a short sequence in an entire bacterial
genome.
Specifically we take the *leuL* gene (*leu* operon leader peptide)
from *E. coli* BL21 and search for it in the genome of a
*Salmonella enterica* strain.

This method only works for short sequences, since the dynamic
programming method requires too much RAM (dozens of gigabyte) for longer
sequences.
"""

# Code source: Patrick Kunzmann
# License: BSD 3 clause

###
import numpy as np
import pyximport
pyximport.install(
    build_in_temp=False,
    language_level=3
)
###

import biotite
import biotite.sequence as seq
import biotite.sequence.io.fasta as fasta
import biotite.sequence.io.genbank as gb
import biotite.sequence.graphics as graphics
import biotite.sequence.align as align
import biotite.database.entrez as entrez
import numpy as np
import matplotlib.pyplot as plt

# Download E. coli BL21 genome for obtaining the leuL sequence
file_name = entrez.fetch("CP001509", ".", "gb", "nuccore", "gb")
gb_file = gb.GenBankFile()
gb_file.read(file_name)
annot_seq = gb.get_annotated_sequence(gb_file, include_only=["gene"])
# Find leuL gene
for feature in annot_seq.annotation:
    if "gene" in feature.qual and feature.qual["gene"] == "leuL":
        leul_feature = feature
# Get leuL sequence
leul_seq = annot_seq[leul_feature]

# Download Salmonella enterica genome for finding its leuL homologs
file_name = entrez.fetch("CP019649", ".",
                         "fa", "nuccore", "fasta")
fasta_file = fasta.FastaFile()
fasta_file.read(file_name)
se_genome = fasta.get_sequence(fasta_file)

# We want to search in the sequence and its reverse complement
genomic_seqs = [se_genome, se_genome.reverse().complement()]



WORD_LENGTH = 12
MAX_GAPS = 1000

print(1)
leul_words = align.WordSequence(leul_seq, word_length=WORD_LENGTH)
genomic_word_seqs = [
    align.WordSequence(sequence, word_length=WORD_LENGTH)
    for sequence in genomic_seqs
]

print(2)
matches = align.find_matches(genomic_word_seqs, leul_words)

print(3)
alignments = []
matrix = align.SubstitutionMatrix.std_nucleotide_matrix()
for i, genome in enumerate(genomic_seqs):
    strand = seq.Location.Strand.FORWARD if i == 0 \
        else seq.Location.Strand.REVERSE
    for ref_pos, query_pos in matches[i]:
        genome_excerpt = genome[ref_pos-MAX_GAPS : ref_pos+MAX_GAPS]
        alignment = align.align_optimal(
            genome_excerpt, leul_seq, matrix, gap_penalty=-7, local=True
        )[0]
        alignments.append((alignment, strand))
    
print(4)
best_alignment, strand = alignments[np.argmax([
    alignment.score for alignment, _ in alignments
])]

print(5)
print(best_alignment)


exit()


########################################################################
# Now that we have both alignments (forward and reverse strand),
# we can can check which of them has a higher score.
# We simply take the score of the first alignment in each list.
# Due to the nature of the dynamic programming algorithm, every
# alignment in each list has the same score.

print("Forward:")
print("Alignment count:", len(alignments))
print("Score:", alignments[0].score)
print()
print("Reverse:")
print("Alignment count:", len(rev_alignments))
print("Score:", rev_alignments[0].score)

########################################################################
# Clearly the alignment with the reverse genome seems to be the
# right one.
# For visualization purposes we have to apply a renumbering function
# for the genomic sequence,
# since the original indices refer to the reverse complement sequence,
# but we want the numbers to refer to the original sequence.

# Use first and only alignment 
alignment = rev_alignments[0]
# Reverse sequence numbering for second sequence (genome) in alignment
number_funcs = [None,   lambda x: len(alignment.sequences[1]) - x]
# Visualize alignment, use custom color
fig = plt.figure(figsize=(8.0, 2.0))
ax = fig.add_subplot(111)
graphics.plot_alignment_similarity_based(
    ax, alignment, matrix=matrix, labels=["E. coli (leuL)", "S. enterica"],
    show_numbers=True, number_functions=number_funcs, show_line_position=True,
    color=biotite.colors["lightorange"]
)
fig.tight_layout()

########################################################################
# We will now go even further and align the translated protein
# sequences.

leul_ec = leul_seq
# Obtain the S enterica leuL sequence
# using the first and last index in the alignment trace
first_i = alignment.trace[0, 1]
last_i  = alignment.trace[-1,1]
# Get sequence slice (mind the exclusive stop)
leul_se = se_genome_rev[first_i : last_i+1]
# Translate sequences into protein sequence using bacterial codon table
codon_table = seq.CodonTable.load("Bacterial, Archaeal and Plant Plastid")
leul_ec = leul_ec.translate(complete=True, codon_table=codon_table)
leul_se = leul_se.translate(complete=True, codon_table=codon_table)

# Align the protein sequences (using BLOSUM62 and affine gap penalty)
matrix = align.SubstitutionMatrix.std_protein_matrix()
alignments = align.align_optimal(
    leul_ec, leul_se, matrix, gap_penalty=(-10,-1)
)
alignment = alignments[0]

# Lets try a matplotlib colormap this time
# Color the symbols rather than the background
fig = plt.figure(figsize=(8.0, 1.0))
ax = fig.add_subplot(111)
graphics.plot_alignment_similarity_based(
    ax, alignment, matrix=matrix, labels=["E. coli (leuL)", "S. enterica"],
    cmap="summer_r", color_symbols=True
)
fig.tight_layout()
plt.show()