"""
run_all_unified.py
==================
Chay tat ca thuat toan va merge ket qua vao file thong nhat

Usage: python run_all_unified.py
"""

import os
import csv
from pathlib import Path
from readfile import parse_cap_file
from run_experiments import solve_for_baseline
from greedy1 import solve_greedy_1
from greedy2 import solve_greedy_2
from greedy2m1 import move1_reassignment, build_greedy_2_solution as build_m1
from greedy2m2 import move2_close_facility, build_greedy_2_solution as build_m2
from greedy2m3 import move3_local_search, build_greedy_2_solution as build_m3
from greedy2m4 import move4_swap, build_greedy_2_solution as build_m4
from greedy2m5 import move5_customer_swap, build_greedy_2_solution as build_m5
from greedy2_vnd import vnd_all_moves, build_greedy_2_solution as build_vnd
from greedy2_vnd4 import vnd_all_moves as vnd4_all_moves, build_greedy_2_solution as build_vnd4
from greedy2_vnd3 import vnd_all_moves as vnd3_all_moves, build_greedy_2_solution as build_vnd3

def run_all_algorithms():
    """Chay tat ca thuat toan va luu ket qua voi format thong nhat"""
    
    test_files = [f"cap{i}{j}.txt" for i in [4,6,7,8,9,10,11,12,13] for j in range(1,5)] + ["cap51.txt"]
    input_dir = "data_preprocessed"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Danh sach thuat toan: (ten, file_output, ham_chinh, ham_khoi_tao)
    algorithms = [
        ("MILP", "baselines_milp.csv", solve_for_baseline, None),
        ("Greedy1", "results_greedy1.csv", solve_greedy_1, None),
        ("Greedy2", "results_greedy2.csv", solve_greedy_2, None),
        ("Move1", "results_greedy2m1.csv", move1_reassignment, build_m1),
        ("Move2", "results_greedy2m2.csv", move2_close_facility, build_m2),
        ("Move3", "results_greedy2m3.csv", move3_local_search, build_m3),
        ("Move4", "results_greedy2m4.csv", move4_swap, build_m4),
        ("Move5", "results_greedy2m5.csv", move5_customer_swap, build_m5),
        ("VND3", "results_greedy2_vnd3.csv", vnd3_all_moves, build_vnd3),
        ("VND4", "results_greedy2_vnd4.csv", vnd4_all_moves, build_vnd4),
        ("VND", "results_greedy2_vnd.csv", vnd_all_moves, build_vnd),
    ]
    
    # Chay tung thuat toan
    for method_name, output_file, solver_func, init_func in algorithms:
        print(f"\n{'='*60}")
        print(f"Running {method_name}...")
        print(f"{'='*60}")
        
        out_path = os.path.join(output_dir, output_file)
        
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["File", "Status", "Objective (Baseline)", "Time (s)", "Facilities Opened", "Note"])
            
            for fn in test_files:
                print(f"  {fn:<12}...", end=" ", flush=True)
                data = parse_cap_file(os.path.join(input_dir, fn))
                
                if not data:
                    w.writerow([fn, "ERROR", "N/A", "N/A", "0", method_name])
                    print("ERROR (parse)")
                    continue
                
                try:
                    if method_name == "MILP":
                        res = solver_func(data, time_limit=60)
                    elif init_func:
                        # Move1/2/3/4/5/VND can Greedy2 truoc
                        init_sol = init_func(data)
                        if not init_sol:
                            w.writerow([fn, "ERROR", "N/A", "N/A", "0", method_name])
                            print("ERROR (init)")
                            continue
                        res = solver_func(data, init_sol)
                    else:
                        # Greedy1, Greedy2
                        res = solver_func(data)
                    
                    if res:
                        obj_val = res.get('objective', 'N/A')
                        time_val = res.get('time', 0)
                        fac_val = res.get('opened_facilities', 0)
                        status = res.get('status', 'FEASIBLE')
                        
                        # Format objective value
                        if obj_val != 'N/A':
                            obj_str = f"{obj_val:.4f}"
                        else:
                            obj_str = "N/A"
                            status = "INFEASIBLE"
                        
                        w.writerow([fn, status, obj_str, f"{time_val:.4f}", fac_val, method_name])
                        print(f"[{status}] Obj={obj_str} Time={time_val:.4f}s")
                    else:
                        w.writerow([fn, "ERROR", "N/A", "N/A", "0", method_name])
                        print("ERROR (solve)")
                except Exception as e:
                    w.writerow([fn, "ERROR", "N/A", "N/A", "0", method_name])
                    print(f"ERROR ({str(e)[:30]})")
        
        print(f"[OK] Saved {out_path}")
    
    # Merge tat ca ket qua vao mot file
    print(f"\n{'='*60}")
    print("Merging all results...")
    print(f"{'='*60}")
    
    merge_results(output_dir, test_files, algorithms)
    print("[OK] Merge complete!")

def merge_results(output_dir, test_files, algorithms):
    """Merge tat ca ket qua thanh mot file thong nhat"""
    
    merged_file = os.path.join(output_dir, "results_all_unified.csv")
    
    # Doc ket qua tu tat ca file
    all_results = {}  # {filename: {method: {obj, time, facilities, status}}}
    
    for method_name, output_file, _, _ in algorithms:
        file_path = os.path.join(output_dir, output_file)
        
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fn = row['File']
                if fn not in all_results:
                    all_results[fn] = {}
                
                all_results[fn][method_name] = {
                    'objective': row['Objective (Baseline)'],
                    'time': row['Time (s)'],
                    'facilities': row['Facilities Opened'],
                    'status': row['Status'],
                }
    
    # Viet file merged
    method_names = [m[0] for m in algorithms]
    
    with open(merged_file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        
        # Header
        header = ["File"]
        for method in method_names:
            header.extend([f"{method}_Obj", f"{method}_Time", f"{method}_Fac", f"{method}_Status"])
        w.writerow(header)
        
        # Du lieu
        for fn in test_files:
            row = [fn]
            if fn in all_results:
                for method in method_names:
                    if method in all_results[fn]:
                        res = all_results[fn][method]
                        row.extend([
                            res['objective'],
                            res['time'],
                            res['facilities'],
                            res['status']
                        ])
                    else:
                        row.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            else:
                for _ in method_names:
                    row.extend(['N/A', 'N/A', 'N/A', 'N/A'])
            
            w.writerow(row)
    
    print(f"[OK] Merged results saved to {merged_file}")

if __name__ == "__main__":
    run_all_algorithms()
