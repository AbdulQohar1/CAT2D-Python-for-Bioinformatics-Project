import os
import glob
import urllib.request
import subprocess

# download data set from zenodo
def download_data(url, raw_data):
  print(f'downloading data from zenodo...')
  # create the output directory if it doesn't exist
  os.makedirs(raw_data, exist_ok=True)

  # list of files to download
  files = [
    "SLGFSK-N_231335_r1_chr5_12_17.fastq.gz",
    "SLGFSK-N_231335_r2_chr5_12_17.fastq.gz",
    "SLGFSK-T_231336_r1_chr5_12_17.fastq.gz",
    "SLGFSK-T_231336_r2_chr5_12_17.fastq.gz",
    "hg19.chr5_12_17.fa.gz"
    ]

  # download each  file
  for file in files:
    file_url = "https://zenodo.org/record/2582555/files/" + file
    # construct complete file path
    file_path = os.path.join(raw_data, file) 
    print(f"Downloading {file}...")
    # download file to the full path
    urllib.request.urlretrieve(file_url, file_path) 
    print(f"Done with {file}")

  print('All files downloaded successfully!')

download_data(url="https://zenodo.org/record/2582555", raw_data="raw_data")

#write the name of the files in raw_data folder into list.txt
file_names = ["SLGFSK-N_231335", "SLGFSK-T_231336"]
with open('list.txt', 'w') as f:
  for name in file_names:
    f.write(f'{name} \n')

print(f"File names written to list.txt")

# installing packages (fastqc, multiqc) using conda
print("installing FastQC and MultiQC packages")
os.system('conda install -c bioconda fastqc multiqc  -y')
# conda install -c bioconda fastqc multiqc -y
print("installation complete!")

# write the names of the files in raw_data folder into list.txt
raw_data_dir = "/content/project/raw_data"
fastqc_report_dir = "/content/project/Fastqc_report"

with open('/content/project/list.txt', 'w') as f:
  for file_name in os.listdir(raw_data_dir):
    f.write(f'{file_name} \n')
print(f"File names written to list.txt")

def run_fastqc(raw_data_path, fastqc_report):
  print("data processing...")

  # create Fastqc_report directory
  os.makedirs(fastqc_report, exist_ok=True)
  print("Fastqc_Report directory created")

  # get a list of fastq.gz files in the raw_data directory
  fastq_files = glob.glob(os.path.join(raw_data_path, "*.fastq.gz"))

  # process each fastq file
  for fastq_file in fastq_files:
    try:
      subprocess.run(['fastqc', fastq_file, '-o', fastqc_report], check=True)
      print(f"FastQC report generated for {fastq_file}")
    except FileNotFoundError as e:
      print(f'Error running FastQC on {fastq_file}: {e}')
      print(f'Skipping file: {fastq_file}')
    except subprocess.CalledProcessError as e:
      print(f'Error running FastQC on {fastq_file}: {e}')
      print(f'Skipping file: {fastq_file}')

  print("FastQC processing completed!")

print("MultiQC processing...")
subprocess.run(['multiqc', '/content/project/Fastqc_report', '-o', '/content/project/Fastqc_report'])

print("download and unzip Trimmomatic...")
# !wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.39.zip
os.system("unzip Trimmomatic-0.39.zip -d /content/Trimmomatic")

