import os, time, csv
from readfile import parse_cap_file

METHOD = "Move3"

def build_greedy_2_solution(data):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    assigned_to = [-1] * J
    is_open = [False] * I
    remaining_capacity = list(s)
    total_cost = 0
    for j in sorted(range(J), key=lambda j: d[j], reverse=True):
        best_fac = -1; min_cost = float('inf')
        for i in range(I):
            if remaining_capacity[i] >= d[j]:
                ac = c[i][j] + (0 if is_open[i] else f[i])
                if ac < min_cost:
                    min_cost = ac; best_fac = i
        if best_fac == -1: return None
        if not is_open[best_fac]: is_open[best_fac] = True; total_cost += f[best_fac]
        assigned_to[j] = best_fac; remaining_capacity[best_fac] -= d[j]; total_cost += c[best_fac][j]
    return {"objective": total_cost, "assigned_to": assigned_to, "is_open": is_open}

def move3_local_search(data, sol):
    """Open one closed facility, then reassign profitable customers to it."""
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    assigned_to = list(sol['assigned_to'])
    is_open = list(sol['is_open'])
    total_cost = sol['objective']
    start = time.time()

    while True:
        best_delta = 0
        best_facility = None
        best_customers = None

        for new_fac in range(I):
            if is_open[new_fac]:
                continue

            remaining = s[new_fac]
            delta = f[new_fac]
            moved = []

            candidates = sorted(
                (j for j in range(J) if c[new_fac][j] < c[assigned_to[j]][j]),
                key=lambda j: c[new_fac][j] - c[assigned_to[j]][j]
            )

            for j in candidates:
                if remaining < d[j]:
                    continue
                delta += c[new_fac][j] - c[assigned_to[j]][j]
                remaining -= d[j]
                moved.append(j)

            if moved and delta < best_delta:
                best_delta = delta
                best_facility = new_fac
                best_customers = moved

        if best_facility is None:
            break

        is_open[best_facility] = True
        for j in best_customers:
            assigned_to[j] = best_facility
        total_cost += best_delta

    return {"status": "FEASIBLE", "objective": total_cost, "time": time.time() - start, "opened_facilities": sum(is_open)}

if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir, output_dir = "data_preprocessed", "output"
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "results_greedy2m3.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["File", "Status", "Objective (Baseline)", "Time (s)", "Facilities Opened", "Note"])
        for fn in test_files:
            data = parse_cap_file(os.path.join(input_dir, fn))
            if not data:
                w.writerow([fn, "ERROR", "N/A", "N/A", "0", METHOD])
                continue
            sol = build_greedy_2_solution(data)
            if not sol:
                w.writerow([fn, "ERROR", "N/A", "N/A", "0", METHOD])
                continue
            res = move3_local_search(data, sol)
            w.writerow([fn, res["status"], f"{res['objective']:.4f}", f"{res['time']:.4f}", res["opened_facilities"], METHOD])
    print(f"Saved {out}")
