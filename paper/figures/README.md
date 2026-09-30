# Manuscript figures

Figures are generated from immutable development reports by:

```bash
python scripts/generate_paper_figures.py
```

- `fig1-assurance-architecture` is a system-model diagram.
- `fig2-development-results` reads the iteration 21, 22, 23, 25, 26, and 27
  terminal reports under `_workloads/reproduction/`.
- `fig3-minimal-cutsets` reads iteration 26 and asserts the reported minimal
  prevention and silent-compromise cut sets before rendering.

SVG is used by the Markdown manuscript. PDF is suitable for LaTeX/venue
conversion, and PNG is retained for visual inspection. The figures summarize
heterogeneous deterministic development matrices and must not be interpreted
as pooled effectiveness estimates.
