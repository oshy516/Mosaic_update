"""Regenerate the four vector figures with Python 3, pdflatex and pgfplots."""
import csv
from pathlib import Path
import shutil
from statistics import geometric_mean
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
PREAMBLE = r"""\documentclass[border=1pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{libertine,newtxmath,pgfplots}
\usetikzlibrary{patterns}
\pgfplotsset{compat=1.17,every axis/.append style={
  scale only axis,tick align=outside,major tick length=2pt,
  tick label style={font=\figfont},label style={font=\figfont},
  legend style={font=\figfont,draw=none,fill=none,inner sep=1pt},
  legend image post style={xscale=.50},ymajorgrids,grid style={black!15},axis line style={black!65},clip=false,
  scaled y ticks=false}}
\newcommand{\figfont}{\fontsize{7.5}{8.2}\selectfont}
\definecolor{ppcg}{RGB}{199,56,73}
\definecolor{compare}{RGB}{191,170,210}
\definecolor{mosaic}{RGB}{147,197,235}
\definecolor{tvm}{RGB}{248,189,211}
\definecolor{mosaicppcg}{RGB}{181,145,204}
\begin{document}\begin{tikzpicture}[font=\figfont]
"""
END = r'\end{tikzpicture}\end{document}'


def rows(name):
    with (ROOT / 'data' / (name + '.csv')).open() as f:
        return list(csv.DictReader(f))


def ticks(labels):
    positions = ','.join(str(i) for i in range(len(labels)))
    return 'xtick={' + positions + '},xticklabels={' + ','.join(labels) + '}'


def bars(values, color, shift, width, pattern=None):
    style = f'fill={color},draw=black!80,line width=.3pt'
    if pattern:
        style += f',postaction={{pattern={pattern},pattern color=black!55}}'
    coords = ' '.join(f'({i},{v})' for i, v in enumerate(values) if v != 'NA')
    return rf'\addplot[ybar,area legend,bar width={width}pt,bar shift={shift}pt,{style}] coordinates {{{coords}}};' + '\n'


def node(x, y, label, style='', dx=0):
    return rf'\node[inner sep=.7pt,{style}] at ([xshift={dx}pt]axis cs:{x},{y}) {{{label}}};' + '\n'


def reference(xmin, xmax):
    return rf'\draw[dashed,black!75,line width=.45pt] (axis cs:{xmin},1)--(axis cs:{xmax},1);' + '\n'


def mean(values, expected):
    gm = geometric_mean(float(v) for v in values if v != 'NA')
    if f'{gm:.2f}' != expected:
        raise ValueError(f'Geometric mean {gm} does not round to {expected}')
    return expected


def h800():
    data = rows('h800_speedup')
    labels = [r['kernel'] for r in data] + ['Geomean']
    series = [[r[key] for r in data] for key in ('speedup_vs_ppcg','speedup_vs_eatss')]
    assert len(data) == 25 and sum(v != 'NA' for v in series[1]) == 22
    for values, expected in zip(series, ('1.25', '1.30')):
        values.append(mean(values, expected))
    plot = r"""\begin{axis}[width=360pt,height=77pt,xmin=-.60,xmax=25.75,ymin=0,ymax=3,
      ylabel={Speedup of Mosaic ($\times$)},ytick={0,1,2,3},
      xticklabel style={rotate=45,anchor=north east,inner sep=1pt},
      legend columns=2,legend style={at={(.64,.95)},anchor=north}, """ + ticks(labels) + ']\n'
    plot += bars(series[0], 'ppcg', -2.9, 5.4, 'north east lines')
    plot += bars(series[1], 'compare', 2.9, 5.4, 'horizontal lines')
    plot += r'\legend{vs PPCG,vs EATSS}' + '\n' + reference(-.6,25.75)
    for i,v in enumerate(series[1]):
        if v == 'NA':
            plot += node(i, .035, 'n/a', 'rotate=90,anchor=west', 2.9)
    plot += node(25, 1.25, '1.25', 'rotate=90,anchor=west', -2.9)
    plot += node(25, 1.79, '1.30', 'rotate=90,anchor=west', 3.3)
    return plot + r'\end{axis}'


