import os
import time
import csv
from ortools.linear_solver import pywraplp
from readfile import parse_cap_file

def solve_for_baseline(data, time_limit=60):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver:
        return None
    y = [solver.IntVar(0, 1, f'y_{i}') for i in range(I)]
    x = [[solver.IntVar(0, 1, f'x_{i}_{j}') for j in range(J)] for i in range(I)]
    for j in range(J):
        solver.Add(sum(x[i][j] for i in range(I)) == 1)
    for i in range(I):
        solver.Add(sum(d[j] * x[i][j] for j in range(J)) <= s[i] * y[i])
    for i in range(I):
        for j in range(J):
            solver.Add(x[i][j] <= y[i])
    objective = solver.Objective()
    for i in range(I): objective.SetCoefficient(y[i], f[i])
    for i in range(I):
        for j in range(J): objective.SetCoefficient(x[i][j], c[i][j])
    objective.SetMinimization()
    solver.SetTimeLimit(time_limit * 1000)
    status = solver.Solve()
    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return {"status": "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE", "objective": solver.Objective().Value(), "time": solver.wall_time() / 1000.0, "opened_facilities": sum(1 for i in range(I) if y[i].solution_value() > 0.5)}
    return {"status": "INFEASIBLE" if status == pywraplp.Solver.INFEASIBLE else "FAILED", "objective": None, "time": 0, "opened_facilities": 0}

if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir = "data_preprocessed"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, "baselines_milp.csv")
    print(f"Starting MILP experiments on {len(test_files)} files from {input_dir}. Results saved to {results_file}...")
    print("Note: Time limit is 60 seconds/file. Beyond 60s, will skip to avoid hanging.")
    print("-" * 60)
    with open(results_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Status", "Objective (Baseline)", "Time (s)", "Facilities Opened", "Note"])
        for filename in test_files:
            print(f"Solving {filename:<12}...", end=" ", flush=True)
            data = parse_cap_file(os.path.join(input_dir, filename))
            if data:
                res = solve_for_baseline(data, time_limit=60)
                note = ""
                writer.writerow([filename, res['status'], res['objective'], f"{res['time']:.4f}" if res['time'] else "N/A", res['opened_facilities'], note])
                print(f"[{res['status']}] Obj: {res['objective']} ({res['time']:.2f}s) {note}")
            else:
                writer.writerow([filename, "ERROR", "N/A", "N/A", "0", "File read error"])
                print("Error reading file.")
    print("\n" + "=" * 60)
    print(f"Completed! Open {results_file} to see full summary.")
