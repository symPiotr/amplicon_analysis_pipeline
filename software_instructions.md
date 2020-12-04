## Setting up access to the necessary software
Before starting any analyses, you want to make sure that you can use the necessary software. Doing this early will save you lots of frustration further down the line!  
  
  
### 1. Ensuring that you have "/mnt/matrix/symbio/bin" in your PATH
If you are working on the Institute of Environmental Sciences cluster, this is by far the easiest way of getting access to most software that we use.
After logging in to the cluster, in the command line mode, type into the terminal:  
  
`echo $PATH | sed 's/:/\n/g'`  
  
You should see a list of directories that the shell searches through when you enter a command. **Is "/mnt/matrix/symbio/bin" there?**  
  
Yes? Good! :smile:    
  
No? Type into the terminal:
```
echo "export PATH=/mnt/matrix/symbio/bin:$PATH" >> ~/.bashrc
source ~/.bashrc
```
... or add the above line to your .bashrc in another way.  
  
You should be set! :sunglasses:  
  

### 2. Ensuring that you have access to "symbio" conda environment on the cluster
_... to be written ..._
  
  
### 3. PEAR software
PEAR is a fast, memory-efficient and accurate pair-end read merger. You should have access through "/mnt/matrix/symbio/bin".  
More info at [https://cme.h-its.org/exelixis/web/software/pear/](https://cme.h-its.org/exelixis/web/software/pear/).  
  
  
### 4. VSEARCH software
VSEARCH is a versatile open-source tool for amplicon data analysis. You should have access through "/mnt/matrix/symbio/bin".  
More info at [https://github.com/torognes/vsearch](https://github.com/torognes/vsearch).  
  
  
### 5. USEARCH software
USEARCH is a powerful, popular versatile tool for amplicon data analysis. You should have access through "/mnt/matrix/symbio/bin".  
More info at [https://www.drive5.com/usearch/](https://www.drive5.com/usearch/).   
  
  
### 6. Our custom scripts
Our pipeline uses simple Python scripts for manipulating the output of some tools so that it is suitable as input to other tools. You should have access through "/mnt/matrix/symbio/bin". Alternatively, you may want to upload them somewhere where they can be executed!
* [add_values_to_zOTU_fasta.py](add_values_to_zOTU_fasta.py)  
  
  
### 7. R, qiime1
_... to be written ..._
