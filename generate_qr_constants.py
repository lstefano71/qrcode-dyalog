#!/usr/bin/env python3
"""Generate verified QR code constants for Dyalog APL QR encoder."""

# =============================================================================
# 1. GF(256) LOG AND ANTILOG TABLES (polynomial 0x11D)
# =============================================================================

def generate_gf_tables():
    """Generate GF(256) exp/log tables using primitive polynomial 0x11D."""
    exp_table = [0] * 256
    log_table = [0] * 256
    
    val = 1
    for i in range(255):
        exp_table[i] = val
        log_table[val] = i
        val <<= 1
        if val >= 256:
            val ^= 0x11D
    exp_table[255] = 0  # convention
    # log_table[0] stays 0 (undefined, unused)
    
    # Cross-check: exp[0]=1, exp[1]=2, exp[7]=128, exp[8]=29 (0x1D = 256 XOR 0x11D = 256^285... 
    # actually 256 XOR 0x11D: 0x100 XOR 0x11D = 0x01D = 29)
    assert exp_table[0] == 1
    assert exp_table[1] == 2
    assert exp_table[7] == 128
    assert exp_table[8] == 29  # 256 ^ 0x11D = 29
    assert exp_table[254] == 142
    # Verify log is inverse of exp
    for i in range(255):
        assert log_table[exp_table[i]] == i, f"Failed at i={i}"
    
    return exp_table, log_table

# =============================================================================
# 2. ALIGNMENT PATTERN CENTER POSITIONS (versions 1-40)
# =============================================================================

# From QR code specification Table E.1
ALIGNMENT_POSITIONS = [
    [],                          # Version 1
    [6, 18],                     # Version 2
    [6, 22],                     # Version 3
    [6, 26],                     # Version 4
    [6, 30],                     # Version 5
    [6, 34],                     # Version 6
    [6, 22, 38],                 # Version 7
    [6, 24, 42],                 # Version 8
    [6, 26, 46],                 # Version 9
    [6, 28, 50],                 # Version 10
    [6, 30, 54],                 # Version 11
    [6, 32, 58],                 # Version 12
    [6, 34, 62],                 # Version 13
    [6, 26, 46, 66],             # Version 14
    [6, 26, 48, 70],             # Version 15
    [6, 26, 50, 74],             # Version 16
    [6, 30, 54, 78],             # Version 17
    [6, 30, 56, 82],             # Version 18
    [6, 30, 58, 86],             # Version 19
    [6, 34, 62, 90],             # Version 20
    [6, 28, 50, 72, 94],         # Version 21
    [6, 26, 50, 74, 98],         # Version 22
    [6, 30, 54, 78, 102],        # Version 23
    [6, 28, 54, 80, 106],        # Version 24
    [6, 32, 58, 84, 110],        # Version 25
    [6, 30, 58, 86, 114],        # Version 26
    [6, 34, 62, 90, 118],        # Version 27
    [6, 26, 50, 74, 98, 122],    # Version 28
    [6, 30, 54, 78, 102, 126],   # Version 29
    [6, 26, 52, 78, 104, 130],   # Version 30
    [6, 30, 56, 82, 108, 134],   # Version 31
    [6, 34, 60, 86, 112, 138],   # Version 32
    [6, 30, 58, 86, 114, 142],   # Version 33
    [6, 34, 62, 90, 118, 146],   # Version 34
    [6, 30, 54, 78, 102, 126, 150],  # Version 35
    [6, 24, 50, 76, 102, 128, 154],  # Version 36
    [6, 28, 54, 80, 106, 132, 158],  # Version 37
    [6, 32, 58, 84, 110, 136, 162],  # Version 38
    [6, 26, 54, 82, 110, 138, 166],  # Version 39
    [6, 30, 58, 86, 114, 142, 170],  # Version 40
]

# =============================================================================
# 3. DATA CAPACITY TABLE
# From QR spec tables 7 and 9
# Format: (total_data_codewords, ec_per_block, blocks_g1, data_per_block_g1, blocks_g2, data_per_block_g2)
# =============================================================================

