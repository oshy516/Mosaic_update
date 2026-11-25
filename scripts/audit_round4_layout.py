"""Check the round-four layout, figure coordinates and data-derived Table 6 after latexmk."""
from pathlib import Path
import os
import csv,re,math,statistics,pymupdf
root=Path(__file__).resolve().parents[1]
src=root/'manuscript'
orig=Path(os.environ.get('MOSAIC_ORIGINAL', root.parent/'mosaic'))
doc=pymupdf.open(root/'mosaic_r1_marked.pdf')
def check(ok,title):
 assert ok,title
 print('PASS',title)
def spans(pg):
 return [s for b in doc[pg-1].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']]
for p,y0,y1,color,name in [(13,84,221,0xc00000,'Algorithm 1'),(19,83,240,0x7030a0,'Table 6')]:
 body=[s for s in spans(p) if y0 <= sum(s['bbox'][1::2])/2<=y1 and s['bbox'][0]>40 and s['text'].strip()]
 check(body and all(s['color']==color for s in body),name+' caption, label and body color')
for p,nums in [(1,['45','47']),(21,['45','[47]']),(22,['44'])]:
 seen=[s['text'].strip() for s in spans(p) if s['color']==0x7030a0]
 for n in nums:check(any(n in s for s in seen) or (n=='[47]' and ''.join(seen).find('[47]')>=0),f'p{p} added purple reference {n}')
m=(src/'sec.eval.tex').read_text();o=(orig/'sec.eval.tex').read_text()
def environment(s,label,env):
 return next(x for x in re.findall(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}',s,re.S) if r'\label{'+label+'}' in x)
for label,env in [('fig:network-operators','wrapfigure'),('fig:network-operator-curves','figure'),('fig:e2e-fourbar','wrapfigure'),('fig:ablation','wrapfigure'),('fig:bounded-ppcg-sweep','figure'),('tab:platforms','table')]:
 before,after=[environment(s,label,env) for s in (o,m)]
 c=lambda x:x.split(r'\caption{')[1].split('\n')[0]
 check(c(before)==c(after),label+' original caption')
 if label=='fig:network-operator-curves':
  coords=lambda x:re.findall(r'coordinates\s*\{([^}]+)\};',x)
  check(len(coords(after))==24 and coords(before)==coords(after),'Fig. 7 all 24 coordinate series unchanged')
  ticks=re.findall(r'ytick=\{([^}]+)\}',after)
  check(len(ticks)==12 and all(math.log10(float(v)).is_integer() for t in ticks for v in t.split(',')) and 'opacity=0' not in after,'Fig. 7 six visible right axes and 12 integer-power scales')
 if label=='fig:ablation':
  values=lambda t: [re.findall(r'\(([0-9.]+),([0-9.]+)\)',b) for b in re.findall(r'coordinates\s*\{(.*?)\};',t,re.S)]
  check(values(before)==values(after) and len(values(after))==3 and 'area legend' in after,'Fig. 9 all 15 heights and single-swatch legends')
table=environment(m,'tab:tilemind','table')
raw=list(csv.DictReader((root/'data/tilemind_comparison.csv').open()))
for op in ['GEMM','Conv2D']:
 group=[]
 for row in raw:
  if row['op']!=op:continue
  shape=list(map(int,row['shape'].split('x')))
  dims=lambda xs:r'{\times}'.join(map(str,xs))
  if op=='GEMM': view=dims(shape)
  else:
   n,k,p,q,c,r,s,h,w=shape;check((h-r+1,w-s+1)==(p,q),'Table 6 unit-stride Conv2D shape '+row['shape'])
   view=dims((n,c,h,w))+r'\;\rightarrow\;'+dims((n,k,p,q))
  mt,tt=float(row['mosaic_ms']),float(row['tilemind_ms']);spd=tt/mt; key='$'+view+f'$ & {mt:.3f} & {tt:.3f} & {spd:.2f}'+r'$\times$'
  assert table.count(key)==1,key
  group.append((table.index(key),2*math.prod(shape[:7]),spd))
 flops=[g[1] for g in sorted(group)]
 check(flops==sorted(flops) and len(group)==5 and f'{statistics.geometric_mean(g[2] for g in group):.2f}'+r'$\times$' in table,'Table 6 '+op+' FLOP order, five shape/time/ratio rows and geometric mean')
for label in ('marked','clean'):
 p=root/f'mosaic_r1_{label}.pdf';check(len(pymupdf.open(p))==25,label+' 25 pages including references')
 nums=re.findall(r'\\bibcite\{([^}]+)\}\{\{(\d+)\}',(src/('mosaic' if label=='marked' else 'main_clean')).with_suffix('.aux').read_text())
 d=dict(nums);check(len(d)==48 and [d[k] for k in ('tilemind','yuki-tss','zhai2024tlm','zhao2020micro','akg','zhao2024tocs','ansor')]==list(map(str,range(42,49))),label+' bibliography [42]-[48]')
