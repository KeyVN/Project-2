import os

def parse_cap_file(filepath):
    """
    Đọc file dữ liệu Capacitated Facility Location từ OR-Library
    và trả về một dictionary chứa các tham số đã được parse.
    """
    if not os.path.exists(filepath):
        print(f"Lỗi: Không tìm thấy file {filepath}")
        return None

    with open(filepath, 'r') as file:
        data = file.read().split()
        
    if not data:
        return None

    iterator = iter(data)

    try:
        num_facilities = int(next(iterator)) # |I|
        num_customers = int(next(iterator))  # |J|

        capacities = []   # s_i
        fixed_costs = []  # f_i
        demands = []      # d_j
        
        temp_cost_matrix = [] 

        for _ in range(num_facilities):
            capacities.append(float(next(iterator)))
            fixed_costs.append(float(next(iterator)))

        for _ in range(num_customers):
            demands.append(float(next(iterator)))
            
            customer_costs = []
            for _ in range(num_facilities):
                customer_costs.append(float(next(iterator)))
            
            temp_cost_matrix.append(customer_costs)

        cost_matrix = [
            [temp_cost_matrix[j][i] for j in range(num_customers)]
            for i in range(num_facilities)
        ]

        return {
            "num_facilities": num_facilities,
            "num_customers": num_customers,
            "capacities": capacities,
            "fixed_costs": fixed_costs,
            "demands": demands,
            "cost_matrix": cost_matrix
        }

    except StopIteration:
        print("Lỗi: Dữ liệu trong file bị thiếu so với cấu trúc chuẩn.")
        return None
    except ValueError as e:
        print(f"Lỗi định dạng số liệu: {e}")
        return None

# ==========================================
# KHỐI LỆNH KIỂM TRA (TEST SCRIPT)
# ==========================================
if __name__ == "__main__":
    test_filepath = os.path.join("data", "cap71.txt")
    
    parsed_data = parse_cap_file(test_filepath)
    
    if parsed_data:
        print(f"Đọc thành công file: {test_filepath}\n")
        print(f"Số lượng cơ sở ứng viên (I): {parsed_data['num_facilities']}")
        print(f"Số lượng khách hàng (J)    : {parsed_data['num_customers']}")
        print("-" * 50)
        
        # In thử thông tin của 3 cơ sở đầu tiên
        print("Thông tin 3 cơ sở đầu tiên:")
        for i in range(3):
            print(f"  Cơ sở {i}: Sức chứa = {parsed_data['capacities'][i]}, Chi phí mở = {parsed_data['fixed_costs'][i]}")
            
        print("-" * 50)
        
        # In thử nhu cầu của 3 khách hàng đầu tiên
        print("Nhu cầu của 3 khách hàng đầu tiên:")
        for j in range(3):
            print(f"  Khách hàng {j}: Nhu cầu = {parsed_data['demands'][j]}")
            
        print("-" * 50)
        
        # In thử chi phí từ cơ sở 0 đến 3 khách hàng đầu tiên
        print("Chi phí c[i][j] từ Cơ sở 0 đến Khách hàng 0, 1, 2:")
        for j in range(3):
            print(f"  c[0][{j}] = {parsed_data['cost_matrix'][0][j]}")