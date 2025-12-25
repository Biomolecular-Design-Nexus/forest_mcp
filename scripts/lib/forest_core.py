"""
Core FOREST algorithm functions.

Extracted and simplified from FOREST2020/FOREST.py to minimize dependencies
and create self-contained functionality for MCP tool wrapping.

Original author: Kaoru R. Komatsu
"""

import re
from collections import Counter
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


# ==============================================================================
# Core Pattern Matching
# ==============================================================================

# Regex pattern for loop structures: one or more '(' followed by one or more '.' followed by one or more ')'
LOOP_PATTERN = re.compile(r'\(+\.+\)+')


# ==============================================================================
# Utility Functions (inlined from FOREST.py)
# ==============================================================================

def bracket_divider(seq: str) -> List[str]:
    """
    Divide sequence at the boundary between ')' or '.' and other characters.

    Original: FOREST.py lines 27-33
    """
    i = 0
    while i < len(seq) and (seq[i] == "." or seq[i] == ")"):
        i += 1
    return [seq[0:i], seq[i:]]


def revcom(seq: str) -> str:
    """
    Generate reverse complement of a nucleotide sequence.

    Original: FOREST.py lines 35-42
    """
    seq = seq.upper()
    seq = seq.replace("A", "t")
    seq = seq.replace("U", "a")
    seq = seq.replace("T", "a")
    seq = seq.replace("G", "c")
    seq = seq.replace("C", "g")
    return seq[::-1].upper()


def hitpoint_brew(hitpoint: int, seq: str) -> str:
    """
    Extract sequence up to a specific bracket count.

    Original: FOREST.py lines 44-50
    """
    i = 0
    while hitpoint != 0 and i < len(seq):
        if seq[i] == ")" or seq[i] == "(":
            hitpoint -= 1
        i += 1
    return seq[0:i]


def hitpoint_counter(hitpoint: int, seq: str, bracket: str) -> str:
    """
    Count brackets and extract sequence partition.

    Original: FOREST.py lines 52-65
    """
    partition = ""
    i = 0
    if bracket == ")":
        while hitpoint != partition.count(bracket) and i < len(seq):
            partition = seq[0:i]
            i += 1
        return partition
    elif bracket == "(":
        seq_rev = seq[::-1]
        while hitpoint != partition.count(bracket) and i < len(seq_rev):
            partition = seq_rev[0:i]
            i += 1
        return partition[::-1]
    return ""


def loop_brew(seq: str) -> List[str]:
    """
    Extract terminal loop structures from RNA secondary structure.

    This is the core loop extraction algorithm from FOREST.
    Original: FOREST.py lines 67-121
    """
    output = []
    main = LOOP_PATTERN.findall(seq)
    part = LOOP_PATTERN.split(seq)

    for m in range(len(main)):
        n = m + 1
        if n >= len(part):
            break

        left = part[m]
        right = part[n]

        if left == "":
            left = "."
        if right == "":
            right = "."

        part_left = bracket_divider(left)[1]
        part_right = bracket_divider(right)[0]
        whole = ''.join([part_left, main[m], part_right])
        hitpoint_right_g = hitpoint_left_g = min(whole.count("("), whole.count(")"))

        main_c = Counter(main[m])

        hitpoint_left = hitpoint_left_g - int(main_c.get("(", 0))
        hitpoint_right = hitpoint_right_g - int(main_c.get(")", 0))

        if hitpoint_right == 0 and hitpoint_left == 0:
            output.append(main[m].strip('.'))

        elif hitpoint_right < 0 or hitpoint_left < 0:
            refseq = main[m]

            if hitpoint_right < 0:
                refseq = hitpoint_counter(hitpoint_right_g, refseq, ")")
                hitright_left = hitpoint_counter(hitpoint_left, left, "(")
                final_out = ''.join([hitright_left, refseq])

            elif hitpoint_left < 0:
                refseq = hitpoint_counter(hitpoint_left_g, refseq, "(")
                hitright_left = hitpoint_counter(hitpoint_right, right, ")")
                final_out = ''.join([refseq, hitright_left])

            elif hitpoint_right < 0 and hitpoint_left < 0:
                # Error case - skip
                continue

            output.append(final_out)

        else:
            final_right = hitpoint_counter(hitpoint_right, part_right, ")")
            final_left = hitpoint_counter(hitpoint_left, part_left, "(")
            output.append(''.join([final_left, main[m], final_right]))

    return output


