#!/usr/bin/env python3
"""
Script: dna_template_design.py
Description: Generate DNA template sequences with reverse complementary DNA and T7 promoter for oligo pool ordering

Original Use Case: examples/use_case_3_dna_template_design.py
Dependencies Removed: subprocess calls to FOREST.py, repo path dependencies

Usage:
    python scripts/dna_template_design.py --input <input_file> --barcodes <barcodes_file> --output <output_file>

Example:
    python scripts/dna_template_design.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 2 --output results/dna_templates.txt
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
    "num_barcodes": 3,
    "barcode_prefix": "GGG",
    "stem_length": 17,
    "t7_promoter": "GCGCTAATACGACTCACTATA",
    "output_format": "fasta",
    "include_metadata": True
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_dna_template_design(
    input_file: Union[str, Path],
    barcodes_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Design DNA template pool with reverse complementary sequences and T7 promoter.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        barcodes_file: Path to file containing DNA barcodes
        output_file: Path to save DNA templates (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - templates: DNA template data
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_dna_template_design("input.fa.txt", "barcodes.txt", "templates.txt")
        >>> print(f"Generated {len(result['templates'])} DNA templates")
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

    # Extract motifs from all sequences
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

    # Generate DNA templates
    dna_templates = {}
    barcode_index = 0
    used_barcodes = []

    # Get unique sequences for barcode calculation
    unique_sequences = [seq_info[1] for seq_info in all_motifs.values() if seq_info[1]]
    total_barcodes_needed = len(unique_sequences) * config['num_barcodes']

    if total_barcodes_needed > len(barcodes):
        raise ValueError(f"Not enough barcodes: need {total_barcodes_needed}, have {len(barcodes)}")

    print(f"# Loading {len(barcodes)} barcodes", file=sys.stderr)
    print(f"# Number of barcodes per RNA structure: {config['num_barcodes']}", file=sys.stderr)
    print(f"# Number of RNA structures: {len(unique_sequences)}", file=sys.stderr)

    # Generate DNA template pool
    for motif_name, (structure, sequence) in all_motifs.items():
        if not sequence or not structure:
            continue

        for barcode_id in range(1, config['num_barcodes'] + 1):
            if barcode_index >= len(barcodes):
                break

            template_name = f"{motif_name}_Barcode_{barcode_id}_template"
            barcode = barcodes[barcode_index]

            # Create RNA probe sequence: prefix + barcode + conjugated stem + sequence
            conjugated_sequence = conjugate_stem(sequence, config['stem_length'])
            rna_probe = config['barcode_prefix'] + barcode + conjugated_sequence

            # Create DNA template: T7 promoter + reverse complement of RNA probe
            dna_template_sequence = config['t7_promoter'] + rna_probe
            dna_template_revcomp = revcom(dna_template_sequence.upper().replace("U", "T"))

            # Store the DNA template (reverse complement for oligo pool ordering)
            dna_templates[template_name] = ["", dna_template_revcomp]  # No structure for DNA

            barcode_index += 1
            used_barcodes.append(barcode)

    # Save output if requested
    output_path = None
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_fasta_results(dna_templates, output_path)

    # Prepare metadata
    metadata = {
        "input_file": str(input_file),
        "barcodes_file": str(barcodes_file),
        "processed_sequences": processed_sequences,
        "total_motifs": len(all_motifs),
        "total_templates": len(dna_templates),
        "barcodes_used": len(used_barcodes),
        "barcodes_available": len(barcodes),
        "config": config
    }

    return {
        "templates": dna_templates,
        "used_barcodes": used_barcodes,
        "output_file": str(output_path) if output_path else None,
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
    parser.add_argument('--output', '-o',
                        help='Output file path (default: stdout)')
    parser.add_argument('--config', '-c',
                        help='Config file (JSON)')
    parser.add_argument('--num_barcodes', '-bn', type=int, default=3,
                        help='Number of barcodes per RNA structure (default: 3)')
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
    if args.num_barcodes != 3:
        cli_overrides['num_barcodes'] = args.num_barcodes
    if args.max_length != 134:
        cli_overrides['max_length'] = args.max_length

    try:
        # Run DNA template design
        result = run_dna_template_design(
            input_file=args.input,
            barcodes_file=args.barcodes,
            output_file=args.output,
            config=config,
            **cli_overrides
        )

        # Print summary
        metadata = result['metadata']
        print(f"✅ Successfully processed {metadata['processed_sequences']} sequences", file=sys.stderr)
        print(f"✅ Extracted {metadata['total_motifs']} motifs", file=sys.stderr)
        print(f"✅ Generated {metadata['total_templates']} DNA templates", file=sys.stderr)
        print(f"✅ Used {metadata['barcodes_used']} barcodes", file=sys.stderr)

        if args.output:
            print(f"✅ Results saved to: {result['output_file']}", file=sys.stderr)
        else:
            # Print to stdout if no output file specified
            save_fasta_results(result['templates'])

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()