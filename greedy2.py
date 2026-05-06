import os
import time
import csv
from readfile import parse_cap_file

def solve_greedy_2(data):
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

    start_time = time.time()

    customers = list(range(J))
    customers.sort(key=lambda j: d[j], reverse=True)

    for j in customers:
        best_facility = -1
        min_added_cost = float('inf')

        for i in range(I):
            if remaining_capacity[i] >= d[j]:
                added_cost = c[i][j]
                
                if not is_open[i]:
                    added_cost += f[i]

                if added_cost < min_added_cost:
                    min_added_cost = added_cost
                    best_facility = i

        if best_facility == -1:
            return None

        if not is_open[best_facility]:
            is_open[best_facility] = True
            total_cost += f[best_facility]
        
        assigned_to[j] = best_facility
        remaining_capacity[best_facility] -= d[j]
        total_cost += c[best_facility][j]

    end_time = time.time()

    return {
        "objective": total_cost,
        "time": end_time - start_time,
        "opened_count": sum(is_open)
    }

if __name__ == "__main__":
    test_files = []
    
    for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
        for j in range(1, 5): 
            test_files.append(f"cap{i}{j}.txt")
    test_files.append("cap51.txt")
    test_files.extend(["capa.txt", "capb.txt", "capc.txt"])

    results_file = "results_greedy2.csv"
    print(f"Đang chạy Greedy 2 (Ưu tiên khách hàng khó) trên {len(test_files)} file...")
    print("-" * 50)

    with open(results_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Objective", "Time (s)", "Facilities"])

        for filename in test_files:
            path = os.path.join("data", filename)
            data = parse_cap_file(path)
            if data:
                res = solve_greedy_2(data)
                if res:
                    writer.writerow([filename, res['objective'], f"{res['time']:.6f}", res['opened_count']])
                    print(f" {filename:<12}: Obj = {res['objective']:,.2f} | Time = {res['time']:.4f}s")
                else:
                    writer.writerow([filename, "INFEASIBLE", "N/A", "0"])
                    print(f" {filename:<12}: Vô nghiệm")

    print(f"\nHoàn tất! Kết quả được lưu tại {results_file}")