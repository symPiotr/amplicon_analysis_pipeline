# Symbiosis Evolution Group - the recommended amplicon analysis workflow
Here we provide the details of the custom amplicon data analysis workflow developed in December 2020 by Diego Castillo Franco, Michał Kolasa and Piotr Łukasik.  
  
We recommend this pipeline for the use by the [Symbiosis Evolution Group](http://symbio.eko.uj.edu.pl) at the Institute of Environmental Sciences of Jagiellonian University. The instructions are primarily intended for to the group members and associates, and especially for those working on the institutional computing clusters - but we intend to make them broadly accessible.  

Most of the key steps described below will be described in separate documents within this repository... ultimately. It will also contain the key scripts, or links to scripts. But it is work in progress!  
  
To follow these steps effectively, you should have basic familiarity with the Unix command line and sequence analysis.  
  
&nbsp;  
  
  
### Section 1. The overview of our amplicon sequencing data
Most of our libraries comprise a mix of amplicons for five targets expected in insects:
* Insect cytochrome oxidase I (COI) gene    [length: ~418 bp, plus primers]
* Bacterial 16S rRNA v4 and v1-v2 regions   [length: ~253 bp or ~300 bp, plus primers]
* Fungal ITS1 and ITS2 regions              [highly variable length]

The libraries are sequenced on Illumina in 250bp paired-end or 300bp paired-end modes, resulting in reads with the following organization:

R1: [VariableLengthInsert][Forward_Primer][Sequence of interest ..............]\
R2: [VariableLengthInsert][Reverse_Primer][Sequence of interest ..............]\
    Note: We are currently using variable length inserts of 0 to 3 bp only for COI and 16S-v4 targets!

The sequences are or will soon be listed in the file [amplicon_sequences.txt](amplicon_sequences.txt).  
  
&nbsp;  


### Section 2. Ensuring that you have access to the necessary software

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

&nbsp;  


### Section 3. The overview of the amplicon analysis pipeline
Our current bioinformatic pipeline follows these steps:  
* Split up the amplicon libraries into datasets corresponding to different targets. Each of them will be analyzed separately.  
* For all libraries in your experiment, for your chosen target (COI or 16S rRNA), assemble reads into contigs. The procedure is somewhat different for ITS.
* Quality-filter contigs, rename them.  
* Trim primers from contigs.  
* Dereplicate data: identify groups of identical sequences, pick representatives.  
* Sort reads by size, remove singletons.  
* Denoise data - identify error-free genotypes (= ASVs, zOTUs).  
* Compute zOTU table - check how many times each of the zOTUs is found in each of the libraries.  
* Assign taxonomy to your zOTUs.  
* OTU picking and chimera removal using zOTUs as input.  
* Compute OTU table.  
* Data interpretation, visualization, diversity analyses...  
  
The recommended  details of these steps, for different targets, are provided below!  
  
&nbsp;  
  

### Section 4. Where is the data? How to break it up?
By default, the Symbiosis Evolution Group amplicon sequencing data are copied to the shared space on the computing cluster: **/mnt/matrix/symbio/raw_data**. For each of the sequencing runs, we have a dedicated directory with the name that includes the date when sequencing took place. Within each of the directories, we have files corresponding to the forward and reverse read (R1 & R2) for each of the libraries included in that lane. Typically, the first character of the file name represents one of the "projects" grouping samples from a single experiment.  
```
piotr.lukasik@fsm:~$ ls -l /mnt/matrix/symbio/raw_data/ | head -5
total 896
dr-xr-xr-x  3 piotr.lukasik symbio  32768 Nov  7  2019 20191008_Pilot_IBA_MiSeq
dr-xr-xr-x  3 piotr.lukasik symbio  32768 Dec 19  2019 20191109_MiSeq_first_run
dr-xr-xr-x  3 piotr.lukasik symbio  40960 Feb 19  2020 20191127_MiSeq_2nd_run
dr-xr-xr-x  2 piotr.lukasik symbio  53248 Mar 19  2020 20200316_MiSeq_3rd
piotr.lukasik@fsm:~$ ls -l /mnt/matrix/symbio/raw_data/20200924_MiSeq | head -5
total 8436000
-r--r--r-- 1 piotr.lukasik symbio   7601229 Sep 29 15:05 A-CIXPIL_S44_L001_R1_001.fastq.gz
-r--r--r-- 1 piotr.lukasik symbio  10802954 Sep 29 15:05 A-CIXPIL_S44_L001_R2_001.fastq.gz
-r--r--r-- 1 piotr.lukasik symbio   3529128 Sep 29 15:05 A-CRYFAG1_S55_L001_R1_001.fastq.gz
-r--r--r-- 1 piotr.lukasik symbio   5205965 Sep 29 15:05 A-CRYFAG1_S55_L001_R2_001.fastq.gz
```  
  
Information about the nature of the samples is generally available within the Symbiosis Evolution Group's SharePoint "Methods" folders. We are working on consolidating the sample info into a database... Again, work in progress!  
  
Piotr has developed a script that breaks up the amplicon sequencing datasets into batches corresponding to different targets, so that instead of the original \*\_R1_* and \*\_R2_* file for each sample we get several pairs of files corresponding to different amplification targets. For example, instead of a single \*\_R1_* file for the sample "W_377" in one of the recent runs, we have five files:  
```
piotr.lukasik@fsm:~/splitting/split$ ls -lh *_W_377_R1*
-rw-r--r-- 1 piotr.lukasik users 2.2M Sep 30 10:43 16S-V1V2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 5.1M Sep 30 10:43 16S-v4_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 1.2M Sep 30 10:43 COI-BF3BR2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users  81K Sep 30 10:43 ITS2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 410K Sep 30 10:43 ITS1a_W_377_R1.fastq
```  
These data are generally available within **/mnt/matrix/symbio/split_data** folder... but we have been much less consistent about this.  
Details of the splitting script and approach will soon be available at [https://github.com/symPiotr/split_amplicon_libs](https://github.com/symPiotr/split_amplicon_libs).  
**Library splitting is the first key step of our pipeline: you want to be analyzing data for each of the targets separately. Until the pipeline is available, please talk to Piotr!**  
    
&nbsp;  
  

### Section 5. The analysis of bacterial 16S rRNA amplicon data
_... work in progress ..._  

    
&nbsp;  
  

### Section 6. The analysis of COI amplicon data
_... to be written ..._  


### Section 7. The analysis of fungal ITS amplicon data
_... to be written ..._  


### Section 8. Template quantification using spike-ins
_... to be written ..._  


### Section 9. Follow-up analyses and data visualization
_... to be written ..._  


### Section 10. Data submission to public repositories
_... to be written ..._  

