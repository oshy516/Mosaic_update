# Mosaic · TACO R1

[Open the marked manuscript (PDF, 27 pages)](mosaic_r1_marked.pdf)

The manuscript compares analytical choices of GPU tile sizes and thread-block dimensions. The table links each new or redrawn figure to the exact data used in the revision. [Read the supplementary experiment results](supplementary_results.md) for measured regret, register feasibility, shared-memory staging, network solve times, and the H800 platform.

| Manuscript figure | Figure | Data |
|---|---|---|
| Fig. 4 · H800 PolyBench speedups | [Grouped bar chart](figures/h800.pdf) | [25 kernels, timings and speedups](data/h800_speedup.csv) |
| Fig. 5 · Mosaic and TileMind on RTX 4090 | [GEMM and Conv2D](figures/tilemind.pdf) | [10 shapes, timings and speedups](data/tilemind_comparison.csv) |
| Fig. 7 · Deep learning operators | [Log-scale bar chart](figures/operator_bars.pdf) | [5 operators, speedups and baseline times](data/operator_bars.csv) |
| Fig. 9 · End-to-end workloads | [Log-scale bar chart](figures/network_bars.pdf) | [3 networks, speedups and baseline times](data/network_bars.csv) |

In Fig. 4, each ratio is baseline time divided by Mosaic time. EATSS has no executable for three kernels, marked `NA` in the CSV. The geometric means use the 25 available PPCG ratios and the 22 available EATSS ratios. In Fig. 5, the five displayed shapes for each operator had the largest speedups in that size sweep. Conv2D shapes in the CSV use N×K×P×Q×C×R×S×H×W. The plot labels reorder the same dimensions to N×K×C×P×Q×R×S×H×W.

## Regenerate the figures

From the repository root, run:

```sh
python3 scripts/plot_figures.py
```

The script checks the geometric means, reads the four CSVs, and writes the four PDFs to `figures/`. It uses Python 3 and pdfLaTeX with the standalone, Libertine, newtxmath, and pgfplots packages. Regenerating the charts requires no GPU.
