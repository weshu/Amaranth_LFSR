from amaranth.sim import Simulator
from unittest import TestCase
from hw.project_name.UpCounter import * 

class TestUpCounter(TestCase):
    def testCase1(self):
        self.dut = UpCounter(25)
        def process():
            # Disabled counter should not overflow.
            yield self.dut.en.eq(0)
            for _ in range(30):
                yield
                assert not (yield self.dut.ovf)

            # Once enabled, the counter should overflow in 25 cycles.
            yield self.dut.en.eq(1)
            for _ in range(25):
                yield
                assert not (yield self.dut.ovf)
            yield
            assert (yield self.dut.ovf)

            # The overflow should clear in one cycle.
            yield
            assert not (yield self.dut.ovf)
        sim = Simulator(self.dut)
        with sim.write_vcd("./tests/waveform/test_up_counter_case1.vcd"):
            sim.add_clock(1e-6)
            sim.add_sync_process(process)
            sim.run()