def process_trimmed_reads():
  # create trimmed_reads and Fastqc_results directories
  os.makedirs("/content/project/trimmed_reads", exist_ok=True)
  os.makedirs("/content/project/trimmed_reads/Fastqc_results", exist_ok=True)

  # get a list of forward read files in the raw_data directory
  raw_data_path = "/content/project/raw_data"
  r1_files = glob.glob(os.path.join(raw_data_path, "*_r1_*.fastq.gz"))

  # process each pair of read files
  for r1_path in r1_files:
    sample = os.path.basename(r1_path).split('_r1_')[0]
    r2_path = os.path.join(raw_data_path, f"{sample}_r2_chr5_12_17.fastq.gz")

    print(f"Processing sample: {sample}")
    r1_paired_out = f'/content/project/trimmed_reads/{sample}_r1_paired.fq.gz'
    r1_unpaired_out = f'/content/project/trimmed_reads/{sample}_r1_unpaired.fq.gz'
    r2_paired_out = f'/content/project/trimmed_reads/{sample}_r2_paired.fq.gz'
    r2_unpaired_out = f'/content/project/trimmed_reads/{sample}_r2_unpaired.fq.gz'

    trimmomatic_command = [
      'java', '-jar', '/content/Trimmomatic/Trimmomatic-0.39/trimmomatic-0.39.jar', 'PE', '-threads', '8',
      r1_path, r2_path,
      r1_paired_out, r1_unpaired_out,
      r2_paired_out, r2_unpaired_out,
      'ILLUMINACLIP:/content/Trimmomatic/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:8:keepBothReads',
      'LEADING:3', 'TRAILING:10', 'MINLEN:25'
    ]

    try:
      print(f"Running Trimmomatic for {sample}...")
      subprocess.run(trimmomatic_command, check=True)
      print(f"Trimmomatic completed for {sample}")

      fastqc_cmd = [
        'fastqc', r1_paired_out, r2_paired_out, '-o', '/content/project/trimmed_reads/Fastqc_results'
      ]

      print(f"Running FastQC on trimmed reads for {sample}...")
      subprocess.run(fastqc_cmd, check=True)
      print(f"FastQC completed for trimmed reads of {sample}")

    except subprocess.CalledProcessError as e:
      print(f'Error running command for {sample}: {e}')
      print(f'Skipping sample: {sample}')

  print("Trimmomatic and FastQC processing of trimmed reads completed!")

# multiqc processing of trimmed Fastqc results
print("MultiQC processing trimmed Fastqc results...")
subprocess.run(['multiqc', '/content/project/trimmed_reads/Fastqc_results', '-o', '/content/project/trimmed_reads/Fastqc_results'])
print("MultiQC processing complete!")

# postprocessing reads
# install bwa, samtools, bamtools
print("Installing bioinformatics post processing packages...")

os.system("apt-get update")
os.system("apt-get install -y bwa samtools bamtools")
print('post processing packages installation completed...')

def unzip_and_index_reference():
  # unzip the reference genome
  os.system("gunzip /content/project/raw_data/hg19.chr5_12_17.fa.gz")
  print('reference file unzip completed...')

  print("Indexing the reference genome using bwa...")
  reference_genome = "/content/project/raw_data/hg19.chr5_12_17.fa"

  try:
    subprocess.run(['bwa', 'index', reference_genome], check=True)
    print(f"Indexing of {reference_genome} completed.")
  except subprocess.CalledProcessError as e:
    print(f"Error during bwa index command execution: {e}")

# mapping directory
trimmed_reads_path = "/content/project/trimmed_reads"
mapping_dir = "/content/project/Mapping"
reference_genome = "/content/project/hg19.chr5_12_17.fa"

samples = set()
for file_name in os.listdir(trimmed_reads_path):
  if "_r1_paired.fq.gz" in file_name:
    samples.add(file_name.split("_r1_paired.fq.gz")[0])

print("Sample names from trimmed reads:")
for sample in samples:
  print(sample)


def bwa_alignment():
  # create Mapping directory
  os.makedirs("/content/project/Mapping", exist_ok=True)
  print("Mapping directory created")

  # Process each sample
  for sample in samples:
    print(f"Performing BWA alignment for sample: {sample}")

    # Define input and output paths
    r1_paired_in = os.path.join(trimmed_reads_path, f"{sample}_r1_paired.fq.gz")
    r2_paired_in = os.path.join(trimmed_reads_path, f"{sample}_r2_paired.fq.gz")
    sam_output = os.path.join("/content/project/Mapping", f"{sample}.sam")

    # BWA command
    rg_id = sample.split('_')[1] if '_' in sample else sample
    rg_sm = "Normal" if "N_" in sample else "Tumor"

    bwa_command = [
      'bwa', 'mem', '-R',
      f'@RG\\tID:{rg_id}\\tSM:{rg_sm}',
      reference_genome,
      r1_paired_in, r2_paired_in
    ]

    # Run the BWA command and redirect output to the SAM file
    try:
      with open(sam_output, 'w') as outfile:
        subprocess.run(bwa_command, check=True, stdout=outfile)
      print(f"BWA alignment completed and saved to {sam_output}")
    except subprocess.CalledProcessError as e:
      print(f'Error running BWA for {sample}: {e}')
      print(f'Skipping sample: {sample}')

  print("BWA alignment for all samples completed!")

