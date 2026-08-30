# Counter-Electrode Dependence of the Working-Electrode Capacitance in Three-Electrode TiO2 + rGO Cells: Classical Controls and Interpretation within a Quantum-Discord Framework

**Authors:** Kevin A. Gonzalez, Nicolás H. Toledo, and David A. Miranda  
**Affiliation:** Universidad Industrial de Santander, 680002 Bucaramanga, Santander, Colombia

## Scope

This repository releases the author-selected raw Excel exports for the 10 reliable bar measurements used in the paper, together with the dummy-control exports and Python workflow needed to reproduce the data-driven figures associated with the manuscript and its Supplementary Material. It supports traceability from each released export to its loading, validation, transformation, display selection, and plotting function.

The EIS measurements are macroscopic impedance observations. They do not directly measure quantum discord or entanglement. The repository reproduces the reported counter-electrode-dependent spectral comparisons and classical controls; it does not establish the proposed quantum-information interpretation independently of the manuscript's assumptions and limitations.

## Contents

```text
.
├── README.md
├── data_visualization.ipynb
├── requirements.txt
├── CITATION.cff
├── LICENSE
├── .zenodo.json
├── data/
│   ├── README.md
│   ├── figure_provenance.csv
│   ├── raw_sha256.csv
│   ├── Main_Fig4/
│   ├── Main_Fig5/
│   ├── Main_Fig6-7/
│   └── Supplementary_Fig1/ ... Supplementary_Fig4/
└── scr/
    ├── __init__.py
    ├── eis_figures.py
    ├── figure_styles.py
    └── validate_notebook.py
```

- `data/` contains 23 complete raw Excel exports, their SHA-256 integrity manifest, and the figure-provenance map.
- `scr/` contains all reusable loading, validation, transformation, and plotting functions.
- `data_visualization.ipynb` is the single public notebook and displays every data-driven main-text and Supplementary Material figure supported by the released exports.

The repository does not include manuscript PDFs, internal reviews, historical drafts, generated image files, laboratory records, or the original working notebook. Figures 1–3 are a photograph and experimental diagrams rather than numerical data plots; they are identified in the provenance map but are not reproduced here.

## Installation

The workflow was tested with Python 3.13.5 and the exact package versions in `requirements.txt`.

```bash
python -m venv .venv
```

Activate the environment on Linux or macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Open `data_visualization.ipynb` in a Jupyter-compatible interface and run it from top to bottom with the repository root as the working directory. A headless validation that executes every cell in memory is also provided:

```bash
python -m scr.validate_notebook
```

Neither route creates a figure-output directory or writes generated images by default.

## Figure styling

The notebook imports the editable `FIGURE_STYLES` dictionary from `scr/figure_styles.py`, initialized with the manuscript defaults. Use it to test colors, markers, marker visibility (`show_marker`), marker fill (`marker_fill`), line visibility (`show_line`), line styles, marker sizes, legend labels, legend placement, and optional titles. Empty title values are ignored, so the default figures do not add subplot titles that are absent from the paper. Marker filling is controlled independently for each plotted series.

To keep the notebook readable, it does not display the complete style dictionary. Each figure call uses the small `figure_config(...)` helper, so local overrides can be passed only to the figure being tested while the default configuration remains in `scr/figure_styles.py`.

Figures 5–7 and S1–S4 are rendered as capacitance Nyquist panels at left plus two capacitance Bode panels at right. The upper Bode panel plots C' versus frequency and the lower Bode panel plots C'' versus frequency. Both Bode panels use a common logarithmic x-axis and right-side y-axis labels; y-limits are not imposed by default. The default panel titles identify the Nyquist and Bode views as `(a)` and `(b)`, and the panel geometry is set for a wider-than-tall layout. Figure 4 remains the original impedance validation figure.

The potentiostat exported the `C' (F)` and `C'' (F)` columns directly. The reproduction workflow uses those exported capacitance columns for Figures 5–7 and S1–S4; it does not recalculate capacitance from impedance for the plotted experimental series. The convention used for capacitance is `C^* = C' - jC''`. Impedance is documented as the measured quantity `Z_m`, without complex-asterisk notation.

Figure 7 marks the nominal dummy-cell frequency with a black dotted vertical line, calculated as `1/(2*pi*R2*C)`. The default dummy values are `R1 = 100 Ohm`, `R2 = 1 kOhm`, `C = 1 uF`, `tau_dummy = 1.00 ms`, and `f_dummy = 159.15 Hz`. The line is controlled by `SHOW_FIGURE_7_DUMMY_FREQUENCY` in the notebook and by `FIGURE_STYLES["figure_7"]["bode"]["dummy_resonance"]["show"]` in `scr/figure_styles.py`. The dummy-cell measurement itself is not plotted.

