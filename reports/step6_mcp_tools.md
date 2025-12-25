# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: FOREST
- **Version**: 1.0.0
- **Created Date**: 2024-12-24
- **Server Path**: `src/server.py`
- **Protocol**: Model Context Protocol (MCP)
- **Technology**: FastMCP

## Overview

The FOREST MCP server provides tools for RNA secondary structure analysis and probe design. FOREST (Functional Organization of RNA Element Selection and Testing) enables extraction of terminal motifs from RNA structures and design of molecular probes for various applications.

---

## Job Management Tools

All asynchronous operations are managed through a job queue system that supports tracking, cancellation, and result retrieval.

| Tool | Description | Usage |
|------|-------------|-------|
| `get_job_status` | Check job progress and current status | `get_job_status(job_id="abc123")` |
| `get_job_result` | Retrieve completed job results | `get_job_result(job_id="abc123")` |
| `get_job_log` | View job execution logs | `get_job_log(job_id="abc123", tail=50)` |
| `cancel_job` | Cancel running job | `cancel_job(job_id="abc123")` |
| `list_jobs` | List all jobs with optional status filter | `list_jobs(status="running")` |

---

## Synchronous Tools (Fast Operations < 2 min)

These tools execute immediately and return results directly. Suitable for small to medium datasets.

| Tool | Description | Source Script | Est. Runtime | Max Dataset Size |
|------|-------------|---------------|--------------|------------------|
| `extract_rna_motifs` | Extract terminal motifs from RNA structures | `motif_extraction.py` | ~0.15 sec | ~1000 sequences |
| `design_rna_library` | Design RNA probe library with barcodes | `library_design.py` | ~0.25 sec | ~10000 probes |
| `design_dna_templates` | Generate DNA templates with T7 promoter | `dna_template_design.py` | ~0.20 sec | ~5000 templates |
| `design_microarray_barcodes` | Design microarray capture sequences | `microarray_design.py` | ~0.18 sec | ~2000 barcodes |
| `run_forest_workflow` | Complete FOREST pipeline (all 4 steps) | `comprehensive_workflow.py` | ~0.30 sec | ~500 sequences |

### Tool Details

#### extract_rna_motifs
- **Description**: Extract single and multi-terminal loop motifs from RNA secondary structures using the FOREST algorithm
- **Source Script**: `scripts/motif_extraction.py`
- **Estimated Runtime**: ~0.15 seconds for small datasets

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and dot-bracket structures |
| output_file | str | No | None | Optional path to save extracted motifs |
| max_length | int | No | 134 | Maximum motif length to extract |

**Example:**
```
extract_rna_motifs(
    input_file="examples/data/test.fa.txt",
    output_file="results/motifs.txt",
    max_length=134
)
```

**Returns:**
```json
{
  "status": "success",
  "motifs": [list of extracted motifs],
  "num_sequences": 2,
  "num_motifs": 9,
  "output_file": "results/motifs.txt",
  "processing_time": 0.15
}
```

---

#### design_rna_library
- **Description**: Design RNA probe library by concatenating barcodes with RNA motifs and adding stabilizing stems
- **Source Script**: `scripts/library_design.py`
- **Estimated Runtime**: ~0.25 seconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| barcodes_file | str | Yes | - | Path to file with DNA barcodes (one per line) |
| output_file | str | No | None | Optional path to save RNA library |
| num_barcodes | int | No | 5 | Number of barcodes to use per motif |

**Example:**
```
design_rna_library(
    input_file="examples/data/test.fa.txt",
    barcodes_file="examples/data/barcode25mer_100000.txt",
    num_barcodes=5
)
```

---

#### design_dna_templates
- **Description**: Generate DNA template sequences with reverse complement and T7 promoter for oligonucleotide pool synthesis
- **Source Script**: `scripts/dna_template_design.py`
- **Estimated Runtime**: ~0.20 seconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| barcodes_file | str | Yes | - | Path to file with DNA barcodes |
| output_file | str | No | None | Optional path to save DNA templates |
| num_barcodes | int | No | 3 | Number of barcodes to use per template |

