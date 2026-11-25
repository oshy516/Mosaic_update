# 第四轮修订对照

页码取自本轮标记版 PDF。无标记版的分页和文字相同。表中英文可用于 PDF 搜索。

| 条目 | 位置 | 段首或定位词 |
| --- | --- | --- |
| A1、A2 | 第 1 页，摘要 | “Across 25 PolyBench kernels” 段；EATSS 前为紫色，TVM MetaSchedule 前为绿色。 |
| B1 | 第 1 页，§1 | “GPUs are the dominant execution platform”；polyhedral frameworks 引文中的 [45]、[47] 为新增编号。 |
| Table 2 | 第 7 页，Model notation | “Resident blocks per SM” 行分别给出 “32-bit slots” 和 “live values per thread”。 |
| S1、C4 依据 | 第 10 页，§5.2，Eq. (8) 后 | “When smem … = 0” 段；依次搜索 “counts 32-bit slots” 和 “C4 is evaluated at the pre-register residency”。 |
| K1、Algorithm 1 | 第 13 页，§5.4 | “Two-stage analytical selection in Mosaic”；标题、Require、Ensure、行号 1–7 和注释均为红色。 |
| K3、Table 3 | 第 14 页，§6 实验设置 | “Experimental platforms.”；H800 列为蓝色，原表注保留。 |
| §6 精度 | 第 14 页 | “All PolyBench/C 4.2.1 measurements”；搜索 “Shared-memory footprints and traffic are measured in bytes”。 |
| E1、E2 | 第 15 页，§6 | “We compare against PPCG’s heuristic” 段给出 EATSS 的 r_d = 1；“The selected tile and thread-block components” 段给出 TVM 的 TIR 参数传递。 |
| E3、E4 | 第 15 页，§6 | “Register and occupancy validation.” 和 “Modeled placement versus backend staging.” |
| E5、Fig. 4 | 第 16 页 §6.1，第 17 页图顶 | “On the H800 (Fig. 4)”；图注为 “Mosaic speedup over PPCG and EATSS on the H800.” |
| E6、Fig. 5 | 第 17–18 页，§6.2；Fig. 5 在第 17 页 | “Extending the analysis to covariance”；Jacobi-2D 解释续至第 18 页。Fig. 5 的 0.973× 标注置于末组柱上方。 |
| Table 5、Fig. 6 | 第 18–19 页，§6.3；Table 5、Fig. 6 在第 18 页 | “For a direct comparison with optimized reference libraries” 及 “On the RTX 4090, Tensor Cores accelerate TF32”；图注 “Performance of deep learning operators.” |
| E7、K2、E8 | 第 19 页，§6.3 | “Table 6. Mosaic and TileMind execution time” 与 “Comparison with TileMind.”；表注、表头、10 个形状及两行几何平均均为紫色。 |
| E9、Fig. 7 | 第 19 页 §6.3；图在第 20 页 | “To compare Mosaic against search-based autotuning”；搜索 “Fig. 7 reports MetaSchedule’s full tuning time” 和 “with the same trial budgets”。 |
| §6.4、Fig. 8 | 第 20 页 | “We compose the operators into three end-to-end workloads” 段给出组织方式及 “MetaSchedule’s tuned parameters on the same schedules”；图注 “Performance of end-to-end workloads.” |
| Fig. 9 | 第 21 页，§6.5 的消融图 | “Ablation of Mosaic’s individual components.”；单色块图例、柱顶数值。 |
| E10、§6.6 | 第 21 页 | “Finally, we examine the cost” 段含 “For the PolyBench kernels in Table 4”；下一段以 “For a network” 开始。 |
| B2、TileMind | 第 21 页，§7 | “Existing approaches on optimizing loop nests” 段追加 [45] 和句末 [47]；TileMind 段首为 “TileMind [42] likewise decouples”。 |
| B3 | 第 22 页，§7 | “Search-based optimization.” 段；“recursive search” 引文组末新增 [44]。 |
| A3、SIMT 范围 | 第 22 页，§8 | “We presented Mosaic” 段含 “than with the parameters tuned by”；“Mosaic operates after transformation scheduling” 段含 conventional CUDA-core SIMT 范围。 |

[带标记 PDF](mosaic_r1_marked.pdf) · [无标记 PDF](mosaic_r1_clean.pdf) · [数据与审查报告](round4_report.md)
