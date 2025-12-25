#!/usr/bin/env python3
"""
Script: motif_extraction.py
Description: Extract single and multi-terminal loop motifs from RNA secondary structures

Original Use Case: examples/use_case_1_motif_extraction.py
Dependencies Removed: subprocess calls to FOREST.py, repo path dependencies

Usage:
    python scripts/motif_extraction.py --input <input_file> --output <output_file>

Example:
    python scripts/motif_extraction.py --input examples/data/test.fa.txt --output results/motifs.txt
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any
import json
import sys

# Add scripts/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from lib.forest_core import (
    terminal_motif_extraction,
    parse_fasta_with_structure,
    save_fasta_results
)

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "max_length": 134,
    "output_format": "fasta",
    "include_metadata": True
}

# ==============================================================================
# Core Function
# ==============================================================================
def run_motif_extraction(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract RNA terminal motifs using FOREST algorithm.

    Args:
        input_file: Path to FASTA file with RNA sequences and structures
        output_file: Path to save extracted motifs (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - motifs: Extracted motif data
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_motif_extraction("input.fa.txt", "output.txt")
        >>> print(f"Extracted {len(result['motifs'])} motifs")
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Parse input file
    try:
        parsed_data = parse_fasta_with_structure(input_file)
    except Exception as e:
        raise ValueError(f"Failed to parse input file: {e}")

    if not parsed_data:
        raise ValueError("No valid sequences found in input file")

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

    # Save output if requested
    output_path = None
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_fasta_results(all_motifs, output_path)

    # Prepare metadata
    metadata = {
        "input_file": str(input_file),
        "processed_sequences": processed_sequences,
        "total_motifs": len(all_motifs),
        "config": config
    }

    return {
        "motifs": all_motifs,
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
    parser.add_argument('--output', '-o',
                        help='Output file path (default: stdout)')
    parser.add_argument('--config', '-c',
                        help='Config file (JSON)')
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
    if args.max_length != 134:  # Only override if not default
        cli_overrides['max_length'] = args.max_length

    try:
        # Run extraction
        result = run_motif_extraction(
            input_file=args.input,
            output_file=args.output,
            config=config,
            **cli_overrides
        )

        # Print summary
        metadata = result['metadata']
        print(f"✅ Successfully processed {metadata['processed_sequences']} sequences", file=sys.stderr)
        print(f"✅ Extracted {metadata['total_motifs']} motifs", file=sys.stderr)

        if args.output:
            print(f"✅ Results saved to: {result['output_file']}", file=sys.stderr)
        else:
            # Print to stdout if no output file specified
            save_fasta_results(result['motifs'])

        return result

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()