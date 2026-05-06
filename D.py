import os
import urllib.request

os.makedirs("data", exist_ok=True)

base_url = "https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/"

file_names = []

for i in [4, 6, 7, 8, 9, 10, 11, 12, 13]:
    for j in range(1, 5):
        file_names.append(f"cap{i}{j}")

file_names.append("cap51")

file_names.extend(["capa", "capb", "capc"])

file_names.sort()

print(f"Bắt đầu tải tổng cộng {len(file_names)} file dữ liệu từ OR-Library...")

for file_name in file_names:
    url = f"{base_url}{file_name}.txt"
    output_path = os.path.join("data", f"{file_name}.txt") 
    
    try:
        print(f"Đang tải {file_name}...")
        urllib.request.urlretrieve(url, output_path)
        print(f"  -> Thành công")
    except Exception as e:
        print(f"  -> Lỗi khi tải {file_name}: {e}")

print("\nHoàn tất quá trình tải toàn bộ dữ liệu! Bạn có thể kiểm tra trong thư mục 'data'.")