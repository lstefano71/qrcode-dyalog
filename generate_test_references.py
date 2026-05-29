#!/usr/bin/env python3
"""Generate reference QR code matrices for testing QR.Encode in Dyalog APL.

Usage:
    pip install qrcode
    python generate_test_references.py

Produces:
  - test_references/*.txt  — one file per test case (QR module matrix, no quiet zone)
  - test_references/manifest.json — machine-readable test case definitions

The APL test script (test_qr.apls) reads the manifest and reference files
to verify QR.Encode output.
"""

import json
import os

import qrcode
from qrcode.util import lost_point

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_references")

EC_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

EC_NAMES = {"L": "Low", "M": "Medium", "Q": "Quartile", "H": "High"}


def generate_reference(data, error, version, mask):
    """Generate a QR code matrix. Returns (rows_as_strings, actual_mask)."""
    if mask is not None:
        qr = qrcode.QRCode(
            version=version, error_correction=EC_MAP[error],
            mask_pattern=mask, border=0,
        )
        qr.add_data(data, optimize=0)
        qr.make(fit=False)
        actual_mask = mask
    else:
        best_mask, best_score = 0, float("inf")
        for m in range(8):
            qr = qrcode.QRCode(
                version=version, error_correction=EC_MAP[error],
                mask_pattern=m, border=0,
            )
            qr.add_data(data, optimize=0)
            qr.make(fit=False)
            score = lost_point(qr.modules)
            if score < best_score:
                best_score = score
                best_mask = m
        qr = qrcode.QRCode(
            version=version, error_correction=EC_MAP[error],
            mask_pattern=best_mask, border=0,
        )
        qr.add_data(data, optimize=0)
        qr.make(fit=False)
        actual_mask = best_mask

    expected_size = 17 + 4 * version
    matrix = qr.get_matrix()
    assert len(matrix) == expected_size
    rows = ["".join("1" if cell else "0" for cell in row) for row in matrix]
    return rows, actual_mask


