import os, time, csv
from readfile import parse_cap_file

METHOD = "Move2"

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

def move2_close_facility(data, sol):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    assigned_to = list(sol['assigned_to'])
    is_open = list(sol['is_open'])
    total_cost = sol['objective']
    remaining_capacity = list(s)
    for j in range(J):
        remaining_capacity[assigned_to[j]] -= d[j]
    start = time.time()
    iterations = 0
    while True:
        iterations += 1
        best_delta = 0; best_closure = -1; best_reassignments = {}
        for i in range(I):
            if not is_open[i]: continue
            customers_of_i = [j for j in range(J) if assigned_to[j] == i]
            if not customers_of_i: continue
            temp_cap = list(remaining_capacity)
            delta = -f[i]; possible = True; temp_reassignments = {}
            for j in sorted(customers_of_i, key=lambda x: d[x], reverse=True):
                best_k = -1; min_add = float('inf')
                for k in range(I):
                    if k == i or not is_open[k] or temp_cap[k] < d[j]: continue
                    add = c[k][j] - c[i][j]
                    if add < min_add:
                        min_add = add; best_k = k
                if best_k == -1:
                    possible = False; break
                temp_cap[best_k] -= d[j]; delta += min_add; temp_reassignments[j] = best_k
            if possible and delta < best_delta:
                best_delta = delta; best_closure = i; best_reassignments = temp_reassignments
        if best_closure != -1:
            is_open[best_closure] = False
            for j, new_fac in best_reassignments.items():
                assigned_to[j] = new_fac
            total_cost += best_delta
        else: break
    return {"status": "FEASIBLE", "objective": total_cost, "time": time.time() - start, "opened_facilities": sum(is_open)}

if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir, output_dir = "data_preprocessed", "output"
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "results_greedy2m2.csv")
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
            res = move2_close_facility(data, sol)
            w.writerow([fn, res["status"], f"{res['objective']:.4f}", f"{res['time']:.4f}", res["opened_facilities"], METHOD])
    print(f"Saved {out}")
