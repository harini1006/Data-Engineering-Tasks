import os
import json
import re

def run_ingestion(input_dir, output_file):
    combined_data = []
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} not found.")
        return

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            
            # Extract page number from filename (e.g., data_page_1.json)
            page_match = re.search(r'page_(\d+)', filename)
            page_num = int(page_match.group(1)) if page_match else "Unknown"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for record in data:
                        record['page'] = page_num # Add page metadata
                        combined_data.append(record)
            except Exception as e:
                print(f"Skipping corrupted file {filename}: {e}") # Graceful error handling

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4)
    
    print(f"Successfully ingested {len(combined_data)} records into {output_file}.")