def build_test_cases():
    """Build the full list of test cases."""
    cases = []

    def add(filename, data, ec, version, mask):
        cases.append((filename, data, ec, version, mask))

    # ── Original 10 core tests ────────────────────────────────────────────────
    add("tc01_alpha_Q_mask0.txt", "HELLO WORLD", "Q", 1, 0)
    add("tc02_alpha_H_mask3.txt", "HELLO WORLD", "H", 2, 3)
    add("tc03_num_M_mask2.txt", "01234567", "M", 1, 2)
    add("tc04_byte_L_mask5.txt", "Hello, world!", "L", 1, 5)
    add("tc05_alpha_H_mask7.txt", "AC-42", "H", 1, 7)
    add("tc06_byte_M_mask1.txt", "https://example.com", "M", 2, 1)
    add("tc07_num_Q_mask4.txt", "0123456789012345", "Q", 1, 4)
    add("tc08_alpha_M_auto.txt", "HELLO WORLD", "M", 1, None)
    add("tc09_num_H_auto.txt", "1234567890", "H", 1, None)
    add("tc10_byte_L_mask6.txt", "Test1234!", "L", 1, 6)

    # ── Exhaustive mask coverage: alphanumeric ────────────────────────────────
    for mask in range(8):
        add(f"tc_alpha_M_mask{mask}.txt", "HELLO WORLD", "M", 1, mask)

    # ── Exhaustive mask coverage: numeric ─────────────────────────────────────
    for mask in range(8):
        add(f"tc_num_L_mask{mask}.txt", "0123456789", "L", 1, mask)

    # ── Exhaustive mask coverage: byte ────────────────────────────────────────
    for mask in range(8):
        add(f"tc_byte_Q_mask{mask}.txt", "Hello APL!", "Q", 1, mask)

    # ── All EC levels with same data and mask ─────────────────────────────────
    for ec in "LMQH":
        add(f"tc_alpha_ec{ec}_mask2.txt", "TEST DATA", ec, 1, 2)

    # ── Version tests (V1–V6) ─────────────────────────────────────────────────
    add("tc_version1_mask0.txt", "12345", "H", 1, 0)
    add("tc_version2_mask1.txt", "12345678901234567890", "H", 2, 1)
    add("tc_version3_mask2.txt", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456", "H", 3, 2)
    add("tc_version4_mask3.txt", "ABCDEFGHIJ" * 5, "H", 4, 3)
    add("tc_version5_mask4.txt", "ABCDEFGHIJ" * 6 + "ABCD", "H", 5, 4)
    add("tc_version6_mask5.txt", "ABCDEFGHIJ" * 8 + "ABCD", "H", 6, 5)

    # ── Auto mask with various inputs ─────────────────────────────────────────
    add("tc_auto_num_short.txt", "42", "M", 1, None)
    add("tc_auto_alpha_url.txt", "HTTP://EXAMPLE.COM", "L", 1, None)
    add("tc_auto_byte_email.txt", "a@b.com", "Q", 1, None)
    add("tc_auto_num_long.txt", "31415926535897932384626433832795028", "M", 2, None)
    add("tc_auto_alpha_v2.txt", "THE QUICK BROWN FOX JUMPS", "Q", 2, None)
    add("tc_auto_byte_v2.txt", "Hello, World! 12345", "L", 2, None)

    # ── Edge cases: capacity boundaries ───────────────────────────────────────
    add("tc_maxcap_v1L_byte.txt", "X" * 17, "L", 1, 3)
    add("tc_maxcap_v1H_num.txt", "9" * 17, "H", 1, 5)
    add("tc_maxcap_v1M_alpha.txt", "ABCDEFGHIJ0123456789", "M", 1, 1)

    # ── Single character inputs ───────────────────────────────────────────────
    add("tc_single_num.txt", "7", "H", 1, 0)
    add("tc_single_alpha.txt", "Z", "H", 1, 0)
    add("tc_single_byte.txt", "z", "L", 1, 0)

    # ── Special character patterns ────────────────────────────────────────────
    add("tc_spaces.txt", "   ", "L", 1, 2)
    add("tc_allzeros.txt", "0000000", "M", 1, 6)
    add("tc_url_lower.txt", "https://www.dyalog.com", "M", 2, 4)

    # ── V2 with alignment patterns, all masks ─────────────────────────────────
    for mask in range(8):
        add(f"tc_v2_byte_mask{mask}.txt", "Version 2 alignment test!", "M", 2, mask)

    # ── Numeric remainder edge cases ──────────────────────────────────────────
    add("tc_num_rem0.txt", "123456789", "L", 1, 0)     # 9 digits, rem 0
    add("tc_num_rem1.txt", "1234567890", "L", 1, 0)    # 10 digits, rem 1
    add("tc_num_rem2.txt", "12345678", "L", 1, 0)      # 8 digits, rem 2

    # ── Alphanumeric remainder edge cases ─────────────────────────────────────
    add("tc_alpha_even.txt", "AB", "H", 1, 0)          # even length
    add("tc_alpha_odd.txt", "ABC", "H", 1, 0)          # odd length

    # ── Byte mode with various content ────────────────────────────────────────
    add("tc_byte_punct.txt", "!@#$%^&*()", "L", 1, 3)
    add("tc_byte_mixed.txt", "abc123DEF", "M", 1, 7)

    return cases


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cases = build_test_cases()
    manifest = []

    print(f"Generating {len(cases)} reference QR matrices in {OUTPUT_DIR}/")
    print()

    for filename, data, error, version, mask in cases:
        filepath = os.path.join(OUTPUT_DIR, filename)
        rows, actual_mask = generate_reference(data, error, version, mask)

        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(row + "\n")

        manifest.append({
            "file": filename,
            "data": data,
            "ec": EC_NAMES[error],
            "version": version,
            "mask": mask if mask is not None else -1,
            "actual_mask": actual_mask,
            "size": len(rows),
        })

        mask_desc = f"mask {mask}" if mask is not None else f"auto (chose {actual_mask})"
        print(f"  {filename:35s}  {len(rows)}x{len(rows[0])}  {mask_desc}")

    # Write JSON manifest for APL test script
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Write README
    readme_path = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# QR Test Reference Files\n\n")
        f.write("Generated by `generate_test_references.py` using the Python `qrcode` library.\n\n")
        f.write("## Regeneration\n\n")
        f.write("```bash\n")
        f.write("pip install qrcode\n")
        f.write("python generate_test_references.py\n")
        f.write("```\n\n")
        f.write(f"## Test Cases ({len(cases)} total)\n\n")
        f.write("See `manifest.json` for the full machine-readable list.\n\n")
        f.write("## File Format\n\n")
        f.write("Each `.txt` file contains the QR module matrix (no quiet zone).\n")
        f.write("One row per line; each character is `0` (white) or `1` (black).\n")
        f.write("Parse in APL: `ref ← '1'=↑⊃⎕NGET filename 1`\n")

    print()
    print(f"Done. {len(cases)} references + manifest.json written.")


if __name__ == "__main__":
    main()