def convert_sam_to_sorted_bam_and_index(sample_set):
  sample_list = list(sample_set)

  # Process each sample
  for sample in sample_list :
    print(f"Processing sample: {sample}")

    sam_input = os.path.join("/content/project/Mapping", f"{sample}.sam")
    bam_output = os.path.join("/content/project/Mapping", f"{sample}.sorted.bam")

    # Check if SAM file exists before processing
    if not os.path.exists(sam_input):
      print(f"Warning: {sam_input} not found, skipping {sample}")
      continue

    # Convert SAM to BAM and sort
    print(f"Converting {sample}.sam to sorted BAM...")
    sam_to_bam_command = [
      'samtools', 'view', '-@', '20', '-S', '-b', sam_input
    ]
    sort_bam_command = [
      'samtools', 'sort', '-@', '8', '-o',  bam_output, '-'
    ]

    try:
      # subprocess.Popen pipes the output from view to sort
      view_process = subprocess.Popen(sam_to_bam_command, stdout=subprocess.PIPE)
      sort_process = subprocess.Popen(sort_bam_command, stdin= view_process.stdout)
      view_process.stdout.close()

      view_process.wait()
      sort_process.wait()

      # check both processes for errors
      if view_process.returncode != 0:
        raise subprocess.CalledProcessError(view_process.returncode, sam_to_bam_command)
      if sort_process.returncode != 0:
        raise subprocess.CalledProcessError(sort_process.returncode, sort_bam_command)

      print(f"Conversion and sorting completed for {sample}.sorted.bam")

      # Index BAM file
      print(f"Indexing {sample}.sorted.bam...")
      index_command = [
        'samtools', 'index', bam_output
      ]
      subprocess.run(index_command, check=True)
      print(f"Indexing completed for {sample}.sorted.bam.bai")

    except FileNotFoundError as e:
      print(f'Error: Command not found. Please ensure samtools is installed: {e}')
      print(f'Skipping sample: {sample}')
    except subprocess.CalledProcessError as e:
      print(f'Error during processing for {sample}: {e}')
      print(f'Skipping sample: {sample}')

  print("SAM to sorted BAM conversion and indexing for all samples completed!")

# BAM file filtering
def bam_file_filtering(sample_set):
  sample_list = list(sample_set)

  for sample in sample_list:
    print(f"Processing sample: {sample}")

    sorted_bam = os.path.join("/content/project/Mapping", f"{sample}.sorted.bam")
    filtered_bam = os.path.join("/content/project/Mapping", f"{sample}.filtered1.bam")

    # Check if sorted BAM file exists before processing
    if not os.path.exists(sorted_bam):
      print(f"Warning: {sorted_bam} not found, skipping {sample}")
      continue

    # Filter BAM file command
    print(f"Filtering {sample}.sorted.bam...")
    bam_filtering_command = [
      'samtools', 'view', '-q', '1', '-f', '0x2', '-F', '0x8', '-b', sorted_bam
    ]

    try:
      # filter BAM file
      with open(filtered_bam, 'wb') as outfile:
        subprocess.run(bam_filtering_command, check=True, stdout=outfile)
      print(f"Filtering completed for {sample}.filtered1.bam")

      # generate flagstat report
      print(f'Generating flagstat for {sample}.filtered1.bam...')
      flagstat_output = os.path.join('/content/project/Mapping', f"{sample}.filtered1.flagstat.txt")

      # flagstat command
      flagstat_command = [
        'samtools', 'flagstat', filtered_bam
      ]

      with open(flagstat_output, 'w') as outfile:
        subprocess.run(flagstat_command, check=True, stdout=outfile)
      print(f"Flagstat completed for {sample}. Results saved to {flagstat_output}")

    except FileNotFoundError as e:
      print(f'Error: Command not found. Please ensure samtools is installed: {e}')
      print(f'Skipping sample: {sample}')
    except subprocess.CalledProcessError as e:
      print(f'Error during processing for {sample}: {e}')

  print("BAM file filtering for all samples completed!")

