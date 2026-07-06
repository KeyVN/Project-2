import os

def parse_cap_file(filepath):
    """
    Read Capacitated Facility Location data.
    Supports:
    - standard OR-Library format (with fixed_costs)
    - variant format with only capacities (capa/capb/capc style)
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return None

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        raw = file.read().replace('\n', ' ').split()

    if not raw:
        return None

    # Extract only numeric tokens
    tokens = []
    for word in raw:
        try:
            tokens.append(float(word))
        except ValueError:
            continue

    if len(tokens) < 2:
        print(f"Error: No numeric data found in {filepath}")
        return None

    try:
        idx = 0
        num_facilities = int(tokens[idx]); idx += 1
        num_customers = int(tokens[idx]); idx += 1

        capacities = []
        fixed_costs = []
        demands = []
        temp_cost_matrix = []

        # Try standard format first (with fixed_costs)
        needed_standard = 2 + 2 * num_facilities + num_customers * (1 + num_facilities)
        
        # Try variant format (without fixed_costs, only capacities)
        needed_variant = 2 + num_facilities + num_customers * (1 + num_facilities)

        if len(tokens) >= needed_standard:
            # Standard format
            for _ in range(num_facilities):
                capacities.append(tokens[idx]); idx += 1
                fixed_costs.append(tokens[idx]); idx += 1

            for _ in range(num_customers):
                demands.append(tokens[idx]); idx += 1
                customer_costs = []
                for _ in range(num_facilities):
                    customer_costs.append(tokens[idx]); idx += 1
                temp_cost_matrix.append(customer_costs)

        elif len(tokens) >= needed_variant:
            # Variant format (no fixed_costs) - assign default fixed_costs
            for _ in range(num_facilities):
                capacities.append(tokens[idx]); idx += 1
                fixed_costs.append(100.0)  # Default fixed cost

            for _ in range(num_customers):
                demands.append(tokens[idx]); idx += 1
                customer_costs = []
                for _ in range(num_facilities):
                    customer_costs.append(tokens[idx]); idx += 1
                temp_cost_matrix.append(customer_costs)
        else:
            print(f"Error: Expected at least {needed_variant} tokens, got {len(tokens)}")
            return None

        cost_matrix = [[temp_cost_matrix[j][i] for j in range(num_customers)] for i in range(num_facilities)]

        return {
            "num_facilities": num_facilities,
            "num_customers": num_customers,
            "capacities": capacities,
            "fixed_costs": fixed_costs,
            "demands": demands,
            "cost_matrix": cost_matrix
        }

    except (IndexError, ValueError) as e:
        print(f"Error: Data parsing failed - {e}")
        return None


if __name__ == "__main__":
    test_filepath = os.path.join("data", "cap71.txt")
    
    parsed_data = parse_cap_file(test_filepath)
    
    if parsed_data:
        print(f"Successfully read file: {test_filepath}\n")
        print(f"Number of facilities (I): {parsed_data['num_facilities']}")
        print(f"Number of customers (J): {parsed_data['num_customers']}")
        print("-" * 50)
        
        print("First 3 facilities info:")
        for i in range(3):
            print(f"  Facility {i}: Capacity = {parsed_data['capacities'][i]}, Fixed cost = {parsed_data['fixed_costs'][i]}")
            
        print("-" * 50)
        
        print("First 3 customers demand:")
        for j in range(3):
            print(f"  Customer {j}: Demand = {parsed_data['demands'][j]}")
            
        print("-" * 50)
        
        print("Cost c[i][j] from Facility 0 to Customer 0, 1, 2:")
        for j in range(3):
            print(f"  c[0][{j}] = {parsed_data['cost_matrix'][0][j]}")
