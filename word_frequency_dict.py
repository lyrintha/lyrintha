#!/usr/bin/env python3
import sys
import re
from collections import defaultdict

def extract_words(line):
    """Extract words from a line using regex optimized for log files"""
    # Pattern captures sequences with letters, numbers, and common log symbols
    word_pattern = re.compile(r"[\w\-:/=']+")
    return word_pattern.findall(line)

def build_word_frequency_dict(file_path, max_lines=1000):
    """Build a dictionary of words with their frequencies from first N lines"""
    word_counts = defaultdict(int)
    total_words = 0
    
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
                
                # Extract and count words
                words = extract_words(cleaned_line)
                total_words += len(words)
                
                for word in words:
                    normalized_word = word.lower()  # Case normalization
                    word_counts[normalized_word] += 1
                
                line_count += 1
                if line_count % 100 == 0:
                    print(f"Processed {line_count} lines...")
        
        print(f"Successfully processed {line_count} lines")
        print(f"Total words extracted: {total_words}")
        
        return word_counts
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error building word frequency dictionary: {str(e)}")
        sys.exit(1)

def save_word_frequency_dict(frequency_dict, output_file):
    """Save word frequency dictionary with sorting by frequency, then length (descending)"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Sort priority: 
            # 1. Frequency (descending)
            # 2. Word length (descending)
            # 3. Alphabetical order (ascending) for final tiebreaker
            sorted_words = sorted(
                frequency_dict.items(),
                key=lambda x: (-x[1], -len(x[0]), x[0])
            )
            
            total = sum(count for _, count in sorted_words)
            
            f.write(f"{'Rank':<6} | {'Word':<30} | Length | Frequency | Percentage\n")
            f.write("-" * 100 + "\n")
            
            for rank, (word, count) in enumerate(sorted_words, 1):
                word_length = len(word)
                percentage = (count / total) * 100 if total > 0 else 0
                f.write(
                    f"{rank:<6} | {word[:27] + '...' if len(word)>30 else word:<30} | "
                    f"{word_length:<6} | {count:<9} | {percentage:.2f}%\n"
                )
        
        print(f"Word frequency dictionary saved to {output_file}")
        print(f"Unique words found: {len(frequency_dict)}")
        
    except Exception as e:
        print(f"Error saving dictionary: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./word_frequency_dict.py <input_file> <output_dict_file>")
        print("Example: ./word_frequency_dict.py sorted_logs.txt word_frequencies.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print("Building word frequency dictionary from first 1000 lines...")
    frequency_dict = build_word_frequency_dict(input_file, max_lines=10000)
    
    save_word_frequency_dict(frequency_dict, output_file)

if __name__ == "__main__":
    main()
