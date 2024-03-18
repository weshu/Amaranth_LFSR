import numpy as np

_debug_amaranth_lfsr_ = 1

def print_debug(instr):
    if _debug_amaranth_lfsr_:
        print(instr)

def print_warnning(instr):
        print('[Warnning]:')
        print(instr)

def print_error(instr):
        print('[Error]:')
        print(instr)

def bit_array_to_int(bit_array):
    """
    Convert the bit_array to the int64 value
    This function returns the integer value equivalent to the input bit vector.
    Using a NumPy dot product and shifting operations on powers of two based on an array range `[0, len-1]`.
    It should be noticed that the max int value is 63 bits for int64.
    for example,
       - bit_array: [0, 0, 1, 0] --> 4
       - bit_array: [1, 1]       --> 3

    ---   Inputs: [bit0, bit1, bit2, .... ], max bit63

    ---   Returns: int64 -- The decimal number corresponding with given ``bit_array``

    """
    return int(np.dot(bit_array.astype(int), 2 ** np.arange(len(bit_array))))