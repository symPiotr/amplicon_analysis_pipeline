# Symbiosis Evolution Group - the recommended amplicon analysis workflow
Here we provide the details of the custom amplicon data analysis workflow developed in December 2020 by Diego Castillo Franco, Michał Kolasa and Piotr Łukasik.
We recommended this pipeline for the use by the Symbiosis Evolution Group at the Institute of Environmental Sciences of Jagiellonian University.
The instructions are primarily intended for group members and associates, especially those who work on one of the institutional computing clusters - but we intend to make them broadly accessible.

Most of the key steps described below will be described in separate documents within this repository... ultimately. It will also contain the key scripts, or links to scripts. But it is work in progress!

To follow these steps effectively, you should have basic familiarity with the Unix command line and sequence analysis.



### Section 1. The overview of our amplicon sequencing data
_... work in progress! ..._
Most of our libraries comprise a mix of amplicons for five targets expected in insects:
* Insect cytochrome oxidase I (COI) gene [length: ~418 bp, plus primers]
* Bacterial 16S rRNA v4 and v1-v2 regions [length: ~253 bp or ~300 bp, plus primers]
* Fungal ITS1 and ITS2 regions [highly variable length]

The libraries are sequenced on Illumina in 250bp paired-end or 300bp paired-end modes, resulting in reads with the following organization:

R1: [VariableLengthInsert][Forward_Primer][Sequence of interest ..............
R2: [VariableLengthInsert][Reverse_Primer][Sequence of interest ..............
   * Note: We are currently using variable length inserts of 0 to 3 bp only for COI and 16S-v4 targets!

The sequences will be listed separately!


### Section 2. Ensuring that you have access to the necessary software
_... work in progress! ..._
check if you have all softwares installed (pear, usearch, add_values_to_zOTU_fasta.py and qiime1)

### Section 3. The overview of the amplicon analysis pipeline
... to be completed ...


### Section 4. Where is the data? Preliminary analyses.
... to be completed ...


### Section 5. The analysis of bacterial 16S rRNA amplicon data
... to be completed ...


### Section 6. The analysis of COI amplicon data
... to be completed ...


### Section 7. The analysis of fungal ITS amplicon data
... to be completed ...


### Section 8. Template quantification using spike-ins
... to be completed ...


### Section 9. Follow-up analyses and data visualization
... to be completed ...


### Section 10. Data submission to public repositories
... to be completed ...

