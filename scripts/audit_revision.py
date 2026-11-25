"""Read-only checks for the English R1 sources, PDFs and data. Run after latexmk."""
import csv
import hashlib
import os
import re
from collections import Counter
from pathlib import Path
from statistics import geometric_mean
import subprocess
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'manuscript'
ORIGINAL = Path(os.environ.get('MOSAIC_ORIGINAL', ROOT.parent / 'mosaic'))
HAN = re.compile(r'[\u4e00-\u9fff]')
PALETTE = {'#7030a0', '#0070c0', '#c00000', '#00b050'}


def check(ok, message):
    if not ok:
        raise ValueError(message)
    print('PASS', message)


def section(directory, file, env, contains=''):
    tex = (directory / file).read_bytes()
    pattern = rb'\\begin\{' + env.encode() + rb'\}.*?\\end\{' + env.encode() + rb'\}'
    choices = [m for m in re.findall(pattern, tex, re.S) if contains.encode() in m]
    if len(choices) != 1:
        raise ValueError((file, env, contains, len(choices)))
    return choices[0]


def records(name):
    with (ROOT / 'data' / (name + '.csv')).open() as f:
        return list(csv.DictReader(f))


def test_data():
    prompt_path = ROOT / 'codex_manuscript_revision_prompt.md'
    prompt = prompt_path.read_text() if prompt_path.is_file() else None
    for name,key in [('h800_speedup','D1'),('tilemind_comparison','D2')]:
        if prompt is None:
            continue
        supplied = re.search('### '+key+r'\s.*?\n\x60{3}csv\n(.*?)\n\x60{3}', prompt, re.S)[1]
        check((ROOT/'data'/(name+'.csv')).read_text() == supplied.replace(r'\_','_')+'\n',
              f'{key} CSV matches the supplied block')
    h = records('h800_speedup')
    missing = {r['kernel'] for r in h if r['speedup_vs_eatss']=='NA'}
    check(len(h)==25 and missing=={'doitgen','heat-3d','jacobi-1d'},'H800 sample and missing bars')
    mismatch = {'bicg','doitgen','gramschmidt','mvt','symm','trisolv','trmm'}
    def gm(rows, col):
        return geometric_mean(float(r[col]) for r in rows if r[col]!='NA')
    t = records('tilemind_comparison')
    values = [gm(h,'speedup_vs_ppcg'),gm(h,'speedup_vs_eatss'),
              gm([r for r in h if r['kernel'] in mismatch],'speedup_vs_ppcg')]
    for op in ['GEMM','Conv2D']:
        group = [r for r in t if r['op']==op]
        check(len(group)==5 and all(abs(float(r['tilemind_ms'])/float(r['mosaic_ms'])-
                                        float(r['speedup'])) <= 0.5e-6 for r in group),
              op+' ratios agree with supplied times to six decimals')
        values.append(gm(group,'speedup'))
    check([round(v,2) for v in values]==[1.25,1.30,1.20,1.26,2.44],
          'D1/D2/D6 geometric means '+', '.join(f'{v:.6f}' for v in values))
    regrets = [.34,20.59,8.10,0,.08,2.52,2.91,7.74,13.34]
    def regret(xs):
        return 100*(geometric_mean(1+x/100 for x in xs)-1)
    check(round(regret(regrets[:5]),2)==5.53 and round(regret(regrets),2)==5.98
          and sum(v<10 for v in regrets)==7,'D3 regret aggregates')
    cases = records('gemm_c4')
    times = [float(r['median_ms']) for r in cases]
    feasible = min(t for t,r in zip(times,cases) if r['violates']=='0')
    rejected = [t for t,r in zip(times,cases) if r['violates']=='1']
    check(len(cases)==2232 and len(rejected)==941 and sum(t<feasible for t in rejected)==2
          and round(100*(feasible/min(times)-1),2)==0.80, 'full GEMM C4 classification')
    other = [r for r in h if r['kernel'] not in mismatch]
    check(len(other)==18 and round(gm(other,'speedup_vs_ppcg'),2)==1.28, 'H800 staging agreement, 18 kernels: 1.28x')
    tex = (ORIGINAL/'sec.eval.tex').read_text()
    for name,label,series in [
        ('operator_bars','fig:network-operators',['ppcg','mosaic']),
        ('network_bars','fig:e2e-fourbar',['ppcg','mosaic_ppcg','tvm','mosaic_tvm'])]:
        figure = tex.split(r'\label{'+label+'}')[0].rsplit(r'\begin{wrapfigure}',1)[1]
        lower = figure.split(r'\nextgroupplot')[-1]
        plots = re.findall(r'coordinates\s*\{(.*?)\};', lower, re.S)
        data = records(name)
        check(len(plots)==len(series),name+' source series count')
        for col,plot in zip(series,plots):
            entries = re.findall(r'\(([\w.]+),([\d.]+)\)\[([^]]*)\]',plot)
            check([r[col] for r in data]==[e[1] for e in entries],name+' '+col+' exact bar values')
            if col in ('ppcg','tvm'):
                labels = [re.search(r'[\d.]+',e[2])[0] for e in entries]
                check(labels==[r[col+'_ms'] for r in data],name+' '+col+' millisecond labels')
        check((ROOT/'figures'/(name+'.pdf')).read_bytes()==
              (SOURCE/'figures'/(name+'.pdf')).read_bytes(),name+' embedded asset')


