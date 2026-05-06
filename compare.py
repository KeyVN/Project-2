import csv
import os

def load_results(filename):
    results = {}
    if not os.path.exists(filename):
        return results
    with open(filename, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results[row['File']] = row
    return results

def compare_algorithms():
    g1_data = load_results('results_greedy1_opt.csv')
    g2_data = load_results('results_greedy2.csv')

    all_files = sorted(list(set(list(g1_data.keys()) + list(g2_data.keys()))))
    
    output_file = 'greedy_comparison_report.csv'
    
    print(f"{'File':<12} | {'Greedy 1 Opt':<15} | {'Greedy 2':<15} | {'Better Alg':<12} | {'Gap (%)'}")
    print("-" * 70)

    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File", "G1 Objective", "G1 Time", "G1 Fac", "G2 Objective", "G2 Time", "G2 Fac", "Winner", "Diff (%)"])

        for file in all_files:
            g1 = g1_data.get(file, {})
            g2 = g2_data.get(file, {})

            obj1_str = g1.get('Objective', 'INFEASIBLE')
            obj2_str = g2.get('Objective', 'INFEASIBLE')

            # Xử lý Infeasible
            if obj1_str == 'INFEASIBLE' and obj2_str == 'INFEASIBLE':
                writer.writerow([file, "INF", "-", "-", "INF", "-", "-", "TIE", "-"])
                print(f"{file:<12} | {'INF':<15} | {'INF':<15} | {'TIE':<12} | -")
                continue
            
            # Nếu 1 trong 2 Infeasible
            if obj1_str == 'INFEASIBLE':
                writer.writerow([file, "INF", "-", "-", obj2_str, g2['Time (s)'], g2['Facilities'], "Greedy 2", "-"])
                print(f"{file:<12} | {'INF':<15} | {float(obj2_str):<15.2f} | {'Greedy 2':<12} | -")
                continue
            if obj2_str == 'INFEASIBLE':
                writer.writerow([file, obj1_str, g1['Time (s)'], g1['Facilities'], "INF", "-", "-", "Greedy 1", "-"])
                print(f"{file:<12} | {float(obj1_str):<15.2f} | {'INF':<15} | {'Greedy 1':<12} | -")
                continue

            # So sánh khi cả 2 đều có nghiệm
            obj1 = float(obj1_str)
            obj2 = float(obj2_str)
            
            winner = "Greedy 1" if obj1 < obj2 else "Greedy 2"
            
            # Tính % lệch giữa cái tốt hơn và cái tệ hơn
            if winner == "Greedy 2":
                gap = ((obj1 - obj2) / obj2) * 100
            else:
                gap = ((obj2 - obj1) / obj1) * 100

            writer.writerow([file, obj1, g1['Time (s)'], g1['Facilities'], obj2, g2['Time (s)'], g2['Facilities'], winner, f"{gap:.2f}%"])
            print(f"{file:<12} | {obj1:<15.2f} | {obj2:<15.2f} | {winner:<12} | {gap:.2f}%")

    print(f"\n=> Đã lưu báo cáo so sánh chi tiết tại: {output_file}")

if __name__ == "__main__":
    compare_algorithms()