import unittest
from tools.hexaddress import *
from tools.subtraction_analyzer import *

class TestAddressAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2EF17638)
        self.analyzer.assign(address, 'target')

    def test_has_address(self):
        expected = 0x2EF17638
        address = self.analyzer.address.value
        self.assertEqual(address, expected)

    def test_valid_address_range_target(self):
        self.assertTrue(self.analyzer.is_valid_range())

    def test_invalid_address_range_target(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0xb6bab6bb)
        analyzer.assign(address, 'target')
        self.assertFalse(analyzer.is_valid_range())

    def test_is_reachable(self):
        byte1 = 0x00

        self.assertTrue(self.analyzer.is_reachable(byte1))
        self.assertFalse(self.analyzer.is_reachable(byte1, underload=True))
        self.assertFalse(self.analyzer.is_reachable(byte1, pattern='RC'))
        self.assertTrue(self.analyzer.is_reachable(byte1, underload=False))
        self.assertFalse(self.analyzer.is_reachable(byte1, underload=True, pattern='CC'))


    def test_assign_pattern(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2E440200)
        analyzer.assign(address, 'target')

        analyzer.assign_pattern(4) #00
        analyzer.assign_pattern(3)
        analyzer.assign_pattern()
        result1 = analyzer.patterns[4]
        result2 = analyzer.patterns[3]
        result3 = analyzer.patterns[1]

        expected1 = {
            'WITH': [],
            'WITHOUT': ['CC', 'DD', 'RR', 'reachable']
        }

        expected2 = {
            'WITH': [],
            'WITHOUT': ['DD', 'RD','RR', 'reachable']
        }

        expected3 = {
            'WITH': [],
            'WITHOUT': ['CD', 'DD', 'RD','RR', 'reachable']
        }

        self.assertEqual(expected1, result1)
        self.assertEqual(expected2, result2)
        self.assertEqual(expected3, result3)

    def test_assign_operand_restriction(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2E440200)
        analyzer.assign(address, 'target')

    def test_find_reachable_pattern(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2E3F0046)
        analyzer.assign(address, 'target')

        #analyzer.assign_pattern()
        result1 = analyzer.valid_pattern()
        expected1 = ['RR', 'RR', 'RR', 'RR']

        self.assertEqual(expected1, result1)

    def test_find_reachable_pattern2(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2E3F00FF)
        analyzer.assign(address, 'target')

        #analyzer.assign_pattern()
        result1 = analyzer.valid_pattern()
        expected1 = ['RR', 'RR', 'RR', 'uRR']

        self.assertEqual(expected1, result1)

    def test_find_reachable_pattern3(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x00770077)
        analyzer.assign(address, 'target')

        #analyzer.assign_pattern()
        result1 = analyzer.valid_pattern()
        expected1 = ['DD','RC','DD','RC']

        self.assertEqual(expected1, result1)

    def test_find_reachable_pattern4(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0xB7000000)
        analyzer.assign(address, 'target')

        #analyzer.assign_pattern()
        result1 = analyzer.valid_pattern()
        expected1 = []

        self.assertEqual(expected1, result1)

    def test_find_reachable_pattern5(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x0400c090)
        analyzer.assign(address, 'target')

        #analyzer.assign_pattern()
        result1 = analyzer.valid_pattern()
        #expected1 = ['RR', 'uRR', 'uRD', 'RC']
        expected1 = ['RR', 'RR', 'uRR', 'uRR']


        result = analyzer.get_operands()
        # print hex(result[0])
        # print hex(result[1])

        self.assertEqual(expected1, result1)

    def test_calculate_byte(self):
        byte = 0x46
        result = self.analyzer.calculate_byte(byte, 'RR', decriment=False)
        expected = (0x4f,0x9)

        self.assertEqual(expected, result)

    def test_calculate_byte_underflow(self):
        byte = 0x8b
        result = self.analyzer.calculate_byte(byte, 'uRR', decriment=True)
        expected = (0x9,0x7d)

        self.assertEqual(expected, result)

    def test_calculate_byte_rc(self):
        byte = 0x46
        result = self.analyzer.calculate_byte(byte, 'RC', decriment=False)
        expected = (0xc2,0x7c)

        self.assertEqual(expected, result)

    def test_calculate_byte_rd(self):
        byte = 0x46
        result = self.analyzer.calculate_byte(byte, 'RD', decriment=False)
        expected = (0x80, 0x3a)

        self.assertEqual(expected, result)

    def test_calculate_byte_rd2(self):
        byte = 0x00
        result = self.analyzer.calculate_byte(byte, 'CC', decriment=True)
        expected = (0xc3,0xc2)

        self.assertEqual(expected, result)

    def test_calculate_byte_dd(self):
        byte = 0x00
        result = self.analyzer.calculate_byte(byte, 'DD', decriment=False)
        expected = (0x80,0x80)

        self.assertEqual(expected, result)

    def test_calculate_byte_rr_decriment(self):
        byte = 0x2E
        result = self.analyzer.calculate_byte(byte, 'RR', decriment=True)
        result = result[0] - result[1]
        expected = 0x2F

        self.assertEqual(expected, result)

    def test_check_operands(self):
        ##0x2EF17638
        ##0x4cf2863a - 0x1e011002
        byte1 = [0x1e, 0xf2, 0x10, 0x3a]
        byte2 = [0x4c, 0x01, 0x86, 0x02]

        results = self.analyzer.check_operands(byte1, byte2)
        expected = (0x4cf2863a, 0x1e011002)

        self.assertEqual(expected, results)

    def test_get_operands(self):
        expected = 0x2EF17638
        result = self.analyzer.get_operands()
        result = result[0] - result[1]
        self.assertEqual(expected, result)

    def test_get_operands2(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2ef1a5be)
        analyzer.assign(address, 'target')
        expected = address.value
        result = analyzer.get_operands()
        result = result[0] - result[1]
        self.assertEqual(expected, result)

    def test_get_operands3(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x2ef1ffa4)
        analyzer.assign(address, 'target')
        expected = (0x38200909,0x92e0965)
        result = analyzer.get_operands()
        self.assertEqual(expected, result)

    def test_get_operands_with_leading_zero_in_target_can_be_reached(self):
        analyzer = SubtractionAnalyzer()
        address = HexAddress(0x00ff0909)
        analyzer.assign(address, 'target')
        expected = (0xa092929,0x90a2020)
        result = analyzer.get_operands()
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()