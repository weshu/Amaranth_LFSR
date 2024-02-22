import argparse
from amaranth import *
from amaranth.back import verilog

import numpy as np

class Lfsr_config():
    """
    LFSR module configuration parameters

    .. code::

        Settings for common LFSR/CRC implementations:
        Name        Configuration           Length  Polynomial      Initial value   Notes
        CRC16-IBM   Galois, bit-reverse     16      16'h8005        16'hffff
        CRC16-CCITT Galois                  16      16'h1021        16'h1d0f
        CRC32       Galois, bit-reverse     32      32'h04c11db7    32'hffffffff    Ethernet FCS; invert final output
        CRC32C      Galois, bit-reverse     32      32'h1edc6f41    32'hffffffff    iSCSI, Intel CRC32 instruction; invert final output
        PRBS6       Fibonacci               6       6'h21           any
        PRBS7       Fibonacci               7       7'h41           any
        PRBS9       Fibonacci               9       9'h021          any             ITU V.52
        PRBS10      Fibonacci               10      10'h081         any             ITU
        PRBS11      Fibonacci               11      11'h201         any             ITU O.152
        PRBS15      Fibonacci, inverted     15      15'h4001        any             ITU O.152
        PRBS17      Fibonacci               17      17'h04001       any
        PRBS20      Fibonacci               20      20'h00009       any             ITU V.57
        PRBS23      Fibonacci, inverted     23      23'h040001      any             ITU O.151
        PRBS29      Fibonacci, inverted     29      29'h08000001    any
        PRBS31      Fibonacci, inverted     31      31'h10000001    any
        64b66b      Fibonacci, bit-reverse  58      58'h8000000001  any             10G Ethernet
        128b130b    Galois, bit-reverse     23      23'h210125      any             PCIe gen 3

    """
    # width of LFSR
    LFSR_WIDTH = 31
    """
    LFSR_WIDTH : 
        Specify width of LFSR/CRC register
    """
    # LFSR polynomial
    LFSR_POLY = 0x10000001
    """
    LFSR_POLY : 
        Specify the LFSR/CRC polynomial in hex format.  For example, the polynomial
        x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
        would be represented as
        32'h04c11db7
        Note that the largest term (x^32) is suppressed.  This term is generated automatically based
        on LFSR_WIDTH.
    """
    # LFSR configuration: "GALOIS", "FIBONACCI"
    LFSR_CONFIG = "FIBONACCI"
    """
    LFSR_CONFIG : 
        Specify the LFSR configuration, either Fibonacci or Galois.  Fibonacci is generally used
        for linear-feedback shift registers (LFSR) for pseudorandom binary sequence (PRBS) generators,
        scramblers, and descrambers, while Galois is generally used for cyclic redundancy check
        generators and checkers.

    ..  code:: 

        Fibonacci style (example for 64b66b scrambler, 0x8000000001)
        DIN (LSB first)
            |
            V
        (+)<---------------------------(+)<-----------------------------.
            |                              ^                               |
            |  .----.  .----.       .----. |  .----.       .----.  .----.  |
            +->|  0 |->|  1 |->...->| 38 |-+->| 39 |->...->| 56 |->| 57 |--'
            |  '----'  '----'       '----'    '----'       '----'  '----'
            V
        DOUT
        Galois style (example for CRC16, 0x8005)
            ,-------------------+-------------------------+----------(+)<-- DIN (MSB first)
            |                   |                         |           ^
            |  .----.  .----.   V   .----.       .----.   V   .----.  |
            `->|  0 |->|  1 |->(+)->|  2 |->...->| 14 |->(+)->| 15 |--+---> DOUT
                '----'  '----'       '----'       '----'       '----'
    """
    # LFSR feed forward enable
    LFSR_FEED_FORWARD = 0
    """
    LFSR_FEED_FORWARD :
        Generate feed forward instead of feed back LFSR.  Enable this for PRBS checking and self-
        synchronous descrambling.

    .. code::

            Fibonacci feed-forward style (example for 64b66b descrambler, 0x8000000001)
            DIN (LSB first)
                |
                |  .----.  .----.       .----.    .----.       .----.  .----.
                +->|  0 |->|  1 |->...->| 38 |-+->| 39 |->...->| 56 |->| 57 |--.
                |  '----'  '----'       '----' |  '----'       '----'  '----'  |
                |                              V                               |
            (+)<---------------------------(+)------------------------------'
                |
                V
            DOUT
            Galois feed-forward style
                ,-------------------+-------------------------+------------+--- DIN (MSB first)
                |                   |                         |            |
                |  .----.  .----.   V   .----.       .----.   V   .----.   V
                `->|  0 |->|  1 |->(+)->|  2 |->...->| 14 |->(+)->| 15 |->(+)-> DOUT
                   '----'  '----'       '----'       '----'       '----'
    """
    # bit-reverse input and output
    REVERSE = 0
    """
    REVERSE :
        Bit-reverse LFSR input and output.  Shifts MSB first by default, set REVERSE for LSB first.
    """
    # width of data input
    DATA_WIDTH = 8
    """
    DATA_WIDTH :
        Specify width of input and output data bus.

         - The module will perform one shift per input data bit
         - so if the input data bus is not required tie data_in to zero and set DATA_WIDTH to the required number of shifts per clock cycle.  
    """
    # implementation style: "AUTO", "LOOP", "REDUCTION"
    STYLE = "AUTO"
    """
    STYLE :
        Specify implementation style.  Can be "AUTO", "LOOP", or "REDUCTION".  

         - When "AUTO" is selected, implemenation will be "LOOP" or "REDUCTION" based on synthesis translate directives.
         - "REDUCTION" and "LOOP" are functionally identical, however they simulate and synthesize differently.  
            - "REDUCTION" is implemented with a loop over a Verilog reduction operator.  
            - "LOOP" is implemented as a doubly-nested loop with no reduction operator.  
            - "REDUCTION" is very fast for simulation in iverilog and synthesizes well in Quartus but synthesizes poorly in ISE, likely due to large inferred XOR gates causing problems with the optimizer.  
            - "LOOP" synthesizes will in both ISE and Quartus.  
         - "AUTO" will default to "REDUCTION" when simulating and "LOOP" for synthesizers that obey synthesis translate directives.
    """