def dot_replace(seq: str, looplist: List[str]) -> str:
    """
    Replace loop structures with dots for multi-terminal extraction.

    Original: FOREST.py lines 123-127
    """
    for i in looplist:
        num = len(i)
        seq = seq.replace(i, "." * num, 1)
    return seq


def packman(seq: str) -> str:
    """
    Pack/compress secondary structure by removing outer brackets.

    Original: FOREST.py lines 129-143
    """
    if not seq or "." not in seq:
        return seq

    # Find first and last dot positions
    try:
        i = 0
        t = 0
        while i < len(seq) and seq[i] != ".":
            i += 1
        while t < len(seq) and seq[len(seq)-1-t] != ".":
            t += 1
        pack_num = max(i, t)

        i = 0
        t = 0
        while i < len(seq) and seq[:i].count("(") != pack_num:
            i += 1
        while t < len(seq) and seq[len(seq)-1-t:len(seq)].count(")") != pack_num:
            t += 1

        if i < len(seq) and t < len(seq):
            return seq[i:len(seq)-1-t].strip('.')
        else:
            return seq.strip('.')
    except:
        return seq.strip('.')


def loop_list_judge(secondary_loop_list: List[str]) -> str:
    """
    Judge the status of secondary loop list.

    Original: FOREST.py lines 145-152
    """
    if len(secondary_loop_list) >= 1:
        return "Read"
    elif secondary_loop_list == []:
        return "Zero"
    else:
        return "Error"


def locus_find(seq: str, loop: str) -> List[int]:
    """
    Find the position of a loop in the sequence.

    Original: FOREST.py lines 154-157
    """
    try:
        left = seq.index(loop)
        right = left + len(loop)
        return [left, right]
    except ValueError:
        return [0, 0]


def threshold(secondary_seq: str, loop_structure: str, limit: int) -> List[int]:
    """
    Apply length threshold and find locus.

    Original: FOREST.py lines 159-168 (renamed from 'theshold')
    """
    if len(loop_structure) > limit:
        while len(loop_structure) >= limit:
            loop_structure = packman(loop_structure)

    locus = locus_find(secondary_seq, loop_structure)
    return locus


def loop_replace_extract(seq: str, seq2: str, single_structure_result: List[str]) -> List[List[str]]:
    """
    Extract sequences based on loop structures.

    Original: FOREST.py lines 170-178
    """
    output = []
    for i in single_structure_result:
        left = seq.find(i)
        if left >= 0:
            right = left + len(i)
            output.append([seq[left:right], seq2[left:right]])
            rep = '!' * len(i)
            seq = seq.replace(str(i), rep, 1)
    return output


def conjugate_stem(seq: str, n: int = 17) -> str:
    """
    Add stabilizing stem sequences around the RNA motif.

    Original: FOREST.py lines 180-184
    """
    forward = "GTGTACGAAGTTTCAGC"[0:n]
    reverse = "GCTGAAGCTTCGTGCAC"[:n]
    output = forward + seq + reverse
    return output


# ==============================================================================
# Core FOREST Algorithm
# ==============================================================================

