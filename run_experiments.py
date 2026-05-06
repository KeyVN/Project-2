import os
import time
import csv
from ortools.linear_solver import pywraplp
from readfile import parse_cap_file

def solve_for_baseline(data, time_limit=60):
    """Giải MILP và trả về các thông số kết quả"""
    I, J = data['num_facilities'], data['num_customers']
    f, s, d, c = data['fixed_costs'], data['capacities'], data['demands'], data['cost_matrix']

    solver = pywraplp.Solver.CreateSolver('CBC')
    if not solver: return None

    # Khai báo biến
    y = [solver.IntVar(0, 1, f'y_{i}') for i in range(I)]
    x = [[solver.IntVar(0, 1, f'x_{i}_{j}') for j in range(J)] for i in range(I)]

    # Ràng buộc
    for j in range(J):
        solver.Add(sum(x[i][j] for i in range(I)) == 1)
    for i in range(I):
        solver.Add(sum(d[j] * x[i][j] for j in range(J)) <= s[i] * y[i])
    for i in range(I):
        for j in range(J):
            solver.Add(x[i][j] <= y[i])

    # Hàm mục tiêu
    objective = solver.Objective()
    for i in range(I): objective.SetCoefficient(y[i], f[i])
    for i in range(I):
        for j in range(J): objective.SetCoefficient(x[i][j], c[i][j])
    objective.SetMinimization()

    solver.SetTimeLimit(time_limit * 1000)
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        return {
            "status": "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE",
            "objective": solver.Objective().Value(),
            "time": solver.wall_time() / 1000.0,
            "opened_facilities": sum(1 for i in range(I) if y[i].solution_value() > 0.5)
        }
    return {"status": "INFEASIBLE" if status == pywraplp.Solver.INFEASIBLE else "FAILED", "objective": None, "time": None, "opened_facilities": 0}

if __name__ == "__main__":
    # Tự động sinh danh sách TOÀN BỘ 40 file đã tải
    test_files = []
    for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
        for j in range(1, 5):
            test_files.append(f"cap{i}{j}.txt")
    test_files.append("cap51.txt")
    test_files.extend(["capa.txt", "capb.txt", "capc.txt"])

    results_file = "baselines_milp_full.csv"
    print(f"Bắt đầu chạy thực nghiệm {len(test_files)} file. Kết quả lưu vào {results_file}...")
    print("Lưu ý: Có Time Limit là 60 giây/file. Quá 60s máy sẽ tự bỏ qua để tránh treo.")
    print("-" * 60)

    with open(results_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        # Thêm cột Ghi chú để dễ theo dõi
        writer.writerow(["File", "Status", "Objective (Baseline)", "Time (s)", "Facilities Opened", "Note"])

        for filename in test_files:
            print(f"Đang giải {filename:<12}...", end=" ", flush=True)
            path = os.path.join("data", filename)
            data = parse_cap_file(path)
            
            if data:
                # Gọi hàm giải MILP với giới hạn thời gian 60 giây (bạn có thể tăng lên nếu muốn)
                res = solve_for_baseline(data, time_limit=60)
                
                note = ""
                if res['status'] == "INFEASIBLE":
                    note = "Vô nghiệm do sức chứa quá gắt"
                elif res['status'] == "FEASIBLE" and res['time'] >= 60:
                    note = "Chạm Time Limit, chưa chắc là tối ưu nhất"
                    
                writer.writerow([filename, res['status'], res['objective'], f"{res['time']:.4f}" if res['time'] else "N/A", res['opened_facilities'], note])
                print(f"[{res['status']}] Obj: {res['objective']} ({res['time']}s) {note}")
            else:
                print("Lỗi đọc file.")

    print("\n" + "=" * 60)
    print(f"Hoàn tất! Hãy mở file {results_file} để xem bảng tổng hợp toàn bộ.")
