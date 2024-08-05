import os 
import pandas as pd 
import csv 
import re
from xvfbwrapper import Xvfb
import subprocess as sp
from .constants import MAF_TSV_COL_MAP, VCF_TSV_COL_MAP

def file_exists(myfile, kill = False):
    '''
    Checks to make sure a file exists, optionally kills the script
    '''
    if not os.path.isfile(myfile):
        raise Exception(f"ERROR: File '{myfile}' does not exist!")


def convert_annotated_file_to_bed(dmp_df, tumorid, region_file, nf4_mode):
    '''
    Converts annotated files (annotated_exonic/AllSomaticMutIndel_withAlleleDepth) to BED format for screenshotting
    '''
    # Read and format DMP input
    dmp_df = dmp_df.fillna('')
    dmp_df = dmp_df[dmp_df.Sample == tumorid]
    if nf4_mode:
        dmp_df['AAchange'] = dmp_df['AAchange'].str.replace('*','Ter')


# Create output bed
    # out_bed = tumorid + ".bed"
    out_complete = region_file
    # out_file = open(out_complete, 'wb')
    out_file = open(out_complete, 'w')
    out_writer = csv.writer(out_file, delimiter="\t")

    for idx, row in dmp_df.iterrows():
        chromosome = row['Chrom']
        ref = row['Ref']
        alt = row['Alt']
        ref_length = len(ref)
        alt_length = len(alt)
        start_position = row['Start']
        if nf4_mode:
            aa_change =  "_" + row['AAchange']
        else:
            aa_change = ''
# non-indels
        if ref_length == alt_length:
            end_position = row['Start']
            ss_file = str(row['Chrom']) + ":" + str(start_position) + aa_change + ".png"
# indels
        elif ref_length != alt_length:
            if ref_length < alt_length: # insertion
                ref = "-"
                alt = alt[ref_length:]
                end_position = start_position # while incorrect for normal BED, this is necessary for IGV because IGV will take SS at midpoint between start/end
                ss_file = str(row['Chrom']) + ":" + str(start_position) + aa_change + ".png"
            elif ref_length > alt_length: # deletion
                alt = "-"
                ref = ref[alt_length:]
                hgvs_start = row['Start']
                start_position += 1
                end_position = start_position # while incorrect for normal BED, this is necessary for IGV because IGV will take SS at midpoint between start/end
                ss_file = str(row['Chrom']) + ":" + str(hgvs_start) + aa_change + ".png"

        bed_file = [chromosome, start_position, end_position, ss_file]
        out_writer.writerow(bed_file)


def make_chrom_region_list(region_file, nf4_mode= False):
    '''
    Creates a list of tuples representing the regions from the BED file;
    [(chrom, start, stop), ...]
    '''
    region_list = []
    with open(region_file) as f:
        for line in f:
            if nf4_mode == True:
                if len(line.split()) >= 4:
                    chrom, start, stop, name = line.split()[0:4]
                    region_list.append((chrom, start, stop, name))
            else:
                if len(line.split()) >= 3:
                    chrom, start, stop = line.split()[0:3]
                    region_list.append((chrom, start, stop))
                elif len(line.split()) == 2:
                    chrom, start = line.split()
                    region_list.append((chrom, start, start))
    return(region_list)


def make_IGV_chrom_loc(region):
    '''
    return a chrom location string in IGV format
    region is a tuple with at least 3 entries
    '''
    chrom, start, stop = region[0:3]
    return('{}:{}-{}'.format(chrom, start, stop))


def make_snapshot_filename(region, height, suffix = None):
    '''
    formats a filename for the IGV snapshot
    region is a tuple with at least 3 entries; if a 4th entry exists, use it as the filename
    '''
    if len(region) >= 4:
        chrom, start, stop, name = region[0:4]
        return('{}'.format(name)) # '{}.png'.format(name) # don't include file extension! user must do this ahead of time!
    elif len(region) == 3:
        chrom, start, stop = region
        if suffix == None:
            return('{}_{}_{}_h{}.png'.format(chrom, start, stop, height))
        elif suffix != None:
            return('{}_{}_{}_h{}{}.png'.format(chrom, start, stop, height, str(suffix)))


def mkdir_p(path, return_path=False):
    '''
    recursively create a directory and all parent dirs in its path
    '''
    import errno

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    if return_path:
        return path


def initialize_file(string, output_file):
    '''
    Write a string to the file in 'write' mode, overwriting any contents
    '''
    with open(output_file, "w") as myfile:
        myfile.write(string + '\n')


def append_string(string, output_file):
    '''
    Append a string to a file
    '''
    with open(output_file, "a") as myfile:
        myfile.write(string + '\n')


def check_for_bai(bam_file):
    '''
    Check to make sure a 'file.bam.bai' file is present in the same dir as the 'file.bam' file
    '''
    file_exists(bam_file[:-4] + '.bai', kill = True)