def mark_duplicates(sample_set):
  sample_list = list(sample_set)

  # process each sample for duplicate marking
  for sample in sample_list:
    print(f"Processing sample: {sample}")

    # define file paths
    filtered_bam = os.path.join(mapping_dir, f"{sample}.filtered1.bam")
    namecollate_prefix = os.path.join(mapping_dir, f"{sample}.namecollate")
    namecollate_bam = f"{namecollate_prefix}.bam"
    fixmate_bam = os.path.join(mapping_dir, f"{sample}.fixmate.bam")
    positionsort_bam = os.path.join(mapping_dir, f"{sample}.positionsort.bam")
    clean_bam = os.path.join(mapping_dir, f"{sample}.clean.bam")

    # check if filtered BAM file exists before processing
    if not os.path.exists(filtered_bam):
      print(f"Warning: {filtered_bam} not found, skipping {sample}")
      continue

    print(f"Starting duplicate marking for {sample}...")

    try:
      # step 1: samtools collate (note: uses prefix, not full filename)
      print(f"Running samtools collate for {sample}...")
      collate_command = ['samtools', 'collate', filtered_bam, namecollate_prefix]
      subprocess.run(collate_command, check=True)
      print(f"samtools collate completed for {sample}")

      # step 2: samtools fixmate
      print(f"Running samtools fixmate for {sample}...")
      fixmate_command = ['samtools', 'fixmate', '-m', '-O', 'BAM', namecollate_bam, fixmate_bam]
      result = subprocess.run(fixmate_command, check=True, capture_output=True, text=True)
      print(f"samtools fixmate completed for {sample}")

      # step 3: samtools sort by position
      print(f"Running samtools sort for {sample}...")
      sort_command = ['samtools', 'sort', '-@', '4', '-o', positionsort_bam, fixmate_bam]
      subprocess.run(sort_command, check=True)
      print(f"samtools sort completed for {sample}")

      # step 4: samtools markdup
      print(f"Running samtools markdup for {sample}...")
      markdup_command = ['samtools', 'markdup', '-@', '4', '-r', positionsort_bam, clean_bam]
      subprocess.run(markdup_command, check=True)
      print(f"samtools markdup completed for {sample}")

      # step 5: Index the clean BAM file
      print(f"Indexing {sample}.clean.bam...")
      index_command = ['samtools', 'index', clean_bam]
      subprocess.run(index_command, check=True)
      print(f"Indexing completed for {sample}.clean.bam")

      # generate final statistics
      print(f"Generating final flagstat for {sample}.clean.bam...")
      flagstat_output = os.path.join(mapping_dir, f"{sample}.clean.flagstat.txt")
      flagstat_command = ['samtools', 'flagstat', clean_bam]

      with open(flagstat_output, 'w') as outfile:
        subprocess.run(flagstat_command, check=True, stdout=outfile)
      print(f"Final flagstat saved to {flagstat_output}")

    except FileNotFoundError as e:
      print(f'Error: Command not found. Please ensure samtools is installed: {e}')
      print(f'Skipping sample: {sample}')
      continue
    except subprocess.CalledProcessError as e:
      print(f'Error during processing for {sample}: {e}')
      print(f'Command failed with return code: {e.returncode}')
      print(f'Skipping sample: {sample}')
      continue

  print("Duplicate marking for all samples completed!")

# !sudo apt-get install freebayes

