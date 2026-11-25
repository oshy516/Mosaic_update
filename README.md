# Mosaic · TACO R1

[Marked manuscript](mosaic_r1_marked.pdf) · [Clean manuscript](mosaic_r1_clean.pdf) · [Round-four report](round4_report.md) · [Page map](revision_map.md)

Both manuscript PDFs contain 25 pages including references.

The manuscript compares analytical choices of GPU tile sizes and thread-block dimensions. The table links each new or redrawn figure to the exact data used in the revision. [Read the supplementary experiment results](supplementary_results.md) for measured regret, register feasibility, shared-memory staging, network solve times, and the H800 platform.

| Manuscript figure | Figure | Data |
|---|---|---|
| Fig. 4 · H800 PolyBench speedups | [Grouped bar chart](figures/h800.pdf) | [25 kernels, timings and speedups](data/h800_speedup.csv) |
| Table 6 · Mosaic and TileMind on RTX 4090 | [GEMM and Conv2D, p. 19](mosaic_r1_marked.pdf#page=19) | [10 shapes, timings and speedups](data/tilemind_comparison.csv) |
| Fig. 6 · Deep learning operators | [Log-scale bar chart](figures/operator_bars.pdf) | [5 operators, speedups and baseline times](data/operator_bars.csv) |
| Fig. 7 · MetaSchedule | [Six dual-axis plots, p. 20](mosaic_r1_marked.pdf#page=20) | [Measured coordinates in the figure source](manuscript/sec.eval.tex) |
| Fig. 8 · End-to-end workloads | [Log-scale bar chart](figures/network_bars.pdf) | [3 networks, speedups and baseline times](data/network_bars.csv) |
| Fig. 9 · Ablation | [Grouped bars, p. 21](mosaic_r1_marked.pdf#page=21) | [Measured coordinates in the figure source](manuscript/sec.eval.tex) |

In Fig. 4, each ratio is baseline time divided by Mosaic time. EATSS has no executable for three kernels, marked `NA` in the CSV. The geometric means use the 25 available PPCG ratios and the 22 available EATSS ratios. Conv2D shapes in the CSV use N×K×P×Q×C×R×S×H×W. Table 6 shows the input N×C×H×W and output N×K×P×Q, sorted by FLOPs within each kernel group.

## Regenerate the figures

From the repository root, run:

```sh
python3 scripts/plot_figures.py
```

The script checks the geometric means, reads the three chart CSVs, and writes the three PDFs to `figures/`. It uses Python 3 and pdfLaTeX with the standalone, Libertine, newtxmath, and pgfplots packages. Regenerating the charts requires no GPU.


## Build the manuscript

From the manuscript directory, run `latexmk -pdf mosaic.tex` for the marked copy or `latexmk -pdf main_clean.tex` for the clean copy. The bibliography, document class and figure inputs are included.

The [GEMM C4 classification](data/gemm_c4.csv) contains all 2,232 successful configurations. The [classification script](scripts/classify_gemm_c4.py) takes the sweep timing CSV, the PPCG source directory keyed by configuration hash, the register-validation hardware profile, and the destination CSV.
