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
rename -n 's/16S-V4_P_//' *fastq
rename -f 's/16S-V4_P_//' *fastq
```
&nbsp;  
  
  
### Assembling paired-end reads using PEAR
For 16S-V4, 16S-V1+V2, or COI-BF3BR2 regions, forward and reverse reads largely overlap. We start from assembling them into contigs. This needs to be done for every sample in the dataset.  
The recommended tool is **PEAR** [https://cme.h-its.org/exelixis/web/software/pear/](https://cme.h-its.org/exelixis/web/software/pear/), a versatile, efficient and popular paired-end read merger. Read the [manual](https://cme.h-its.org/exelixis/web/software/pear/doc.html) and choose the best options for your dataset, includins read size!  
  
The general syntax that should work for 2x250 bp or 2x300 bp paired-end reads for 16S-V4 and 16S-V1+V2 region is:
```
pear -f SampleName_R1.fastq -r SampleName_R2.fastq -o SampleName -v 15 -n 250 -m 400 -q 30 -j 20
```  
For the COI region, you want to set larger -n & -m values (min and max contig length), say, 400 and 470?  
  
You want to execute this command on all the pairs of fastq files in your experiment. You can do it in many ways. For example, you can use **basename** command inside a **"for"** loop to extract all sample names and pass them on to PEAR, all in a single step:
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
    vsearch -fastq_filter $SampleName.fastq -fastaout $SampleName.fasta -relabel "$SampleName"._ -fasta_width 0
done
```  
  
Now, let's merge all the resulting fasta files into one. And then move them out of the way... for example, like this ---  
```
mkdir contigs
cat *fasta > all_samples.fasta
mv *fast? contigs/ && mv contigs/all_samples.fasta .
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
  
Here, I am using **grep** to only extract the sequences with correct primer seqs and correct length, followed by another **grep** that excludes lines with two dashes (possibly inserted by the first instance of grep, depending on the version), and then **sed** to trim the primers and any inserts. 
```
##### 16S rRNA - V4 region #####
egrep -B 1 "GTG[TC]CAGC[CA]GCCGCGGTAA.{250,260}ATTAGA[AT]ACCC[CGT][ACGT]GTAGTCC" all_samples.fasta | egrep -v "^\-\-$" |
sed -E 's/.*GTG[TC]CAGC[CA]GCCGCGGTAA//; s/ATTAGA[AT]ACCC[ACGT][ACGT]GTAGTCC.*//' > all_samples_trimmed.fasta   

##### 16S rRNA - V1-V2 region #####
egrep -B 1 "AG[AC]GTT[TC]GAT[TC][AC]TGGCTCAG.{250,350}ACTCCTACGGGAGGCAGCA" all_samples.fasta | egrep -v "^\-\-$" |
sed -E 's/.*AG[AC]GTT[TC]GAT[TC][AC]TGGCTCAG//; s/ACTCCTACGGGAGGCAGCA.*//' > all_samples_trimmed.fasta   
  
