# 16S rRNA amplicon data analysis - recommended workflow
This pipeline starts with raw amplicon data for 16S rRNA V4 region, or alternatively V1-V2 region (16S-V4_SampleName_R1.fastq & 16S-V4_SampleName_R2.fastq for each sample). It is assumed that the data were extracted from the original multi-target amplicon data using the approach described in [README](README.md): only read pairs where both the forward and the reverse read contained error-free primer sequences were extracted.  
&nbsp;  
  
  
### Setting up work space
Start from copying all files to your working directory:  
```
cp SourceDirectory/16S-V4*fastq WorkingDirectory/`  
```    
Before proceeding, consider simplifying file names. For example, perhaps you can remove the "16S-v4_P_" portion of the file names, using *rename* command or another approach? When using *rename*, make sure that the command works before committing!
```
rename -n 's/16S-v4_P_//' *fastq
rename -f 's/16S-v4_P_//' *fastq
```
&nbsp;  
  
  
### Assembling paired-end reads using PEAR
For 16S-V4 and 16S-V1+V2 regions, forward and reverse reads largely overlap. We start from assembling them into contigs. This needs to be done for every sample in the dataset.  
The recommended tool is **PEAR** [https://cme.h-its.org/exelixis/web/software/pear/](https://cme.h-its.org/exelixis/web/software/pear/), a versatile, efficient and popular paired-end read merger. Read the [manual](https://cme.h-its.org/exelixis/web/software/pear/doc.html) and choose the best options for your dataset, includins read size!  
  
The syntax that should work for 16S-V4 and 16S-V1+V2 reads is  
```
pear -f SampleName_R1.fastq -r SampleName_R2.fastq -o SampleName -v 15 -n 250 -m 400 -q 30 -j 20
```  
   
You want to execute this on all the pairs of fastq files in your experiment. There are multiple ways of going about this. One of the possibilities is (1) gathering all SampleNames in your working directory and saving them to a file; and (2) using "while" loop for executing pear using all SampleNames:  
```
ls *R1* | sed 's/_R1.fastq//g' > Sample.Names
while read SampleName; do pear -f "$SampleName"_R1.fastq -r "$SampleName"_R2.fastq -o "$SampleName" -v 15 -n 250 -m 400 -q 30 -j 20; done < Sample.Names
```  

### remove all useless files (unassembled, discarded, etc)

rm *unassembled*
rm *discarded*

### rename pear output
rename -n 's/.assembled//' *fastq
rename -f 's/.assembled//' *fastq

### move original reada out of the way
mkdir reads && mv *_R?.fastq reads/

### In this step is possible to increase quality filters but you will lose sequences, in this case I avoided because we are working with a low number of sequences.
###Fastq to fasta convertion
for i in `ls *fastq`; do bn=`basename $i .fastq`; vsearch -fastq_filter $bn.fastq -fastaout $bn.fasta --fastq_maxlen 310 -relabel $bn._; done

###joining all libraries into one fasta files
cat ~/*fasta > all_samples.fasta


### Primer trimming. 
### This example is for V4 primers (variable lenght)
sed -E 's/.{0,10}GTG[TC]CAGC[CA]GCCGCGGTAA//; s/ATTAGA[AT]ACCC[ACGT][ACGT]GTAGTCC.{0,10}//' all_samples.fasta > all_samples_trimmed.fasta


#### Dereplicate data - pick representative sequences
vsearch --derep_fulllength all_samples_trimmed.fasta --output all_samples_derep.fasta -sizeout -uc all_samples_derep_info.txt


######!!! 
vsearch --maxseqlength 260 --minseqlength 250 --output all_samples_derep_filtered.fasta
vsearch -fastq_minlen 250 
 
 
 
##Sort by size and singletons removal
vsearch -sortbysize all_samples_derep.fasta --output all_samples_derep_sorted.fasta -minsize 2
 
###Denoising
usearch -unoise3 all_samples_derep_sorted.fasta -zotus zotus.fasta -tabbedout unoise3.txt
 
##Make zOTU table
usearch -otutab all_samples.fasta -zotus zotus.fasta -otutabout zotu_table_wo_tax.txt

### Assign taxonomy
conda activate qiime1
parallel_assign_taxonomy_blast.py -i zotus.fasta -o assign_taxonomy_asv -r ~/symbio/db/SILVA_138/SILVA-138-SSURef_full_seq.fasta -t ~/symbio/db/SILVA_138/SILVA-138-SSURef_full_seq_taxonomy.txt

###Add size to zotu
add_values_to_zOTU_fasta.py zotu_table_wo_tax.txt zotus.fasta


 
### OTU picking and chimeras removal using ASV as input

usearch -sortbysize new_zotus.fasta -fastaout new_zotus_sorted.fasta -minsize 2

usearch -cluster_otus new_zotus_sorted.fasta -otus all_samples_otus.fasta -minsize 2 -relabel OTU -uparseout zotu_otu_relationship.txt

usearch -usearch_global all_samples.fasta -db all_samples_otus.fasta -strand plus -id 0.97 -otutabout otu_table_wo_tax.txt

parallel_assign_taxonomy_blast.py -i all_samples_otus.fasta -o assign_taxonomy_otu -r ~/symbio/db/SILVA_138/SILVA-138-SSURef_full_seq.fasta -t ~/symbio/db/SILVA_138/SILVA-138-SSURef_full_seq_taxonomy.txt





### join otu tables in R (zotu_table/otu_table with taxonomic classification)
R
otu = read.table("otu_table_wo_tax.txt", head=T, comment.char="&", sep="\t")
tax = read.table("all_samples_otus_tax_assignments.txt", head=F, sep="\t")
otu2=otu[order(otu[,1]),]
tax2=tax[order(tax[,1]),]
otu.tax = cbind(otu2, taxonomy=tax2$V2)
write.table(otu.tax, "otu_table_tax.txt", quote=F, col.names=T, row.names=F, sep="\t")