# Total codewords per version (data + EC)
TOTAL_CODEWORDS = [
    26, 44, 70, 100, 134, 172, 196, 242, 292, 346,
    404, 466, 532, 581, 655, 733, 815, 901, 991, 1085,
    1156, 1258, 1364, 1474, 1588, 1706, 1828, 1921, 2051, 2185,
    2323, 2465, 2611, 2761, 2876, 3034, 3196, 3362, 3532, 3706
]

# EC codewords per block for each version and level [version-1][level]
# Level order: L=0, M=1, Q=2, H=3
EC_CODEWORDS_PER_BLOCK = [
    [7, 10, 13, 17],      # V1
    [10, 16, 22, 28],     # V2
    [15, 26, 18, 22],     # V3
    [20, 18, 26, 16],     # V4
    [26, 24, 18, 22],     # V5
    [18, 16, 24, 28],     # V6
    [20, 18, 18, 26],     # V7
    [24, 22, 22, 26],     # V8
    [30, 22, 20, 24],     # V9
    [18, 26, 24, 28],     # V10
    [20, 30, 28, 24],     # V11
    [24, 22, 26, 28],     # V12
    [26, 22, 24, 22],     # V13
    [30, 24, 20, 24],     # V14
    [22, 24, 30, 24],     # V15
    [24, 28, 24, 30],     # V16
    [28, 28, 28, 28],     # V17
    [30, 26, 28, 28],     # V18
    [28, 26, 26, 26],     # V19
    [28, 26, 28, 28],     # V20
    [28, 26, 28, 30],     # V21
    [28, 28, 28, 24],     # V22
    [30, 28, 28, 30],     # V23
    [30, 28, 28, 30],     # V24
    [26, 28, 28, 30],     # V25
    [28, 28, 28, 30],     # V26
    [30, 28, 28, 30],     # V27
    [30, 28, 28, 30],     # V28
    [30, 28, 28, 30],     # V29
    [30, 28, 28, 30],     # V30
    [30, 28, 28, 30],     # V31
    [30, 28, 28, 30],     # V32
    [30, 28, 28, 30],     # V33
    [30, 28, 28, 30],     # V34
    [30, 28, 28, 30],     # V35
    [30, 28, 28, 30],     # V36
    [30, 28, 28, 30],     # V37
    [30, 28, 28, 30],     # V38
    [30, 28, 28, 30],     # V39
    [30, 28, 28, 30],     # V40
]

# Number of blocks: [version-1][level] = (blocks_group1, blocks_group2)
BLOCK_COUNTS = [
    # V1
    [(1,0), (1,0), (1,0), (1,0)],
    # V2
    [(1,0), (1,0), (1,0), (1,0)],
    # V3
    [(1,0), (1,0), (2,0), (2,0)],
    # V4
    [(1,0), (2,0), (2,0), (4,0)],
    # V5
    [(1,0), (2,0), (2,2), (2,2)],
    # V6
    [(2,0), (4,0), (4,0), (4,0)],
    # V7
    [(2,0), (4,0), (2,4), (4,1)],
    # V8
    [(2,0), (2,2), (4,2), (4,2)],
    # V9
    [(2,0), (3,2), (4,4), (4,4)],
    # V10
    [(2,2), (4,1), (6,2), (6,2)],
    # V11
    [(4,0), (1,4), (4,4), (3,8)],
    # V12
    [(2,2), (6,2), (4,6), (7,4)],
    # V13
    [(4,0), (8,1), (8,4), (12,4)],
    # V14
    [(3,1), (4,5), (11,5), (11,5)],
    # V15
    [(5,1), (5,5), (5,7), (11,7)],
    # V16
    [(5,1), (7,3), (15,2), (3,13)],
    # V17
    [(1,5), (10,1), (1,15), (2,17)],
    # V18
    [(5,1), (9,4), (17,1), (2,19)],
    # V19
    [(3,4), (3,11), (17,4), (9,16)],
    # V20
    [(3,5), (3,13), (15,5), (15,10)],
    # V21
    [(4,4), (17,0), (17,6), (19,6)],
    # V22
    [(2,7), (17,0), (7,16), (34,0)],
    # V23
    [(4,5), (4,14), (11,14), (16,14)],
    # V24
    [(6,4), (6,14), (11,16), (30,2)],
    # V25
    [(8,4), (8,13), (7,22), (22,13)],
    # V26
    [(10,2), (19,4), (28,6), (33,4)],
    # V27
    [(8,4), (22,3), (8,26), (12,28)],
    # V28
    [(3,10), (3,23), (4,31), (11,31)],
    # V29
    [(7,7), (21,7), (1,37), (19,26)],
    # V30
    [(5,10), (19,10), (15,25), (23,25)],
    # V31
    [(13,3), (2,29), (42,1), (23,28)],
    # V32
    [(17,0), (10,23), (10,35), (19,35)],
    # V33
    [(17,1), (14,21), (29,19), (11,46)],
    # V34
    [(13,6), (14,23), (44,7), (59,1)],
    # V35
    [(12,7), (12,26), (39,14), (22,41)],
    # V36
    [(6,14), (6,34), (46,10), (2,64)],
    # V37
    [(17,4), (29,14), (49,10), (24,46)],
    # V38
    [(4,18), (13,32), (48,14), (42,32)],
    # V39
    [(20,4), (40,7), (43,22), (10,67)],
    # V40
    [(19,6), (18,31), (34,34), (20,61)],
]