def verify_input_files_list(files_list):
    '''
    Check to make sure input files meet criteria
    Add more criteria as issues are found
    '''
    for file in files_list:
        if file.endswith(".bam"):
            check_for_bai(file)


def start_batchscript(input_files, IGV_batchscript_file, IGV_snapshot_dir, genome_version, image_height):
    '''
    Initialize the batchscript file and write setup information to it
    '''
    # ~~~~ WRITE BATCHSCRIPT SETUP INFO ~~~~~~ #
    # print("\nWriting IGV batch script to file:\n{}\n".format(IGV_batchscript_file))
    # write the first line to the file; this overwrites the contents!
    initialize_file("new", IGV_batchscript_file)
    # add the genome version
    append_string("genome " + genome_version, IGV_batchscript_file)
    # add the snapshot dir
    append_string("snapshotDirectory " + IGV_snapshot_dir, IGV_batchscript_file)
    # add all of the input files to load as tracks
    for file in input_files:
        append_string("load " + file, IGV_batchscript_file)
    # add the track height
    append_string("maxPanelHeight " + image_height, IGV_batchscript_file)
    # add preferences for IGV
    append_string("preference SAM.SHOW_SOFT_CLIPPED true", IGV_batchscript_file)
    append_string("preference SAM.SHOW_CENTER_LINE true", IGV_batchscript_file)
    append_string("preference SAM.QUALITY_THRESHOLD 0", IGV_batchscript_file)
    append_string("preference SAM.ALLELE_THRESHOLD 0.01", IGV_batchscript_file)
    append_string("preference SAM.COLOR_BY READ_STRAND", IGV_batchscript_file)
    append_string("preference SAM.DOWNSAMPLE_READS false", IGV_batchscript_file)
    # sleep .5 seconds before each subsequent command, fixes rare instance of SS before sort/collapse can complete
    append_string("setSleepInterval 500", IGV_batchscript_file)



def write_batchscript_regions(region_file, IGV_batchscript_file, image_height, height_in_name, suffix, nf4_mode, group_by_strand=False):
    '''
    Write the batchscript regions
    '''
    # get the snapshot regions from the BED file
    # print("\nGetting regions from BED file...\n")
    region_list = make_chrom_region_list(region_file, nf4_mode)
    # print('Read {} regions'.format(len(region_list)))
    # ~~~~ WRITE BATCHSCRIPT CHROM LOC INFO ~~~~~~ #
    # iterate over all the regions to take snapshots of
    for region in region_list:
        # chrom, start, stop = region
        # convert region into IGV script format
        IGV_loc = make_IGV_chrom_loc(region)
        # create filename for output snapshot image_height
        snapshot_filename = make_snapshot_filename(region, image_height, suffix = suffix)
        if not height_in_name:
            snapshot_filename = re.sub('_h\\d+','',snapshot_filename)
        # write to the batchscript
        append_string("goto " + IGV_loc, IGV_batchscript_file)
        # sort by base and collapse reads
        append_string("collapse", IGV_batchscript_file)
        append_string("sort base", IGV_batchscript_file)
        # if user specifies, group reads by read strand
        if group_by_strand:
            append_string("group strand", IGV_batchscript_file)
        append_string("snapshot " + snapshot_filename, IGV_batchscript_file)


def write_IGV_script(input_files,
                     region_file,
                     IGV_batchscript_file,
                     IGV_snapshot_dir,
                     genome_version,
                     image_height,
                     height_in_name,
                     suffix = None,
                     nf4_mode = False,
                     group_by_strand=False):
    '''
    write out a batchscrpt for IGV
    '''
    start_batchscript(input_files, IGV_batchscript_file, IGV_snapshot_dir, genome_version, image_height)
    write_batchscript_regions(region_file, IGV_batchscript_file, image_height, height_in_name, suffix, nf4_mode, group_by_strand=group_by_strand)
    append_string("exit", IGV_batchscript_file)


def run_IGV_script(igv_script, igv_jar, memMB, tumorid):
    '''
    Run an IGV batch script
    '''
    import datetime
    # build the system command to run IGV
    startTime = datetime.datetime.now()
    # print("\nCurrent time is:\n{}\n".format(startTime))
    # print("\nRunning the IGV command...")
    # Xvfb will be run through xvfbwrapper, get automatic display ID. Display will start/stop through python, no stale files/etc will be generated

    # get_dotenv(environment="local")
    igv_lib_dir = os.getenv("IGV_LIB_DIRECTORY")
    igv_args_file = os.getenv("IGV_ARGS_FILE")

    with Xvfb(width=1920, height=1080, colordepth=24, nolisten='tcp') as xvfb:
        xvfb.extra_xvfb_args += ['+extension', 'RANDR', 'c', '20']
        java_memory = "-Xmx"+memMB+"m"
        sp.call([
            'java',
            '-showversion',
            java_memory,
            f"--module-path={igv_lib_dir}", 
            f"@{igv_args_file}",
            '-Dapple.laf.useScreenMenuBar=true',
            '-Djava.net.preferIPv4Stack=true',
            '--module=org.igv/org.broad.igv.ui.Main',
            '-b',
            igv_script
        ])

    elapsed_time = datetime.datetime.now() - startTime
    # print("\nIGV finished; elapsed time is:\n{}\n".format(elapsed_time))

