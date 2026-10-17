# Manuscript figures

Figures are generated from the tracked, hash-linked aggregate evidence snapshot
in `paper/data/development_figure_data.json` by:

```bash
python scripts/generate_paper_figures.py
```

- `fig1-assurance-architecture` is a system-model diagram.
- `fig2-development-results` reads the iteration 21, 22, 23, 25, 26, and 27
  aggregates.
- `fig3-minimal-cutsets` reads iteration 26 and asserts the reported minimal
  prevention and silent-compromise cut sets before rendering.

When the full local reports exist under `_workloads/reproduction/`, the
generator verifies each report against its recorded SHA-256 digest before
rendering. A clean public clone does not require those ignored multi-gigabyte
workspaces to reproduce the published figures.

SVG is used by the Markdown manuscript. PDF is suitable for LaTeX/venue
conversion, and PNG is retained for visual inspection. The figures summarize
heterogeneous deterministic development matrices and must not be interpreted
as pooled effectiveness estimates.