##### COI - product amplified using BF3-BR2 primers #####
egrep -B 1 "CC[ACT]GA[TC]AT[AG]GC[ACT]TT[TC]CC[ACT]CG.{400,430}TG[AG]TT[TC]TT[TC]GG[ACGT]CA[TC]CC[ACT]G" all_samples.fasta | egrep -v "^\-\-$" |
sed -E 's/.*CC[ACT]GA[TC]AT[AG]GC[ACT]TT[TC]CC[ACT]CG//; s/TG[AG]TT[TC]TT[TC]GG[ACGT]CA[TC]CC[ACT]G.*//' > all_samples_trimmed.fasta   
```  
  
&nbsp;  
  
  
### Dereplicate data - pick representative sequences
Now, we are using VSEARCH to identify unique genotypes, and pick representative sequences.  
```
vsearch -derep_fulllength all_samples_trimmed.fasta -output all_samples_derep.fasta -sizeout -uc all_samples_derep_info.txt
```  
  
Then, the genotypes are sorted by abundance, and singletons removed.  
```
vsearch -sortbysize all_samples_derep.fasta --output all_samples_derep_sorted.fasta -minsize 2
```
  
&nbsp;  
  
  
### Denoising
At this step, we want to use USEARCH's UNOISE algorithm for denoising our data: the identification of unique error-free genotypes (= zOTUs, ASVs), merging sequences with errors with these genotypes, and identification and removal of chimeric sequences.
```
usearch -unoise3 all_samples_derep_sorted.fasta -zotus zotus.fasta -tabbedout denoising_summary.txt
```  
  
Now, lets make zOTU table, containing information on how many times each of the zOTUs occurred in each of the libraries. We will do this by mapping trimmed reads to zOTUs.  
```
usearch -otutab all_samples_trimmed.fasta -zotus zotus.fasta -otutabout zotu_table.txt
```  
  
&nbsp;  
  
### OTU picking and chimeras removal using ASV as input

Add information about the number of sequences corresponding to each zOTU to \"**zotus.fasta**". For the subsequent steps to go as planned, that information need to be provided in a specific format... For now, Piotr wrote a lightweight script that takes two previously generated files --- **zotu_table_wo_tax.txt** and **zotus.fasta** --- and exports a new file, **new_zotus.fasta**, with the required info.  
```
add_values_to_zOTU_fasta.py zotu_table.txt zotus.fasta
```  
  
Now, let's use usearch to do the clustering. First, we sort the recently output fasta; then, we do clustering; finally, we assign all sequences to the clusters and compute the OTU table.  
```
usearch -sortbysize new_zotus.fasta -fastaout new_zotus_sorted.fasta -minsize 2  
usearch -cluster_otus new_zotus_sorted.fasta -otus otus.fasta -minsize 2 -relabel OTU -uparseout zotu_otu_relationships.txt  
usearch -usearch_global all_samples.fasta -db otus.fasta -strand plus -id 0.97 -otutabout otu_table.txt  
```
  
&nbsp;
  
### Assign taxonomy

At this step, we want to compare zOTU and OTU sequences against a curated sequence database in order to assign taxonomy. As in the previous cases, there are several ways to go about this: different tools, different databases, and different criteria. We think that one of the best ways is the function [**sintax**](https://www.drive5.com/usearch/manual/sintax_algo.html) implemented in **usearch** and **vsearch**, which does compute the probability of assignment to each taxonomic rank. This can be quite helpful when working with non-model organisms!   
&nbsp;
As reference databases, at the moment, we have successfully tested:  
* for 16S rRNA, a modified [SILVA v. 138](https://www.arb-silva.de) database, with multiple unpublished Auchenorrhyncha sequences and our spike-in sequences added:  
**/mnt/matrix/symbio/db/SILVA_138/SILVA_endo_spikeins_RDP.fasta**  
* for insect COI, a modified [MIDORI](http://www.reference-midori.info/index.html) database, with some erroneus sequences removed, and Alphaproteobacterial and spike-in sequences added:  
**/mnt/matrix/symbio/db/MIDORI/MIDORI_with_tax_spikeins_endo_RDP.fasta**  
  
Then, for 16S rRNA, you might want to use these commands to annotate your zOTU and representative OTU sequences ---  
```
vsearch --sintax zotus.fasta -db /mnt/matrix/symbio/db/SILVA_138/SILVA_endo_spikeins_RDP.fasta -tabbedout zotus.tax -strand both -sintax_cutoff 0.5
vsearch --sintax otus.fasta -db /mnt/matrix/symbio/db/SILVA_138/SILVA_endo_spikeins_RDP.fasta -tabbedout otus.tax -strand both -sintax_cutoff 0.5
```   
&nbsp;
And for COI, you might want to try these ---  
```
vsearch --sintax zotus.fasta -db /mnt/matrix/symbio/db/MIDORI/MIDORI_with_tax_spikeins_endo_RDP.fasta -tabbedout zotus.tax -strand both -sintax_cutoff 0.5
vsearch --sintax otus.fasta -db /mnt/matrix/symbio/db/MIDORI/MIDORI_with_tax_spikeins_endo_RDP.fasta -tabbedout otus.tax -strand both -sintax_cutoff 0.5
```   
  
In the output, you will find the confidence values of assignment at each taxonomic level, like here:    *d:Bacteria(1.00),p:Proteobacteria(1.00),c:Betaproteobacteria(0.92),o:Betaproteobacteria(0.92),f:Candidatus_Vidania(0.92),g:Vidania_endosymbiont_of_Dictyophara_multireticulata(0.89)*  
We feel that the info about the taxonomic level, e.g. "d:", "p:"... makes the output a bit cluttered. You can remove it using **sed**:  
```
sed -i 's/[dpcofgs]\://g' zotus.tax
sed -i 's/[dpcofgs]\://g' otus.tax
```  
&nbsp;  
  
  
### Putting all the results together
At this stage, the biologically relevant pieces of information that we have generated are:  
* The sequences of all zOTUs;  
* Information on the abundance of each zOTU in each library;  
* Info on the taxonomic classification of each zOTU;  
* Info on zOTU - OTU relationship: which OTU each of the zOTUs got classified to?  
* Same type of information for OTUs --- representative sequence, abundance, taxonomic classification...   
  
We need to put the info together. Of course, there are many ways of doing this! Piotr has spent many years doing this in Excel, which required lots of manual effort and was prone to human error. Diego had suggested doing this in R. But an easy way would be using the two scripts that Piotr has just written, [combine_zOTU_files.py](combine_zOTU_files.py) and [combine_OTU_files.py](combine_OTU_files.py).  
```
combine_zOTU_files.py zotu_table.txt zotus.tax zotus.fasta zotu_otu_relationships.txt
combine_OTU_files.py otu_table.txt otus.tax otus.fasta
```  
  
The output files, **zotu_table_expanded.txt** and **otu_table_expanded.txt**, should contain all the info that you may need to start focusing on the biology :)
  
Enjoy!  
  
  
  
