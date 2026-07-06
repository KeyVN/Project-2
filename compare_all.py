import csv
from pathlib import Path

base = Path(r'D:\IT\Project-2\output')
files = {
    'MILP': base / 'baselines_milp.csv',
    'Greedy1': base / 'results_greedy1.csv',
    'Greedy2': base / 'results_greedy2.csv',
    'Move1': base / 'results_greedy2m1.csv',
    'Move2': base / 'results_greedy2m2.csv',
    'Move3': base / 'results_greedy2m3.csv',
    'Move4': base / 'results_greedy2m4.csv',
    'VND': base / 'results_greedy2_vnd.csv',
}

data = {}
for method, path in files.items():
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fn = row['File']
            data.setdefault(fn, {})[method] = {
                'obj': float(row['Objective (Baseline)']) if row['Objective (Baseline)'] not in ('N/A', '') else None,
                'time': float(row['Time (s)']) if row['Time (s)'] not in ('N/A', '') else None,
                'fac': int(row['Facilities Opened']) if row['Facilities Opened'] not in ('N/A', '') else None,
                'status': row['Status']
            }

print('=' * 80)
print('ALL METHODS VS MILP')
print('=' * 80)
print()

methods = ['Greedy1', 'Greedy2', 'Move1', 'Move2', 'Move3', 'Move4', 'VND']
for method in methods:
    gaps = []
    wins = ties = 0
    for fn, results in data.items():
        if 'MILP' in results and method in results:
            milp = results['MILP']
            m = results[method]
            if milp['status'] in ('OPTIMAL', 'FEASIBLE') and m['status'] == 'FEASIBLE' and milp['obj'] is not None and m['obj'] is not None:
                gap = (m['obj'] - milp['obj']) / milp['obj'] * 100
                gaps.append(gap)
                if 'Greedy2' in results and results['Greedy2']['obj'] is not None:
                    if m['obj'] < results['Greedy2']['obj'] - 0.01:
                        wins += 1
                    elif abs(m['obj'] - results['Greedy2']['obj']) < 0.01:
                        ties += 1
    if gaps:
        print(f'{method:8s}: n={len(gaps):2d} | avg={sum(gaps)/len(gaps):6.2f}% | min={min(gaps):6.2f}% | max={max(gaps):6.2f}% | wins_vs_G2={wins:2d} | ties={ties:2d}')
    else:
        print(f'{method:8s}: NO DATA')

print()
print('=' * 80)
print('MOVE COMPARISON DETAILS')
print('=' * 80)
print()

move_methods = ['Move1', 'Move2', 'Move3', 'Move4', 'VND']
print(f"{'File':<15s} {'MILP':>12s} {'G2':>12s} {'M1':>12s} {'M2':>12s} {'M3':>12s} {'M4':>12s} {'VND':>12s} {'Best':>6s}")
print('-' * 110)
for fn in sorted(data.keys()):
    if 'MILP' not in data[fn] or data[fn]['MILP']['obj'] is None:
        continue
    row = [fn, f"{data[fn]['MILP']['obj']:12.2f}"]
    objs = {}
    for m in ['Greedy2'] + move_methods:
        if m in data[fn] and data[fn][m]['obj'] is not None:
            objs[m] = data[fn][m]['obj']
            row.append(f"{data[fn][m]['obj']:12.2f}")
        else:
            row.append(f"{'N/A':>12s}")
    row.append(min(objs, key=objs.get) if objs else 'N/A')
    print(' '.join(row))

print()
print('=' * 80)
print('WIN MATRIX AMONG MOVES')
print('=' * 80)
print()

win_matrix = {m1: {m2: 0 for m2 in move_methods} for m1 in move_methods}
for fn, results in data.items():
    for m1 in move_methods:
        for m2 in move_methods:
            if m1 != m2 and m1 in results and m2 in results and results[m1]['obj'] is not None and results[m2]['obj'] is not None:
                if results[m1]['obj'] < results[m2]['obj'] - 0.01:
                    win_matrix[m1][m2] += 1

print(f"{'':>8s} " + ' '.join(f'{m:>6s}' for m in move_methods))
print('-' * 50)
for m1 in move_methods:
    print(f'{m1:>8s} ' + ' '.join(f'{("--" if m1==m2 else win_matrix[m1][m2]):>6s}' if m1==m2 else f'{win_matrix[m1][m2]:>6d}' for m2 in move_methods))