def bam_left_align(sample_set):
  sample_list = list(sample_set)

  # process each sample for left alignment
  for sample in sample_list:
    print(f"Processing sample: {sample}")

    # define file paths
    clean_bam = os.path.join(mapping_dir, f"{sample}.clean.bam")
    leftalign_bam = os.path.join(mapping_dir, f"{sample}.leftAlign.bam")

    # check if clean BAM file exists before processing
    if not os.path.exists(clean_bam):
      print(f"Warning: {clean_bam} not found, skipping {sample}")
      continue

    print(f"Starting left alignment for {sample}...")

    try:
      print(f"Running bamleftalign for {sample}...")

      # subprocess.Popen to handles the pipe operation
      cat_process = subprocess.Popen(['cat', clean_bam], stdout=subprocess.PIPE)

      bamleftalign_command = [
        'bamleftalign',
        '-f', reference_genome,
        '-m', '5',
        '-c'
      ]

      with open(leftalign_bam, 'w') as outfile:
        bamleftalign_process = subprocess.Popen(
          bamleftalign_command,
          stdin=cat_process.stdout,
          stdout=outfile,
          stderr=subprocess.PIPE
        )

        # close cat stdout to allow it to receive SIGPIPE
        cat_process.stdout.close()

        # wait for both processes to complete
        cat_returncode = cat_process.wait()
        bamleftalign_returncode = bamleftalign_process.wait()

      print(f"Left alignment completed for {sample}")

    except subprocess.CalledProcessError as e:
      print(f'Error during processing for {sample}: {e}')
      print(f'Skipping sample: {sample}')
      continue
    except Exception as e:
      print(f'Unexpected error for {sample}: {e}')
      print(f'Skipping sample: {sample}')
      continue

  print("BAM left alignment for all samples completed!")

def bam_recalibration_and_refiltering(sample_set):
  sample_list = list(sample_set)

  for sample in sample_list:
    print(f"Processing sample: {sample}")

    # Define file paths
    leftalign_bam = os.path.join(mapping_dir, f"{sample}.leftAlign.bam")
    recalibrate_bam = os.path.join(mapping_dir, f"{sample}.recalibrate.bam")
    refilter_bam = os.path.join(mapping_dir, f"{sample}.refilter.bam")

    # Check if leftAlign BAM file exists
    if not os.path.exists(leftalign_bam):
      print(f"Warning: {leftalign_bam} not found, skipping {sample}")
      continue

    # Check if reference genome exists
    if not os.path.exists(reference_genome):
      print(f"Warning: {reference_genome} not found, skipping {sample}")
      continue

    try:
      # Step 1: Recalibration using samtools calmd
      print(f"Running samtools calmd for {sample}...")
      calmd_command = [
          'samtools', 'calmd',
          '-@', '32',
          '-b',
          leftalign_bam, reference_genome
      ]

      with open(recalibrate_bam, 'w') as outfile:
          subprocess.run(calmd_command, check=True, stdout=outfile)
      print(f"Recalibration completed for {sample}")

      # Step 2: Refiltering using bamtools filter
      print(f"Running bamtools filter for {sample}...")
      filter_command = [
        'bamtools', 'filter',
        '-in', recalibrate_bam,
        '-mapQuality', '<=254'
      ]

      with open(refilter_bam, 'w') as outfile:
        subprocess.run(filter_command, check=True, stdout=outfile)
      print(f"Refiltering completed for {sample}")

    except FileNotFoundError as e:
      print(f'Error: Command not found: {e}')
      print(f'Skipping sample: {sample}')
      continue
    except subprocess.CalledProcessError as e:
      print(f'Error during processing for {sample}: {e}')
      print(f'Skipping sample: {sample}')
      continue

  print("BAM recalibration and refiltering for all samples completed!")

#getting variant calling package
print("Downloading VarScan...")
# !wget https://sourceforge.net/projects/varscan/files/VarScan.v2.3.9.jar

# create the variant directory
os.makedirs("/content/project/Variants", exist_ok=True)

# Get sample names from trimmed reads directory
trimmed_reads_path = "/content/project/trimmed_reads"
mapping_dir = "/content/project/Mapping"
variants_dir = "/content/project/Variants"
reference_genome = "/content/project/raw_data/hg19.chr5_12_17.fa"