class Lfsr(Elaboratable):
    """
    Top module of the LFSR
    All the function will be complete within a clock cycle.

    IO ports
    ----------
    data_in : Signal(DATA_WIDTH), in
        The parallel data input, these data bits will be shifted through the LFSR
    stat_in : Signal(LFSR_WIDTH), in
        LFSR/CRC current state input
    data_out : Signal(DATA_WIDTH), out
        The parallel data output, these data bits will be shifted out of LFSR 
    stat_out : Signal(LFSR_WIDTH), out
        LFSR/CRC next state output
    """
    def __init__(self, config:Lfsr_config):
        self.config = config
        self.data_in = Signal(config.DATA_WIDTH)
        self.stat_in = Signal(config.LFSR_WIDTH)
        self.data_out = Signal(config.DATA_WIDTH)
        self.stat_out = Signal(config.LFSR_WIDTH)
        self.ports = (  self.data_in,
                        self.stat_in,
                        self.data_out,
                        self.stat_out
                    )

    def calc_mask(self):
        """
        next_state[offset] = XOR([mask_state[offset] & stat_in, mask_data[offset] & data_in])

        for default configuration:
            DATA_WIDTH = 8
            LFSR_WIDTH = 31
            LFSR_POLY = 0x10000001
            LFSR_CONFIG = "FIBONACCI"
            LFSR_FEED_FORWARD = 0
            REVERSE = 0
            STYLE = "AUTO"
        the mask_state matrix is:
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 1.]
            [1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
            ...
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 0. 0. 0. 0. 0. 0. 0. 0.]
        the mask_data matrix is:
            [1. 0. 0. 0. 0. 0. 0. 0.]
            [0. 1. 0. 0. 0. 0. 0. 0.]
            [0. 0. 1. 0. 0. 0. 0. 0.]
            [0. 0. 0. 1. 0. 0. 0. 0.]
            [0. 0. 0. 0. 1. 0. 0. 0.]
            [0. 0. 0. 0. 0. 1. 0. 0.]
            [0. 0. 0. 0. 0. 0. 1. 0.]
            [0. 0. 0. 0. 0. 0. 0. 1.]
            [0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0.]
            ...
            [0. 0. 0. 0. 0. 0. 0. 0.]
            [0. 0. 0. 0. 0. 0. 0. 0.]
        for next_state[0], it is XOR([stat_in[20], stat_in[23], data_in[0]])
            stat_in[23], after 1 clock cycle, will shift 8 bits(DATA_WIDTH) to be bit[31]
            stat_in[20], after 1 clock cycle, will shift 8 bits(DATA_WIDTH) to be bit[28]
            plus data_in bit [0]

        ..  code:: 

            DIN (LSB first)
                |
                V
                (+)<---------------------------(+)<------------------------.
                |                              ^                          |
                |  .----.  .----.       .----. |  .----.  .----.  .----.  |
                +->|  0 |->|  1 |->...->| 28 |-+->| 29 |->| 30 |->| 31 |--'
                |  '----'  '----'       '----'    '----'  '----'  '----'
                V
            DOUT
        """
        # fixed masks for data and state
        mask_state = np.zeros((self.config.LFSR_WIDTH, self.config.LFSR_WIDTH))
        mask_data  = np.zeros((self.config.LFSR_WIDTH, self.config.DATA_WIDTH))

        state_val = np.zeros(self.config.LFSR_WIDTH)
        data_val  = np.zeros(self.config.DATA_WIDTH)

        # init bit mask
        for i in range(self.config.LFSR_WIDTH):
            mask_state[i][i] = 1

        for i in range(self.config.DATA_WIDTH):
            data_mask = np.zeros(self.config.DATA_WIDTH)
            data_mask[self.config.DATA_WIDTH-1-i] = 1
            state_val = mask_state[self.config.LFSR_WIDTH-1]
            data_val  = mask_data[self.config.LFSR_WIDTH-1]
            data_val = np.logical_xor(data_val,data_mask)
            
            for j in range(self.config.LFSR_WIDTH):
                if((self.config.LFSR_POLY>>(j+1)) & 1):
                    state_val = np.logical_xor(mask_state[j],state_val)
                    data_val = np.logical_xor(mask_data[j],data_val)
                    
            mask_state[1:self.config.LFSR_WIDTH] = mask_state[0:self.config.LFSR_WIDTH-1]   
            mask_data[1:self.config.LFSR_WIDTH] = mask_data[0:self.config.LFSR_WIDTH-1]
            
            if (self.config.LFSR_FEED_FORWARD):
                state_val = np.zeros(self.config.LFSR_WIDTH)
                data_val  = data_mask
            mask_state[0] = state_val
            mask_data[0]  = data_val
        
        print(mask_state)
        print(mask_data)
        self.mask_state = mask_state
        self.mask_data  = mask_data

    def elaborate(self, platform):
        self.calc_mask()
        # start the logic part
        m = Module()
        powers_of_two_stat = 2 ** np.arange(self.config.LFSR_WIDTH) 
        powers_of_two_data = 2 ** np.arange(self.config.DATA_WIDTH)
        for i in range(self.config.LFSR_WIDTH):
            _mask_stat = Const(int(np.dot(self.mask_state[i], powers_of_two_stat)),unsigned(self.config.LFSR_WIDTH))
            _mask_data = Const(int(np.dot(self.mask_data[i], powers_of_two_data)),unsigned(self.config.DATA_WIDTH))
            m.d.comb += [self.stat_out[i].eq((self.stat_in & _mask_stat).xor() ^ (self.data_in & _mask_data).xor())
                        ]

        # for (n = 0; n < DATA_WIDTH; n = n + 1) begin : lfsr_data
        #     wire [LFSR_WIDTH+DATA_WIDTH-1:0] mask = lfsr_mask(n+LFSR_WIDTH);
        #     assign data_out[n] = ^({data_in, state_in} & mask);
        # end
        return m


if __name__ == '__main__':
    """
    main function to generate verilog
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-src", dest="emit_src", default=True, action="store_false",
        help="suppress generation of source location attributes")
    cfg = Lfsr_config()
    top = Lfsr(cfg)
    with open("./hw/gen/Lfsr.v", "w") as f:
        f.write(verilog.convert(top, ports=top.ports,emit_src=parser.parse_args().emit_src))