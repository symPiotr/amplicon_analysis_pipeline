# Symbiosis Evolution Group - the recommended amplicon analysis workflow
Here we provide the details of the custom amplicon data analysis workflow developed in December 2020 by Diego Castillo Franco, Michał Kolasa and Piotr Łukasik.  
  
We recommend this pipeline for the use by the [Symbiosis Evolution Group](http://symbio.eko.uj.edu.pl) at the Institute of Environmental Sciences of Jagiellonian University. The instructions are primarily intended for to the group members and associates, and especially for those working on the institutional computing clusters - but we intend to make them broadly accessible.  

Most of the key steps described below will be described in separate documents within this repository... ultimately. It will also contain the key scripts, or links to scripts. But it is work in progress!  
  
To follow these steps effectively, you should have basic familiarity with the Unix command line and sequence analysis.  
  
&nbsp;  
  
  
### Section 1. The overview of our amplicon sequencing data
Most of our libraries comprise a mix of amplicons for five targets expected in insects:  
* Insect cytochrome oxidase I (COI) gene    \[length: ~418 bp, plus primers]
* Bacterial 16S rRNA v4 and v1-v2 regions   \[length: ~253 bp or ~300 bp, plus primers]
* Fungal ITS1 and ITS2 regions              \[highly variable length]

The libraries are sequenced on Illumina in 250bp paired-end or 300bp paired-end modes, resulting in reads with the following organization:  
  
R1: \[VariableLengthInsert]\[Forward_Primer]\[Sequence of interest ..............]\
R2: \[VariableLengthInsert]\[Reverse_Primer]\[Sequence of interest ..............]\
&nbsp;&nbsp;&nbsp;&nbsp;Note: We are currently using variable length inserts of 0 to 3 bp only for COI and 16S-v4 targets!  
  
The sequences are or will soon be listed in the file [amplicon_sequences.txt](amplicon_sequences.txt).  
  
&nbsp;  


### Section 2. Setting up working environment
Before getting started on any analyses, make sure that you have access to all the necessary software.  
If you work on the Institute cluster, you should have access as long as you have "/mnt/matrix/symbio/bin" in your PATH.  
Specifically, you want to be able to use:  

* pear  
* usearch  
* vsearch  
* custom scripts: [add_values_to_zOTU_fasta.py](add_values_to_zOTU_fasta.py), [combine_OTU_files.py](combine_OTU_files.py), [combine_zOTU_files.py](combine_zOTU_files.py)  
  
It may also help to activate "symbio" conda environment, which will facilitate access to software that you may want to be using for the subsequent steps:   
  
* qiime1  
* R  

While on the cluster, if you type the names of these commands into the terminal, you should be getting responses clearly distinct from ***command not found***! :stuck_out_tongue_winking_eye:  
  
But if not, check [instructions for setting up the necessary software](software_instructions.md)!  

&nbsp;  


### Section 3. The key steps in the amplicon analysis pipeline
Our current bioinformatic pipeline follows these steps:  
* Split up the amplicon libraries into datasets corresponding to different targets. Each of them will be analyzed separately.  
* For all libraries in your experiment, for your chosen target (COI or 16S rRNA), assemble reads into contigs. The procedure is somewhat different for ITS.
* Quality-filter contigs, rename them, trim primers and any flanking sequences.
* Dereplicate data: identify groups of identical sequences, pick representatives. Remove singletons.
* Denoise data - identify error-free genotypes (= ASVs, zOTUs). Compute zOTU table - check how many times each of the zOTUs is found in each of the libraries.  
* Assign taxonomy to your zOTUs.  
* Identify and remove chimeras, pick OTUs, compute OTU table.
* Combine all the info in a convenient form

We will soon be adding further steps:  
* Template quantification using spike-ins
* Filter reagent contaminants
* Data interpretation, visualization, diversity analyses... a complicated piece that will be developed!  
  
The outline of these steps is or will be provided below. In most cases, you will be directed to detailed pipelines. At least, that's the plan :stuck_out_tongue: 
  
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
  
Information about the nature of the samples is generally available within the Symbiosis Evolution Group's SharePoint "Methods" folders. We are working on consolidating the sample info into a database. You will find more info here soon!  
&nbsp;  
  
The majority of the *fastq.gz files comprises read corresponding to different targets amplified from the same sample --- but generally, you want to be analyzing the reads corresponding to only one target at a time! Hence, **the first step in our pipeline comprises breaking up amplicon sequencing datasets into batches corresponding to different targets.** Instead of the original \*_R1.fastq.gz and \*_R2.fastq.gz files, for each sample, we want to get several pairs of files corresponding to different amplification targets. For example, instead of a single forward read file for the sample "W_377" in one of the recent runs, we have five files:  
```
piotr.lukasik@fsm:~/splitting/split$ ls -lh *_W_377_R1*
-rw-r--r-- 1 piotr.lukasik users 2.2M Sep 30 10:43 16S-V1V2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 5.1M Sep 30 10:43 16S-v4_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 1.2M Sep 30 10:43 COI-BF3BR2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users  81K Sep 30 10:43 ITS2_W_377_R1.fastq
-rw-r--r-- 1 piotr.lukasik users 410K Sep 30 10:43 ITS1a_W_377_R1.fastq
```  
... plus another five corresponding to the reverse read! Some of these split data are available within **/mnt/matrix/symbio/split_data** folder. If this is not the case with your data, you can do the splitting yourself using Piotr's [**split_amplicon_libs.py** script, described at https://github.com/symPiotr/split_amplicon_libs](https://github.com/symPiotr/split_amplicon_libs).  
You can also just talk to Piotr :)   
&nbsp;  
One way or another, before proceeding with the next steps of the analysis, for each sample, you want to have files corresponding to a single target only, \*R1.fastq and \*R2.fastq. Copying them all to your working directory probably makes sense!  
    
&nbsp;  
  

### Section 5. The analysis of bacterial 16S rRNA and insect COI amplicon data: from raw sequences, through ASVs, to OTU tables.
This is the core portion of the workflow.  
  
The fully annotated analysis steps and commands are available at [COI_and_16S_rRNA_amplicon_bioinformatic_pipeline.md](COI_and_16S_rRNA_amplicon_bioinformatic_pipeline.md).  
  
Here are some complete sets of commands that have been successfully used with real data. After ensuring that you are working on the right sets of files, you should be able to copy-and-paste into your terminal most of the commands... but do this at your own risk!  
  
* Data analysis pipeline for [16S rRNA v4 region for some flies, successfully run on 2021-01-12 on fsm](20210112_16S-rRNA-v4_pipeline.txt). 
* Data analysis pipeline for [COI for some wasps, successfully run on 2020-12-18 on fsm](20201218_Wasp_COI_pipeline.txt).
    
&nbsp;  
  

### Section 6. The analysis of fungal ITS amplicon data
_... to be written ..._  
    
&nbsp;  
  

### Section 7. Template quantification using spike-ins
_... to be written ..._  
    
&nbsp;  
  

### Section 8. Detection and filtering of reagent contamination
_... to be written ..._  
    
&nbsp;  
  

### Section 9. Follow-up analyses and data visualization
_... to be written ..._  
    
&nbsp;  
  

### Section 10. Data submission to public repositories
_... to be written ..._  

