#!/usr/bin/env python3
"""
FOREST Use Case 5: Comprehensive Workflow

Run the complete FOREST workflow including motif extraction, library design,
DNA template design, and microarray design. This demonstrates the full pipeline
for RNA structure dataset analysis and multiplexed affinity assay design.

Usage:
    python examples/use_case_5_comprehensive_workflow.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 2
    python examples/use_case_5_comprehensive_workflow.py --input examples/data/test_100.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 3
"""

import argparse
import sys
import os
import subprocess

def run_forest_command(cmd, description, output_file=None):
    """Run a FOREST command with proper error handling"""
    print(f"\n=== {description} ===")
    print(f"Command: {' '.join(cmd)}")

    try:
        if output_file:
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=True)
            print(f"✓ Results saved to: {output_file}")
        else:
            print("Output:")
            result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, check=True)

        if result.stderr:
            print(f"Warnings: {result.stderr}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ Error: Python interpreter not found")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive FOREST workflow",
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
        '--output_dir', '-o',
        default='forest_output',
        help='Output directory for all results'
    )

    parser.add_argument(
        '--num_barcodes', '-bn',
        type=int,
        default=2,
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

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print("FOREST Comprehensive Workflow")
    print("=" * 50)
    print(f"Input file: {args.input}")
    print(f"Barcodes file: {args.barcodes}")
    print(f"Number of barcodes: {args.num_barcodes}")
    print(f"Max length: {args.max_length}")
    print(f"Output directory: {args.output_dir}")

    base_cmd = [
        sys.executable,
        'repo/FOREST2020/FOREST.py',
        args.input,
        '-L', str(args.max_length)
    ]

    # Step 1: Motif Extraction
    motif_cmd = base_cmd.copy()
    motif_output = os.path.join(args.output_dir, 'motifs.txt')
    success1 = run_forest_command(motif_cmd, "1. Motif Extraction", motif_output)

    # Step 2: RNA Library Design
    library_cmd = base_cmd + [
        '--library',
        '--barcodes', args.barcodes,
        '-bn', str(args.num_barcodes)
    ]
    library_output = os.path.join(args.output_dir, 'rna_library.txt')
    success2 = run_forest_command(library_cmd, "2. RNA Library Design", library_output)

    # Step 3: DNA Template Design
    template_cmd = base_cmd + [
        '--library',
        '--barcodes', args.barcodes,
        '--templates',
        '-bn', str(args.num_barcodes)
    ]
    template_output = os.path.join(args.output_dir, 'dna_templates.txt')
    success3 = run_forest_command(template_cmd, "3. DNA Template Design", template_output)

    # Step 4: Microarray Design
    array_cmd = base_cmd + [
        '--library',
        '--barcodes', args.barcodes,
        '--array',
        '-bn', str(args.num_barcodes)
    ]
    array_output = os.path.join(args.output_dir, 'microarray_barcodes.txt')
    success4 = run_forest_command(array_cmd, "4. Microarray Design", array_output)

    # Summary
    print("\n" + "=" * 50)
    print("WORKFLOW SUMMARY")
    print("=" * 50)

    steps = [
        ("Motif Extraction", success1, motif_output),
        ("RNA Library Design", success2, library_output),
        ("DNA Template Design", success3, template_output),
        ("Microarray Design", success4, array_output)
    ]

    all_success = True
    for step_name, success, output_file in steps:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{step_name:<20} {status:<10} {output_file if success else 'N/A'}")
        if not success:
            all_success = False

    print("\n" + "=" * 50)
    if all_success:
        print("✓ All steps completed successfully!")
        print(f"Check results in: {args.output_dir}/")
    else:
        print("✗ Some steps failed. Check error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()