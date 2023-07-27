import unittest

from lsst.ts.mtaircompressor import utils


class StatusToBoolsTestCase(unittest.TestCase):
    def test_simple(self) -> None:
        bools = utils.status_bit_to_bools(["Bit 1", "Bit 2", None, "Bit 3"], 0x0D)
        assert bools == {"Bit 1": True, "Bit 2": False, "Bit 3": True}
