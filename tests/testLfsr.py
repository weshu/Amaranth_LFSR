from os import stat
import numpy as np
from unittest import TestCase
from amaranth.sim import Simulator, Settle
from amaranth.lib import crc
from numpy.lib.polynomial import poly
from hw.Lfsr.Lfsr import Lfsr, Lfsr_config_fibonacci, Lfsr_config_galois

import zlib
import itertools

def chunks(lst, n, padvalue=None):
    return itertools.zip_longest(*[iter(lst)]*n, fillvalue=padvalue)

def crc32(data):
    return zlib.crc32(data) & 0xffffffff

def crc32c(data, crc=0xffffffff, poly=0x1edc6f41):
    """
    When errors, poly can be set to 0x10000001/0x00000003 for step by step debug
    0x1edc6f41
    """
    poly_reverse = int(np.binary_repr(poly,32)[::-1],2)
    for d in data:
        crc = crc ^ d
        for bit in range(0, 8):
            if crc & 1:
                crc = (crc >> 1) ^ poly_reverse
            else:
                crc = crc >> 1
    return ~crc & 0xffffffff

def crc_tb(cfg,reffunc):
    dut = Lfsr(cfg)
    byte_lanes = cfg.DATA_WIDTH // 8
    data_mask = 2**(cfg.DATA_WIDTH) - 1
    state_mask = 2**(cfg.LFSR_WIDTH) - 1

    def process():
        ref_dblock  = bytes([(x+1)*0x11 for x in range(byte_lanes)])
        ref_din  = int.from_bytes(ref_dblock, 'little')
        yield dut.data_in.eq(ref_din)
        yield dut.stat_in.eq(state_mask)
        yield Settle()
        stateout = yield dut.stat_out
        val = ~stateout & state_mask
        ref = reffunc(ref_dblock)
        if(0):
            print("%s"%bin(val)[2:].zfill(cfg.LFSR_WIDTH))
            print(f'CRC: {val:08x}, expected = {ref:08x} @ DIN = {ref_din:08x}')
        assert (ref==val), \
                f'CRC: {val:08x}, expected = {ref:08x} @ DIN = {ref_din:08x}'

        ref_dblock = bytearray(itertools.islice(itertools.cycle(range(256)),1024))
        yield dut.stat_in.eq(state_mask)
        for b in chunks(ref_dblock, byte_lanes):
            yield dut.data_in.eq(int.from_bytes(b,'little'))
            yield Settle()
            stateout = yield dut.stat_out
            yield dut.stat_in.eq(stateout)

        val = ~stateout & state_mask
        ref = reffunc(ref_dblock)
        if(0):
            print("%s"%bin(val)[2:].zfill(cfg.LFSR_WIDTH))
            print(f'CRC: {val:08x}, expected = {ref:08x}')
        assert (ref==val), \
                f'CRC: {val:08x}, expected = {ref:08x}'

    sim = Simulator(dut)
    with sim.write_vcd("./tests/waveform/test_lfsr_"+reffunc.__name__+".vcd"):
        sim.add_process(process)
        sim.run()

def prbs9(state=0x1ff):
    while True:
        for i in range(8):
            if bool(state & 0x10) ^ bool(state & 0x100):
                state = ((state & 0xff) << 1) | 1
            else:
                state = (state & 0xff) << 1
        yield ~state & 0xff

def prbs31(state=0x7fffffff):
    while True:
        for i in range(8):
            if bool(state & 0x08000000) ^ bool(state & 0x40000000):
                state = ((state & 0x3fffffff) << 1) | 1
            else:
                state = (state & 0x3fffffff) << 1
        yield ~state & 0xff

def prbs_tb(cfg,reffunc):
    dut = Lfsr(cfg)
    byte_lanes = cfg.DATA_WIDTH // 8
    data_mask = 2**(cfg.DATA_WIDTH) - 1
    state_mask = 2**(cfg.LFSR_WIDTH) - 1

    gen = chunks(reffunc(), byte_lanes)

    def process():
        yield dut.data_in.eq(0)
        yield dut.stat_in.eq(state_mask)
        for i in range(512):
            yield Settle()
            ref = int.from_bytes(bytes(next(gen)), 'big')
            dataout = yield dut.data_out
            stateout = yield dut.stat_out
            val = ~dataout & data_mask
            if(0):
                print("%s"%bin(val)[2:].zfill(cfg.DATA_WIDTH))
            assert (ref==val), \
                    f'PRBS: {val:08x}, expected = {ref:08x} @ iteration = {i:08x}'

            yield dut.stat_in.eq(stateout)
        
    sim = Simulator(dut)
    with sim.write_vcd("./tests/waveform/test_lfsr_"+reffunc.__name__+".vcd"):
        sim.add_process(process)
        sim.run()


class TestLfsr(TestCase):
    def test_CRC32(self):
        cfg = Lfsr_config_galois(
            width=32,
            poly=0x4c11db7,
            data_width=8,
            reverse=1
        )
        crc_tb(cfg, crc32)

    def test_CRC32_DW64(self):
        cfg = Lfsr_config_galois(
            width=32,
            poly=0x4c11db7,
            data_width=64,
            reverse=1
        )
        crc_tb(cfg, crc32)

    def test_CRC32C(self):
        cfg = Lfsr_config_galois(
            width=32,
            poly=0x1edc6f41,
            #poly=0x00000003,
            data_width=8,
            reverse=1
        )
        crc_tb(cfg, crc32c)

    def test_CRC32C_DW64(self):
        cfg = Lfsr_config_galois(
            width=32,
            poly=0x1edc6f41,
            #poly=0x0000003f,
            data_width=64,
            reverse=1
        )
        crc_tb(cfg, crc32c)

    def test_PRBS9(self):
        cfg = Lfsr_config_fibonacci(
            width=9,
            poly=0x021,
            data_width=8,
            reverse=0
        )
        prbs_tb(cfg, prbs9)

    def test_PRBS9_DW64(self):
        cfg = Lfsr_config_fibonacci(
            width=9,
            poly=0x021,
            data_width=64,
            reverse=0
        )
        prbs_tb(cfg, prbs9)

    def test_PRBS31(self):
        cfg = Lfsr_config_fibonacci(
            width=31,
            poly=0x10000001,
            data_width=8,
            reverse=0
        )
        prbs_tb(cfg, prbs31)

    def test_PRBS31_D64(self):
        cfg = Lfsr_config_fibonacci(
            width=31,
            poly=0x10000001,
            data_width=64,
            reverse=0
        )
        prbs_tb(cfg, prbs31)