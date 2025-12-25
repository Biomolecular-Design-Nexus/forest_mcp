# FOREST2020 MCP

> RNA secondary structure analysis and probe design toolkit for functional RNA element identification

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

FOREST (Functional Organization of RNA Element Selection and Testing) is a comprehensive toolkit for RNA secondary structure analysis and probe design. This MCP server enables extraction of terminal motifs from RNA structures and design of molecular probes for multiplexed affinity assays and functional RNA element identification.

### Features
- Extract terminal RNA motifs from secondary structures in dot-bracket format
- Design RNA probe libraries with DNA barcodes for multiplexed assays
- Generate DNA templates with T7 promoter for oligonucleotide pool synthesis
- Design microarray capture sequences for RNA probe hybridization
- Support both synchronous (fast) and asynchronous (background) processing
- Comprehensive batch processing capabilities for high-throughput workflows

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   └── server.py           # MCP server
├── scripts/
│   ├── motif_extraction.py      # Extract terminal RNA motifs
│   ├── library_design.py        # Design RNA probe library
│   ├── dna_template_design.py   # Generate DNA templates
│   ├── microarray_design.py     # Design microarray barcodes
│   ├── comprehensive_workflow.py # Complete FOREST workflow
│   └── lib/                     # Shared utilities
├── examples/
│   └── data/               # Demo data
├── configs/                # Configuration files
└── repo/                   # Original repository
```

---

## Installation

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- No external scientific dependencies required (uses only built-in Python libraries)

### Create Environment

Please strictly follow the information in `reports/step3_environment.md` for the complete setup procedure. An example workflow is shown below:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.10 -y
# or: conda create -p ./env python=3.10 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install MCP dependencies
pip install fastmcp loguru --ignore-installed
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/motif_extraction.py` | Extract terminal motifs from RNA structures | See below |
| `scripts/library_design.py` | Design RNA probe library with barcodes | See below |
| `scripts/dna_template_design.py` | Generate DNA templates with T7 promoter | See below |
| `scripts/microarray_design.py` | Design microarray capture barcodes | See below |
| `scripts/comprehensive_workflow.py` | Complete FOREST workflow | See below |

### Script Examples

#### RNA Motif Extraction

```bash
# Activate environment
mamba activate ./env

# Run script
python scripts/motif_extraction.py \
  --input examples/data/test.fa.txt \
  --output results/motifs.txt \
  --max_length 134
```

**Parameters:**
- `--input, -i`: FASTA file with RNA sequences and dot-bracket structures (required)
- `--output, -o`: Output file path for extracted motifs (optional)
- `--max_length`: Maximum motif length to extract (default: 134)

#### RNA Library Design

```bash
python scripts/library_design.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 5 \
  --output results/library.txt
```

**Parameters:**
- `--input, -i`: FASTA file with RNA sequences and structures (required)
- `--barcodes, -b`: File with DNA barcodes (one per line) (required)
- `--num_barcodes`: Number of barcodes per motif (default: 5)
- `--output, -o`: Output file path (optional)

#### DNA Template Design

```bash
python scripts/dna_template_design.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 3 \
  --output results/templates.txt
```

#### Microarray Design

```bash
python scripts/microarray_design.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 2 \
  --output results/array.txt
```

#### Complete FOREST Workflow

```bash
python scripts/comprehensive_workflow.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --output_dir results/complete/ \
  --num_barcodes 2
```

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name FOREST2020
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add FOREST2020 -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "FOREST2020": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from FOREST2020?
```

#### Basic Usage
```
Use extract_rna_motifs with input file @examples/data/test.fa.txt
```

#### With Configuration
```
Run design_rna_library on @examples/data/test.fa.txt using barcodes @examples/data/barcode25mer_100000.txt with 3 barcodes per motif
```

#### Long-Running Tasks (Submit API)
```
Submit comprehensive_workflow for @examples/data/test_100.fa.txt with barcodes @examples/data/barcode25mer_100000.txt
Then check the job status
```

#### Batch Processing
```
Process these files in batch:
- @examples/data/test.fa.txt
- @examples/data/test_100.fa.txt
Use the submit_batch_motif_extraction tool
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/test.fa.txt` | Reference a specific file |
| `@configs/motif_extraction_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "FOREST2020": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Use extract_rna_motifs with file examples/data/test.fa.txt
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 2 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `extract_rna_motifs` | Extract terminal motifs from RNA structures | `input_file`, `output_file`, `max_length` |
| `design_rna_library` | Design RNA probe library with barcodes | `input_file`, `barcodes_file`, `output_file`, `num_barcodes` |
| `design_dna_templates` | Generate DNA templates with T7 promoter | `input_file`, `barcodes_file`, `output_file`, `num_barcodes` |
| `design_microarray_barcodes` | Design microarray capture barcodes | `input_file`, `barcodes_file`, `output_file`, `num_barcodes` |
| `run_forest_workflow` | Complete FOREST pipeline (all 4 steps) | `input_file`, `barcodes_file`, `output_dir`, `num_barcodes` |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 2 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_motif_extraction` | Background motif extraction | `input_file`, `job_name`, `output_dir`, `max_length` |
| `submit_library_design` | Background library design | `input_file`, `barcodes_file`, `job_name`, `output_dir`, `num_barcodes` |
| `submit_template_design` | Background template design | `input_file`, `barcodes_file`, `job_name`, `output_dir`, `num_barcodes` |
| `submit_microarray_design` | Background microarray design | `input_file`, `barcodes_file`, `job_name`, `output_dir`, `num_barcodes` |
| `submit_comprehensive_workflow` | Background complete workflow | `input_file`, `barcodes_file`, `output_dir`, `job_name`, `num_barcodes` |

### Batch Processing Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_batch_motif_extraction` | Process multiple FASTA files | `input_files`, `output_dir`, `job_name`, `max_length` |
| `submit_batch_forest_workflow` | Run workflow on multiple files | `input_files`, `barcodes_file`, `output_dir`, `job_name`, `num_barcodes` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

