import argparse
from amaranth import *
from amaranth.back import verilog
from .UpCounter import UpCounter

class Top(Elaboratable):
    """
    Top module of the verilog

    IO ports
    ----------
    en : Signal, in
        The counter is incremented if ``en`` is asserted, and retains
        its value otherwise.
    ovf : Signal, out
        ``ovf`` is asserted when the counter reaches its limit.
    """
    def __init__(self):
        self.en  = Signal()
        self.ovf = Signal()

    def elaborate(self, platform):
        m = Module()
        m.submodules.upcnt = upcnt = UpCounter(25)
        m.d.comb += self.ovf.eq(upcnt.ovf)
        m.d.comb += upcnt.en.eq(self.en)
        return m


if __name__ == '__main__':
    """
    main function to generate verilog
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-src", dest="emit_src", default=True, action="store_false",
        help="suppress generation of source location attributes")
    top = Top()
    with open("./hw/gen/Top.v", "w") as f:
        f.write(verilog.convert(top, ports=[top.en, top.ovf],emit_src=parser.parse_args().emit_src))