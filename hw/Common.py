import numpy as np

_DEBUG_AMARANTH_LFSR = 1

def print_debug(msg):
    """
    Print message when in DEBUG mode
    Set _DEBUG_AMARANTH_LFSR to 1 during development and testing.
    """
    if _DEBUG_AMARANTH_LFSR:
        print(msg)

def print_warning(msg):
        print('[Warning]:')
        print(msg)

def print_error(msg):
        print('[Error]:')
        print(msg)

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
    return int(np.multiply(bit_array.astype(int), 2 ** np.arange(len(bit_array))))