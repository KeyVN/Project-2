import os
from readfile import parse_cap_file

def diagnose_data(filename):
    filepath = os.path.join("data", filename)
    data = parse_cap_file(filepath)
    if not data: return

    I = data['num_facilities']
    J = data['num_customers']
    s = data['capacities']
    d = data['demands']

    max_demand = max(d)
    max_capacity = max(s)
    total_demand = sum(d)
    total_capacity = sum(s)

    print(f"--- PHÂN TÍCH FILE: {filename} ---")
    print(f"1. Tổng nhu cầu: {total_demand:.0f}")
    print(f"2. Tổng sức chứa: {total_capacity:.0f}")
    print(f"3. Nhu cầu lớn nhất của 1 khách: {max_demand:.0f}")
    print(f"4. Sức chứa lớn nhất của 1 kho:   {max_capacity:.0f}")
    
    # Kiểm tra điều kiện cần tối thiểu
    if max_demand > max_capacity:
        print("\n=> KẾT LUẬN: Vô nghiệm chắc chắn! Có khách hàng cần nhiều hàng hơn cả sức chứa của kho lớn nhất.")
    
    # Kiểm tra tỷ lệ dư thừa
    ratio = total_capacity / total_demand
    print(f"5. Tỷ lệ Sức chứa/Nhu cầu: {ratio:.2f}")
    if ratio < 1.1:
        print("=> CẢNH BÁO: Tỷ lệ quá thấp (<1.1). Cực kỳ khó để giải bài toán Single-Source vì thiếu không gian xoay sở.")

if __name__ == "__main__":
    diagnose_data("cap41.txt")
    print("\n")
    diagnose_data("cap71.txt") # So sánh với file có nghiệm