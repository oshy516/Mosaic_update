"""Recompute Fig. 1 C4 from successful measurements and the PPCG source for each hash."""
import argparse
import csv
import json
import math
import re
from decimal import Decimal
from pathlib import Path

def classify(summary, sources, profile, output):
    gpu = json.loads(profile.read_text())['gpu_hardware']
    rows = []
    with summary.open() as f:
        for r in csv.DictReader(f):
            if r['status'] != 'ok':
                continue
            key = r['config_hash']
            kernel = (sources/key/'gemm_kernel.cu').read_text()
            host = (sources/key/'gemm_host.cu').read_text()
            decls = re.findall(r'__shared__\s+double\s+shared_(\w+)((?:\[\d+\])+);', kernel)
            assert len(decls) == kernel.count('__shared__'), key
            size = 8*sum(math.prod(map(int,re.findall(r'\d+', dims))) for _, dims in decls)
            match = re.search(r'dim3 k0_dimBlock\((\d+)(?:,\s*(\d+))?\)',host)
            assert match, key
            bj,bi = (int(v or 1) for v in match.groups())
            assert [bi,bj] == [int(r['block_i']),int(r['block_j'])],key
            threads = bi*bj
            bps = max(1,min(gpu['max_blocks_per_sm'],gpu['max_threads_per_sm']//threads,
                            gpu['shared_mem_per_sm']//max(size,1)))
            a,b = int(r['tile_i'])//bi,int(r['tile_j'])//bj
            demand = a*b+a+b+4
            budget = gpu['max_registers_per_sm']//(bps*threads)
            rows.append(dict(config_hash=key,tile_i=r['tile_i'],tile_j=r['tile_j'],block_i=bi,block_j=bj,
                             shared_bytes=size,bps=bps,R_hat=demand,R_avail=budget,
                             violates=int(demand>budget),median_ms=r['kernel_total_ms_median']))
    assert len(rows)==len({r['config_hash'] for r in rows})==2232
    with output.open('w') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    best = min(Decimal(r['median_ms']) for r in rows)
    feasible = min(Decimal(r['median_ms']) for r in rows if not r['violates'])
    bad = [r for r in rows if r['violates']]
    print(len(rows),len(bad),sum(Decimal(r['median_ms'])<feasible for r in bad),
          best,feasible,100*(feasible/best-1))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for arg in ['summary','sources','profile','output']:
        ap.add_argument(arg,type=Path)
    classify(**vars(ap.parse_args()))
