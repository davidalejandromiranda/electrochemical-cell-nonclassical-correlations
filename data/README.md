# Released EIS exports

This directory contains 23 Excel exports used by the public figure-reproduction workflow: the author-selected raw data for the 10 reliable bar measurements reported in the paper, plus the dummy-control exports. The workbook values are unmodified copies of the selected working exports. Files in `Main_Fig6-7/` are named by the corresponding legend labels rather than by plotting colors.

## Coverage

| Directory | Files | Rows per file | Acquired frequency range | Figure use |
|---|---:|---:|---:|---|
| `Main_Fig4/` | 8 | 60 | 100 kHz to 0.1 Hz | Main Figure 4 |
| `Main_Fig5/` | 3 | 80 | 1 MHz to 0.1 Hz | Main Figure 5 |
| `Main_Fig6-7/` | 4 | 80 | 1 MHz to 0.1 Hz | Main Figures 6 and 7 |
| `Supplementary_Fig1/` | 2 | 80 | 1 MHz to 0.1 Hz | Figure S1 |
| `Supplementary_Fig2/` | 2 | 80 | 1 MHz to 0.1 Hz | Figure S2 |
| `Supplementary_Fig3/` | 2 | 80 | 1 MHz to 0.1 Hz | Figure S3 |
| `Supplementary_Fig4/` | 2 | 80 | 1 MHz to 0.1 Hz | Figure S4 |

The acquired frequencies are stored in strictly descending order. Several published plots display only a prefix of a complete series. Those point limits are recorded in `figure_provenance.csv` and implemented in `scr/eis_figures.py`; no low-frequency observations were removed from the released exports.

### Main_Fig6-7 filename normalization

The four `Main_Fig6-7/` workbooks were originally identified by plotting colors in the local working bundle. For the public repository, they are named by the corresponding legend identity:

| Public filename | Local working identifier |
|---|---|
| `Configuration 1.xlsx` | `green.xlsx` |
| `Configuration 3.xlsx` | `red.xlsx` |
| `Configuration 3 + dummy on CE.xlsx` | `purple.xlsx` |
| `Configuration 2 + dummy on CE.xlsx` | `black.xlsx` |

### Acquired versus displayed ranges

All experimental exports listed below were acquired from 1 MHz to 0.1 Hz. The historical plot selections produce these displayed lower limits:

| Figure and series | Displayed points | Displayed frequency range |
|---|---:|---:|
| Figure 5, all three series | 78/80 | 1 MHz to 0.15039 Hz |
| Figure 6, Configuration 1 | 67/80 | 1 MHz to 1.4187 Hz |
| Figure 6, Configuration 3 | 66/80 | 1 MHz to 1.7398 Hz |
| Figure 7, Configuration 3 + dummy | 67/80 | 1 MHz to 1.4187 Hz |
| Figure 7, Configuration 3 | 66/80 | 1 MHz to 1.7398 Hz |
| Figure 7, Configuration 2 + dummy | 69/80 | 1 MHz to 0.94337 Hz |
| Figure 7, optional Configuration 1 | 67/80 | 1 MHz to 1.4187 Hz |
| Figure S1, Configurations 1 / 3 | 71/80; 73/80 | 1 MHz to 0.62729 / 0.41711 Hz |
| Figure S2, both series | 70/80 | 1 MHz to 0.76926 Hz |
| Figure S3, both series | 80/80 | 1 MHz to 0.1 Hz |
| Figure S4, Configurations 1 / 3 | 65/80; 75/80 | 1 MHz to 2.1336 / 0.27736 Hz |

Figure 4 uses all 60 acquired points from 100 kHz to 0.1 Hz for every control series.

## Columns and units

Every workbook contains one sheet, `Sheet1`, with these columns:

| Column | Meaning |
|---|---|
| `Index` | Exported ordinal index |
| `C' (F)` | Real component of complex capacitance exported by the potentiostat, F |
| `C'' (F)` | Imaginary component of complex capacitance exported by the potentiostat and used in the published capacitance plots, F |
| `Frequency (Hz)` | Measurement frequency, Hz |
| `Z' (Ω)` | Real component of impedance, Ω |
| `-Z'' (Ω)` | Negative imaginary impedance component, Ω |
| `Z (Ω)` | Impedance magnitude, Ω |
| `-Phase (°)` | Negative impedance phase, degrees |
| `Time (s)` | Exported acquisition time, s |

The capacitance convention is `C^* = C' - jC''`. The reproduction workflow uses the exported `C' (F)` and `C'' (F)` columns directly after conversion from F to μF; it does not recalculate those plotted capacitance components from impedance. The Figure 5 calculation constructs complex capacitance as `C = C' - i C''` from the exported capacitance columns for each independently characterized bar and evaluates `C_eq = C_1 C_2 / (C_1 + C_2)` in memory.

## Integrity and provenance

- `raw_sha256.csv` records the SHA-256 digest of every Excel file.
- `figure_provenance.csv` maps each manuscript figure to its inputs, plotting function, and display rule.
- `scr/eis_figures.py` checks file coverage, required columns, missing values, row counts, frequency ordering, frequency ranges, and hashes before plotting.

The workbook dimension metadata may be reported as `A1:A1` by direct `openpyxl` read-only iteration. `pandas.read_excel`, which is the tested loader used by this repository, retrieves the complete 60- or 80-row tables and all nine columns. The raw workbooks were not rewritten to change this metadata.

The data package is intentionally limited to the raw exports selected by the authors for the reported figures. It is not a laboratory ledger and should not be used to infer additional sample-history metadata beyond the figure provenance documented here.