def compute_data_capacity():
    """Compute full data capacity table from the spec data."""
    # Returns: capacity[version-1][level] = (total_data_cw, ec_per_block, g1_blocks, g1_data_per, g2_blocks, g2_data_per)
    result = []
    for v in range(40):
        version_data = []
        for level in range(4):
            total_cw = TOTAL_CODEWORDS[v]
            ec_per_block = EC_CODEWORDS_PER_BLOCK[v][level]
            g1_blocks, g2_blocks = BLOCK_COUNTS[v][level]
            total_blocks = g1_blocks + g2_blocks
            total_ec = ec_per_block * total_blocks
            total_data = total_cw - total_ec
            
            # Data codewords per block
            # Group 1 blocks have floor(total_data / total_blocks) codewords
            # Group 2 blocks have ceil(total_data / total_blocks) codewords
            if g2_blocks == 0:
                g1_data_per = total_data // g1_blocks
                g2_data_per = 0
            else:
                g1_data_per = total_data // total_blocks
                g2_data_per = g1_data_per + 1
            
            # Verify
            computed_data = g1_blocks * g1_data_per + g2_blocks * g2_data_per
            assert computed_data == total_data, \
                f"V{v+1} L{level}: {computed_data} != {total_data} (g1={g1_blocks}x{g1_data_per}, g2={g2_blocks}x{g2_data_per})"
            
            version_data.append((total_data, ec_per_block, g1_blocks, g1_data_per, g2_blocks, g2_data_per))
        result.append(version_data)
    return result

# =============================================================================
# 4. CHARACTER COUNT INDICATOR BIT LENGTHS
# =============================================================================

# [version_range][mode] where mode: 0=numeric, 1=alphanumeric, 2=byte, 3=kanji
CHAR_COUNT_BITS = [
    [10, 9, 8, 8],     # Versions 1-9
    [12, 11, 16, 10],  # Versions 10-26
    [14, 13, 16, 12],  # Versions 27-40
]

# =============================================================================
# 5. FORMAT INFORMATION (15-bit BCH encoded)
# =============================================================================

def bch_format_info(data_5bit):
    """Compute 15-bit format info: 5 data bits + 10 EC bits, XOR mask."""
    # Generator polynomial for format info: x^10 + x^8 + x^5 + x^4 + x^2 + x + 1 = 0x537
    gen = 0x537
    # Shift data to make room for 10 check bits
    bits = data_5bit << 10
    # Polynomial division
    for i in range(14, 9, -1):
        if bits & (1 << i):
            bits ^= gen << (i - 10)
    result = (data_5bit << 10) | bits
    # XOR with mask pattern
    result ^= 0x5412  # 101010000010010
    return result

def generate_format_info():
    """Generate format info for all EC level + mask combinations."""
    # EC level indicators: L=01, M=00, Q=11, H=10
    ec_indicators = [0b01, 0b00, 0b11, 0b10]  # L, M, Q, H
    
    result = []
    for level in range(4):
        level_results = []
        for mask in range(8):
            data = (ec_indicators[level] << 3) | mask
            fmt = bch_format_info(data)
            level_results.append(fmt)
        result.append(level_results)
    return result

# =============================================================================
# 6. VERSION INFORMATION (18-bit BCH encoded)
# =============================================================================