def terminal_motif_extraction(name: str, seq: str, seq2: str, max_length: int = 100) -> Dict[str, List[str]]:
    """
    Main terminal motif extraction algorithm.

    Extracts both single and multi-terminal RNA motifs.
    Original: FOREST.py lines 188-236

    Args:
        name: Sequence name/identifier
        seq: Secondary structure (dot-bracket notation)
        seq2: Primary sequence (nucleotides)
        max_length: Maximum motif length

    Returns:
        Dict mapping motif names to [structure, sequence] pairs
    """
    output = {}

    # Single terminal motif extraction
    loop_list = loop_brew(seq)
    result1 = loop_replace_extract(seq, seq2, loop_list)

    strct = seq
    motifcount = 1
    for t in range(len(result1)):
        identical_name = '_'.join([name, "Motif", str(motifcount)])

        lr_locus = threshold(strct, result1[t][0], limit=max_length)
        outseqandstrc = [strct[lr_locus[0]:lr_locus[1]], seq2[lr_locus[0]:lr_locus[1]]]

        if len(outseqandstrc[1]) <= max_length:
            output[identical_name] = outseqandstrc
            motifcount += 1
        rep = '!' * len(result1[t][0])
        strct = strct.replace(str(result1[t][0]), rep, 1)

    # Multiple terminal motif extraction
    def multi_terminal_motif_extraction(name: str, secondary_seq: str,
                                       secondary_loop_list: List[str],
                                       library_length_limit: int,
                                       replace_times: int) -> Dict[str, List[str]]:
        output2 = {}
        if loop_list_judge(secondary_loop_list) == "Read":
            for k, i in enumerate(secondary_loop_list):
                loop_rep = i
                identical_name_multi = '_'.join([name, "Multi", str(k+1), "ComplexLevel", str(1+replace_times)])
                lr_locus = threshold(secondary_seq, loop_rep, library_length_limit)
                outseqandstrc = [seq[lr_locus[0]:lr_locus[1]], seq2[lr_locus[0]:lr_locus[1]]]
                if len(outseqandstrc[1]) <= library_length_limit:
                    output2[identical_name_multi] = outseqandstrc
        return output2

    secondary_seq = dot_replace(seq, loop_list)
    replace_times = 0

    while "(" in secondary_seq:
        secondary_loop_list = loop_brew(secondary_seq)
        output.update(multi_terminal_motif_extraction(name, secondary_seq, secondary_loop_list, max_length, replace_times))
        secondary_seq = dot_replace(secondary_seq, secondary_loop_list)
        replace_times += 1

        # Safety break to avoid infinite loops
        if replace_times > 50:
            break

    return output


# ==============================================================================
# File I/O Functions
# ==============================================================================

def parse_fasta_with_structure(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Parse FASTA file with RNA sequences and secondary structures.

    Expected format:
    >sequence_name
    SEQUENCE_STRING
    STRUCTURE_STRING (dot-bracket notation)

    Returns:
        List of (name, sequence, structure) tuples
    """
    results = []

    with open(file_path) as f:
        name = ""
        sequence = ""
        structure = ""

        for line in f:
            line = line.strip()

            if line.startswith('>'):
                # Save previous entry if complete
                if name and sequence and structure:
                    # Clean structure notation
                    structure = structure.split()[0]  # Take first token
                    structure = structure.replace("&", ".")
                    structure = structure.replace("]", ".").replace("[", ".")  # Remove pseudoknots
                    results.append((name, sequence, structure))

                # Start new entry
                tokens = line.split('|')
                name = tokens[0]
                sequence = ""
                structure = ""

            elif line and line[0].lower() in ["a", "t", "u", "g", "c"]:
                # Sequence line
                sequence = line.upper()

            elif line and (line.startswith('(') or line.startswith('.') or line.startswith(')')):
                # Structure line
                structure = line

        # Don't forget the last entry
        if name and sequence and structure:
            structure = structure.split()[0]
            structure = structure.replace("&", ".")
            structure = structure.replace("]", ".").replace("[", ".")
            results.append((name, sequence, structure))

    return results


def load_barcodes(file_path: Path) -> List[str]:
    """
    Load DNA barcodes from file.

    Args:
        file_path: Path to barcode file

    Returns:
        List of barcode sequences
    """
    barcodes = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and line[0].lower() in ["a", "t", "g", "c"]:
                barcodes.append(line.upper())
    return barcodes


def save_fasta_results(results: Dict[str, List[str]], output_path: Optional[Path] = None) -> None:
    """
    Save results in FASTA format.

    Args:
        results: Dict mapping names to [structure, sequence] pairs
        output_path: Optional file path to save (prints to stdout if None)
    """
    output_lines = []

    for name, (structure, sequence) in results.items():
        if sequence and structure:
            output_lines.append(f">{name}")
            output_lines.append(sequence)
            output_lines.append(structure)

    output_text = '\n'.join(output_lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(output_text)
    else:
        print(output_text)