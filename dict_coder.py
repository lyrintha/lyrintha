#!/usr/bin/env python3
import sys
import pickle
import os
from collections import defaultdict

class DictionaryCoder:
    def __init__(self, dict_path=None):
        self.word_to_id = {}  # Word to integer mapping
        self.id_to_word = {}  # Integer to word mapping
        self.next_id = 0
        if dict_path:
            self.load_dictionary(dict_path)

    def load_dictionary(self, dict_path):
        """Load word frequency dictionary and create mappings"""
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                # Skip header lines
                next(f)  # Skip column names
                next(f)  # Skip separator line
                
                for line in f:
                    # Parse line (rank | word | length | frequency | percentage)
                    parts = line.strip().split('|')
                    if len(parts) < 2:
                        continue
                        
                    word = parts[1].strip()
                    # Remove ellipsis added for long words
                    if word.endswith('...'):
                        word = word[:-3]
                        
                    if word not in self.word_to_id:
                        self.word_to_id[word] = self.next_id
                        self.id_to_word[self.next_id] = word
                        self.next_id += 1
            
            print(f"Loaded dictionary with {len(self.word_to_id)} entries")
        except Exception as e:
            print(f"Error loading dictionary: {str(e)}")
            sys.exit(1)

    def save_mappings(self, output_dir):
        """Save word-id mappings for decoding"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, 'word_to_id.pkl'), 'wb') as f:
                pickle.dump(self.word_to_id, f)
            with open(os.path.join(output_dir, 'id_to_word.pkl'), 'wb') as f:
                pickle.dump(self.id_to_word, f)
            print(f"Saved mappings to {output_dir}")
        except Exception as e:
            print(f"Error saving mappings: {str(e)}")
            sys.exit(1)

    def load_mappings(self, mappings_dir):
        """Load word-id mappings for decoding"""
        try:
            with open(os.path.join(mappings_dir, 'word_to_id.pkl'), 'rb') as f:
                self.word_to_id = pickle.load(f)
            with open(os.path.join(mappings_dir, 'id_to_word.pkl'), 'rb') as f:
                self.id_to_word = pickle.load(f)
            self.next_id = len(self.word_to_id)
            print(f"Loaded mappings with {len(self.word_to_id)} entries")
        except Exception as e:
            print(f"Error loading mappings: {str(e)}")
            sys.exit(1)

    def encode(self, input_file, output_file):
        """Encode a file using the dictionary"""
        try:
            with open(input_file, 'r', encoding='utf-8') as in_f, \
                 open(output_file, 'w', encoding='utf-8') as out_f:
                
                for line in in_f:
                    # Simple tokenization - split on whitespace
                    words = line.strip().split()
                    encoded_line = []
                    
                    for word in words:
                        # Convert to lowercase to match dictionary
                        normalized_word = word.lower()
                        # Use word if exists in dictionary, otherwise use special token 'UNK'
                        if normalized_word in self.word_to_id:
                            encoded_line.append(str(self.word_to_id[normalized_word]))
                        else:
                            # Assign ID for unknown words if not already assigned
                            if 'unk' not in self.word_to_id:
                                self.word_to_id['unk'] = self.next_id
                                self.id_to_word[self.next_id] = 'unk'
                                self.next_id += 1
                            encoded_line.append(str(self.word_to_id['unk']))
                    
                    # Join with spaces to preserve line structure
                    out_f.write(' '.join(encoded_line) + '\n')
            
            print(f"File encoded successfully to {output_file}")
        except Exception as e:
            print(f"Error encoding file: {str(e)}")
            sys.exit(1)

    def decode(self, input_file, output_file):
        """Decode an encoded file using the dictionary"""
        try:
            with open(input_file, 'r', encoding='utf-8') as in_f, \
                 open(output_file, 'w', encoding='utf-8') as out_f:
                
                for line in in_f:
                    # Convert IDs back to words
                    ids = line.strip().split()
                    decoded_line = []
                    
                    for id_str in ids:
                        try:
                            word_id = int(id_str)
                            decoded_line.append(self.id_to_word.get(word_id, 'unk'))
                        except ValueError:
                            decoded_line.append('unk')  # Handle invalid IDs
                    
                    out_f.write(' '.join(decoded_line) + '\n')
            
            print(f"File decoded successfully to {output_file}")
        except Exception as e:
            print(f"Error decoding file: {str(e)}")
            sys.exit(1)

def main():
    if len(sys.argv) < 5:
        print("Usage:")
        print("  Encode: ./dict_coder.py encode <input_file> <output_file> <dict_file> <mappings_dir>")
        print("  Decode: ./dict_coder.py decode <encoded_file> <output_file> <mappings_dir>")
        print("Example:")
        print("  ./dict_coder.py encode input.txt encoded.txt word_frequencies.txt mappings/")
        print("  ./dict_coder.py decode encoded.txt decoded.txt mappings/")
        sys.exit(1)

    mode = sys.argv[1]
    
    if mode == 'encode':
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        dict_file = sys.argv[4]
        mappings_dir = sys.argv[5]
        
        coder = DictionaryCoder(dict_file)
        coder.encode(input_file, output_file)
        coder.save_mappings(mappings_dir)
        
    elif mode == 'decode':
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        mappings_dir = sys.argv[4]
        
        coder = DictionaryCoder()
        coder.load_mappings(mappings_dir)
        coder.decode(input_file, output_file)
        
    else:
        print(f"Unknown mode: {mode}. Use 'encode' or 'decode'")
        sys.exit(1)

if __name__ == "__main__":
    main()