def samtools_mpileup(sample_set):
  # generates mpileup files using samtools mpileup.
  sample_list = list(sample_set)

  # ensure variants directory exists
  os.makedirs(variants_dir, exist_ok=True)

  for sample in sample_list:
    print(f"Processing sample: {sample}")

    # Define file paths
    refilter_bam = os.path.join(mapping_dir, f"{sample}.refilter.bam")
    pileup_file = os.path.join(variants_dir, f"{sample}.pileup")

    # Check if refilter BAM file exists
    if not os.path.exists(refilter_bam):
      print(f"Warning: {refilter_bam} not found, skipping {sample}")
      continue

    print(f"Running samtools mpileup for {sample}...")
    try:
      # samtools mpileup -f reference.fa refilter.bam --min-MQ 1 --min-BQ 28 > pileup
      mpileup_command = [
          'samtools', 'mpileup',
          '-f', reference_genome,
          refilter_bam,
          '--min-MQ', '1',
          '--min-BQ', '28'
      ]

      with open(pileup_file, 'w') as outfile:
        subprocess.run(mpileup_command, check=True, stdout=outfile)

      print(f"Mpileup completed for {sample}")

    except FileNotFoundError as e:
      print(f'Error: samtools not found: {e}')
      print(f'Skipping sample: {sample}')
      continue
    except subprocess.CalledProcessError as e:
      print(f'Error during mpileup for {sample}: {e}')
      print(f'Skipping sample: {sample}')
      continue

  print("Samtools mpileup for all samples completed!")

def varscan_somatic_calling(samples):
  # run VarScan somatic calling for paired normal/tumor samples
  # process each sample pair
  for normal_sample, tumor_sample in samples:
    print(f"Processing sample: {normal_sample} (normal) vs {tumor_sample} (tumor)...")

    # define file paths (inside the loop)
    normal_pileup = os.path.join('/content/project/Variants', f"{normal_sample}.pileup")
    tumor_pileup = os.path.join('/content/project/Variants', f"{tumor_sample}.pileup")

    # create output/result prefix using sample identifiers
    sample_id = normal_sample.split('-')[0]
    result = os.path.join('/content/project/Variants', f"{sample_id}_somatic")

    # purity variables
    normal_purity = 1
    tumor_purity = 0.5

    # check if input files exist
    if not os.path.exists(normal_pileup):
      print(f"Missing file: {normal_pileup}")
      continue
    if not os.path.exists(tumor_pileup):
      print(f"Missing file: {tumor_pileup}")
      continue

    print(f"Running VarScan: {normal_sample} vs {tumor_sample}")

    # varScan command
    varscan_command = [
      'java', '-jar', 'VarScan.v2.3.9.jar', 'somatic',
      normal_pileup, tumor_pileup, result,
      '--normal-purity', str(normal_purity),
      '--tumor-purity', str(tumor_purity),
      '--output-vcf', '1'
    ]

    try:
      # run varscan command
      subprocess.run(varscan_command, check=True)
      print(f"varScan completed for {normal_sample} vs {tumor_sample}")

    except subprocess.CalledProcessError as e:
      print(f"Error during VarScan for {normal_sample} vs {tumor_sample}: {e}")
      continue

  print("VarScan somatic calling completed for all samples!")
# define sample pairs
samples = [
  ("SLGFSK-N_231335", "SLGFSK-T_231336")
]



print("Installing bgzip, tabix, and bcftools..")
# !sudo apt-get update
os.system("sudo apt-get install -y bgzip tabix")
# !sudo apt-get install bcftools
print("Installation complete!")


