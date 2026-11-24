# Supplementary experiment results

The following tables contain the reported aggregates for the marked revision. Timings and speedups used for the four plots are available as [CSV files](data).

## Measured regret on the RTX 4090 (§6.2)

Regret is the selected configuration's time divided by the best measured time, minus one. The aggregate is the geometric mean of the time ratios, minus one. The additional measurements are reported as percentages because they were collected in a separate measurement environment.

| Kernel | Measured regret | Set |
|---|---:|---|
| trisolv | 0.34% | Original |
| syrk | 20.59% | Original |
| gemm | 8.10% | Original |
| atax | ≈0% | Original |
| fdtd-2d | 0.08% | Original |
| covariance | 2.52% | Additional |
| mvt | 2.91% | Additional |
| trmm | 7.74% | Additional |
| jacobi-2d | 13.34% | Additional |

The geometric mean is 5.53% for the original five and 5.98% for all nine. Seven of the nine regrets are below 10%. For syrk, the two configurations had achieved occupancies of 47.0% and 44.3%, and both used less than 1% of peak DRAM throughput. The measured optimum incurred about one-sixteenth as many shared-memory read bank conflicts as Mosaic's selection. Tex Throttle stalls were 25.99 and 35.82 cycles per instruction, respectively.

## Register feasibility (§§5.2 and 6.1)

| Program | Measured configurations classified | Violated C4 | Faster violators | Comparison |
|---|---:|---:|---:|---|
| GEMM | 2,224 | 938 | 2 | Two beat the fastest C4-feasible configuration. The latter was within 0.62% of the measured optimum. |
| Jacobi-2D | 739 | 493 | 0 | The fastest violator was 9.4% slower than Mosaic's selection. |
| ATAX | 784 | 0 | 0 | All satisfied C4. |

The classification covers 3,747 configurations. Section 2.1 reports 2,232 successful launches for the Fig. 1 GEMM sweep. The classification count reported in §6.1 is 2,224.

In the separate compilation check, 14 of 11,240 C4-feasible candidates spilled registers (0.1246%). Counting each FP64 data value as two 32-bit slots retained all five selected kernels and excluded all 14 spilling candidates. For the selected GEMM kernel, the live-value estimate was 21, the slot-based estimate was 38, PTXAS allocated 40 slots per thread, and the budget was 42.

## Shared-memory staging on H800 (§6.1)

| Program-level comparison | Programs |
|---|---|
| Agreement (18) | 2mm, 3mm, adi, atax, cholesky, correlation, covariance, fdtd-2d, gemm, gemver, gesummv, heat-3d, jacobi-1d, jacobi-2d, lu, seidel-2d, syr2k, syrk |
| Disagreement (7) | bicg, doitgen, gramschmidt, mvt, symm, trisolv, trmm |

Auxiliary kernels left to PPCG defaults were counted as consistent, as were written arrays that PPCG staged in accordance with Mosaic's fixed rule. All observed discrepancies had the same direction: Mosaic counted an array in shared memory while PPCG accessed it directly from global memory. The geometric-mean speedup over PPCG among those seven programs was 1.20×. The separate ablation in Fig. 10 reports 1.32× with the register filter and 1.79× with placement-scenario enumeration added.

## Network solve times (§6.6)

| Network | Operator invocations per forward pass | Distinct operators solved | Total solve time |
|---|---:|---|---:|
| AlexNet | Unreported | 8 (5 convolution, 3 fully connected) | 26.6 s |
| Seq2Seq | 7,203 | 3 (embedding, LSTM, dense) | 0.59 s |
| BertTiny | 39 | 7 | 2.73 s |

Solve times are one-time compilation costs. [Fig. 9 data](data/network_bars.csv) gives the baseline execution times and the speedups for the corresponding networks.

## H800 platform (Table 3)

| Property | Value |
|---|---|
| GPU | NVIDIA H800 / Hopper, compute capability 9.0 |
| SMs | 132 |
| L2 cache | 50 MiB |
| Shared memory | 228 KiB per SM, 48 KiB per block by default, 227 KiB per block with opt-in |
| Registers per SM | 65,536 32-bit slots |
| Device memory | 80 GB nominal |
| CUDA / NVCC | 12.8 / 12.8.93 |
| OS and L1 cache | Unreported in the supplied platform records |

[Measured H800 FP64 profile](data/platform/h800_fp64_run03.json) · [CUDA toolchain component manifest](data/platform/toolchain_manifest.json)