def tilemind():
    data = rows('tilemind_comparison')
    plot = ''
    for op, offset, title, gm in [('GEMM', 0, '(a) GEMM', '1.26'), ('Conv2D', 183, '(b) Conv2D', '2.44')]:
        group = [r for r in data if r['op'] == op]
        assert len(group) == 5
        mean([r['speedup'] for r in group], gm)
        labels = []
        for r in group:
            dims = r['shape'].split('x')
            if op == 'Conv2D':
                # D2 stores N,K,P,Q,C,R,S,H,W. Display the README's N,K,C,P,Q,R,S,H,W.
                n,k,p,q,c,fr,fs,h,w = dims
                top = r'{\times}'.join([n,k,c,p,q])
                bottom = r'{\times}'.join([fr,fs,h,w])
                labels.append(r'{\shortstack[r]{$' + top + r'$\\$' + r'{}\times ' + bottom + '$}}')
            else:
                labels.append('{$' + r'{\times}'.join(dims) + '$}')
        ylabel = r'ylabel={Speedup of Mosaic ($\times$)},' if op == 'GEMM' else ''
        width = 157 if op == 'GEMM' else 179
        plot += rf'\begin{{axis}}[at={{({offset}pt,0)}},anchor=south west,width={width}pt,height=56pt,' + ylabel + r"""
          xmin=-.5,xmax=4.5,ymin=.8,ymax=16,ymode=log,log origin y=infty,
          ytick={1,2,4,8,16},yticklabels={1,2,4,8,16},
          xticklabel style={rotate=30,anchor=north east,inner sep=1pt},
          title style={font=\figfont},title={""" + title + '},' + ticks(labels) + ']\n'
        plot += bars([r['speedup'] for r in group], 'mosaic', 0, 14)
        plot += reference(-.5,4.5)
        for i,r in enumerate(group):
            v = float(r['speedup'])
            plot += node(i, v, f'{v:.2f}'+r'$\times$', 'anchor=south')
        plot += r'\end{axis}' + '\n'
    return plot


def original_bars(network):
    data = rows('network_bars' if network else 'operator_bars')
    if network:
        series = [('ppcg','ppcg',-16.5),('mosaic_ppcg','mosaicppcg',-5.5),
                  ('tvm','tvm',5.5),('mosaic_tvm','mosaic',16.5)]
        legend = 'PPCG,Mosaic/PPCG,TVM,Mosaic/TVM'
    else:
        series = [('ppcg','ppcg',-6),('mosaic','mosaic',6)]
        legend = 'PPCG,Mosaic'
    labels = [r['network' if network else 'operator'] for r in data]
    n = len(labels)
    height = '48pt' if network else '57pt'
    plot = r'\begin{axis}[width=161pt,height=' + height + r""",ymode=log,log origin y=infty,
      ymin=.68,ymax=12,ylabel={Execution speedup},
      legend columns=4,legend style={at={(.5,1.03)},anchor=south},
      ytick={1,2,4,8},yticklabels={1,2,4,8},xmin=-.5,xmax=""" + str(n-.5) + ',' + ticks(labels) + ']\n'
    for field,color,dx in series:
        plot += bars([r[field] for r in data],color,dx,8.5)
    plot += r'\legend{' + legend + '}\n' + reference(-.5,n-.5)
    for i,r in enumerate(data):
        for field,_,dx in series:
            v = r[field]
            baseline = field in ('ppcg','tvm')
            label = (r[field+'_ms'] + r'\,ms') if baseline else (v+r'$\times$')
            anchor = 'east' if float(v)>3 else 'west'
            plot += node(i,v,label,'rotate=90,anchor='+anchor,dx)
    return plot + r'\end{axis}'


def main():
    figures = ROOT / 'figures'
    figures.mkdir(exist_ok=True)
    plots = {'h800':h800(), 'tilemind':tilemind(), 'operator_bars':original_bars(False),
             'network_bars':original_bars(True)}
    with TemporaryDirectory() as work:
        for name, plot in plots.items():
            tex = Path(work) / (name + '.tex')
            tex.write_text(PREAMBLE + plot + END)
            result = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',tex.name],
                                    cwd=work, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stdout[-4000:])
            shutil.copy2(tex.with_suffix('.pdf'), figures / (name + '.pdf'))


if __name__ == '__main__':
    main()