### Utility Tools

| Tool | Description |
|------|-------------|
| `validate_input_format` | Validate FASTA/barcode file formats |
| `get_example_data` | List available example datasets |

---

## Examples

### Example 1: Terminal Motif Extraction

**Goal:** Extract RNA motifs from secondary structures for functional analysis

**Using Script:**
```bash
python scripts/motif_extraction.py \
  --input examples/data/test.fa.txt \
  --output results/example1/motifs.txt
```

**Using MCP (in Claude Code):**
```
Use extract_rna_motifs to process @examples/data/test.fa.txt and save results to results/example1/motifs.txt
```

**Expected Output:**
- Extracted terminal motifs in FASTA format
- 9 motifs from 2 input sequences (for test data)
- Processing time: < 1 second

### Example 2: RNA Library Design

**Goal:** Design barcoded RNA probe library for multiplexed assays

**Using Script:**
```bash
python scripts/library_design.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 5 \
  --output results/example2/library.txt
```

**Using MCP (in Claude Code):**
```
Run design_rna_library on @examples/data/test.fa.txt with barcodes @examples/data/barcode25mer_100000.txt using 5 barcodes per motif
```

**Expected Output:**
- RNA probe library with conjugated barcodes
- 45 probes from 9 motifs × 5 barcodes each
- Processing time: < 5 seconds

### Example 3: Complete FOREST Workflow

**Goal:** Run complete pipeline for probe design

**Using Script:**
```bash
python scripts/comprehensive_workflow.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 2 \
  --output_dir results/example3/
```

**Using MCP (in Claude Code):**
```
Use run_forest_workflow with input @examples/data/test.fa.txt, barcodes @examples/data/barcode25mer_100000.txt, output directory results/example3/, and 2 barcodes per sequence
```

**Expected Output:**
- `motifs.txt`: Extracted terminal motifs
- `rna_library.txt`: RNA probe library with barcodes
- `dna_templates.txt`: DNA templates with T7 promoter
- `microarray_barcodes.txt`: Microarray capture barcodes

### Example 4: Batch Processing

**Goal:** Process multiple datasets in parallel

**Using MCP (in Claude Code):**
```
Submit batch_motif_extraction for multiple files:
- examples/data/test.fa.txt
- examples/data/test_100.fa.txt
Save results to results/batch/
```

**Expected Output:**
- Separate output directory for each input file
- Job tracking for monitoring progress
- Combined results summary

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `test.fa.txt` | Small test dataset (2 sequences) for quick testing | All tools |
| `test_100.fa.txt` | Larger dataset (100 sequences) for performance testing | Submit tools |
| `barcode25mer_100000.txt` | 100,000 DNA barcodes for library design | Library/template/microarray tools |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `motif_extraction_config.json` | Motif extraction settings | `max_length`, `output_format` |
| `library_design_config.json` | Library design parameters | `num_barcodes`, `barcode_prefix`, `stem_length` |
| `dna_template_config.json` | Template generation settings | `num_barcodes`, `t7_promoter` |
| `microarray_config.json` | Microarray design parameters | `num_barcodes`, `barcode_prefix` |
| `comprehensive_config.json` | Workflow configuration | `steps`, workflow settings |

### Config Example

```json
{
  "max_length": 134,
  "output_format": "fasta",
  "include_metadata": true
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install fastmcp loguru --ignore-installed
```

**Problem:** Import errors
```bash
# Verify installation
python -c "import sys; sys.path.insert(0, 'src'); from server import mcp; print('Server OK')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove FOREST2020
claude mcp add FOREST2020 -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Tools not working
```bash
# Test server directly
mamba run -p ./env python -c "
import sys
sys.path.insert(0, 'src')
from server import mcp
print('Server loaded successfully')
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

### Common File Issues

**Problem:** File not found errors
- Use absolute paths: `/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/forest_mcp/examples/data/test.fa.txt`
- Verify files exist: `ls examples/data/`
- Check working directory: `pwd`

**Problem:** Invalid file format
```
Use validate_input_format to check file structure before processing
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run integration tests
python tests/run_integration_tests.py
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py
```

### Performance Monitoring

| Operation | Small Dataset | Medium Dataset | Large Dataset | Recommendation |
|-----------|---------------|----------------|---------------|----------------|
| Motif Extraction | 2 seq: 0.15s | 100 seq: 8s | 1000+ seq | Use submit for >1000 |
| Library Design | 9 motifs: 0.25s | 100 motifs: 15s | 10000+ probes | Use submit for >10000 |
| Complete Workflow | 2 seq: 0.30s | 100 seq: 45s | 500+ seq | Use submit for >500 |

---

## License

Based on [FOREST2020](https://github.com/vineetbansal/forest)

## Credits

Original FOREST algorithm developed for RNA secondary structure analysis and probe design. This MCP implementation provides modern interface for high-throughput RNA functional element identification workflows.