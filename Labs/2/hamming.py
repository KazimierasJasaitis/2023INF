import random
from functools import reduce
import operator as op
import sys
import math

def generate_message_bits(n):
    return [random.choice([0, 1]) for _ in range(n)]

def hamming_encode_k(message_bits,k):
    encoded = [None] * (2**(k))
    data_bit_positions = [i for i in range(16) if i not in [0]+[2**i for i in range(k)]]

    for i, bit in zip(data_bit_positions, message_bits):
        encoded[i] = bit

    for j in range(k):
        encoded[2**j] = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i & 2**j])

    encoded[0] = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i != 0])
    
    return encoded

def hamming_encode(data,k):
    encoded_data = []

    for i in range(0, len(data), 11):
        message_bits = data[i:i+11]
        encoded_chunk = hamming_encode_k(message_bits,k)
        encoded_data.extend(encoded_chunk)

    return encoded_data

def add_noise(encoded_data, error_probability=0.05):
    noisy_data = []
    for bit in encoded_data:
        if random.random() < error_probability:
            noisy_bit = 0 if bit == 1 else 1
        else:
            noisy_bit = bit
        noisy_data.append(noisy_bit)
    return noisy_data

def find_error(encoded_data):
    def calculate_parity(positions):
        return reduce(op.xor, [encoded_data[i] for i in positions if i < len(encoded_data)])
    
    error_position = 0
    for j in range(k):
        error_position += 2**j*(calculate_parity([i for i in range(len(encoded_data)) if i & 2**j]))

    overall_parity_positions = [i for i in range(1,len(encoded_data))]
    p0_check = calculate_parity(overall_parity_positions)

    if error_position == 0:
        if p0_check == encoded_data[0]:
            return None
        else:
            return 0
    else:
        if p0_check != encoded_data[0]:
            return error_position
        else:
            return "more"
        
def apply_xor_mask(encoded_data, xor_mask):
    noisy_encoded_data = []
    for i in range(len(encoded_data)):
        noisy_bit = encoded_data[i] ^ xor_mask[i % len(xor_mask)]
        
        noisy_encoded_data.append(noisy_bit)
    return noisy_encoded_data

def read_input_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # The first line contains the value of k
        k = int(lines[0].strip())

        # The second line contains the message bits
        message_bits = [int(bit) for bit in lines[1].strip()]

        # The third line contains the invert positions, which can be empty
        if len(lines) > 2:  # Check if there is a third line
            invert_positions = [int(pos) for pos in lines[2].strip().split()]
        else:
            invert_positions = []

    return k, message_bits, invert_positions



def invert_indicated(noisy_encoded_data, invert_positions):
    for pos in invert_positions:
        if 0 <= pos < len(noisy_encoded_data):
            noisy_encoded_data[pos] = 1 - noisy_encoded_data[pos]
    return noisy_encoded_data

######################################################################
if len(sys.argv) == 2:
    k, message_bits, invert_positions = read_input_from_file(sys.argv[1])
    bits_per_message = (2**k)-k-1
    encoded_data = []

    for i in range(((len(message_bits)-1) // bits_per_message) + 1):
        message_bits_chunk = message_bits[i*bits_per_message:(i+1)*bits_per_message]
        if len(message_bits_chunk) < bits_per_message:
            message_bits_chunk = message_bits_chunk + [1 for i in range(bits_per_message - len(message_bits_chunk)) ]
        encoded_data += hamming_encode(message_bits_chunk,k)
else:
    k = int(input("Enter the value of k (2-6): "))
    message_bits = [int(bit) for bit in input(f"Enter message bits as a string (min. {(2**k)-k-1}): ")]

    bits_per_message = (2**k)-k-1
    encoded_data = []

    for i in range(((len(message_bits)-1) // bits_per_message) + 1):
        message_bits_chunk = message_bits[i*bits_per_message:(i+1)*bits_per_message]
        if len(message_bits_chunk) < bits_per_message:
            message_bits_chunk = message_bits_chunk + [1 for i in range(bits_per_message - len(message_bits_chunk)) ]
        encoded_data += hamming_encode(message_bits_chunk,k)

    print(encoded_data)
    invert_positions_input = input(f"Enter positions to invert bits (separated by spaces, if any (0-{ ((2**k) * int( math.ceil((len(message_bits)/((2**k)-k-1))))) -1 })): ")
    invert_positions = [int(pos) for pos in invert_positions_input.split()] if invert_positions_input else []





noisy_encoded_data = invert_indicated(encoded_data.copy(), invert_positions)

print(f"Message bits: {message_bits}")
print(f"    Sent bits: {encoded_data}")
print(f"Recieved bits: {noisy_encoded_data}")
print(f"          xor: {[a ^ b for a, b in zip(encoded_data, noisy_encoded_data)]}")
print(f"     Position: {[i % 10 for i in range(len(noisy_encoded_data))]}")

errors = []

for i in range(len(noisy_encoded_data) // (bits_per_message+k+1)):
    error = find_error(noisy_encoded_data[i*(bits_per_message+k+1):(i+1)*(bits_per_message+k+1)])
    if error == "more":
        errors.append(f"{i*(2**k)}-{i*(2**k)+(2**k)-1}")
    elif error == None:
        next
    else:
        errors.append(i*(2**k) + error)

if len(errors) >0:
    print(f"errors found in positions: {errors}")
else:
    print(f"no errors found")
    


