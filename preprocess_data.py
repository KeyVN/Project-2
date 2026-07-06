import os
import shutil
from readfile import parse_cap_file

def preprocess_large_demands(data):
    """
    Chia nhỏ các customer có demand lớn hơn max capacity của bất kỳ facility nào.
    Demand quá lớn sẽ bị chia 10 cho đến khi vừa ít nhất 1 kho.
    
    Returns: preprocessed data with split customers
    """
    I = data['num_facilities']
    J = data['num_customers']
    f = data['fixed_costs']
    s = data['capacities']
    d = data['demands']
    c = data['cost_matrix']
    
    max_capacity = max(s)
    
    new_demands = []
    new_cost_columns = [[] for _ in range(I)]  # cost_matrix[i][j] for each facility
    
    split_count = 0
    
    for j in range(J):
        original_demand = d[j]
        
        if original_demand <= max_capacity:
            # Demand vừa, giữ nguyên
            new_demands.append(original_demand)
            for i in range(I):
                new_cost_columns[i].append(c[i][j])
        else:
            # Demand quá lớn, chia nhỏ
            remaining = original_demand
            parts = []
            
            while remaining > max_capacity:
                # Chia 10
                part = remaining / 10.0
                parts.append(part)
                remaining = part
            
            # Phần cuối cùng
            parts.append(remaining)
            
            split_count += 1
            print(f"  Customer {j}: demand {original_demand:.2f} > max_capacity {max_capacity:.2f}")
            print(f"    -> Split into {len(parts)} parts: {[f'{p:.2f}' for p in parts]}")
            
            # Thêm từng phần vào data mới
            for part_demand in parts:
                new_demands.append(part_demand)
                for i in range(I):
                    new_cost_columns[i].append(c[i][j])  # Giữ nguyên cost
    
    # Rebuild cost_matrix
    new_cost_matrix = new_cost_columns
    
    return {
        "num_facilities": I,
        "num_customers": len(new_demands),
        "capacities": s,
        "fixed_costs": f,
        "demands": new_demands,
        "cost_matrix": new_cost_matrix
    }, split_count


def write_cap_file(filepath, data):
    I = data['num_facilities']
    J = data['num_customers']
    s = data['capacities']
    f = data['fixed_costs']
    d = data['demands']
    c = data['cost_matrix']
    
    with open(filepath, 'w', encoding='utf-8') as file:
        # Header: I J
        file.write(f"{I} {J}\n")
        
        # Facilities: capacity fixed_cost
        for i in range(I):
            file.write(f"{s[i]} {f[i]}\n")
        
        # Customers: demand + costs to all facilities
        for j in range(J):
            file.write(f"{d[j]}\n")
            for i in range(I):
                file.write(f"{c[i][j]} ")
            file.write("\n")


if __name__ == "__main__":
    # Tạo folder output
    output_dir = "data_preprocessed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created folder: {output_dir}\n")
    
    # Danh sách file test
    test_files = []
    for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
        for j in range(1, 5):
            test_files.append(f"cap{i}{j}.txt")
    test_files.append("cap51.txt")
    
    print(f"Processing {len(test_files)} files...")
    print("=" * 60)
    
    processed_count = 0
    split_files = []
    
    for filename in test_files:
        path = os.path.join("data", filename)
        data = parse_cap_file(path)
        
        if not data:
            print(f"[ERROR] {filename}: Cannot read file")
            continue
        
        max_capacity = max(data['capacities'])
        max_demand = max(data['demands'])
        
        if max_demand <= max_capacity:
            # Không cần xử lý, copy nguyên file
            output_path = os.path.join(output_dir, filename)
            shutil.copy2(path, output_path)
            print(f"[COPY] {filename}: max_demand={max_demand:.2f} <= max_capacity={max_capacity:.2f}")
        else:
            # Cần chia nhỏ demand
            print(f"[SPLIT] {filename}: max_demand={max_demand:.2f} > max_capacity={max_capacity:.2f}")
            preprocessed_data, split_count = preprocess_large_demands(data)
            
            output_path = os.path.join(output_dir, filename)
            write_cap_file(output_path, preprocessed_data)
            
            print(f"  -> Split {split_count} customers, new total customers: {preprocessed_data['num_customers']}")
            split_files.append(filename)
            processed_count += 1
        
        print()
    
    print("=" * 60)
    print(f"Completed! Processed {processed_count} files with splits.")
    if split_files:
        print(f"Files with splits: {', '.join(split_files)}")
    print(f"\nPreprocessed data saved to: {output_dir}/")