**Example:**
```
design_dna_templates(
    input_file="examples/data/test.fa.txt",
    barcodes_file="examples/data/barcode25mer_100000.txt",
    num_barcodes=3
)
```

---

#### design_microarray_barcodes
- **Description**: Design DNA barcode sequences for microarray capture of RNA probes
- **Source Script**: `scripts/microarray_design.py`
- **Estimated Runtime**: ~0.18 seconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| barcodes_file | str | Yes | - | Path to file with DNA barcodes |
| output_file | str | No | None | Optional path to save microarray barcodes |
| num_barcodes | int | No | 2 | Number of barcodes to use per sequence |

**Example:**
```
design_microarray_barcodes(
    input_file="examples/data/test.fa.txt",
    barcodes_file="examples/data/barcode25mer_100000.txt",
    num_barcodes=2
)
```

---

#### run_forest_workflow
- **Description**: Run complete FOREST workflow combining all four steps (motifs + library + templates + microarray)
- **Source Script**: `scripts/comprehensive_workflow.py`
- **Estimated Runtime**: ~0.30 seconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| barcodes_file | str | Yes | - | Path to file with DNA barcodes |
| output_dir | str | Yes | - | Directory to save all output files |
| num_barcodes | int | No | 2 | Number of barcodes to use per sequence |

**Example:**
```
run_forest_workflow(
    input_file="examples/data/test.fa.txt",
    barcodes_file="examples/data/barcode25mer_100000.txt",
    output_dir="results/workflow/"
)
```

**Returns:** Creates 4 output files:
- `output_dir/motifs.txt` - Extracted RNA motifs
- `output_dir/rna_library.txt` - RNA probe library
- `output_dir/dna_templates.txt` - DNA templates
- `output_dir/microarray_barcodes.txt` - Microarray barcodes

---

## Submit Tools (Long Operations & Batch Processing)

These tools return a job_id immediately and process in the background. Use for large datasets, batch processing, or workflow integration.

| Tool | Description | Source Script | Use Case | Supports Batch |
|------|-------------|---------------|----------|-----------------|
| `submit_motif_extraction` | Background motif extraction | `motif_extraction.py` | >1000 sequences | ✅ Yes |
| `submit_library_design` | Background library design | `library_design.py` | >10000 probes | ✅ Yes |
| `submit_template_design` | Background template design | `dna_template_design.py` | >5000 templates | ✅ Yes |
| `submit_microarray_design` | Background microarray design | `microarray_design.py` | >2000 barcodes | ✅ Yes |
| `submit_comprehensive_workflow` | Background complete workflow | `comprehensive_workflow.py` | >500 sequences | ✅ Yes |

### Submit Tool Details

#### submit_motif_extraction
- **Description**: Submit RNA motif extraction for background processing
- **Use Case**: Large datasets (>1000 sequences) or workflow integration
- **Supports Batch**: ✅ Yes via `submit_batch_motif_extraction`

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| output_dir | str | No | job directory | Directory to save outputs |
| max_length | int | No | 134 | Maximum motif length to extract |
| job_name | str | No | auto-generated | Custom job name for tracking |

**Example:**
```
submit_motif_extraction(
    input_file="large_dataset.fa",
    output_dir="results/motifs/",
    job_name="motif_analysis_batch1"
)
→ Returns: {"job_id": "abc123", "status": "submitted"}
```

---

#### submit_comprehensive_workflow
- **Description**: Submit complete FOREST workflow for background processing
- **Use Case**: Production workflows, large datasets (>500 sequences)
- **Supports Batch**: ✅ Yes via `submit_batch_forest_workflow`

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to FASTA file with RNA sequences and structures |
| barcodes_file | str | Yes | - | Path to file with DNA barcodes |
| output_dir | str | Yes | - | Directory to save all outputs |
| num_barcodes | int | No | 2 | Number of barcodes to use per sequence |
| job_name | str | No | auto-generated | Custom job name for tracking |

