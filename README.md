# qrcode-dyalog

A QR Code encoder written in Dyalog APL 20.

## Usage

```apl
      'High' QR.Encode 'HELLO WORLD'
      ('Medium' 3) QR.Encode 'test'   ⍝ force mask pattern 3
```

The left argument specifies the error correction level (`'Low'`, `'Medium'`, `'Quartile'`, or `'High'`). Optionally pass a 2-element vector to also select a specific mask pattern (0–7).

`Encode` returns a Boolean matrix (1s and 0s) representing the QR code modules.

## Features

- Supports numeric, alphanumeric, and byte encoding modes
- Automatic mode selection based on input data
- All four error correction levels
- Reed-Solomon error correction using GF(256) arithmetic
- Automatic or manual mask pattern selection

## Requirements

- Dyalog APL version 20 or later

## Installation

Copy the `QR` namespace folder into your project and load it:

```apl
      ⎕SE.Link.Import # 'path/to/QR'
```

## Running the APL test suite

1. Generate (or refresh) reference matrices:

```powershell
python generate_test_references.py
```

2. Run the APL test script:

```powershell
D:\devel\dyalog\20.0\scriptbin\dyalogscript.ps1 .\test_qr.apls
```

## License

This project is released into the public domain under the [Unlicense](LICENSE).
