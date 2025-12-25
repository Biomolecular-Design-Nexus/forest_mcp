"""MCP Server for FOREST 2020

Provides both synchronous and asynchronous (submit) APIs for RNA structure analysis.
FOREST (Functional Organization of RNA Element Selection and Testing) enables
analysis of RNA secondary structures for probe design and molecular applications.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List
import sys
import json

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
CONFIGS_DIR = MCP_ROOT / "configs"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("FOREST")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 2 min)
# ==============================================================================

@mcp.tool()
def extract_rna_motifs(
    input_file: str,
    output_file: Optional[str] = None,
    max_length: int = 134
) -> dict:
    """
    Extract terminal RNA motifs from secondary structures using FOREST algorithm.

    Fast operation suitable for small datasets (~1-1000 sequences).
    For large datasets, use submit_motif_extraction for async processing.

    Args:
        input_file: Path to FASTA file with RNA sequences and dot-bracket structures
        output_file: Optional path to save extracted motifs
        max_length: Maximum motif length to extract (default: 134)

    Returns:
        Dictionary with extracted motifs and metadata

    Example:
        extract_rna_motifs("examples/data/test.fa.txt", "results/motifs.txt")
    """
    try:
        # Import the script's main function
        from motif_extraction import run_motif_extraction

        result = run_motif_extraction(
            input_file=input_file,
            output_file=output_file,
            max_length=max_length
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"RNA motif extraction failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def design_rna_library(
    input_file: str,
    barcodes_file: str,
    output_file: Optional[str] = None,
    num_barcodes: int = 5
) -> dict:
    """
    Design RNA probe library by combining motifs with DNA barcodes.

    Fast operation suitable for small to medium libraries (~1-10000 probes).
    For large-scale library design, use submit_library_design for async processing.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes (one per line)
        output_file: Optional path to save RNA library
        num_barcodes: Number of barcodes to use per motif (default: 5)

    Returns:
        Dictionary with RNA library and metadata

    Example:
        design_rna_library("examples/data/test.fa.txt", "examples/data/barcode25mer_100000.txt")
    """
    try:
        from library_design import run_library_design

        result = run_library_design(
            input_file=input_file,
            barcodes_file=barcodes_file,
            output_file=output_file,
            num_barcodes=num_barcodes
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"RNA library design failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def design_dna_templates(
    input_file: str,
    barcodes_file: str,
    output_file: Optional[str] = None,
    num_barcodes: int = 3
) -> dict:
    """
    Generate DNA templates with T7 promoter for oligonucleotide pool synthesis.

    Fast operation suitable for small to medium template sets (~1-5000 templates).
    For large-scale template design, use submit_template_design for async processing.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_file: Optional path to save DNA templates
        num_barcodes: Number of barcodes to use per template (default: 3)

    Returns:
        Dictionary with DNA templates and metadata

    Example:
        design_dna_templates("examples/data/test.fa.txt", "examples/data/barcode25mer_100000.txt")
    """
    try:
        from dna_template_design import run_dna_template_design

        result = run_dna_template_design(
            input_file=input_file,
            barcodes_file=barcodes_file,
            output_file=output_file,
            num_barcodes=num_barcodes
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"DNA template design failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def design_microarray_barcodes(
    input_file: str,
    barcodes_file: str,
    output_file: Optional[str] = None,
    num_barcodes: int = 2
) -> dict:
    """
    Design DNA barcode sequences for microarray capture of RNA probes.

    Fast operation suitable for small to medium arrays (~1-2000 barcodes).
    For large-scale microarray design, use submit_microarray_design for async processing.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_file: Optional path to save microarray barcodes
        num_barcodes: Number of barcodes to use per sequence (default: 2)

    Returns:
        Dictionary with microarray barcodes and metadata

    Example:
        design_microarray_barcodes("examples/data/test.fa.txt", "examples/data/barcode25mer_100000.txt")
    """
    try:
        from microarray_design import run_microarray_design

        result = run_microarray_design(
            input_file=input_file,
            barcodes_file=barcodes_file,
            output_file=output_file,
            num_barcodes=num_barcodes
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Microarray barcode design failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def run_forest_workflow(
    input_file: str,
    barcodes_file: str,
    output_dir: str,
    num_barcodes: int = 2
) -> dict:
    """
    Run complete FOREST workflow combining all steps (motifs + library + templates + microarray).

    Fast operation suitable for small to medium datasets (~1-500 sequences).
    For large-scale workflows, use submit_comprehensive_workflow for async processing.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_dir: Directory to save all output files
        num_barcodes: Number of barcodes to use per sequence (default: 2)

    Returns:
        Dictionary with all outputs and metadata

    Example:
        run_forest_workflow("examples/data/test.fa.txt", "examples/data/barcode25mer_100000.txt", "results/workflow/")
    """
    try:
        from comprehensive_workflow import run_comprehensive_workflow

        result = run_comprehensive_workflow(
            input_file=input_file,
            barcodes_file=barcodes_file,
            output_dir=output_dir,
            num_barcodes=num_barcodes
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"FOREST workflow failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations or batch processing)
# ==============================================================================

@mcp.tool()
def submit_motif_extraction(
    input_file: str,
    output_dir: Optional[str] = None,
    max_length: int = 134,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit RNA motif extraction for background processing.

    Use this for large datasets (>1000 sequences) or when you need to process
    multiple files in a workflow. Returns a job_id for tracking.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        output_dir: Directory to save outputs (default: job directory)
        max_length: Maximum motif length to extract (default: 134)
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs

    Example:
        submit_motif_extraction("large_dataset.fa", "results/motifs/", job_name="motif_analysis")
    """
    script_path = str(SCRIPTS_DIR / "motif_extraction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "output": output_dir,
            "max_length": max_length
        },
        job_name=job_name or f"motif_extraction_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_library_design(
    input_file: str,
    barcodes_file: str,
    output_dir: Optional[str] = None,
    num_barcodes: int = 5,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit RNA library design for background processing.

    Use this for large libraries (>10000 probes) or when generating multiple
    libraries in parallel. Returns a job_id for tracking.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_dir: Directory to save outputs (default: job directory)
        num_barcodes: Number of barcodes to use per motif (default: 5)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the library design job

    Example:
        submit_library_design("sequences.fa", "barcodes.txt", "results/library/")
    """
    script_path = str(SCRIPTS_DIR / "library_design.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "barcodes": barcodes_file,
            "output": output_dir,
            "num_barcodes": num_barcodes
        },
        job_name=job_name or f"library_design_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_template_design(
    input_file: str,
    barcodes_file: str,
    output_dir: Optional[str] = None,
    num_barcodes: int = 3,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit DNA template design for background processing.

    Use this for large template sets (>5000 templates) or when preparing
    multiple oligonucleotide pools. Returns a job_id for tracking.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_dir: Directory to save outputs (default: job directory)
        num_barcodes: Number of barcodes to use per template (default: 3)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the template design job

    Example:
        submit_template_design("sequences.fa", "barcodes.txt", "results/templates/")
    """
    script_path = str(SCRIPTS_DIR / "dna_template_design.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "barcodes": barcodes_file,
            "output": output_dir,
            "num_barcodes": num_barcodes
        },
        job_name=job_name or f"template_design_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_microarray_design(
    input_file: str,
    barcodes_file: str,
    output_dir: Optional[str] = None,
    num_barcodes: int = 2,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit microarray barcode design for background processing.

    Use this for large arrays (>2000 barcodes) or when designing multiple
    microarray layouts. Returns a job_id for tracking.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_dir: Directory to save outputs (default: job directory)
        num_barcodes: Number of barcodes to use per sequence (default: 2)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the microarray design job

    Example:
        submit_microarray_design("sequences.fa", "barcodes.txt", "results/microarray/")
    """
    script_path = str(SCRIPTS_DIR / "microarray_design.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "barcodes": barcodes_file,
            "output": output_dir,
            "num_barcodes": num_barcodes
        },
        job_name=job_name or f"microarray_design_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_comprehensive_workflow(
    input_file: str,
    barcodes_file: str,
    output_dir: str,
    num_barcodes: int = 2,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit complete FOREST workflow for background processing.

    Runs all four steps (motifs + library + templates + microarray) in sequence.
    Use this for large datasets (>500 sequences) or production workflows.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file with DNA barcodes
        output_dir: Directory to save all outputs
        num_barcodes: Number of barcodes to use per sequence (default: 2)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the comprehensive workflow

    Example:
        submit_comprehensive_workflow("large_dataset.fa", "barcodes.txt", "results/comprehensive/")
    """
    script_path = str(SCRIPTS_DIR / "comprehensive_workflow.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input": input_file,
            "barcodes": barcodes_file,
            "output_dir": output_dir,
            "num_barcodes": num_barcodes
        },
        job_name=job_name or f"forest_workflow_{Path(input_file).stem}"
    )

# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_motif_extraction(
    input_files: List[str],
    output_dir: Optional[str] = None,
    max_length: int = 134,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch RNA motif extraction for multiple files.

    Processes multiple FASTA files in a single job. Suitable for:
    - Processing many RNA sequence files at once
    - Large-scale motif analysis
    - Parallel processing of independent datasets

    Args:
        input_files: List of FASTA file paths to process
        output_dir: Directory to save all outputs
        max_length: Maximum motif length for all extractions (default: 134)
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job

    Example:
        submit_batch_motif_extraction(["file1.fa", "file2.fa", "file3.fa"], "results/batch_motifs/")
    """
    # Create a batch script that processes multiple files
    batch_args = {
        "inputs": ",".join(input_files),
        "output_dir": output_dir,
        "max_length": max_length
    }

    # Use motif extraction script with comma-separated inputs
    script_path = str(SCRIPTS_DIR / "motif_extraction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args=batch_args,
        job_name=job_name or f"batch_motifs_{len(input_files)}_files"
    )

@mcp.tool()
def submit_batch_forest_workflow(
    input_files: List[str],
    barcodes_file: str,
    output_dir: str,
    num_barcodes: int = 2,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch FOREST workflows for multiple input files.

    Runs complete FOREST analysis on multiple sequence files. Each file
    gets its own subdirectory with all four output types.

    Args:
        input_files: List of FASTA file paths to process
        barcodes_file: Path to file with DNA barcodes (shared across all files)
        output_dir: Directory to save all outputs (subdirs created per file)
        num_barcodes: Number of barcodes to use per sequence (default: 2)
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch workflow

    Example:
        submit_batch_forest_workflow(["dataset1.fa", "dataset2.fa"], "barcodes.txt", "results/batch_forest/")
    """
    batch_args = {
        "inputs": ",".join(input_files),
        "barcodes": barcodes_file,
        "output_dir": output_dir,
        "num_barcodes": num_barcodes
    }

    script_path = str(SCRIPTS_DIR / "comprehensive_workflow.py")

    return job_manager.submit_job(
        script_path=script_path,
        args=batch_args,
        job_name=job_name or f"batch_forest_{len(input_files)}_files"
    )

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def validate_input_format(
    input_file: str,
    format_type: str = "fasta_structure"
) -> dict:
    """
    Validate input file format for FOREST tools.

    Args:
        input_file: Path to file to validate
        format_type: Expected format ("fasta_structure", "barcodes", "fasta_simple")

    Returns:
        Dictionary with validation results

    Example:
        validate_input_format("examples/data/test.fa.txt", "fasta_structure")
    """
    try:
        from lib.forest_core import parse_fasta_with_structure, load_barcodes

        if format_type == "fasta_structure":
            sequences = parse_fasta_with_structure(input_file)
            return {
                "status": "success",
                "format": "fasta_structure",
                "sequences": len(sequences),
                "valid": True,
                "message": f"Valid FASTA file with {len(sequences)} sequences"
            }
        elif format_type == "barcodes":
            barcodes = load_barcodes(input_file, max_barcodes=10)  # Test load first 10
            return {
                "status": "success",
                "format": "barcodes",
                "barcodes_sample": len(barcodes),
                "valid": True,
                "message": f"Valid barcode file (tested first 10)"
            }
        else:
            return {"status": "error", "error": f"Unknown format type: {format_type}"}

    except Exception as e:
        return {
            "status": "error",
            "valid": False,
            "error": str(e)
        }

@mcp.tool()
def get_example_data() -> dict:
    """
    Get information about available example datasets for testing.

    Returns:
        Dictionary with example files and their descriptions
    """
    examples_dir = MCP_ROOT / "examples" / "data"
    examples = []

    if examples_dir.exists():
        for file_path in examples_dir.glob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    examples.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size_bytes": size,
                        "size_human": f"{size / 1024:.1f} KB" if size > 1024 else f"{size} bytes"
                    })
                except:
                    pass

    return {
        "status": "success",
        "examples": examples,
        "total": len(examples),
        "usage": {
            "small_test": "test.fa.txt - 2 sequences for quick testing",
            "medium_test": "test_100.fa.txt - 100 sequences for performance testing",
            "barcodes": "barcode25mer_100000.txt - 100,000 DNA barcodes for library design"
        }
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()