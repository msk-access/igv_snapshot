
# Introduction

A python package to generate and execute IGV screenshot script.
Adapted from [access-mpath-scripts](https://github.com/msk-access/access-mpath-scripts/tree/cb50cd6d3a32870fb89ec7969ae065549de8ac6d)


# Setting up a Dev Environment 

It is recommended to run this tool via the Docker container.

To set up the package locally for development purposes see the following steps. 

## Install External Dependencies

Create an environment with python >= 3.9, Java and IGV installed on path.

Generic Java Install: 

```bash
wget https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz
tar xvf openjdk-11+28_linux-x64_bin.tar.gz
export JAVA_HOME=/path/to/jdk-11
export PATH=$JAVA_HOME/bin:$PATH
```

Generic IGV install: 

```bash
wget https://data.broadinstitute.org/igv/projects/downloads/2.18/IGV_2.18.0.zip -O tmp 
mv tmp IGV_2.18.0.zip 
unzip IGV_2.18.0.zip 
rm -f IGV_2.18.0.zip 
```

Set the following environment variables:

```bash
export IGV_LIB_DIRECTORY="/path/to/IGV_2.16.0/lib/"
export IGV_ARGS_FILE="path/to/igv_snapshot/igv.args"
```

## Install Package and Dependencies

Install package with Poetry.

Install poetry: 

```bash
pip install poetry
cd /path/to/igv_snapshot
poetry install
```
## Run IGV

Example call:
```
python poetry \ 
igv run_screenshot \
--input-files \
"/path/to/sample.bam" \
--input-files \
"/path/to/sample.bai" \
--annotated-variant-file \
"/path/to/variant.{maf,txt,vcf}" \
-t \
"sample" \
-o \
"path/to/outdir" \
-r \
"path/to/bed/file" \
-g \
"/path/to/IGV.json"
```

## Additional Notes

This tool by default uses the Broad hg19 reference file. See `igv_snapshot/data/genome.json`

If you'd like to use a different reference, you will need to download and unzip a version of [IGV](https://data.broadinstitute.org/igv/projects/downloads/).

Then, you will need a [JSON](https://github.com/igvteam/igv/wiki/JSON-Genome-Format) file specifying genome information.

And specify the JSON using the `-g` option. 

Below is an example JSON:

```
{
    "id": "b37_1kg",
    "name": "Human (1kg, b37+decoy)",
    "fastaURL": "https://storage.googleapis.com/genomics-public-data/references/Homo_sapiens_assembly19_1000genomes_decoy/Homo_sapiens_assembly19_1000genomes_decoy.fasta",
    "indexURL": "https://storage.googleapis.com/genomics-public-data/references/Homo_sapiens_assembly19_1000genomes_decoy/Homo_sapiens_assembly19_1000genomes_decoy.fasta.fai",
    "cytobandURL": "https://s3.amazonaws.com/igv.org.genomes/1kg_v37/b37_cytoband.txt",
    "aliasURL": "https://s3.amazonaws.com/igv.org.genomes/1kg_v37/b37_alias.tab",
    "tracks": [
        {
            "name": "Refseq Genes",
            "format": "refgene",
            "id": "hg19_genes",
            "url": "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/database/ncbiRefSeq.txt.gz",
            "indexed": false,
            "removable": false,
            "order": 1000000,
            "infoURL": "https://www.ncbi.nlm.nih.gov/gene/?term=$$"
        }
    ],
    "chromosomeOrder": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,14, 15, 16, 17,18, 19, 20, 21, 22, X, Y"
}
```

