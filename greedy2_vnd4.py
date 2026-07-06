import os, time, csv
from readfile import parse_cap_file

METHOD = "VND_4Moves"

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

def capacities(I, J, s, d, assigned_to):
    remaining = list(s)
    count = [0] * I
    for j in range(J):
        remaining[assigned_to[j]] -= d[j]
        count[assigned_to[j]] += 1
    return remaining, count

def move1_reassign(I, J, f, s, d, c, assigned_to, is_open):
    remaining, count = capacities(I, J, s, d, assigned_to)
    best_delta = 0; best = None
    for j in range(J):
        old = assigned_to[j]
        for new in range(I):
            if new == old or remaining[new] < d[j]: continue
            delta = c[new][j] - c[old][j]
            if not is_open[new]: delta += f[new]
            if count[old] == 1: delta -= f[old]
            if delta < best_delta:
                best_delta = delta; best = (j, old, new)
    if not best: return 0
    j, old, new = best
    assigned_to[j] = new
    if count[old] == 1: is_open[old] = False
    if not is_open[new]: is_open[new] = True
    return best_delta

def move2_close(I, J, f, s, d, c, assigned_to, is_open):
    remaining, _ = capacities(I, J, s, d, assigned_to)
    best_delta = 0; best = None
    for close in range(I):
        if not is_open[close]: continue
        customers = [j for j in range(J) if assigned_to[j] == close]
        if not customers: continue
        temp_cap = list(remaining)
        delta = -f[close]
        reassign = {}
        for j in sorted(customers, key=lambda x: d[x], reverse=True):
            best_fac = -1; best_add = float('inf')
            for fac in range(I):
                if fac == close or not is_open[fac] or temp_cap[fac] < d[j]: continue
                add = c[fac][j] - c[close][j]
                if add < best_add:
                    best_add = add; best_fac = fac
            if best_fac == -1: break
            temp_cap[best_fac] -= d[j]; delta += best_add; reassign[j] = best_fac
        else:
            if delta < best_delta:
                best_delta = delta; best = (close, reassign)
    if not best: return 0
    close, reassign = best
    is_open[close] = False
    for j, fac in reassign.items(): assigned_to[j] = fac
    return best_delta

def move3_open_reassign(I, J, f, s, d, c, assigned_to, is_open):
    best_delta = 0; best = None
    for new_fac in range(I):
        if is_open[new_fac]: continue
        remaining = s[new_fac]
        delta = f[new_fac]
        moved = []
        candidates = sorted(
            (j for j in range(J) if c[new_fac][j] < c[assigned_to[j]][j]),
            key=lambda j: c[new_fac][j] - c[assigned_to[j]][j]
        )
        for j in candidates:
            if remaining < d[j]: continue
            delta += c[new_fac][j] - c[assigned_to[j]][j]
            remaining -= d[j]
            moved.append(j)
        if moved and delta < best_delta:
            best_delta = delta; best = (new_fac, moved)
    if not best: return 0
    new_fac, moved = best
    is_open[new_fac] = True
    for j in moved: assigned_to[j] = new_fac
    return best_delta

def move4_close_open_reassign(I, J, f, s, d, c, assigned_to, is_open):
    remaining, _ = capacities(I, J, s, d, assigned_to)
    best_delta = 0; best = None
    for close in range(I):
        if not is_open[close]: continue
        customers = [j for j in range(J) if assigned_to[j] == close]
        if not customers: continue
        for open_fac in range(I):
            if is_open[open_fac]: continue
            temp_cap = list(remaining)
            temp_cap[close] += sum(d[j] for j in customers)
            temp_cap[open_fac] = s[open_fac]
            delta = f[open_fac] - f[close]
            reassign = {}
            for j in sorted(customers, key=lambda x: d[x], reverse=True):
                best_fac = -1; best_add = float('inf')
                for fac in range(I):
                    if fac == close or (fac != open_fac and not is_open[fac]) or temp_cap[fac] < d[j]: continue
                    add = c[fac][j] - c[close][j]
                    if add < best_add:
                        best_add = add; best_fac = fac
                if best_fac == -1: break
                temp_cap[best_fac] -= d[j]; delta += best_add; reassign[j] = best_fac
            else:
                if delta < best_delta:
                    best_delta = delta; best = (close, open_fac, reassign)
    if not best: return 0
    close, open_fac, reassign = best
    is_open[close] = False
    is_open[open_fac] = True
    for j, fac in reassign.items(): assigned_to[j] = fac
    return best_delta

def move5_customer_swap(I, J, f, s, d, c, assigned_to, is_open):
    remaining, _ = capacities(I, J, s, d, assigned_to)
    best_delta = 0; best = None
    for a in range(J):
        for b in range(a + 1, J):
            fa, fb = assigned_to[a], assigned_to[b]
            if fa == fb: continue
            if remaining[fa] + d[a] - d[b] < 0: continue
            if remaining[fb] + d[b] - d[a] < 0: continue
            delta = c[fb][a] + c[fa][b] - c[fa][a] - c[fb][b]
            if delta < best_delta:
                best_delta = delta; best = (a, b)
    if not best: return 0
    a, b = best
    assigned_to[a], assigned_to[b] = assigned_to[b], assigned_to[a]
    return best_delta

def vnd_all_moves(data, sol):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']
    assigned_to = list(sol['assigned_to'])
    is_open = list(sol['is_open'])
    total_cost = sol['objective']
    start = time.time()
    moves = [move1_reassign, move2_close, move3_open_reassign, move4_close_open_reassign]
    k = 0
    while k < len(moves):
        delta = moves[k](I, J, f, s, d, c, assigned_to, is_open)
        if delta < 0:
            total_cost += delta
            k = 0
        else:
            k += 1
    return {"status": "FEASIBLE", "objective": total_cost, "time": time.time() - start, "opened_facilities": sum(is_open)}

if __name__ == "__main__":
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir, output_dir = "data_preprocessed", "output"
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "results_greedy2_vnd4.csv")
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
            res = vnd_all_moves(data, sol)
            w.writerow([fn, res["status"], f"{res['objective']:.4f}", f"{res['time']:.4f}", res["opened_facilities"], METHOD])
    print(f"Saved {out}")
