import random
from functools import reduce
import operator as op

def generate_message_bits(n):
    return [random.choice([0, 1]) for _ in range(n)]

def hamming_encode_16_11(message_bits):
    if len(message_bits) != 11:
        raise ValueError("Data chunk must contain 11 bits")
    
    encoded = [None] * 16

    data_bit_positions = [i for i in range(16) if i not in [0, 1, 2, 4, 8]]
    for i, bit in zip(data_bit_positions, message_bits):
        encoded[i] = bit

    indices_of_ones = [i for i, bit in enumerate(message_bits) if bit]

    # i & 1 tikrina koks yra least significant bitas
    p1 = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i & 1])
    p2 = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i & 2])
    p4 = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i & 4])
    p8 = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i & 8])
    encoded[1] = p1
    encoded[2] = p2
    encoded[4] = p4
    encoded[8] = p8

    p0 = reduce(op.xor, [bit for i, bit in enumerate(encoded) if bit is not None and i != 0])
    encoded[0] = p0


    return encoded

def hamming_encode(data):
    if len(data) % 11 != 0:
        raise ValueError("Data length must be a multiple of 11 bits")

    encoded_data = []

    for i in range(0, len(data), 11):
        message_bits = data[i:i+11]
        encoded_chunk = hamming_encode_16_11(message_bits)
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

    p1_positions = [i for i in range(len(encoded_data)) if i & 1]
    p2_positions = [i for i in range(len(encoded_data)) if i & 2]
    p4_positions = [i for i in range(len(encoded_data)) if i & 4]
    p8_positions = [i for i in range(len(encoded_data)) if i & 8]

    p1_check = calculate_parity(p1_positions)
    p2_check = calculate_parity(p2_positions)
    p4_check = calculate_parity(p4_positions)
    p8_check = calculate_parity(p8_positions)

    overall_parity_positions = [i for i in range(len(encoded_data)-1)]
    overall_parity_check = calculate_parity(overall_parity_positions)

    error_position = (p1_check * 1) + (p2_check * 2) + (p4_check * 4) + (p8_check * 8)

    if error_position == 0:
        if overall_parity_check == encoded_data[-1]:
            return "No error"
        else:
            return "Even number of errors"
    else:
        if overall_parity_check != encoded_data[-1]:
            return f"Single error at position {error_position}"
        else:
            return "Even number of errors"


n = 1
message_bits = generate_message_bits(n*11)
print(f"Message bits: {message_bits}")

encoded_data = hamming_encode(message_bits)
print(f"    Sent bits: {encoded_data}")

noisy_encoded_data = add_noise(encoded_data,0.2)
print(f"Recieved bits: {noisy_encoded_data}")

print(f"          xor: {[a ^ b for a, b in zip(encoded_data, noisy_encoded_data)]}")

print(f"     Position: {[i for i in range(0,10)]+[i for i in range(0,6)]}")

error_status = find_error(noisy_encoded_data)
print(error_status)
