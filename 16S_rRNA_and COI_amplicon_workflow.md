# 16S rRNA and COI amplicon data analysis
This pipeline starts with raw amplicon data for bacterial 16S rRNA V4 region, or V1-V2 region, or alternatively, for insect cytochrome oxidase I (COI). It is assumed that the data were extracted from the original multi-target amplicon data using the approach described in [README](README.md): only read pairs where both the forward and the reverse read contained error-free primer sequences were extracted. For each sample/target, you should be starting with two files, for example 16S-V4_SampleName_R1.fastq & 16S-V4_SampleName_R2.fastq.  
  
To follow this protocol, you should have basic familiarity with Unix command line and sequence analysis, and motivation to learn more!  
  
  
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
For 16S-V4, 16S-V1+V2, or COI-BF3BR2 regions, forward and reverse reads largely overlap. We start from assembling them into contigs. This needs to be done for every sample in the dataset.  
The recommended tool is **PEAR** [https://cme.h-its.org/exelixis/web/software/pear/](https://cme.h-its.org/exelixis/web/software/pear/), a versatile, efficient and popular paired-end read merger. Read the [manual](https://cme.h-its.org/exelixis/web/software/pear/doc.html) and choose the best options for your dataset, includins read size!  
  
The geenral syntax that should work for 2x250 bp or 2x300 bp paired-end reads for 16S-V4 and 16S-V1+V2 region is:
```
pear -f SampleName_R1.fastq -r SampleName_R2.fastq -o SampleName -v 15 -n 250 -m 400 -q 30 -j 20
```  
   
You want to execute this on all the pairs of fastq files in your experiment. You can do it in many ways. For example, you can use **basename** command inside a **"for"** loop to extract all sample names and pass them on to PEAR, all in a single step:
```
for file in *_R1.fastq; do
    SampleName=`basename $file _R1.fastq`
    pear -f "$SampleName"_R1.fastq -r "$SampleName"_R2.fastq -o "$SampleName" -v 15 -n 250 -m 400 -q 30 -j 20
done
```  
  
After executing PEAR, you may want to clean up your working directory: remove *unassembled* and *discarded* files, rename *assembled* files, and move the original R1 and R2 reads to a separate folder:
```
rm *unassembled* *discarded*
rename -f 's/.assembled//' *fastq
mkdir reads && mv *_R?.fastq reads/
```
&nbsp;  
  
  
### Conversion from FASTQ to FASTA
At this point, we want to convert contigs from FASTQ to FASTA format, and merge files for different samples.  
  
First, we use VSEARCH to convert fastq to fasta, and at the same time, rename all contigs following the format "SampleName_1, SampleName_2, ..." . Basic syntax:  
```
vsearch -fastq_filter SampleName.fastq -fastaout SampleName.fasta -relabel SampleName_ -fasta_width 0
```  
  
Again, we can use **basename** command inside a **"for"** loop to do this for all fastq files in our working directory:  
```
for file in *fastq; do
    SampleName=`basename $file .fastq`
    vsearch -fastq_filter $SampleName.fastq -fastaout $SampleName.fasta -relabel "$SampleName"_ -fasta_width 0
done
```  
  
Now, let's merge all the resulting fasta files into one. And then move them out of the way... for example, like this ---  
```
mkdir contigs
for file in *fasta; do cat $file >> all_samples.fasta; mv $file contigs/; done
mv *fastq contigs/
```  
&nbsp;  
  

### Primer trimming and size filtering
Now, we want to trim primers and remove all contigs with incorrect primers or well outside of the expected length.   
  
How?  
  
Think about the organizations of our contigs:  
\[VariableLengthInsert] \[Forward_Primer] \[**Sequence_of_interest**] \[Reverse-complemented_Reverse_Primer] \[VariableLengthInsert]  
  
For V4, that should be: ??? GTGYCAGCMGCCGCGGTAA **Sequence_of_interest_of_approx_253bp** ATTAGAWACCCBNGTAGTCC ???  
For V1-V2: AGMGTTYGATYMTGGCTCAG **Sequence_of_interest_of_approx_300bp** ACTCCTACGGGAGGCAGCA (no variable-length inserts in this case!).  
For COI: ??? CCHGAYATRGCHTTYCCHCG **Sequence_of_interest_of_approx_418bp** TGRTTYTTYGGNCAYCCHG ???  
  
We want to keep only the middle portion... and only when it is of the correct length! We can use Regular Expressions and **grep** + **sed** to combine size filtering and primer trimming.  
The fact that the sequence in fasta format is often broken up across many lines could be a challenge... but we've taken care of that in the previous step (parameter -fasta_width)!. Another challenge could be degenerate bases in primer sequences... but they follow [IUPAC codes](https://www.bioinformatics.org/sms/iupac.html) and we can easily convert degenerate bases (for example Y or M), into search terms (\[TC], \[AC]). Now would you construct REGEX search terms to capture the primers and variable-length inserts at the same time?  
  
Here, I am using **grep** to only extract the sequences with correct primer seqs and correct length, and then **sed** to trim the primers and any inserts from V4 contigs:  
```
egrep -B 1 "GTG[TC]CAGC[CA]GCCGCGGTAA.{250,260}ATTAGA[AT]ACCC[CGT][ACGT]GTAGTCC" all_samples.fasta |
sed -E 's/.*GTG[TC]CAGC[CA]GCCGCGGTAA//; s/ATTAGA[AT]ACCC[ACGT][ACGT]GTAGTCC.*//' > all_samples_trimmed.fasta
```  
&nbsp;  
  
  
### Dereplicate data - pick representative sequences
Now, we are using VSEARCH to identify unique genotypes, and pick representative.  
```
vsearch -derep_fulllength all_samples_trimmed.fasta -output all_samples_derep.fasta -sizeout -uc all_samples_derep_info.txt
```  
  
Then, the genotypes are sorted by abundance, and singletons removed.  
```
vsearch -sortbysize all_samples_derep.fasta --output all_samples_derep_sorted.fasta -minsize 2
```
  
&nbsp;  
  
  
### Denoising
We want to apply algorithm
usearch -unoise3 all_samples_derep_sorted.fasta -zotus zotus.fasta -tabbedout unoise3.txt
 
Make zOTU table
usearch -otutab all_samples.fasta -zotus zotus.fasta -otutabout zotu_table_wo_tax.txt

  
&nbsp;  
  
  
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

