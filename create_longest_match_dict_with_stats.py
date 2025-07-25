#!/usr/bin/env python3
import sys
from collections import defaultdict

def extract_substrings(line, min_length=3, max_length=50):
    """Extract all possible substrings from a line within specified length range"""
    substrings = set()  # Use set to avoid duplicate substrings in the same line
    line_length = len(line)
    
    for start in range(line_length):
        # Limit end index to prevent overly long substrings
        max_end = min(start + max_length, line_length)
        for end in range(start + min_length, max_end + 1):
            substr = line[start:end]
            substrings.add(substr)
    
    return substrings

def build_enhanced_dict(file_path, max_lines=1000):
    """
    Build a dictionary with longest substrings, including length and frequency
    from first N lines of a file
    """
    # Track all substrings with their frequencies
    substring_stats = defaultdict(lambda: {'count': 0, 'length': 0})
    # Track longest substring for each starting key
    longest_substrings = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = 0
            for line in f:
                if line_count >= max_lines:
                    break
                    
                cleaned_line = line.strip()
                if not cleaned_line:
                    line_count += 1
                    continue
                
                # Extract all meaningful substrings from the line
                substrings = extract_substrings(cleaned_line)
                
                # Update statistics for each substring
                for substr in substrings:
                    # Update global frequency and length stats
                    if len(substr) > substring_stats[substr]['length']:
                        substring_stats[substr]['length'] = len(substr)
                    substring_stats[substr]['count'] += 1
                    
                    # Create grouping key (first 2 characters)
                    key = substr[:2] if len(substr) >= 2 else substr
                    
                    # Update longest substring for this key
                    if key not in longest_substrings or len(substr) > len(longest_substrings[key]):
                        longest_substrings[key] = substr
                
                line_count += 1
                if line_count % 100 == 0:
                    print(f"Processed {line_count} lines...")
        
        print(f"Successfully processed {line_count} lines")
        
        # Create final dictionary with all stats
        final_dict = {}
        for key, longest_sub in longest_substrings.items():
            stats = substring_stats[longest_sub]
            final_dict[key] = {
                'substring': longest_sub,
                'length': stats['length'],
                'frequency': stats['count']
            }
        
        return final_dict
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error building dictionary: {str(e)}")
        sys.exit(1)

def save_enhanced_dict(enhanced_dict, output_file):
    """Save dictionary with length and frequency information"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Sort by length (descending) then frequency (descending)
            sorted_items = sorted(enhanced_dict.items(), 
                                key=lambda x: (-x[1]['length'], -x[1]['frequency']))
            
            f.write(f"{'Key':<10} | {'Substring':<60} | Length | Frequency\n")
            f.write("-" * 100 + "\n")
            
            for key, data in sorted_items:
                f.write(f"{key:<10} | {data['substring'][:57] + '...' if len(data['substring'])>60 else data['substring']:<60} | {data['length']:<6} | {data['frequency']}\n")
        
        print(f"Enhanced dictionary saved to {output_file}")
        print(f"Dictionary contains {len(enhanced_dict)} entries")
        
    except Exception as e:
        print(f"Error saving dictionary: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./create_longest_match_dict_with_stats.py <input_sorted_file> <output_dict_file>")
        print("Example: ./create_longest_match_dict_with_stats.py sorted_logs.txt enhanced_matches.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("Building enhanced dictionary with length and frequency stats...")
    enhanced_dict = build_enhanced_dict(input_file, max_lines=1000)
    
    save_enhanced_dict(enhanced_dict, output_file)

if __name__ == "__main__":
    main()
