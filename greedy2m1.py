import os, time, csv
from readfile import parse_cap_file

METHOD = "Move1"

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

def move1_reassignment(data, sol):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    assigned_to = list(sol['assigned_to'])
    is_open = list(sol['is_open'])
    total_cost = sol['objective']
    remaining_capacity = list(s)
    customer_count = [0] * I
    for j in range(J):
        fac = assigned_to[j]
        remaining_capacity[fac] -= d[j]
        customer_count[fac] += 1
    start = time.time()
    iterations, improvements = 0, 0
    while True:
        iterations += 1
        best_delta = 0; best_move = None
        for j in range(J):
            old_fac = assigned_to[j]
            for new_fac in range(I):
                if new_fac == old_fac or remaining_capacity[new_fac] < d[j]: continue
                delta = c[new_fac][j] - c[old_fac][j]
                if not is_open[new_fac]: delta += f[new_fac]
                if customer_count[old_fac] == 1: delta -= f[old_fac]
                if delta < best_delta:
                    best_delta = delta; best_move = (j, old_fac, new_fac)
        if best_move:
            j, old_fac, new_fac = best_move
            assigned_to[j] = new_fac
            if customer_count[old_fac] == 1: is_open[old_fac] = False
            if not is_open[new_fac]: is_open[new_fac] = True
            total_cost += best_delta; improvements += 1
        else: break
    return {"status": "FEASIBLE", "objective": total_cost, "time": time.time() - start, "opened_facilities": sum(is_open)}

if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir, output_dir = "data_preprocessed", "output"
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "results_greedy2m1.csv")
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
            res = move1_reassignment(data, sol)
            w.writerow([fn, res["status"], f"{res['objective']:.4f}", f"{res['time']:.4f}", res["opened_facilities"], METHOD])
    print(f"Saved {out}")
