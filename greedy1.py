import os
import time
import csv
from readfile import parse_cap_file

def solve_greedy_1(data):
    """
    Thuật toán Greedy 1 (Tối ưu hóa toàn diện): 
    Dùng chiến lược Knapsack kết hợp Tiền xử lý (Pre-computation) để tăng tốc độ.
    """
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
    unassigned_customers = set(range(J))

    start_time = time.time()

    max_c = [max(c[i][j] for i in range(I)) for j in range(J)]

    facility_candidates = []
    for i in range(I):
        cands = []
        for j in range(J):
            savings = max_c[j] - c[i][j]
            eff = savings / d[j] if d[j] > 0 else float('inf')
            cands.append({'id': j, 'savings': savings, 'eff': eff, 'dem': d[j]})
        
        cands.sort(key=lambda x: x['eff'], reverse=True)
        facility_candidates.append(cands)

    while unassigned_customers:
        best_facility = -1
        best_ratio = -1.0
        best_assigned_list = []

        for i in range(I):
            if is_open[i] and remaining_capacity[i] <= 0:
                continue
            
            cap = remaining_capacity[i]
            current_benefit = 0
            current_assigned = []
            
            for cand in facility_candidates[i]:
                if cand['id'] in unassigned_customers:
                    if cand['dem'] <= cap:
                        current_benefit += cand['savings']
                        current_assigned.append(cand['id'])
                        cap -= cand['dem']
            
            if not current_assigned:
                continue

            if is_open[i]:
                cost_to_open = 1e-6 
            else:
                cost_to_open = f[i] if f[i] > 0 else 1e-6

            ratio = current_benefit / cost_to_open
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_facility = i
                best_assigned_list = current_assigned

        if best_facility == -1:
            break 

        if not is_open[best_facility]:
            is_open[best_facility] = True
            total_cost += f[best_facility]
        
        for j in best_assigned_list:
            assigned_to[j] = best_facility
            remaining_capacity[best_facility] -= d[j]
            total_cost += c[best_facility][j]
            unassigned_customers.remove(j)

    end_time = time.time()
    
    if len(unassigned_customers) > 0:
        return None

    return {
        "objective": total_cost,
        "time": end_time - start_time,
        "opened_count": sum(is_open)
    }

if __name__ == "__main__":
    test_files = []
    for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
        for j in range(1, 5): test_files.append(f"cap{i}{j}.txt")
    test_files.append("cap51.txt")
    # test_files.extend(["capa.txt", "capb.txt", "capc.txt"])

    results_file = "results_greedy1.csv"
    print(f"Đang chạy Greedy 1 trên {len(test_files)} file...")

    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Objective", "Time (s)", "Facilities"])

        for filename in test_files:
            path = os.path.join("data", filename)
            data = parse_cap_file(path)
            if data:
                res = solve_greedy_1(data)
                if res:
                    writer.writerow([filename, res['objective'], f"{res['time']:.6f}", res['opened_count']])
                    print(f" {filename:<12}: Obj = {res['objective']:,.2f} | Time = {res['time']:.4f}s")
                else:
                    writer.writerow([filename, "INFEASIBLE", "N/A", "0"])
                    print(f" {filename:<12}: Vô nghiệm")

    print(f"\nHoàn tất! Kết quả lưu tại {results_file}")