def merge_vcf_files(sample):
  # merge VarScan VCF files for paired normal/tumor samples
  variants_dir = "/content/project/Variants"

  # define file paths
  snp_vcf = os.path.join(variants_dir, f"{sample}.snp.vcf")
  indel_vcf = os.path.join(variants_dir, f"{sample}.indel.vcf")
  snp_vcf_gz = os.path.join(variants_dir, f"{sample}.snp.vcf.gz")
  indel_vcf_gz = os.path.join(variants_dir, f"{sample}.indel.vcf.gz")
  merged_vcf = os.path.join(variants_dir, f"{sample}_merged.vcf")

  print(f"Starting VCF merge process for {sample}...")
  # Check if input files exist
  if not os.path.exists(snp_vcf):
    print(f"Missing file: {snp_vcf}")
    return False
  if not os.path.exists(indel_vcf):
    print(f"Missing file: {indel_vcf}")
    return False
  try:
    # Step 1: compress SNP VCF file
    print(f"Compressing SNP VCF file...")
    bgzip_snp_command = ['bgzip', '-c', snp_vcf]
    with open(snp_vcf_gz, 'wb') as outfile:
      subprocess.run(bgzip_snp_command, check=True, stdout=outfile)
    print(f" Created: {os.path.basename(snp_vcf_gz)}")

    # Step 2: compress indel VCF file
    print(f"Compressing indel VCF file...")
    bgzip_indel_command = ['bgzip', '-c', indel_vcf]
    with open(indel_vcf_gz, 'wb') as outfile:
      subprocess.run(bgzip_indel_command, stdout=outfile, check=True)
    print(f" Created: {os.path.basename(indel_vcf_gz)}")

    # Step 3: index SNP VCF && indel VCF file
    print(f"Indexing SNP VCF file...")
    # tabix_snp_command = ['tabix', snp_vcf_gz]
    tabix_snp_command = ['tabix', '-p', 'vcf', snp_vcf_gz]
    subprocess.run(tabix_snp_command, check=True)
    print(f" Indexed: {os.path.basename(snp_vcf_gz)}")

    print(f"Indexing indel VCF file...")
    # tabix_indel_command = ['tabix', indel_vcf_gz]
    tabix_indel_command = ['tabix', '-p', 'vcf', indel_vcf_gz]
    subprocess.run(tabix_indel_command, check=True)
    print(f" Indexed: {os.path.basename(indel_vcf_gz)}")

    # Step 4: Merge VCF files
    print(f"Merging VCF files...")
    merge_vcf_command = ['bcftools', 'merge', '--force-samples', snp_vcf_gz, indel_vcf_gz]
    # merge_vcf_command = ['bcftools', 'merge', snp_vcf_gz, indel_vcf_gz]
    with open(merged_vcf, 'w') as outfile:
      subprocess.run(merge_vcf_command, stdout=outfile, check=True)
    print(f" Created merged VCF: {os.path.basename(merged_vcf)}")

    return True
  except subprocess.CalledProcessError as e:
    print(f"Error during VCF merge for {sample}: {e}")
    return False
  except FileNotFoundError as e:
    print(f"Error: Command not found: {e}")
    return False

# run annotation
print("Running snpEff annotation...")

def download_and_prepare_snpeff():
  print("Downloading snpEff...")
  subprocess.run(
      [ "wget", "-O", "snpEff_latest_core.zip", "https://sourceforge.net/projects/snpeff/files/snpEff_latest_core.zip"
  ], check=True)
  print("Download complete")

  print("Unzipping snpEff...")
  subprocess.run(["unzip", "snpEff_latest_core.zip"], check=True)
  print(" snpEff unzipped successfully!")

  # update java to new version for compatibility
  subprocess.run(["apt-get", "update"], check=True)
  subprocess.run(["apt-get", "install", "-y", "openjdk-21-jdk"], check=True)

  # change to snpEff directory
  if os.path.exists("snpEff"):
    os.chdir("snpEff")
    print("Changed to snpEff directory")

  # download snpEff hg19 database
  print("Downloading snpEff database...")
  subprocess.run([
    "java", "-Xmx8g", "-jar", "snpEff.jar", "download", "hg19"
  ], check=True)
  print("Database download successful")