**Example:**
```
submit_comprehensive_workflow(
    input_file="production_dataset.fa",
    barcodes_file="barcodes.txt",
    output_dir="results/production/",
    job_name="production_run_v1"
)
→ Returns: {"job_id": "def456", "status": "submitted"}
```

---

## Batch Processing Tools

Special tools for processing multiple input files in parallel.

| Tool | Description | Input Type | Output Organization |
|------|-------------|------------|---------------------|
| `submit_batch_motif_extraction` | Process multiple FASTA files | List of FASTA files | Separate results per file |
| `submit_batch_forest_workflow` | Run workflow on multiple files | List of FASTA files + shared barcodes | Subdirectory per file |

### Batch Tool Details

#### submit_batch_motif_extraction
**Example:**
```
submit_batch_motif_extraction(
    input_files=["dataset1.fa", "dataset2.fa", "dataset3.fa"],
    output_dir="results/batch_motifs/",
    job_name="batch_motif_analysis"
)
```

#### submit_batch_forest_workflow
**Example:**
```
submit_batch_forest_workflow(
    input_files=["sample1.fa", "sample2.fa"],
    barcodes_file="shared_barcodes.txt",
    output_dir="results/batch_forest/",
    job_name="multi_sample_analysis"
)
```

**Output Structure:**
```
results/batch_forest/
├── sample1/
│   ├── motifs.txt
│   ├── rna_library.txt
│   ├── dna_templates.txt
│   └── microarray_barcodes.txt
└── sample2/
    ├── motifs.txt
    ├── rna_library.txt
    ├── dna_templates.txt
    └── microarray_barcodes.txt
```

---

## Utility Tools

Additional tools for validation and data exploration.

| Tool | Description | Purpose |
|------|-------------|---------|
| `validate_input_format` | Validate file formats | Check FASTA/barcode file validity |
| `get_example_data` | List available example datasets | Discover test data |

### validate_input_format
**Example:**
```
validate_input_format(
    input_file="examples/data/test.fa.txt",
    format_type="fasta_structure"
)
→ Returns: {"status": "success", "sequences": 2, "valid": true}
```

### get_example_data
**Example:**
```
get_example_data()
→ Returns: List of example files with sizes and descriptions
```

---

## Workflow Examples

### Quick Analysis (Synchronous)
```
1. Extract motifs:
   extract_rna_motifs(
       input_file="examples/data/test.fa.txt",
       output_file="results/motifs.txt"
   )
   → Returns results immediately (~0.15 seconds)

2. Design library:
   design_rna_library(
       input_file="examples/data/test.fa.txt",
       barcodes_file="examples/data/barcode25mer_100000.txt",
       num_barcodes=5
   )
   → Returns library immediately (~0.25 seconds)
```

### Production Workflow (Asynchronous)
```
1. Submit complete workflow:
   submit_comprehensive_workflow(
       input_file="large_dataset.fa",
       barcodes_file="production_barcodes.txt",
       output_dir="results/production/",
       job_name="production_v1"
   )
   → Returns: {"job_id": "abc123", "status": "submitted"}

2. Monitor progress:
   get_job_status(job_id="abc123")
   → Returns: {"status": "running", "progress": "Step 2/4"}

3. Retrieve results:
   get_job_result(job_id="abc123")
   → Returns: {"status": "success", "output_files": [...]}
```

### Batch Processing Workflow
```
1. Submit batch analysis:
   submit_batch_forest_workflow(
       input_files=["sample1.fa", "sample2.fa", "sample3.fa"],
       barcodes_file="barcodes.txt",
       output_dir="results/batch/",
       job_name="multi_sample_study"
   )
   → Returns: {"job_id": "def456", "status": "submitted"}

2. Check logs during processing:
   get_job_log(job_id="def456", tail=20)
   → Returns: Recent log lines showing current file being processed

3. Get final results:
   get_job_result(job_id="def456")
   → Returns: Paths to all output subdirectories and files
```

---

## Input Data Formats

