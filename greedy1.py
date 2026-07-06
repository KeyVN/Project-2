import os
import time
import csv
from readfile import parse_cap_file

METHOD = "Greedy1"


def solve_greedy_1(data):
    I = data['num_facilities']
    J = data['num_customers']
    f = data['fixed_costs']
    s = data['capacities']
    d = data['demands']
    c = data['cost_matrix']

    assigned_to = [-1] * J
    is_open = [False] * I
    remaining_capacity = list(s)
    total_cost = 0
    unassigned = set(range(J))
    start = time.time()

    while unassigned:
        best_facility = -1
        best_ratio = -1.0
        best_assignment = []

        for i in range(I):
            if is_open[i]:
                continue
            candidates = [(j, d[j], c[i][j]) for j in unassigned if d[j] <= s[i]]
            candidates.sort(key=lambda x: x[2])
            cap = s[i]
            packed = []
            serve_cost = 0
            saved_cost = 0
            for j, dem, cost in candidates:
                if dem <= cap:
                    packed.append(j)
                    serve_cost += cost
                    saved_cost += max(c[k][j] for k in range(I)) - cost
                    cap -= dem
            if not packed:
                continue
            ratio = saved_cost / (f[i] + serve_cost) if (f[i] + serve_cost) > 0 else 0
            if ratio > best_ratio:
                best_ratio = ratio
                best_facility = i
                best_assignment = packed

        if best_facility == -1:
            return None

        is_open[best_facility] = True
        total_cost += f[best_facility]
        for j in best_assignment:
            assigned_to[j] = best_facility
            remaining_capacity[best_facility] -= d[j]
            total_cost += c[best_facility][j]
            unassigned.remove(j)

    return {
        "status": "FEASIBLE",
        "objective": total_cost,
        "time": time.time() - start,
        "opened_facilities": sum(is_open),
        "assigned_to": assigned_to,
        "is_open": is_open,
    }


if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir = "data_preprocessed"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "results_greedy1.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["File", "Status", "Objective (Baseline)", "Time (s)", "Facilities Opened", "Note"])
        for fn in test_files:
            data = parse_cap_file(os.path.join(input_dir, fn))
            res = solve_greedy_1(data) if data else None
            if res:
                w.writerow([fn, res["status"], f"{res['objective']:.4f}", f"{res['time']:.4f}", res["opened_facilities"], METHOD])
            else:
                w.writerow([fn, "ERROR", "N/A", "N/A", "0", METHOD])
    print(f"Saved {out}")
