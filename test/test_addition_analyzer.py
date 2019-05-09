import unittest
from tools.hexaddress import *
from tools.addition_analyzer import *

class TestAdditionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = AdditionAnalyzer()
        address = HexAddress(0x2EF17638)
        self.analyzer.assign(address, 'target')

    def test_has_address(self):
        expected = 0x2EF17638
        address = self.analyzer.address.value
        self.assertEqual(address, expected)

    def test_valid_address_range_target(self):
        self.assertTrue(self.analyzer.is_valid_range())

    def test_valid_address_range_operand(self):
        analyzer = AdditionAnalyzer()
        analyzer.assign(HexAddress(0xbfc3bfc3), 'operand')
        self.assertTrue(self.analyzer.is_valid_range())

    def test_reachable_by_regular(self):
        byte1 = self.analyzer.address.bytes[1]
        byte2 = self.analyzer.address.bytes[2]
        byte3 = self.analyzer.address.bytes[3]
        byte4 = self.analyzer.address.bytes[4]

        bad_byte = 0x11
        
        self.assertTrue(self.analyzer.is_reachable_by_regular(byte1))
        self.assertTrue(self.analyzer.is_reachable_by_regular(byte2))
        self.assertTrue(self.analyzer.is_reachable_by_regular(byte3))
        self.assertTrue(self.analyzer.is_reachable_by_regular(byte4))

        self.assertFalse(self.analyzer.is_reachable_by_regular(bad_byte))

    def test_is_in_overload_space(self):
        byte1 = 0x87
        byte2 = 0xff

        byte3 = 0x00
        byte4 = 0x29

        self.assertFalse(self.analyzer.is_in_overload_space(byte1))
        self.assertFalse(self.analyzer.is_in_overload_space(byte2))

        self.assertTrue(self.analyzer.is_in_overload_space(byte3))
        self.assertTrue(self.analyzer.is_in_overload_space(byte4))

    def test_is_in_exclusive_overload_space(self):
        byte1 = 0x87
        byte2 = 0xff

        byte3 = 0x00
        byte4 = 0x28

        self.assertFalse(self.analyzer.is_in_overload_space(byte1))
        self.assertFalse(self.analyzer.is_in_overload_space(byte2))

        self.assertTrue(self.analyzer.is_in_overload_space(byte3))
        self.assertTrue(self.analyzer.is_in_overload_space(byte4))

    def test_reachable_by_extended_without_overload(self):
        byte1 = 0xff
        byte2 = 0x11

        self.assertTrue(self.analyzer.reachable_by_extended_without_overload(byte1))
        self.assertFalse(self.analyzer.reachable_by_extended_without_overload(byte2))

    def test_get_exclusives_cannot_overflow(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x27010203)
        analyzer.assign(address, 'target')
        self.assertRaises(CannotOverflow, analyzer.get_exclusives)

    def test_get_exclusives_outofrange(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x01010203)
        analyzer.assign(address, 'target')
        self.assertRaises(OutOfRange, analyzer.get_exclusives)

    def test_get_exclusives(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x2e010203)
        analyzer.assign(address, 'target')
        result = analyzer.get_exclusives()
        expected = [2,3,4]
        self.assertEqual(result, expected)

    def test_get_exclusives_exclusive_after_plus_one(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x2e111512)
        analyzer.assign(address, 'target')
        result = analyzer.get_exclusives()
        expected = [2,3]
        self.assertEqual(result, expected)

    def test_get_exclusives_none(self):
        result = self.analyzer.get_exclusives()
        expected = []
        self.assertEqual(result, expected)

    def test_find_byte_addition_for_regulars(self):
        result = self.analyzer.find_byte_addition(0x38)
        expected = (0x09, 0x2f)
        self.assertEqual(result, expected)

    def test_find_byte_addition_for_c(self):
        result = self.analyzer.find_byte_addition(0xff, 'c')
        expected = (0x3d, 0xc2)
        self.assertEqual(result, expected)

    def test_find_byte_addition_for_d(self):
        result = self.analyzer.find_byte_addition(0xff, 'd')
        expected = (0x40, 0xbf)
        self.assertEqual(result, expected)

    def test_find_byte_addition_for_c_overload(self):
        result = self.analyzer.find_byte_addition(0x00, 'co')
        expected = (0x3e, 0xc2)
        self.assertEqual(result, expected)

    def test_find_byte_addition_for_d_overload(self):
        result = self.analyzer.find_byte_addition(0x17, 'do')
        expected = (0x58, 0xbf)
        self.assertEqual(result, expected)

    def test_find_byte_addition_fail(self):
        result1 = self.analyzer.find_byte_addition(0x11, 'regular')
        expected1 = None
        result2 = self.analyzer.find_byte_addition(0x00, 'c')
        expected2 = None
        result3 = self.analyzer.find_byte_addition(0x00, 'd')
        expected3 = None
        self.assertEqual(None, expected1)
        self.assertEqual(None, expected2)
        self.assertEqual(None, expected3)

    def test_find_addition(self):
        #Note addition to neighbors should have already happened
        #Force answers to be > 0xff
        pair = self.analyzer.find_addition()
        result = pair[0] + pair[1]
        expected = self.analyzer.address.original
        self.assertEqual(result, expected)

    def test_find_addition_out_of_range(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x01010203)
        analyzer.assign(address, 'target')
        pair = analyzer.find_addition()
        result = pair
        expected = None
        self.assertEqual(result, expected)

    def test_find_addition_with_overflows(self):
        analyzer = AdditionAnalyzer()
        address = HexAddress(0x8a010403)
        analyzer.assign(address, 'target')
        pair = analyzer.find_addition()
        result = hex(pair[0] + pair[1])
        expected = hex(analyzer.address.original)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()