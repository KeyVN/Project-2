import os
import time
import csv
from readfile import parse_cap_file

def solve_greedy_2(data):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']

    assigned_to = [-1] * J
    is_open = [False] * I
    remaining_capacity = list(s)
    total_cost = 0

    customers = list(range(J))
    customers.sort(key=lambda j: d[j], reverse=True)

    for j in customers:
        best_fac = -1
        min_added_cost = float('inf')

        for i in range(I):
            if remaining_capacity[i] >= d[j]:
                added_cost = c[i][j]
                if not is_open[i]:
                    added_cost += f[i]

                if added_cost < min_added_cost:
                    min_added_cost = added_cost
                    best_fac = i

        if best_fac == -1: 
            return None

        if not is_open[best_fac]:
            is_open[best_fac] = True
            total_cost += f[best_fac]
        
        assigned_to[j] = best_fac
        remaining_capacity[best_fac] -= d[j]
        total_cost += c[best_fac][j]

    return {
        "objective": total_cost,
        "assigned_to": assigned_to,
        "is_open": is_open
    }

def move2_close_facility(data, initial_solution):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']

    assigned_to = list(initial_solution['assigned_to'])
    is_open = list(initial_solution['is_open'])
    total_cost = initial_solution['objective']
    
    remaining_capacity = list(s)
    for j in range(J):
        remaining_capacity[assigned_to[j]] -= d[j]

    start_time = time.time()
    improved = True
    iteration = 0

    while improved:
        improved = False
        iteration += 1
        
        best_delta = 0
        best_closure = -1
        best_reassignments = {} 

        for i in range(I):
            if not is_open[i]:
                continue
            
            customers_of_i = [j for j in range(J) if assigned_to[j] == i]
            customers_of_i.sort(key=lambda j: d[j], reverse=True)

            temp_cap = list(remaining_capacity)
            delta = -f[i]
            possible = True
            temp_reassignments = {}

            for j in customers_of_i:
                best_k = -1
                min_added_cost = float('inf')

                for k in range(I):
                    if k == i or not is_open[k]:
                        continue
                    
                    if temp_cap[k] >= d[j]:
                        added_cost = c[k][j] - c[i][j]
                        if added_cost < min_added_cost:
                            min_added_cost = added_cost
                            best_k = k

                if best_k == -1:
                    possible = False
                    break
                
                temp_cap[best_k] -= d[j]
                delta += min_added_cost
                temp_reassignments[j] = best_k

            if possible and delta < best_delta:
                best_delta = delta
                best_closure = i
                best_reassignments = temp_reassignments

        if best_closure != -1:
            total_cost += best_delta
            is_open[best_closure] = False
            remaining_capacity[best_closure] = s[best_closure]
            
            for j, k in best_reassignments.items():
                assigned_to[j] = k
                remaining_capacity[k] -= d[j]
                
            improved = True 

    end_time = time.time()

    return {
        "objective": total_cost,
        "time": end_time - start_time,
        "opened_count": sum(is_open),
        "iterations": iteration
    }

if __name__ == "__main__":
    test_files = []
    for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
        for j in range(1, 5): test_files.append(f"cap{i}{j}.txt")
    test_files.append("cap51.txt")

    results_file = "results_greedy2m2.csv"
    
    print(f"Đang chạy [Greedy 2 + LS Move 2 (Close)] trên {len(test_files)} file...")
    print(f"{'File':<12} | {'Greedy Obj':<15} | {'Move 2 Obj':<15} | {'Kho Mở (Tr->S)':<15}")
    print("-" * 75)

    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Greedy 2 Obj", "Move 2 Obj", "Time (s)", "Iterations", "Facilities"])

        for filename in test_files:
            path = os.path.join("data", filename)
            data = parse_cap_file(path)
            
            if data:
                initial_sol = solve_greedy_2(data)
                
                if initial_sol:
                    greedy_obj = initial_sol['objective']
                    greedy_fac = sum(initial_sol['is_open'])
                    
                    ls_sol = move2_close_facility(data, initial_sol)
                    
                    saved = greedy_obj - ls_sol['objective']
                    fac_str = f"{greedy_fac} -> {ls_sol['opened_count']}"
                    
                    writer.writerow([filename, greedy_obj, ls_sol['objective'], f"{ls_sol['time']:.6f}", ls_sol['iterations'], ls_sol['opened_count']])
                    print(f"{filename:<12} | {greedy_obj:<15.2f} | {ls_sol['objective']:<15.2f} | {fac_str:<15}")
                else:
                    writer.writerow([filename, "INFEASIBLE", "INFEASIBLE", "N/A", "0", "0"])
                    print(f"{filename:<12} | {'INFEASIBLE':<15} | {'INFEASIBLE':<15} | {'-':<15}")
                    
    print(f"\n=> Hoàn tất! Kết quả được lưu tại {results_file}")