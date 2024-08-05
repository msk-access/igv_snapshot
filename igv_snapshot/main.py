# Main Import
import typer
import importlib.metadata
from pathlib import Path
import os 
from .helper import run_screenshotting

# versioning
version_string_of_foo = importlib.metadata.version('igv_snapshot')
__version__ = version_string_of_foo

# globals 
genome_default = importlib.resources.open_text("igv_snapshot.data", "genome.json").name
igv_lib_dir = os.getenv("IGV_LIB_DIRECTORY")
igv_args_file = os.getenv("IGV_ARGS_FILE")

# app
app = typer.Typer()

# command 
@app.command("run_screenshot", help="IGV snapshot automator")
def run_screenshot(
    input_files: list[Path] = typer.Option(..., help="Paths to the files to create snapshots from e.g. .bam, .bigwig, etc."),
    annotated_variant_file: Path = typer.Option(..., help="Input annotated variants file"),
    tumorid: str = typer.Option(None, "-t", help="Tumor Sample Barcode"),
    region_file: Path = typer.Option(..., "-r", metavar="regions", help="BED file with regions to create snapshots over"),
    genome: str = typer.Option(genome_default, "-g", metavar="genome", help="Name of the reference genome, defaults to hg19"),
    igv_jar_bin: Path = typer.Option(f"{igv_lib_dir}/igv.jar", "-bin", metavar="IGV bin path", help="Path to the IGV jar binary to run"),
    outdir: Path = typer.Option("IGV_Snapshots", "-o", metavar="output directory", help="Output directory for snapshots"),
    image_height: str = typer.Option("500", "-ht", metavar="image height", help="Height for the IGV tracks"),
    height_in_name: bool = typer.Option(False, "-htn", help="Use image height in output name."),
    igv_mem: str = typer.Option("8000", "-mem", metavar="IGV memory (MB)", help="Amount of memory to allocate to IGV, in Megabytes (MB)"),
    no_snap: bool = typer.Option(False, "-nosnap", help="Don't make snapshots, only write batchscript and exit"),
    suffix: str = typer.Option(None, "-suffix", help="Filename suffix to place before '.png' in the snapshots"),
    nf4_mode: bool = typer.Option(False, "-nf4", help="'Name field 4' mode; uses the value in the fourth field of the regions file as the filename for each region snapshot"),
    onlysnap: Path = typer.Option(None, "-onlysnap", help="Path to batchscript file to run in IGV. Performs no error checking or other input evaluation, only runs IGV on the batchscript and exits."),
    group_by_strand: bool = typer.Option(False, "-s", "--group_by_strand", help="Group reads by forward/reverse strand."),
):
    """
    Main control function for the script
    """
    run_screenshotting(input_files = [str(f) for f in input_files],
                    region_file = str(region_file),
                    genome = genome,
                    image_height = image_height,
                    height_in_name = height_in_name,
                    outdir = str(outdir),
                    igv_jar_bin = igv_jar_bin,
                    igv_mem = igv_mem,
                    no_snap = no_snap,
                    suffix = suffix,
                    nf4_mode = nf4_mode,
                    onlysnap = onlysnap,
                    group_by_strand=group_by_strand,
                    annotated_variant_file = str(annotated_variant_file),
                    tumorid = tumorid)

def version_callback(value: bool):
    if value:
        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, 
        help="print version"
    ),
):
    return