def read_vcf(file_path):
    # Initialize lists to store VCF data
    vcf_data = []
    column_names = []

    # Open the VCF file and read it line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Skip metadata lines
            if line.startswith('##'):
                continue
            
            # Extract header line and split it into column names
            if line.startswith('#'):
                column_names = line[1:].strip().split('\t')
                continue
            # Append the entire line to the list
            vcf_data.append(line.strip().split('\t'))

    # Create a DataFrame from the list of lines
    df = pd.DataFrame(vcf_data, columns=column_names)
    # Apply the function to the DataFrame to turn INFO values into columns
    df_info = df['INFO'].apply(split_column)
    df = pd.concat([df, df_info], axis=1)
    return df

# Function to split the combined column into separate columns
def split_column(row):
    columns = {}
    for item in row.split(';'):
        if '=' in item:
            key, value = item.split('=')
            columns[key] = value
    return pd.Series(columns)
def read_annotated_file(annotated_variant_file):
    if annotated_variant_file.lower().endswith('maf'):
        dmp_reader = pd.read_csv(annotated_variant_file, delimiter="\t", low_memory=False)
        dmp_df = pd.DataFrame(dmp_reader)
        dmp_df.rename(columns = MAF_TSV_COL_MAP, inplace=True)
    elif annotated_variant_file.lower().endswith('txt'):
        dmp_reader = pd.read_csv(annotated_variant_file, delimiter="\t", low_memory=False)
        dmp_df = pd.DataFrame(dmp_reader)
    elif annotated_variant_file.lower().endswith('vcf'):
        dmp_df = read_vcf(annotated_variant_file)
        dmp_df.rename(columns = VCF_TSV_COL_MAP, inplace=True)
        int_convert = ['Start']
        dmp_df[int_convert] = dmp_df[int_convert].astype(int)
    else:
        raise ValueError('Unsupported annotated_variant_file type. Please provide a file with the following extensions: maf, txt, vcf')
    return dmp_df
def run_screenshotting(input_files, 
                       annotated_variant_file, 
                       tumorid, 
                       region_file, 
                       genome,
                       image_height, 
                       height_in_name,
                       outdir,
                       igv_jar_bin, 
                       igv_mem,
                       no_snap, 
                       suffix, 
                       nf4_mode, 
                       onlysnap,
                       group_by_strand):
    '''
    Main control function for the script
    '''
    #TODO check input as maf, vcf, txt
    #TODO support vcf reading
    #TODO do the read here
    if onlysnap is not None:
        batchscript_file = str(onlysnap)
        file_exists(batchscript_file, kill = True)
        run_IGV_script(igv_script = batchscript_file, igv_jar = igv_jar_bin, memMB = igv_mem)
        return()
    # print('\nGenerating BED file for IGV SS\n{}\n'.format(igv_jar_bin))
    annotated_variant_df = read_annotated_file(annotated_variant_file)
    convert_annotated_file_to_bed(annotated_variant_df, tumorid, region_file, nf4_mode)

    # default IGV batch script output location
    batchscript_file = os.path.join(outdir, "IGV_snapshots.bat")

    # make sure the regions file exists
    file_exists(region_file, kill = True)

    # make sure the IGV jar exists
    file_exists(igv_jar_bin, kill = True)

    # check the input files to make sure they are valid
    verify_input_files_list(input_files)


    # print('\n~~~ IGV SNAPSHOT AUTOMATOR ~~~\n')
    # print('Reference genome:\n{}\n'.format(genome))
    # print('Track height:\n{}\n'.format(image_height))
    # print('IGV binary file:\n{}\n'.format(igv_jar_bin))
    # print('Output directory will be:\n{}\n'.format(outdir))
    # print('Batchscript file will be:\n{}\n'.format(batchscript_file))
    # print('Region file:\n{}\n'.format(region_file))
    # print('Input files to snapshot:\n')
    for file in input_files:
        # print(file)
        file_exists(file, kill = True)

    # make the output directory
    # print('\nMaking the output directory...')
    mkdir_p(outdir)
    # write the IGV batch script
    write_IGV_script(input_files = input_files, region_file = region_file,
                     IGV_batchscript_file = batchscript_file,
                     IGV_snapshot_dir = outdir, genome_version = genome,
                     image_height = image_height, height_in_name = height_in_name,
                     suffix = suffix, nf4_mode = nf4_mode, 
                     group_by_strand=group_by_strand)

    # make sure the batch script file exists
    file_exists(batchscript_file, kill = True)

    # run the IGV batch script
    if no_snap == False:
        run_IGV_script(igv_script = batchscript_file, igv_jar = igv_jar_bin, memMB = igv_mem, tumorid = tumorid)


