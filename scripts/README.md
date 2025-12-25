# FOREST MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (`argparse`, `pathlib`, `typing`, `json`, standard library)
2. **Self-Contained**: Core FOREST functions inlined in `lib/forest_core.py`, no repo dependencies
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Config File | Independent |
|--------|-------------|-------------|-------------|
| `motif_extraction.py` | Extract terminal RNA motifs | `configs/motif_extraction_config.json` | ✅ Yes |
| `library_design.py` | Design RNA probe library with barcodes | `configs/library_design_config.json` | ✅ Yes |
| `dna_template_design.py` | Generate DNA templates for oligo pools | `configs/dna_template_config.json` | ✅ Yes |
| `microarray_design.py` | Design microarray capture barcodes | `configs/microarray_config.json` | ✅ Yes |
| `comprehensive_workflow.py` | Complete FOREST workflow (all steps) | `configs/comprehensive_config.json` | ✅ Yes |

## Shared Library

Core FOREST functions are in `lib/forest_core.py`:
- **terminal_motif_extraction()**: Main FOREST algorithm
- **parse_fasta_with_structure()**: Parse FASTA files with RNA structures
- **load_barcodes()**: Load barcode files
- **conjugate_stem()**: Add stabilizing stems
- **revcom()**: Reverse complement sequences
- **save_fasta_results()**: Save results in FASTA format

## Usage

```bash
# Basic usage
python scripts/motif_extraction.py --input examples/data/test.fa.txt --output results/motifs.txt

# With configuration file
python scripts/library_design.py --input FILE --barcodes FILE --output FILE --config configs/library_design_config.json

# Complete workflow
python scripts/comprehensive_workflow.py --input FILE --barcodes FILE --output_dir results/
```

## Examples

### 1. Extract RNA Motifs
```bash
python scripts/motif_extraction.py \
  --input examples/data/test.fa.txt \
  --output results/motifs.txt \
  --max_length 134
```

### 2. Design RNA Library
```bash
python scripts/library_design.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 3 \
  --output results/rna_library.txt
```

### 3. Complete Workflow
```bash
python scripts/comprehensive_workflow.py \
  --input examples/data/test.fa.txt \
  --barcodes examples/data/barcode25mer_100000.txt \
  --num_barcodes 2 \
  --output_dir results/comprehensive/
```

## Configuration Files

Each script accepts a JSON configuration file with the `--config` parameter:

```json
{
  "max_length": 134,
  "num_barcodes": 5,
  "barcode_prefix": "GGG",
  "stem_length": 17,
  "output_format": "fasta"
}
```

Configuration files are stored in `configs/` directory.

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped as an MCP tool:

```python
# Import the script function
from scripts.motif_extraction import run_motif_extraction

# In MCP tool definition:
@mcp.tool()
def extract_motifs(input_file: str, output_file: str = None, max_length: int = 134):
    """Extract RNA terminal motifs using FOREST algorithm."""
    return run_motif_extraction(input_file, output_file, max_length=max_length)
```

## Input/Output Formats

### Input Files
- **RNA Sequences**: FASTA format with secondary structures in dot-bracket notation
- **Barcodes**: Text file with one DNA barcode per line

### Output Files
- **FASTA Format**: All scripts output FASTA format with sequence names and structures/sequences
- **JSON Metadata**: Scripts return structured metadata about processing results

## Dependencies

- **Python Standard Library Only**: `argparse`, `pathlib`, `typing`, `json`, `re`, `collections`
- **No External Packages**: No numpy, pandas, biopython, or other dependencies
- **No Repo Dependencies**: All FOREST code inlined in `lib/forest_core.py`

## Testing

All scripts have been tested with the example data:

```bash
# Test all scripts
python scripts/motif_extraction.py --input examples/data/test.fa.txt --output results/test_motifs.txt
python scripts/library_design.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 3 --output results/test_library.txt
python scripts/comprehensive_workflow.py --input examples/data/test.fa.txt --barcodes examples/data/barcode25mer_100000.txt --num_barcodes 2 --output_dir results/test_comprehensive/
```

Expected outputs match the original FOREST.py results from Step 4 testing.