## Identification of somatic and germline variants from tumor and normal sample pairs

# Introduction
Genetic mutations, ranging from single-nucleotide substitutions to more complex multi-base alterations in DNA or RNA, are fundamental drivers of biological variation. While some mutations confer evolutionary advantages and others remain neutral, a significant proportion are deleterious and contribute to human disease. Cancer, the second leading cause of mortality globally, is particularly associated with harmful mutations that disrupt key regulatory genes. Among these, mutations in tumor suppressor genes are especially critical, as they can impair normal cell-cycle control and enable uncontrolled proliferation, tissue invasion, and destruction of healthy cells.

Mutations implicated in cancer may be germline (inherited and present in all cells) or somatic (acquired during an individual’s lifetime). A frequent genetic alteration linked to cancer progression is Loss of Heterozygosity (LOH), in which one functional copy of a gene, or a group of genes, is lost. LOH events compromise genomic stability and often accelerate tumorigenesis. 

From a detection perspective, germline mutations can be readily identified by comparing an individual’s genome sequence to a standardized reference. In contrast, somatic mutations require a paired analysis of both tumor and matched normal tissue DNA from the same patient, in order to distinguish acquired changes from inherited variation. This distinction highlights the complexity of cancer genomics and underscores the need for precise computational and experimental approaches in mutation profiling.

This project re-implements a Linux-based bioinformatics workflow in Python to identify both germline and somatic variants, including those impacted by Loss of Heterozygosity (LOH). By comparing matched healthy and tumor tissue samples, the pipeline pinpoints variant sites and affected genes that may contribute to the disease development. 

Sources of reproduced workflows: 
On GitHub: https://github.com/Fredrick-Kakembo/Somatic-and-Germline-variant-Identification-from-Tumor-and-normal-Sample-Pairs

There's a [report](https://docs.google.com/document/d/1JAIOBHPqU7JYxFztsD6F1roz6BJmerrtpcXdrsqHXRM/edit?usp=sharing)  here that describes the steps involved, software packages used, and data used to test the script.

## Requirements

- **Python 3.6+**
- **Conda** (for package installation)
- **Bioinformatics tools** (installed automatically if missing):
  - FastQC, MultiQC, Trimmomatic, BWA, Samtools, Bamtools, VarScan, bgzip, tabix, bcftools, snpEff, Gemini

> **Note:** The script uses `os.system` and `subprocess` to install and run most tools while some requires using direct linux command for complete and effective installation process. Ensure you have admin privileges and internet access. 

Also the gradual workflow execution process can be found in the execution.ipynb file. 
---


# Sources of reporduced workflows: 
On GitHub: https://github.com/Fredrick-Kakembo/Somatic-and-Germline-variant-Identification-from-Tumor-and-normal-Sample-Pairs
On Galaxy: https://training.galaxyproject.org/training-material/topics/variant-analysis/tutorials/somatic-variants/tutorial.html 



## Directory Structure
```
project/
├── project.py
├── list.txt
├── raw_data/
│   ├── SLGFSK-N_231335_r1_chr5_12_17.fastq.gz
│   ├── SLGFSK-N_231335_r2_chr5_12_17.fastq.gz
│   ├── SLGFSK-T_231336_r1_chr5_12_17.fastq.gz
│   ├── SLGFSK-T_231336_r2_chr5_12_17.fastq.gz
│   └── hg19.chr5_12_17.fa.gz
├── Fastqc_report/
├── trimmed_reads/
│   ├── *_paired.fq.gz
│   ├── *_unpaired.fq.gz
│   └── Fastqc_results/
├── Mapping/
│   ├── *.sam
│   ├── *.sorted.bam
│   ├── *.filtered1.bam
│   ├── *.clean.bam
│   ├── *.leftAlign.bam
│   ├── *.recalibrate.bam
│   ├── *.refilter.bam
│   └── *.flagstat.txt
├── Variants/
│   ├── *.pileup
│   ├── *.snp.vcf
│   ├── *.indel.vcf
│   ├── *_merged.vcf
│   └── *_merged_annotated.vcf
├── Annotation/
│   └── gemini.db
└── README.md
```


