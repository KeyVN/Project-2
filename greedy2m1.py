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

def move1_reassignment(data, initial_solution):
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']

    assigned_to = list(initial_solution['assigned_to'])
    is_open = list(initial_solution['is_open'])
    total_cost = initial_solution['objective']
    
    remaining_capacity = list(s)
    customer_count = [0] * I
    for j in range(J):
        fac = assigned_to[j]
        remaining_capacity[fac] -= d[j]
        customer_count[fac] += 1

    start_time = time.time()
    improved = True
    iteration = 0

    while improved:
        improved = False
        iteration += 1
        
        best_delta = 0
        best_move = None  

        for j in range(J):
            old_fac = assigned_to[j]
            
            for new_fac in range(I):
                if new_fac == old_fac:
                    continue
                
                if remaining_capacity[new_fac] >= d[j]:
                    delta = c[new_fac][j] - c[old_fac][j]
                    
                    if not is_open[new_fac]:
                        delta += f[new_fac]
                        
                    if customer_count[old_fac] == 1:
                        delta -= f[old_fac]

                    if delta < best_delta:
                        best_delta = delta
                        best_move = (j, old_fac, new_fac)

        if best_move is not None:
            j, old_fac, new_fac = best_move
            
            total_cost += best_delta
            
            assigned_to[j] = new_fac
            remaining_capacity[old_fac] += d[j]
            customer_count[old_fac] -= 1
            if customer_count[old_fac] == 0:
                is_open[old_fac] = False  
                
            remaining_capacity[new_fac] -= d[j]
            customer_count[new_fac] += 1
            if not is_open[new_fac]:
                is_open[new_fac] = True   
            
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

    results_file = "results_greedy2m1.csv"
    
    print(f"Đang chạy [Greedy 2 + LS Move 1] trên {len(test_files)} file...")
    print(f"{'File':<12} | {'Greedy 2 Obj':<15} | {'Move 1 Obj':<15} | {'Tiết kiệm':<12} | {'Loops'}")
    print("-" * 75)

    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Greedy 2 Obj", "Move 1 Obj", "Time (s)", "Iterations", "Facilities"])

        for filename in test_files:
            path = os.path.join("data", filename)
            data = parse_cap_file(path)
            
            if data:
                initial_sol = solve_greedy_2(data)
                
                if initial_sol:
                    greedy_obj = initial_sol['objective']
                    ls_sol = move1_reassignment(data, initial_sol)
                    saved = greedy_obj - ls_sol['objective']
                    
                    writer.writerow([filename, greedy_obj, ls_sol['objective'], f"{ls_sol['time']:.6f}", ls_sol['iterations'], ls_sol['opened_count']])
                    print(f"{filename:<12} | {greedy_obj:<15.2f} | {ls_sol['objective']:<15.2f} | {saved:<12.2f} | {ls_sol['iterations']}")
                else:
                    writer.writerow([filename, "INFEASIBLE", "INFEASIBLE", "N/A", "0", "0"])
                    print(f"{filename:<12} | {'INFEASIBLE':<15} | {'INFEASIBLE':<15} | {'0':<12} | 0")
                    
    print(f"\n=> Hoàn tất! Kết quả được lưu tại {results_file}")