# Symbiosis Evolution Group - the recommended amplicon analysis workflow
Here we provide the details of the custom amplicon data analysis workflow developed in December 2020 by Diego Castillo Franco, Michał Kolasa and Piotr Łukasik.
We recommended this pipeline for the use by the Symbiosis Evolution Group at the Institute of Environmental Sciences of Jagiellonian University.
The instructions are primarily intended for group members and associates, especially those who work on one of the institutional computing clusters - but we intend to make them broadly accessible.

Most of the key steps described below will be described in separate documents within this repository... ultimately. It will also contain the key scripts, or links to scripts. But it is work in progress!

To follow these steps effectively, you should have basic familiarity with the Unix command line and sequence analysis.



### Section 1. The overview of our amplicon sequencing data
_... work in progress! ..._  

Most of our libraries comprise a mix of amplicons for five targets expected in insects:
* Insect cytochrome oxidase I (COI) gene    [length: ~418 bp, plus primers]
* Bacterial 16S rRNA v4 and v1-v2 regions   [length: ~253 bp or ~300 bp, plus primers]
* Fungal ITS1 and ITS2 regions              [highly variable length]

The libraries are sequenced on Illumina in 250bp paired-end or 300bp paired-end modes, resulting in reads with the following organization:

R1: [VariableLengthInsert][Forward_Primer][Sequence of interest ..............]\
R2: [VariableLengthInsert][Reverse_Primer][Sequence of interest ..............]\
    Note: We are currently using variable length inserts of 0 to 3 bp only for COI and 16S-v4 targets!

The sequences are or will soon be listed in the file [amplicon_sequences.txt](amplicon_sequences.txt).  
  
  
### Section 2. Ensuring that you have access to the necessary software
_... work in progress! ..._  

Before getting started on any analyses, make sure that you have access to all the necessary software.  
If you work on the Institute cluster, you should have access as long as you have "/mnt/matrix/symbio/bin" in your PATH, and especially once you have activated "symbio" conda environment. Specifically, you want to be able to use:  
  
* pear  
* usearch  
* vsearch  
* custom script [add_values_to_zOTU_fasta.py](add_values_to_zOTU_fasta.py)  
* qiime1  
* R  

While on the cluster, if you type the names of these commands into the terminal, you should be getting responses clearly distinct from ***command not found***! :stuck_out_tongue_winking_eye:  
  
But if not, check [instructions for setting up the necessary software](software_instructions.md)!  

  

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