def test_sources():
    for file,env,label in [('mosaic.tex','abstract',''),('sec.intro.tex','itemize',''),
                           ('sec.eval.tex','table',r'\label{tab:benchmark}'),
                           ('sec.eval.tex','table',r'\label{tab:vendor-comparison}')]:
        before = section(ORIGINAL,file,env,label)
        after = section(SOURCE,file,env,label)
        if env == 'abstract':
            for addition in (rb'\revO{the energy-aware }', rb'\revRthree{the parameters tuned by }'):
                check(after.count(addition)==1, 'requested abstract insertion '+addition.decode())
                after=after.replace(addition,b'')
        check(before==after,f'{file} {label or env} original text verified, SHA256 '+hashlib.sha256(after).hexdigest())
    check(not any(HAN.search(f.read_text(errors='replace')) for f in SOURCE.rglob('*')
                  if f.is_file() and f.suffix in {'.tex','.bib'}),
          'no Han characters in manuscript text files')
    def adapters(folder):
        return sum(len(re.findall(r'adapter',f.read_text(),re.I)) for f in folder.glob('*.tex'))
    check(adapters(SOURCE)<=adapters(ORIGINAL),f'adapter occurrences {adapters(ORIGINAL)} -> {adapters(SOURCE)}')
    s=(SOURCE/'sec.eval.tex').read_text().replace(r'\times','×').replace(r'\%','%').replace('~',' ')
    check(all(v in s for v in ('0.80%','5.98%','14 spilling','1.28','with the same trial budgets')),
          'round-four evaluation anchors')
    check(all(v not in s for v in ('2,224','3,747','largest speedups','fig:tilemind','[TBD]')),
          'superseded evaluation text removed')
    check(not any(word.lower() in s.lower() for word in ('representative','Tex Throttle','latency-only')), 'excluded evaluation wording')
    check('the TIR printed from the schedule selected by MetaSchedule' in s,
          'TVM parameter-transfer wording')


def test_pdfs():
    extracts=[]
    with TemporaryDirectory() as tmp:
        for mode in ['marked','clean']:
            pdf=ROOT/f'mosaic_r1_{mode}.pdf'
            text=subprocess.check_output(['pdftotext','-layout',pdf,'-'])
            extracts.append(text)
            check(b'??' not in text and not HAN.search(text.decode()),mode+' PDF text / references')
            logname=('mosaic' if mode=='marked' else 'main_clean')+'.log'
            logpath=SOURCE/logname
            if not logpath.is_file():
                logpath=ROOT/'audit'/'build'/logname
            check(not re.search(r'undefined references|(?:Reference|Citation).*?undefined|multiply defined|^!',
                                logpath.read_text(errors='replace'),re.I|re.M),mode+' final compilation log')
            xml=Path(tmp)/(mode+'.xml')
            subprocess.run(['pdftohtml','-q','-i','-xml','-hidden',pdf,xml],check=True)
            tree=ET.parse(xml)
            colors={f.get('id'):f.get('color') for f in tree.iter('fontspec')}
            spans=Counter(colors[t.get('font')] for t in tree.iter('text') if ''.join(t.itertext()).strip())
            check(PALETTE<=set(spans) if mode=='marked' else set(spans)=={'#000000'},
                  f'{mode} text colors on {len(list(tree.iter("page")))} pages, '
                  +(', '.join(sorted(PALETTE)) if mode=='marked' else 'black only'))
        check(extracts[0]==extracts[1],'marked and clean PDF text and pagination match exactly')


if __name__=='__main__':
    test_sources()
    test_data()
    test_pdfs()
