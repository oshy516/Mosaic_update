# 第四轮修订报告

标记版和无标记版均为 **25 页，含 48 条参考文献**。两版按页提取的文字完全相同；完成交叉引用和 BibTeX 重编后，无未定义引用。审查发现一处指令冲突：原稿自带禁词 “representative”。本轮按禁词要求删去该词，并把它单独列为第三处原文删除。[逐项定位](revision_map.md) · [逐词差异](original_changes.md)

## E3　寄存器筛选及比较口径

按每个实验自己的计时记录纳入该实验中 Mosaic 的可行选择。耗时单位为 ms。ATAX、Jacobi-2D 使用 §6.2 的有界 PPCG sweep；GEMM 使用 Fig. 1 的二维 tile/block 配置实验。

| 程序 | 成功配置 | C4 违例 | 最快可行（含 Mosaic） | 最快违例 | 比最快可行更快的违例 |
| --- | ---: | ---: | ---: | ---: | ---: |
| GEMM | 2,232 | 941 | 25.934214 | 25.728223 | 2 |
| ATAX | 784 | 0 | 0.1920 | — | 0 |
| Jacobi-2D | 739 | 493 | 266.16 | 291.165408670 | 0 |

- **GEMM。** 用逐配置 CSV 重算，1,291 个通过。两项更快的违例分别是 25.728223 和 25.868135。最快可行配置耗时与最快实测配置耗时之比减一为 0.800642%，保留两位为 **0.80%**。同一 Fig. 1 实验口径的 Mosaic 选择耗时 29.438389（归档重测记录的三个运行中位数），纳入比较后最小可行耗时仍为 25.934214。Table 4 的独立 GEMM 绝对时间不与 Fig. 1 混用。[逐配置 CSV](data/gemm_c4.csv) · [GEMM 分类代码](scripts/classify_gemm_c4.py)
- **ATAX 和 Jacobi-2D。** 从 PolyBench-NN 的「sweep/benchmark_results.csv」按 benchmark、variant_id 取最后一次记录，再只保留成功项。这与该实验生成汇总表的规则相同。ATAX 是 784/784；Jacobi-2D 是 739/784。逐项从生成的 CUDA 读取线程块维度与共享内存声明，再以 RTX 4090 验证 profile 核对两个 kernel 的 C4。仅在 sweep 中取最优时，两者最快可行值分别为 0.526335991、266.701181069；分别加入 Table 4 的 Mosaic 实测选择 0.1920、266.16 后得到上表。Jacobi-2D 最快违例为 v000655；100 × (291.165408670 / 266.16 − 1) = **9.394879%**，与回复信的一位小数 9.4% 一致。[有界 sweep 核对代码](scripts/check_bounded_c4.py)
- E3 的“五项选择、14 项溢出”沿用已有的 FP64 编译验证。以上是对已有测量的静态重算，本轮没有重新在 GPU 上计时。

## E4　H800 分组几何平均

对 Fig. 4 CSV 中的每个原始 speedup_vs_ppcg 取自然对数，按组求算术均值后取指数。7 个 staging 不一致程序为 bicg、doitgen、gramschmidt、mvt、symm、trisolv、trmm。结果如下。[Fig. 4 数据](data/h800_speedup.csv)

| 程序集合 | 个数 | 几何均值 | 正文显示 |
| --- | ---: | ---: | ---: |
| staging 不一致 | 7 | 1.202093885 | 1.20× |
| staging 一致 | 18 | 1.275389688 | **1.28×** |
| 全部程序 | 25 | 1.254427706 | 1.25× |

E5 相对于 EATSS 的比值使用 22 个有测量值的程序，几何平均为 1.303731，正文为 1.30×。doitgen、heat-3d、jacobi-1d 保持缺测。

## 表、图和引文

- **Table 6。** 与 Table 5 同用 scriptsize。D2 的 Conv2D 原始字段依次为 N,K,P,Q,C,R,S,H,W；按字段名转换为输入 N,C,H,W 与输出 N,K,P,Q，逐行验证 H−R+1=P、W−S+1=Q。GEMM 以 2MNK、Conv2D 以 2NKPQCRS 排序；末两项卷积的 FLOPs 相同，保留指定次序。以未舍入的 ms 计算 TileMind/Mosaic，比值几何平均分别为 1.26×、2.44×。[十个形状的原始计时](data/tilemind_comparison.csv)
- **K3。** 原稿 LaTeX 与原 PDF 的 Table 3 都包含 “All experiments use CUDA’s default 48 KiB per-block shared-memory limit without opt-in.”。本轮逐字保留。
- **F1–F3。** 逐图检查了最终 PDF 的 Fig. 4–9。Fig. 4 保留原图；Fig. 5 移动 0.973×；Fig. 6、8 将高柱数值移到柱外。Fig. 7 保持整图边界，给六组双轴之间留出标签空间，并显式显示整数次幂。Fig. 9 保持图的宽高，调整标注空间，每个图例一个色块，数值与 Fig. 6、8 同用 7.5 pt 标注字号。外部三个图形 PDF 的页面尺寸与上轮相同。原图注保留。
- **B1–B3。** MICRO 2020 的题名和 DOI 已存在于未引用键 polytef，更新为指定键 zhao2020micro；书目中每篇只保留一条。按最终编译，TileMind **[42]**、Yuki et al. 2010 **[43]**、Zhai OSDI 2024 **[44]**、Zhao & Di MICRO 2020 **[45]**、AKG **[46]**（原 [44]）、Zhao et al. TOCS 2024 **[47]**、Ansor **[48]**（原 [45]）。原有 [1]–[43] 编号保持。按键对比 BibTeX 生成的书目，45 个旧条目的排印内容逐字节一致。三个引文组原有编号与括号为黑色，只将新编号标紫；B2 新增的整组 [47] 为紫色。

## 原文和 PDF 核查

提取两版 PDF 的图表、正文和引用并逐词核对。规范化后的正文差异仅有三处：§6 精度旧从句、§6 的禁词 “representative”、§7 的原 TileMind 概括。第一、三处在原清单，第二处来自本轮明确禁词要求。全部 48 个原始差异块的归类、图号及文献编号变化均已登记。最终编译仅保留原 PPCG 命令行示例约 4.44 pt 的横向溢出提示。[原文改动清单](original_changes.md) · [完整源码差异](audit/original_to_round4.tex) · [检查记录](audit/checks.txt)
