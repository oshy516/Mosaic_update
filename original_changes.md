# 第四轮原文一致性审查

基线为原投稿的 23 页 PDF 和它的 LaTeX 源。对照为本轮 25 页标记版。源稿检查展开主文件实际输入的八个章节再运行 latexdiff。表格、算法、图和文献按各自的标签核对，排版与文本分别检查。[完整源码差异](audit/original_to_round4.tex)

## 去掉修订色后的正文差异

| 原稿位置 | 原稿中不再出现的文字 | 第四轮处理 |
| --- | --- | --- |
| §6 精度段，修订稿第 14 页 | “Because the cost model reasons about tile footprints, register working sets, and traffic in bytes rather than in elements, the” | 原稿把寄存器也按字节描述。按登记的精度替换着绿，保留后续 “element width enters only …”。 |
| §6 寄存器验证，修订稿第 15 页 | “representative” | 该词存在于原稿。第四轮 §1.4 明确禁用，§1.1 的原文保留清单却没有列出这次删除。本轮按明确禁词删除该词。这是清单之外唯一的正文删除。 |
| §7 分析式优化，修订稿第 21 页 | “; TileMind targets CPU cache residency rather than GPU execution-space selection” | 按已登记的 TileMind 概括替换删除；新 TileMind 段为紫色。原句中 EATSS 的判断、前段关于 TileMind 的 MILP 从句均保留。 |

原 §6.4 的 “over TVM MetaSchedule … , it achieves” 已恢复为原色。绿色仅插入 “’s tuned parameters on the same schedules”。摘要、结论和 §6.3 MetaSchedule 原句的新增限定也只标插入部分。剔除颜色后，正文按词顺序比对只剩上表三处。[规范化正文逐词差异](audit/round4_pdf_body_diff.tsv)

## 完整 PDF 差异分类

从两份 PDF 提取带位置、字体颜色的文本。按坐标剔除页眉、页脚、边栏行号，保留 ACM 链接色，剔除修订稿的四种标记色。对合字、换行、断词和空白做规范化。按编译后位置单独读取表和图，避免浮动体换页造成整段假差异。第一遍保留所有编号和黑色标点，第二遍对正文还原文献、图号和页数的对应关系，并合并字体边界引起的词间差别。[全部 48 个逐词差异块](audit/round4_pdf_diff.tsv) · [提取与比对脚本](scripts/compare_round4_pdfs.py)

| 第一遍差异块序号（不计表头） | 核对结果 |
| --- | --- |
| 1 | ACM 自引中的总页数 23 → 25。 |
| 2–4、15、17–18 | 原 AKG、Ansor 编号顺延；去掉新增紫色编号后会留下黑色逗号。 |
| 5 | 原 PDF 在字体交界把 “cost” 和数学符号 T_block 抽取为相连字符串；两版同一公式、同一原文。 |
| 6、7、16 | 上表所列三处正文删除或替换。 |
| 8–14 | 正文引用的旧 Fig. 4–7 随 Fig. 4 的插入顺延。 |
| 19 | 新 Fig. 4 的图形文字。图注及其标签为修订色。 |
| 20 | 对应的原 Fig. 4 现为 Fig. 5；图注文字及 0.973× 数值保留，只移动标注。 |
| 21–32 | Fig. 6 图内坐标、图例和标签的抽取次序及自动图号；图注原文保留。 |
| 33–38 | Fig. 7 对数轴整数次幂刻度及图号。六个面板的 24 条曲线坐标完全相同。 |
| 39–41 | Fig. 8 图内刻度、条形序列、图例、标签次序及图号。图注原文保留。 |
| 42–45 | Fig. 9 三个原先手工放置的数值改为按系列顺序随柱标注；15 个柱高逐项相同，图注原文保留。 |
| 46–48 | 三篇新增文献、原 AKG／Ansor 编号移动，以及词序匹配在相同数字 “45 pages” 中的切分。 |

Table 3、4、5 的未着色 PDF 文本逐词一致。Table 4、5 的 LaTeX 表体与图注逐字节一致。Table 6、Algorithm 1 的标题、自动标签和内容均已用相应修订色标记。[静态检查记录](audit/checks.txt)
