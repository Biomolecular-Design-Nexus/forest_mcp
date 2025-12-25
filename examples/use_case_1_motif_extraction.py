#!/usr/bin/env python3
"""
FOREST Use Case 1: Terminal Motif Extraction

Extract single and multi-terminal loop motifs from RNA secondary structures
in dot-bracket format. This is the core functionality of FOREST.

Usage:
    python examples/use_case_1_motif_extraction.py --input examples/data/test.fa.txt --max_length 134
    python examples/use_case_1_motif_extraction.py --input examples/data/test_100.fa.txt --max_length 134
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description="Extract RNA terminal motifs using FOREST algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--input', '-i',
        default='examples/data/test.fa.txt',
        help='Input file: Multiple FASTA file with RNA secondary structures in dot-bracket format'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    parser.add_argument(
        '--max_length', '-L',
        type=int,
        default=134,
        help='Limit the maximum length of extracted motifs'
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Import FOREST module
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'repo', 'FOREST2020'))

    # Build command for FOREST
    import subprocess

    cmd = [
        sys.executable,
        'repo/FOREST2020/FOREST.py',
        args.input,
        '-L', str(args.max_length)
    ]

    print(f"Running command: {' '.join(cmd)}")
    print(f"Input file: {args.input}")
    print(f"Max length: {args.max_length}")
    print("-" * 50)

    try:
        if args.output:
            with open(args.output, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
            print(f"Results saved to: {args.output}")
        else:
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, check=True)

        if result.stderr:
            print("Warnings/Errors:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error running FOREST: {e}", file=sys.stderr)
        if e.stderr:
            print(f"Error details: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Python interpreter not found", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()