#!/usr/bin/env python3
import sys
import string

def levenshtein_distance(s1, s2):
    """Pure Python implementation of Levenshtein distance"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def clean_line(line):
    """Clean a single line by removing non-printable characters"""
    printable = set(string.printable)
    return ''.join([c if c in printable else '?' for c in line])

def process_batch(batch, batch_num, output_file):
    """Process a single batch: sort and append to output file"""
    if not batch:
        return
    
    # Use first line of batch as reference for this batch
    base_line = batch[0]
    
    # Calculate distances and sort
    batch_with_distance = []
    for line in batch:
        distance = levenshtein_distance(base_line, line)
        batch_with_distance.append((distance, line))
    
    # Sort by distance
    batch_with_distance.sort(key=lambda x: x[0])
    sorted_batch = [item[1] for item in batch_with_distance]
    
    # Append to output file
    mode = 'a' if batch_num > 0 else 'w'  # Overwrite for first batch, append for others
    with open(output_file, mode, encoding='utf-8') as f:
        for line in sorted_batch:
            f.write(line + '\n')
    
    print(f"Processed batch {batch_num + 1} with {len(batch)} lines")

def read_and_process_in_batches(input_file, output_file, batch_size=1000):
    """Read file in batches, process each, and output results"""
    try:
        batch = []
        batch_num = 0
        printable = set(string.printable)
        
        with open(input_file, 'rb') as file:
            for byte_line in file:
                # Decode line with error handling
                line = byte_line.decode('utf-8', errors='replace')
                # Clean non-printable characters
                cleaned_line = clean_line(line).strip()
                
                if cleaned_line:  # Only add non-empty lines
                    batch.append(cleaned_line)
                
                # Process batch when it reaches desired size
                if len(batch) >= batch_size:
                    process_batch(batch, batch_num, output_file)
                    batch = []
                    batch_num += 1
        
        # Process remaining lines in last batch
        if batch:
            process_batch(batch, batch_num, output_file)
        
        print(f"All batches processed. Results saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./sort_log_by_edit_distance_batch.py <input_log_file> <output_file>")
        print("Example: ./sort_log_by_edit_distance_batch.py logs.txt sorted_logs.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    batch_size = 1000  # Number of lines per batch
    
    print(f"Starting batch processing with batch size: {batch_size} lines")
    read_and_process_in_batches(input_file, output_file, batch_size)

if __name__ == "__main__":
    main()
