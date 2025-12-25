#!/usr/bin/env python3
"""
FOREST Use Case 3: DNA Template Pool Design

Generate DNA template sequences that contain reverse complementary DNA of RNA probes
with T7 promoter for ordering an oligo pool. This is used for creating the physical
DNA templates needed for RNA structure library synthesis.

Usage:
    python examples/use_case_3_dna_template_design.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 3
    python examples/use_case_3_dna_template_design.py --input examples/data/test_100.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 2
"""

import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(
        description="Design DNA template pool using FOREST algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--input', '-i',
        default='examples/data/test.fa.txt',
        help='Input file: Multiple FASTA file with RNA secondary structures'
    )

    parser.add_argument(
        '--barcodes', '-b',
        default='examples/data/barcode25mer_100000.txt',
        help='Barcode file containing DNA barcodes'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    parser.add_argument(
        '--num_barcodes', '-bn',
        type=int,
        default=3,
        help='Number of barcodes per RNA structure'
    )

    parser.add_argument(
        '--max_length', '-L',
        type=int,
        default=134,
        help='Limit the maximum length of extracted motifs'
    )

    args = parser.parse_args()

    # Check if input files exist
    for file_path, name in [(args.input, 'Input'), (args.barcodes, 'Barcode')]:
        if not os.path.exists(file_path):
            print(f"Error: {name} file '{file_path}' not found", file=sys.stderr)
            sys.exit(1)

    # Build command for FOREST
    import subprocess

    cmd = [
        sys.executable,
        'repo/FOREST2020/FOREST.py',
        args.input,
        '--library',
        '--barcodes', args.barcodes,
        '--templates',
        '-bn', str(args.num_barcodes),
        '-L', str(args.max_length)
    ]

    print(f"Running command: {' '.join(cmd)}")
    print(f"Input file: {args.input}")
    print(f"Barcodes file: {args.barcodes}")
    print(f"Number of barcodes: {args.num_barcodes}")
    print(f"Max length: {args.max_length}")
    print("Output: DNA templates with T7 promoter")
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