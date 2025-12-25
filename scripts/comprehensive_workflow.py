#!/usr/bin/env python3
"""
Script: comprehensive_workflow.py
Description: Complete FOREST workflow combining all steps: motif extraction, library design, DNA templates, and microarray design

Original Use Case: examples/use_case_5_comprehensive_workflow.py
Dependencies Removed: subprocess calls to FOREST.py, repo path dependencies

Usage:
    python scripts/comprehensive_workflow.py --input <input_file> --barcodes <barcodes_file> --output_dir <output_dir>

Example:
    python scripts/comprehensive_workflow.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 2 --output_dir results/comprehensive
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import sys

# Add scripts/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from lib.forest_core import (
    terminal_motif_extraction,
    parse_fasta_with_structure,
    load_barcodes,
    conjugate_stem,
    revcom,
    save_fasta_results
)

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "max_length": 134,
    "num_barcodes": 2,
    "barcode_prefix": "GGG",
    "stem_length": 17,
    "t7_promoter": "GCGCTAATACGACTCACTATA",
    "output_format": "fasta",
    "include_metadata": True
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_comprehensive_workflow(
    input_file: Union[str, Path],
    barcodes_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Run complete FOREST workflow: motifs → RNA library → DNA templates → microarray barcodes.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file containing DNA barcodes
        output_dir: Directory to save all workflow outputs
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - motifs: Extracted motifs
            - rna_library: RNA probe library
            - dna_templates: DNA template sequences
            - array_barcodes: Microarray capture barcodes
            - output_files: Paths to output files
            - metadata: Execution metadata

    Example:
        >>> result = run_comprehensive_workflow("input.fa.txt", "barcodes.txt", "output/")
        >>> print(f"Generated {len(result['motifs'])} motifs and {len(result['rna_library'])} probes")
    """
    # Setup
    input_file = Path(input_file)
    barcodes_file = Path(barcodes_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Validate input files
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if not barcodes_file.exists():
        raise FileNotFoundError(f"Barcodes file not found: {barcodes_file}")

    # Parse input files
    try:
        parsed_data = parse_fasta_with_structure(input_file)
    except Exception as e:
        raise ValueError(f"Failed to parse input file: {e}")

    try:
        barcodes = load_barcodes(barcodes_file)
    except Exception as e:
        raise ValueError(f"Failed to parse barcodes file: {e}")

    if not parsed_data:
        raise ValueError("No valid sequences found in input file")
    if not barcodes:
        raise ValueError("No valid barcodes found in barcodes file")

    # ==============================================================================
    # Step 1: Extract Terminal Motifs
    # ==============================================================================
    print("Step 1: Extracting terminal motifs...", file=sys.stderr)

    all_motifs = {}
    processed_sequences = 0

    for name, sequence, structure in parsed_data:
        try:
            motifs = terminal_motif_extraction(
                name=name.lstrip('>'),  # Remove '>' prefix
                seq=structure,
                seq2=sequence,
                max_length=config['max_length']
            )
            all_motifs.update(motifs)
            processed_sequences += 1
        except Exception as e:
            print(f"Warning: Failed to process sequence {name}: {e}", file=sys.stderr)
            continue

    print(f"  ✅ Extracted {len(all_motifs)} motifs from {processed_sequences} sequences", file=sys.stderr)

    # ==============================================================================
    # Step 2: Design RNA Library with Barcodes
    # ==============================================================================
    print("Step 2: Designing RNA probe library...", file=sys.stderr)

    rna_library = {}
    barcode_index = 0
    used_barcodes = []

    # Check barcode requirements
    unique_sequences = [seq_info[1] for seq_info in all_motifs.values() if seq_info[1]]
    total_barcodes_needed = len(unique_sequences) * config['num_barcodes']

    if total_barcodes_needed > len(barcodes):
        raise ValueError(f"Not enough barcodes: need {total_barcodes_needed}, have {len(barcodes)}")

    # Generate barcoded RNA library
    for motif_name, (structure, sequence) in all_motifs.items():
        if not sequence or not structure:
            continue

        for barcode_id in range(1, config['num_barcodes'] + 1):
            if barcode_index >= len(barcodes):
                break

            probe_name = f"{motif_name}_Barcode_{barcode_id}"
            barcode = barcodes[barcode_index]

            # Create barcoded RNA probe
            conjugated_sequence = conjugate_stem(sequence, config['stem_length'])
            probe_sequence = config['barcode_prefix'] + barcode + conjugated_sequence

            rna_library[probe_name] = [structure, probe_sequence.upper().replace("T", "U")]

            barcode_index += 1
            used_barcodes.append(barcode)

    print(f"  ✅ Generated {len(rna_library)} RNA probes using {len(used_barcodes)} barcodes", file=sys.stderr)

    # ==============================================================================
    # Step 3: Design DNA Templates with T7 Promoter
    # ==============================================================================
    print("Step 3: Designing DNA templates...", file=sys.stderr)

    dna_templates = {}

    for probe_name, (structure, rna_sequence) in rna_library.items():
        template_name = f"{probe_name.replace('_Barcode_', '_Barcode_')}_template"

        # Create DNA template: T7 promoter + reverse complement of RNA probe
        dna_template_sequence = config['t7_promoter'] + rna_sequence
        dna_template_revcomp = revcom(dna_template_sequence.upper().replace("U", "T"))

        dna_templates[template_name] = ["", dna_template_revcomp]

    print(f"  ✅ Generated {len(dna_templates)} DNA templates", file=sys.stderr)

    # ==============================================================================
    # Step 4: Design Microarray Capture Barcodes
    # ==============================================================================
    print("Step 4: Designing microarray barcodes...", file=sys.stderr)

    array_barcodes = {}

    for i, barcode in enumerate(used_barcodes):
        # Find corresponding probe name
        probe_names = [name for name in rna_library.keys() if f"_Barcode_{(i % config['num_barcodes']) + 1}" in name]
        if probe_names:
            base_name = probe_names[0].replace(f"_Barcode_{(i % config['num_barcodes']) + 1}", "")
            array_name = f"{base_name}_Barcode_{(i % config['num_barcodes']) + 1}_array"

            # Create microarray capture sequence
            capture_target = config['barcode_prefix'] + barcode
            capture_sequence = revcom(capture_target)

            array_barcodes[array_name] = ["", capture_sequence]

    print(f"  ✅ Generated {len(array_barcodes)} microarray barcodes", file=sys.stderr)

    # ==============================================================================
    # Save All Outputs
    # ==============================================================================
    output_files = {}

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each step's results
        output_files = {
            "motifs": output_dir / "motifs.txt",
            "rna_library": output_dir / "rna_library.txt",
            "dna_templates": output_dir / "dna_templates.txt",
            "array_barcodes": output_dir / "microarray_barcodes.txt"
        }

        save_fasta_results(all_motifs, output_files["motifs"])
        save_fasta_results(rna_library, output_files["rna_library"])
        save_fasta_results(dna_templates, output_files["dna_templates"])
        save_fasta_results(array_barcodes, output_files["array_barcodes"])

        # Convert paths to strings for JSON serialization
        output_files = {k: str(v) for k, v in output_files.items()}

        print(f"  ✅ All outputs saved to: {output_dir}", file=sys.stderr)

    # Prepare metadata
    metadata = {
        "input_file": str(input_file),
        "barcodes_file": str(barcodes_file),
        "processed_sequences": processed_sequences,
        "total_motifs": len(all_motifs),
        "total_rna_probes": len(rna_library),
        "total_dna_templates": len(dna_templates),
        "total_array_barcodes": len(array_barcodes),
        "barcodes_used": len(used_barcodes),
        "barcodes_available": len(barcodes),
        "config": config
    }

    return {
        "motifs": all_motifs,
        "rna_library": rna_library,
        "dna_templates": dna_templates,
        "array_barcodes": array_barcodes,
        "used_barcodes": used_barcodes,
        "output_files": output_files,
        "metadata": metadata
    }


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Input FASTA file with RNA sequences and structures')
    parser.add_argument('--barcodes', '-b', required=True,
                        help='Barcode file containing DNA barcodes')
    parser.add_argument('--output_dir', '-o', required=True,
                        help='Output directory for all workflow results')
    parser.add_argument('--config', '-c',
                        help='Config file (JSON)')
    parser.add_argument('--num_barcodes', '-bn', type=int, default=2,
                        help='Number of barcodes per RNA structure (default: 2)')
    parser.add_argument('--max_length', '-L', type=int, default=134,
                        help='Maximum motif length (default: 134)')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with CLI args
    cli_overrides = {}
    if args.num_barcodes != 2:
        cli_overrides['num_barcodes'] = args.num_barcodes
    if args.max_length != 134:
        cli_overrides['max_length'] = args.max_length

    try:
        # Run comprehensive workflow
        result = run_comprehensive_workflow(
            input_file=args.input,
            barcodes_file=args.barcodes,
            output_dir=args.output_dir,
            config=config,
            **cli_overrides
        )

        # Print summary
        metadata = result['metadata']
        print("\n" + "="*60, file=sys.stderr)
        print("COMPREHENSIVE FOREST WORKFLOW COMPLETED", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"✅ Processed {metadata['processed_sequences']} input sequences", file=sys.stderr)
        print(f"✅ Extracted {metadata['total_motifs']} terminal motifs", file=sys.stderr)
        print(f"✅ Generated {metadata['total_rna_probes']} RNA probes", file=sys.stderr)
        print(f"✅ Generated {metadata['total_dna_templates']} DNA templates", file=sys.stderr)
        print(f"✅ Generated {metadata['total_array_barcodes']} microarray barcodes", file=sys.stderr)
        print(f"✅ Used {metadata['barcodes_used']}/{metadata['barcodes_available']} barcodes", file=sys.stderr)

        if result['output_files']:
            print(f"\nOutput files:", file=sys.stderr)
            for step, filepath in result['output_files'].items():
                print(f"  {step}: {filepath}", file=sys.stderr)

        print("="*60, file=sys.stderr)

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()