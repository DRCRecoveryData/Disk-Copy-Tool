import os
import re
from concurrent.futures import ThreadPoolExecutor
from itertools import count

# Global thread-safe counter
file_counter = count(1)

def carve_jpeg(file_path):
    """Carves JPEGs from a given file."""
    pattern_ffe1 = re.compile(b'\xFF\xD8\xFF\xE1..\x45\x78\x69\x66')
    pattern_ffe0 = re.compile(b'\xFF\xD8\xFF\xE0')
    
    output_dir = 'Carved'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    start_positions = [m.start() for m in pattern_ffe1.finditer(data)]
    other_positions = [m.start() for m in pattern_ffe0.finditer(data)]
    all_positions = sorted(set(start_positions + other_positions))
    
    carved_files = []
    for i, start in enumerate(all_positions):
        end = all_positions[i + 1] if i + 1 < len(all_positions) else len(data)
        jpeg_data = data[start:end]
        
        # Get a unique number for each file
        file_number = next(file_counter)
        output_filename = os.path.join(output_dir, f"{file_number:04d}.JPG")
        
        with open(output_filename, 'wb') as out_file:
            out_file.write(jpeg_data)
        carved_files.append(output_filename)
        print(f"Carved: {output_filename}")

def main():
    file_path = input("Enter the path of the image file: ").strip()
    if os.path.isfile(file_path):
        carve_jpeg(file_path)
    else:
        print("File not found.")

if __name__ == "__main__":
    main()