The Configuration 1 Pt-CE measurement is available in `data/Main_Fig6-7/Configuration 1.xlsx` and can be added to Figure 7 by setting `FIGURE_STYLES["figure_7"]["series"]["configuration_1_pt_ce"]["show"] = True`.

The plotting functions also accept the same dictionary through their `style=` argument, for example:

```python
figure = plot_figure_6(DATA_ROOT, style=FIGURE_STYLES["figure_6"])
```

## Figure coverage

| Item | Repository input | Function | Coverage |
|---|---|---|---|
| Figure 1 | — | — | Photograph; not data-generated |
| Figures 2–3 | — | — | Experimental diagrams; not data-generated |
| Figure 4 | `data/Main_Fig4/` | `plot_figure_4` | Eight dummy-cell/potentiostat validation exports and coded reference model |
| Figure 5 | `data/Main_Fig5/` | `plot_figure_5` | Measured Configuration 2 and calculated equivalent response |
| Figure 6 | `data/Main_Fig6-7/Configuration 1.xlsx`, `Configuration 3.xlsx` | `plot_figure_6` | Configuration 1 versus Configuration 3 |
| Figure 7 | `data/Main_Fig6-7/Configuration 3 + dummy on CE.xlsx`, `Configuration 3.xlsx`, `Configuration 2 + dummy on CE.xlsx`; optional `Configuration 1.xlsx` | `plot_figure_7` | Passive dummy-cell comparison |
| Figures S1–S4 | corresponding `data/Supplementary_Fig*/` directory | `plot_supplementary_figure_1` … `_4` | Four additional Configuration 1–Configuration 3 comparisons |

Exact source filenames and historical display-point selections are recorded in `data/figure_provenance.csv`. Display selections are applied in code to the complete arrays loaded from the raw exports. They do not truncate or overwrite the released files.

## Data provenance and integrity

The release contains the complete 23-file Excel set selected by the authors for the public repository:

- eight 60-point control exports covering 100 kHz to 0.1 Hz;
- fifteen 80-point experimental exports for the 10 valid bars organized into five pairs, covering 1 MHz to 0.1 Hz.

The five pairs were formed because the individual Configuration 1 characterizations, measured with Pt as CE, produced comparable spectra. Pairing was therefore based on the Pt-CE characterization step rather than on the subsequent Configuration 3 outcome.

All exports have a single `Sheet1`, nine expected numeric columns, strictly descending frequency, and no missing cells in the released tables. `data/raw_sha256.csv` records their audited SHA-256 digests. The notebook verifies the hashes and structural expectations before generating figures.

Raw workbook values are retained exactly. The four `Main_Fig6-7/` files were renamed from color-based filenames to their legend identities; the SHA-256 hashes in `data/raw_sha256.csv` verify that the workbook contents were not changed. Derived capacitance arrays and the Figure 5 equivalent response are generated in memory; they are not committed as a second canonical dataset.

## Reproducibility level

This repository supports:

1. reproducing Figures 4–7 and S1–S4 from the stored released Excel exports;
2. regenerating the derived Figure 5 equivalent-capacitance curve in memory from its two Configuration 1 inputs;
3. inspecting and rerunning the documented display selections and dummy-cell reference model.

It does not reproduce instrument acquisition, electrode fabrication, or an exact historical software environment. It also does not introduce a new statistical analysis, fit, selection threshold, or uncertainty estimate.

## Scope boundaries

- The repository intentionally contains only the author-selected raw data for the 10 reliable bar measurements used in the paper, plus the dummy-control exports used for the reported controls.
- It does not include local working files, measurements outside the author-selected reliable-data set, instrument-acquisition sessions, electrode-fabrication records, internal reviews, or manuscript drafts.
- Independent bar-pair comparisons do not establish within-cell repeatability or statistical reproducibility.
- Figure 4 control exports have a different acquired maximum frequency and point count from the electrochemical comparison exports; both ranges are documented rather than homogenized.

## Citation, licensing, and archiving

Use `CITATION.cff` to cite the repository release. It records the associated paper title, authors, repository URL, and planned release version `1.0.0`; it intentionally does not include ORCID identifiers, a DOI, or a publication date that has not yet been assigned.

This repository uses dual licensing:

- Code in `scr/`, `data_visualization.ipynb`, and Python snippets in the documentation: MIT License.
- Raw data and documentation in `data/`, `README.md`, `data/README.md`, `CITATION.cff`, and `.zenodo.json`: Creative Commons Attribution 4.0 International (CC BY 4.0).

The `.zenodo.json` file prepares dataset metadata for the future Zenodo deposition. No tag, GitHub release, Zenodo deposition, or DOI has been created in this staging copy.

## AI-assisted work

Python generates the numerical data plots. Generative AI was not used to alter experimental evidence. Codex assisted with repository audit, organization, code extraction, validation, and reproducibility documentation. The manuscript records separate language and illustration assistance; authors remain responsible for the scientific content and conclusions.
