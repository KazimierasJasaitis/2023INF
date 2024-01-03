import sys

class Node:
    def __init__(self, char=None):
        self.char = char
        self.left = None
        self.right = None

def deserialize_tree(file, k):
    root = build_tree(file, k)
    return root

def get_bit(file):
    global buffer, bits_in_buffer, byte_index, bit_index, bits_read
    bits_read += 1
    if byte_index >= len(buffer) or bits_in_buffer == 0:
        buffer = file.read(1024)
        byte_index = 0
        bits_in_buffer = len(buffer) * 8
        if not buffer:
            return None

    current_byte = buffer[byte_index]
    bit = (current_byte >> (7 - bit_index)) & 1
    bit_index += 1
    if bit_index == 8:
        bit_index = 0
        byte_index += 1
    bits_in_buffer -= 1
    return bit

def read_char(file, k):
    bits = [get_bit(file) for _ in range(k)]
    if None in bits:
        return None
    return ''.join(str(bit) for bit in bits)

def build_tree(file, k):
    bit = get_bit(file)
    if bit is None:
        return None
    if bit == 1:
        char = read_char(file, k)
        return Node(char=char)
    else:
        left = build_tree(file, k)
        right = build_tree(file, k)
        node = Node()
        node.left = left
        node.right = right
        return node

def decode_content(file, root, k, total_bits):
    decoded_content = ""
    node = root
    global bits_read
    while bits_read < total_bits:
        sys.stdout.write("\033[K")
        print(f"\r{round(bits_read/total_bits,2)*100}%", end='', flush=True)
        bit = get_bit(file)
        if bit is None:
            break
        node = node.left if bit == 0 else node.right
        if node.char is not None:
            decoded_content += node.char
            node = root
    return decoded_content

def get_ignore_bits_len(file):
    file.seek(-1, 2)
    last_byte = int.from_bytes(file.read(1), 'big')
    return (last_byte & 0b111) + 3  # Last 3 bits + 3 bits that contain the number

def get_tail_bits(file, ignore_bits_len):
    # Move to the end of the file to read the last byte
    file.seek(-1, 2)
    last_byte = int.from_bytes(file.read(1), 'big')
    
    bytes_to_move_back = -(-ignore_bits_len // 8) 

    # Move back the calculated number of bytes and read
    file.seek(-bytes_to_move_back, 2)
    tail_bytes = file.read(bytes_to_move_back)

    # Convert the tail bytes to a bit string
    tail_bits = ''.join(f'{byte:08b}' for byte in tail_bytes)

    # Since ignore_bits_len can be more than 8, the tail_len is stored in more than one byte
    # We need to slice from the end, excluding the ignore_bits_len itself
    if ignore_bits_len > 8:
        # Extract tail bits excluding the ignore_bits_len bits
        tail_bits = tail_bits[-ignore_bits_len:-3]  # Last 3 bits indicate the length
    else:
        # If ignore_bits_len is 8 or less, we can simply use the last byte
        tail_bits = tail_bits[-8:-3]

    return tail_bits


def main(input_path, output_path):
    try:
        with open(input_path, 'rb') as file:
            global buffer, bits_in_buffer, byte_index, bit_index, bits_read
            buffer, bits_in_buffer, byte_index, bit_index, bits_read = [], 0, 0, 0, 0

            ignore_bits_len = get_ignore_bits_len(file)
            tail_bits = get_tail_bits(file,ignore_bits_len)
            file_size = file.tell()
            total_bits = (file_size * 8) - ignore_bits_len

            file.seek(0)
            k_bits = read_char(file, 4)
            k = int(k_bits, 2) + 1

            root = deserialize_tree(file, k)

            decoded_content = decode_content(file, root, k, total_bits)
            decoded_content += tail_bits
            with open(output_path, 'wb') as output_file:
                output_file.write(bytes(int(decoded_content[i:i+8], 2) for i in range(0, len(decoded_content), 8)))
            

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python decoder.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)