### RNA Sequences with Structures (FASTA + Dot-Bracket)
```
>sequence_1
GGGGAAAAACCCC
((((....))))

>sequence_2
AAAGCGUAAUUUCGCUAACCC
.((....)).((....))...
```

### DNA Barcodes File
```
AAACGTAACGTAACGTAACGTAACGT
AAACGTAACGTAACGTAACGTATCGT
AAACGTAACGTAACGTAACGTCTCGT
[... one barcode per line ...]
```

---

## Output Formats

All outputs are in FASTA format with descriptive headers:

### Motifs Output
```
>motif_1_from_sequence_1_terminal_single
AAAAA

>motif_2_from_sequence_1_terminal_multi
CCCC
```

### RNA Library Output
```
>probe_1_motif_AAAAA_barcode_AAACGTAACGT
GGGAAACGTAACGTAAAAAAACCAAAGUCCCCUUU

>probe_2_motif_CCCC_barcode_AAACGTAACGT
GGGAAACGTAACGTCCCCACCAAAGUCCCCUUU
```

### DNA Templates Output
```
>template_1_T7_AAAAA_barcode_AAACGTAACGT
GCGCTAATACGACTCACTATAGGGAAACGTAACGTAAAAACCAAAGUCCCCUUU

>template_1_revcom_AAAAA_barcode_AAACGTAACGT
AAAGGGACCUUUGGUUUUACGUUACGUCC
```

### Microarray Barcodes Output
```
>array_barcode_1_for_AAAAA
GGGAAACGTAACGT

>array_barcode_2_for_CCCC
GGGAAACGTAACGT
```

---

## Performance Characteristics

| Operation | Small Dataset | Medium Dataset | Large Dataset | Recommendation |
|-----------|---------------|----------------|---------------|----------------|
| Motif Extraction | 2 seq: 0.15s | 100 seq: 8s | 1000+ seq | Use submit for >1000 |
| Library Design | 9 motifs: 0.25s | 100 motifs: 15s | 10000+ probes | Use submit for >10000 |
| DNA Templates | 24 probes: 0.20s | 500 probes: 30s | 5000+ templates | Use submit for >5000 |
| Microarray Design | 24 probes: 0.18s | 200 probes: 10s | 2000+ barcodes | Use submit for >2000 |
| Complete Workflow | 2 seq: 0.30s | 100 seq: 45s | 500+ seq | Use submit for >500 |

---

## Error Handling

All tools return structured error responses:

```json
{
  "status": "error",
  "error": "File not found: invalid_file.fa",
  "error_type": "FileNotFoundError"
}
```

Common error types:
- `FileNotFoundError`: Input file doesn't exist
- `ValueError`: Invalid file format or parameters
- `PermissionError`: Cannot write to output location
- `RuntimeError`: Algorithm processing error

---

## Configuration

The server uses configuration files in `configs/` directory:

- `motif_extraction_config.json`: Motif extraction parameters
- `library_design_config.json`: Library design settings
- `dna_template_config.json`: Template generation settings
- `microarray_config.json`: Microarray design parameters
- `comprehensive_config.json`: Workflow configuration

These configs are loaded automatically and can be overridden by tool parameters.

---

## Success Criteria ✅

- [x] MCP server created at `src/server.py`
- [x] Job management system implemented for async operations
- [x] 5 sync tools created for fast operations (<2 min)
- [x] 5 submit tools created for long-running operations
- [x] 2 batch processing tools for multiple file processing
- [x] 5 job management tools working (status, result, log, cancel, list)
- [x] All tools have clear descriptions optimized for LLM use
- [x] Error handling returns structured responses
- [x] All 5 original FOREST scripts wrapped as MCP tools
- [x] Both sync and submit APIs implemented
- [x] Comprehensive documentation created

**Total Tools Created: 17**
- 5 Synchronous tools
- 5 Submit tools
- 2 Batch processing tools
- 5 Job management tools

The FOREST MCP server successfully converts all original FOREST functionality into a modern, scalable MCP interface supporting both immediate and background processing workflows.