import heapq
import sys
import os
from collections import Counter

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def calculate_frequencies(file_path, k):
    frequencies = Counter()
    buffer = 0
    bits_in_buffer = 0

    with open(file_path, 'rb') as file:
        while True:
            if bits_in_buffer < k:
                byte = file.read(1)
                if not byte:
                    break
                buffer = (buffer << 8) | int.from_bytes(byte, 'big')
                bits_in_buffer += 8

            if bits_in_buffer >= k:
                bits_to_yield = (buffer >> (bits_in_buffer - k)) & ((1 << k) - 1)
                frequencies[format(bits_to_yield, f'0{k}b')] += 1
                bits_in_buffer -= k
                buffer &= (1 << bits_in_buffer) - 1

    # if bits_in_buffer > 0:
        # frequencies[format(buffer, f'0{bits_in_buffer}b')] += 1

    return frequencies

def build_huffman_tree(frequencies):
    priority_queue = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(priority_queue)
    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)
    return priority_queue[0] if priority_queue else None

def generate_codes(node, prefix="", codebook={}):
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)
    return codebook

def serialize_tree(node):
    bit_string = ""
    if node is None:
        return bit_string

    if node.char is not None:
        bit_string += '1' + node.char
    else:
        bit_string += '0'
        bit_string += serialize_tree(node.left)
        bit_string += serialize_tree(node.right)

    return bit_string

def main(file_path, k, output_path):
    try:
        frequencies = calculate_frequencies(file_path, k)
        root = build_huffman_tree(frequencies)
        
        if root:
            print("Huffman Tree Built")
            codebook = generate_codes(root)
            with open(output_path, 'wb') as output_file:
                write_encoded_data(k, root, file_path, codebook, output_file)
        else:
            print("No data to build a Huffman tree.")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_encoded_data(k, tree, file_path, codebook, output_file):
    bit_buffer = format(k - 1, '04b') + serialize_tree(tree)
    buffer = 0
    bits_in_buffer = 0

    with open(file_path, 'rb') as file:
        file_size = os.path.getsize(file_path)
        total_bits = file_size * 8
        bits_read = 0

        while True:
            chunk = file.read(1024)
            if not chunk:
                break

            for byte in chunk:
                buffer = (buffer << 8) | byte
                bits_in_buffer += 8

                while bits_in_buffer >= k:
                    bits_to_yield = (buffer >> (bits_in_buffer - k)) & ((1 << k) - 1)
                    bit_buffer += codebook[format(bits_to_yield, f'0{k}b')]
                    bits_in_buffer -= k
                    buffer &= (1 << bits_in_buffer) - 1
                    
                while len(bit_buffer) >= 8:
                    write_byte(bit_buffer[:8], output_file)
                    bit_buffer = bit_buffer[8:]

            bits_read += len(chunk) * 8
            # sys.stdout.write("\033[K")
            # print(f"\r{round((bits_read / total_bits * 100), 1)}%", end='', flush=True)

        # Handle leftover bits
        if bits_in_buffer > 0:
            tail_bits = format(buffer, f'0{bits_in_buffer}b')
            bit_buffer += tail_bits

            tail_length = format(bits_in_buffer, '04b')
            bit_buffer += tail_length

        write_padding(bit_buffer, output_file)


def write_byte(bits, output_file):
    output_file.write(int(bits, 2).to_bytes(1, 'big'))

def write_padding(bit_buffer, output_file):
    if (((8 - len(bit_buffer) % 8) % 8) < 3):
        padding_len = (((8 - len(bit_buffer) % 8) % 8)) + 5
    else:
        padding_len = (((8 - len(bit_buffer) % 8) % 8)-3)
    
    padding = '0' * padding_len + format(padding_len, '03b')
    bit_buffer += padding
    while len(bit_buffer) >= 8:
        write_byte(bit_buffer[:8], output_file)
        bit_buffer = bit_buffer[8:]

    #print(bit_buffer)
    # print(''.join(str(1) for i in range(padding_len)))
    # print(format(padding_len, '03b'))
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_path> <k>")
        sys.exit(1)

    file_path = sys.argv[1]
    k = int(sys.argv[2])
    filename_without_extension = os.path.splitext(os.path.basename(file_path))[0]
    output_path = "resources/" + filename_without_extension + "_encoded.huff"

    main(file_path, k, output_path)

    # sys.stdout.write("\033[F\033[K")
    file_size = os.path.getsize(file_path)
    print(f"Original file size: {file_size} bytes")
    file_size_new = os.path.getsize(output_path)
    print(f"Compressed file size: {file_size_new} bytes")
    compression_percentage = ((file_size - file_size_new) * 100) / file_size
    print(f"Compressed by {format(compression_percentage, '.2f')}%")
