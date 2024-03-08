import numpy as np

_debug_amaranth_lfsr_ = 0

def dprint(instr):
    if _debug_amaranth_lfsr_:
        print(instr)

def bit_array_to_int(bit_array):
    """
    convert the input bit_array to the int value
    for example,
       - bit_array: [0, 0, 1, 0] --> 4
       - bit_array: [1, 1]       --> 3
    """
    return int(np.dot(bit_array.astype(int), 2 ** np.arange(len(bit_array))))