def run_snpeff_annotation():
  # define file paths
  merged_vcf = "/content/project/Variants/SLGFSK_merged.vcf"
  annotated_vcf = "/content/project/Variants/SLGFSK_merged_annotated.vcf"

  # change to snpEff directory
  if os.path.exists("snpEff"):
    os.chdir("snpEff")
    print("Changed to snpEff directory")

  # download database with error capture
  print("Downloading snpEff database...")
  subprocess.run([
    "java", "-Xmx8g", "-jar", "snpEff.jar", "download", "hg19"
  ], capture_output=True, text=True, check=True)
  print("Database download successful")

  print("Annotating variants with snpEff...")
  try:
    with open(annotated_vcf, "w") as outfile:
      result = subprocess.run([
        "java", "-Xmx8g", "-jar", "snpEff.jar", "hg19", merged_vcf
      ], stdout=outfile, stderr=subprocess.PIPE, text=True, check=True)
    print("Annotation complete!")
    print(f"Output saved to: {annotated_vcf}")
  except subprocess.CalledProcessError as e:
    print(f"Annotation failed with exit code: {e.returncode}")
    print(f"Error output: {e.stderr}")


#clinical annotation using gemini
# wget https://raw.github.com/arq5x/gemini/master/gemini/scripts/gemini_install.py
#python gemini_install.py /usr/local /usr/local/share/gemini

# gemini load -v Variants/SLGFSK.ann.vcf -t snpEff Annotation/gemini.db
print
subprocess.run(["wget", "https://raw.github.com/arq5x/gemini/master/gemini/scripts/gemini_install.py"], check=True)
print("gemini successfully installed!")

def load_gemini():
  # create annotation directory for gemini
  os.makedirs("/content/project/Annotation", exist_ok=True)

  # define file paths
  ann_vcf_file="/content/project/Variants/SLGFSK_merged_annotated.vcf"
  gemini_db="/content/project/Annotation/gemini.db"

  try:
    subprocess.run(["gemini", "load", "-v", ann_vcf_file, "-t", "snpEff", gemini_db], check=True)
    print("Gemini database loaded successfully!")
  except subprocess.CalledProcessError as e:
    print(f"Error loading Gemini database: {e}")


run_fastqc(raw_data_dir, fastqc_report_dir)
process_trimmed_reads()
unzip_and_index_reference()
bwa_alignment()
convert_sam_to_sorted_bam_and_index(samples)
bam_file_filtering(samples)
mark_duplicates(samples)
bam_left_align(samples)
bam_recalibration_and_refiltering(samples)
samtools_mpileup(samples)
varscan_somatic_calling(samples)
merge_vcf_files("SLGFSK")
download_and_prepare_snpeff()
run_snpeff_annotation()
load_gemini()
























# def download_and_prepare_snpeff():
#   # print("Downloading snpEff...")
#   # subprocess.run(
#   #     [ "wget", "-O", "snpEff_latest_core.zip", "https://snpeff.odsp.astrazeneca.com/versions/snpEff_latest_core.zip"
#   # ], check=True)
#   #     # "wget", "-O", "snpEff_latest_core.zip", "https://sourceforge.net/projects/snpeff/files/snpEff_latest_core.zip/download",
#   # # ], check=True)
#   # print("✓ Download complete")

#   # print("Unzipping snpEff...")
#   # subprocess.run(["unzip", "snpEff_latest_core.zip"], check=True)
#   # print("snpEff unzipped successfully!")

#   print("Downloading snpEff database...")
#   subprocess.run([
#     "java", "-Xmx8g", "-jar", "snpEff.jar", "download", "hg19"
#   ], check=True)

#   print("Annotating variants with snpEff...")
#   merged_vcf = "/content/project/Variants/SLGFSK_merged.vcf"
#   annotated_vcf = "/content/project/Variants/SLGFSK_merged_annotated.vcf"

#   # with open(merged_vcf, "r") as infile:
#   with open(annotated_vcf, "wb") as outfile:
#     subprocess.run([
#       "java", "-Xmx8g", "-jar", "snpEff.jar", "hg19", merged_vcf
#       ], stdout=outfile, check=True)

# download_and_prepare_snpeff()