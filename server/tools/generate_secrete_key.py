import os
import argparse

if __name__ == '__main__':
    # CLI args
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--output-path', type=str, required=True, help='Path to binary file that save the secrete key')
    parser.add_argument('--key-length', type=int, default=24, help='Length of generated key')
    
    args = parser.parse_args()
    
    # Generate key
    key = os.urandom(args.key_length)
    
    # Save key
    with open(args.output_path, 'wb') as f:
        f.write(key)
    
    