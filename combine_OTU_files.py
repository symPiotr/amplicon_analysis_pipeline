#! /usr/bin/env python3

import sys, re

if len(sys.argv) != 4:
	sys.exit('This script combines info on otus from several files, outputting "otu_table_expanded.txt"\n'
	         'Usage: ./combine_OTU_files.py <OTU_count_table> <OTU_taxonomy> <OTU_fasta>\n'
	         'For example: ./combine_OTU_files.py otu_table.txt otus.tax otus.fasta\n')

Script, OTU_counts, OTU_tax, OTU_fasta = sys.argv

##### Setting names of output files
Output_table = "otu_table_expanded.txt"


##### Setting up the key arrays --- LIST for keeping sequences in order, and DICT for managing sequence info
OTU_list = []
OTU_dict = {}


##### Opening OTU table
COUNTS = open(OTU_counts, "r")

for line in COUNTS:
    if line.startswith("#"):
        COUNT_headings = line.strip().split()[2:]    ### Keeping the names of libraries
    else:
        LINE = line.strip().split()
        OTU_list.append(LINE[0])
        OTU_dict[LINE[0]] = [LINE[1:]]

COUNTS.close()



##### Adding taxonomy info to DICT
TAX = open(OTU_tax, "r")

for line in TAX:
    LINE = line.strip().split()
    if LINE[0] in OTU_list:
        OTU_dict[LINE[0]].append(LINE[1])
    else:
        print('FATAL ERROR! Taxonomy file contains OTUs that are not in OTU count table! ---', LINE[0])
        sys.exit()

TAX.close()


##### Adding sequences from the FASTA file to DICT
FASTA = open(OTU_fasta, "r")
Sequence = ''
Seq_heading = FASTA.readline().strip().strip(">")

for line in FASTA:   # Copying the sequence (potentially spread across multiple lines) to a single line
    if line.startswith('>'):    # if the line contains the heading
        if Seq_heading not in OTU_list and Seq_heading != "":     # EXIT if the previous Seq_heading is not in a list!
            print('FATAL ERROR! Fasta file contains OTUs that are not in OTU count table! ---', Seq_heading)
            sys.exit()
            
        OTU_dict[Seq_heading].append(Sequence) # save the existing Seq_heading and Sequence to a DICT
        Sequence = ''    # clear sequence
        Seq_heading = line.strip().strip(">")  # use the current line as the new heading!

    else:
        Sequence = Sequence + line.strip().upper()

OTU_dict[Seq_heading].append(Sequence) # Saves the final sequence (Seq_heading and Sequence) to a list

FASTA.close()



##### Outputting the Expanded Count Table

OUTPUT_TABLE = open(Output_table, "w")

print("OTU_ID", "Taxonomy", "Sequence", "Total", sep = "\t", end = "\t", file = OUTPUT_TABLE)
for item in COUNT_headings:
    print(item, end = "\t", file = OUTPUT_TABLE)
print("", file = OUTPUT_TABLE)

for OTU in OTU_list:
    Total = 0
    for no in OTU_dict[OTU][0]:
        Total += int(no)
    
    # Terms in DICT: 'Zotu32': [['0', '1', '100'], 'd:Bacteria(1.00)...', 'TACGT...']
    # I want to export: "OTU_ID", "Taxonomy"[1], "Sequence"[2], "Total"
    print(OTU, OTU_dict[OTU][1], OTU_dict[OTU][2], Total, sep = "\t", end = "\t", file = OUTPUT_TABLE)
    
    for no in OTU_dict[OTU][0]:
        print(no, end = "\t", file = OUTPUT_TABLE)
    
    print("", file = OUTPUT_TABLE)

OUTPUT_TABLE.close()


print(f"Script executed successfully.Output --- {Output_table}\nEnjoy! Piotr :)")