def bch_version_info(version):
    """Compute 18-bit version info: 6 data bits + 12 EC bits."""
    # Generator polynomial: x^12 + x^11 + x^10 + x^9 + x^8 + x^5 + x^2 + 1 = 0x1F25
    gen = 0x1F25
    bits = version << 12
    temp = bits
    for i in range(17, 11, -1):
        if temp & (1 << i):
            temp ^= gen << (i - 12)
    result = bits | temp
    return result

def generate_version_info():
    """Generate version info for versions 7-40."""
    result = []
    for v in range(7, 41):
        result.append(bch_version_info(v))
    return result

# =============================================================================
# 7. MODE CAPACITY TABLE
# =============================================================================

def compute_mode_capacities(data_capacity):
    """Compute max characters per version/level/mode."""
    result = []
    for v in range(40):
        version_data = []
        for level in range(4):
            total_data_cw = data_capacity[v][level][0]
            total_data_bits = total_data_cw * 8
            
            # Determine version range for char count bits
            if v < 9:
                vr = 0
            elif v < 26:
                vr = 1
            else:
                vr = 2
            
            mode_caps = []
            # Numeric mode: 10 bits per 3 chars, 7 bits per 2 chars, 4 bits per 1 char
            # Available bits = total - 4 (mode indicator) - char_count_bits
            for mode_idx, mode_info in enumerate([
                (10, 3, 4, 1),   # numeric: 10 bits/3 chars, remainder 4bits/1char or 7bits/2chars
                (11, 2, 6, 1),   # alphanumeric: 11 bits/2 chars, 6 bits/1 char
                (8, 1, 0, 0),    # byte: 8 bits/1 char
            ]):
                if mode_idx == 0:  # Numeric
                    cc_bits = CHAR_COUNT_BITS[vr][0]
                    avail = total_data_bits - 4 - cc_bits
                    # Each group of 3 digits = 10 bits, 2 digits = 7 bits, 1 digit = 4 bits
                    # Max chars: find largest n where bits_needed(n) <= avail
                    # bits_needed(n) = (n//3)*10 + {0:0, 1:4, 2:7}[n%3]
                    # Solve: start from upper bound and work down
                    # Upper bound: avail/3.33... roughly
                    n = (avail * 3) // 10 + 3
                    while True:
                        rem = n % 3
                        bits_needed = (n // 3) * 10 + [0, 4, 7][rem]
                        if bits_needed <= avail:
                            break
                        n -= 1
                    mode_caps.append(n)
                elif mode_idx == 1:  # Alphanumeric
                    cc_bits = CHAR_COUNT_BITS[vr][1]
                    avail = total_data_bits - 4 - cc_bits
                    # Each pair = 11 bits, odd one = 6 bits
                    n = (avail * 2) // 11 + 2
                    while True:
                        rem = n % 2
                        bits_needed = (n // 2) * 11 + [0, 6][rem]
                        if bits_needed <= avail:
                            break
                        n -= 1
                    mode_caps.append(n)
                else:  # Byte
                    cc_bits = CHAR_COUNT_BITS[vr][2]
                    avail = total_data_bits - 4 - cc_bits
                    n = avail // 8
                    mode_caps.append(n)
            
            version_data.append(mode_caps)
        result.append(version_data)
    return result

# =============================================================================
# MAIN: Generate and print all tables
# =============================================================================

if __name__ == "__main__":
    # 1. GF(256) tables
    exp_table, log_table = generate_gf_tables()
    
    print("# === GF(256) ANTILOG (EXP) TABLE (polynomial 0x11D) ===")
    print("# antilog[i] = 2^i mod 0x11D, antilog[255] = 0")
    print(f"GF_EXP = {exp_table}")
    print()
    print("# === GF(256) LOG TABLE ===")
    print("# log[0] = 0 (undefined), log[x] = i where 2^i = x")
    print(f"GF_LOG = {log_table}")
    print()
    
    # 2. Alignment positions
    print("# === ALIGNMENT PATTERN CENTER POSITIONS (versions 1-40) ===")
    print("ALIGNMENT_POSITIONS = [")
    for i, pos in enumerate(ALIGNMENT_POSITIONS):
        print(f"    {pos},  # Version {i+1}")
    print("]")
    print()
    
    # 3. Data capacity
    data_cap = compute_data_capacity()
    print("# === DATA CAPACITY TABLE ===")
    print("# Format: [version-1][level] = (total_data_cw, ec_per_block, g1_blocks, g1_data_per, g2_blocks, g2_data_per)")
    print("# Levels: 0=L, 1=M, 2=Q, 3=H")
    print("DATA_CAPACITY = [")
    for v in range(40):
        print(f"    # Version {v+1}")
        print(f"    [{data_cap[v][0]}, {data_cap[v][1]}, {data_cap[v][2]}, {data_cap[v][3]}],")
    print("]")
    print()
    
    # 4. Character count bits
    print("# === CHARACTER COUNT INDICATOR BIT LENGTHS ===")
    print("# [version_range][mode] where mode: 0=numeric, 1=alphanumeric, 2=byte, 3=kanji")
    print("# Version ranges: 0=V1-9, 1=V10-26, 2=V27-40")
    print(f"CHAR_COUNT_BITS = {CHAR_COUNT_BITS}")
    print()
    
    # 5. Format information
    fmt_info = generate_format_info()
    print("# === FORMAT INFORMATION STRINGS (15-bit) ===")
    print("# format_info[ec_level][mask_pattern] - levels: 0=L, 1=M, 2=Q, 3=H")
    print("FORMAT_INFO = [")
    level_names = ['L', 'M', 'Q', 'H']
    for level in range(4):
        print(f"    # EC Level {level_names[level]}")
        print(f"    [{', '.join(f'0b{v:015b}' for v in fmt_info[level])}],")
    print("]")
    print()
    # Also print as integers
    print("FORMAT_INFO_INT = [")
    for level in range(4):
        print(f"    {fmt_info[level]},  # {level_names[level]}")
    print("]")
    print()
    
    # 6. Version information
    ver_info = generate_version_info()
    print("# === VERSION INFORMATION STRINGS (18-bit, versions 7-40) ===")
    print("VERSION_INFO = [")
    for i, v in enumerate(ver_info):
        print(f"    0b{v:018b},  # Version {i+7}")
    print("]")
    print()
    print(f"VERSION_INFO_INT = {ver_info}")
    print()
    
    # 7. Mode capacities
    mode_caps = compute_mode_capacities(data_cap)
    print("# === MODE CAPACITY TABLE ===")
    print("# mode_capacity[version-1][level] = [numeric, alphanumeric, byte]")
    print("# Levels: 0=L, 1=M, 2=Q, 3=H")
    print("MODE_CAPACITY = [")
    for v in range(40):
        print(f"    # Version {v+1}")
        print(f"    [{mode_caps[v][0]}, {mode_caps[v][1]}, {mode_caps[v][2]}, {mode_caps[v][3]}],")
    print("]")
    print()
    
    # Verification against known values
    print("# === VERIFICATION ===")
    # V1-L numeric capacity should be 41
    print(f"# V1-L numeric: {mode_caps[0][0][0]} (expected 41)")
    print(f"# V1-M numeric: {mode_caps[0][1][0]} (expected 34)")
    print(f"# V1-Q numeric: {mode_caps[0][2][0]} (expected 27)")
    print(f"# V1-H numeric: {mode_caps[0][3][0]} (expected 17)")
    print(f"# V1-L alphanumeric: {mode_caps[0][0][1]} (expected 25)")
    print(f"# V1-L byte: {mode_caps[0][0][2]} (expected 17)")
    print(f"# V40-L numeric: {mode_caps[39][0][0]} (expected 7089)")
    print(f"# V40-L alphanumeric: {mode_caps[39][0][1]} (expected 4296)")
    print(f"# V40-L byte: {mode_caps[39][0][2]} (expected 2953)")
    
    # Format info verification (known values from spec)
    # M mask 0 should be 101010000010010 XOR ... let's check known: 
    # Data for M, mask 0: ec=00, mask=000 -> data=00000
    # BCH of 00000: remainder of 0 / gen = 0, so result = 0 XOR 0x5412 = 0x5412 = 101010000010010
    print(f"# Format M/mask0: {fmt_info[1][0]:015b} (expected 101010000010010)")
    print(f"# Format L/mask0: {fmt_info[0][0]:015b} (expected 111011111000100)")
