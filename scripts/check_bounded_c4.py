"""Replay §6.2 C4 for the ATAX and Jacobi-2D bounded sweeps from a PolyBench-NN tree."""
import argparse
import csv
import json
import math
import re
from pathlib import Path


def kernel_violates(benchmark, index, tile, host, kernels, gpu):
    block = re.search(rf'dim3 k{index}_dimBlock\((\d+)(?:,\s*(\d+))?\)', host)
    if not block:
        raise ValueError(f'{benchmark}/kernel{index}: missing static block dimensions')
    x, y = int(block[1]), int(block[2] or 1)
    code = kernels.split(f'__global__ void kernel{index}(', 1)[1].split('__global__ void', 1)[0]
    arrays = re.findall(r'__shared__\s+double\s+\w+((?:\[\d+\])+);', code)
    if len(arrays) != code.count('__shared__'):
        raise ValueError(f'{benchmark}/kernel{index}: unsupported shared-memory declaration')
    shared = sum(8 * math.prod(map(int, re.findall(r'\d+', dims))) for dims in arrays)
    threads = x * y
    residency = max(1, min(gpu['max_blocks_per_sm'], gpu['max_threads_per_sm'] // threads,
                           gpu['shared_mem_per_sm'] // max(1, shared)))
    budget = gpu['max_registers_per_sm'] // (residency * threads)
    if benchmark == 'jacobi-2d':
        i, j = tile[0] // y, tile[1] // x
        demand = i * j + i + j + 4
    else:
        demand = tile[0] // x + len(arrays) + 4
    return demand > budget


def replay(tree):
    with (tree / 'sweep/benchmark_results.csv').open() as source:
        latest = {(r['benchmark'], r['variant_id']): r for r in csv.DictReader(source)}
    for name, selected_ms in [('atax', 0.1920), ('jacobi-2d', 266.16)]:
        profile = tree / 'ablation' / name / 'register_validation_4090.json'
        gpu = json.loads(profile.read_text())['gpu_hardware']
        feasible, rejected = [], []
        for (benchmark, variant), row in latest.items():
            if benchmark != name or row['status'] != 'success':
                continue
            directory = tree / 'sweep' / name / variant
            host = (directory / f'{name}_host.cu').read_text()
            kernels = (directory / f'{name}_kernel.cu').read_text()
            tiles = json.loads(row['per_kernel_tile_tuple'])
            classifications = [kernel_violates(name, k, tiles[f'kernel[{k}]'], host, kernels, gpu)
                               for k in range(2)]
            group = rejected if any(classifications) else feasible
            group.append((float(row['kernel_total_median_ms']), variant))
        best = min(selected_ms, min(feasible)[0])
        faster = sum(ms < best for ms, _ in rejected)
        print(f'{name}: {len(feasible)+len(rejected)} measured, {len(rejected)} rejected, '
              f'{faster} faster than {best:.6f} ms. Fastest feasible sweep point: {min(feasible)}.')
        if rejected:
            ms, variant = min(rejected)
            print(f'Fastest rejected: {variant}, {ms:.9f} ms, {100*(ms/selected_ms-1):.6f}% above Mosaic.')
        if faster:
            raise ValueError(f'{name} violates the E3 premise')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('polybench_tree', type=Path)
    replay(parser.parse_args().polybench_tree)
