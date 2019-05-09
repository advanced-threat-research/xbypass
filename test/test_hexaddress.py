import unittest
from tools.hexaddress import *

class TestHexAddress(unittest.TestCase):

    def setUp(self):
        address = 0x2EF17638
        self.address = HexAddress(address)

    def test_can_seperate_bytes(self):
        byte1 = self.address.bytes[1]
        byte2 = self.address.bytes[2]
        byte3 = self.address.bytes[3]
        byte4 = self.address.bytes[4]

        expected1 = 0x2E
        expected2 = 0xF1
        expected3 = 0x76
        expected4 = 0x38

        self.assertEqual(byte1, expected1)
        self.assertEqual(byte2, expected2)
        self.assertEqual(byte3, expected3)
        self.assertEqual(byte4, expected4)

    def test_byte_change_subtract(self):
        pos = 1
        value = 0x01
        
        self.address.byte_change(pos, value, 'subtract')

        result = self.address.value
        expected = 0x01f17638 
        self.assertEqual(result, expected)

    def test_byte_change_subtract_underload(self):
        pos = 2
        value = -0x01
        
        self.address.byte_change(pos, value, 'subtract')

        result = self.address.value
        expected = 0x2dFF7638   
        self.assertEqual(result, expected)

    def test_byte_change_subtract_underload_propogagetes(self):
        pos = 4
        value = -0xff
        address = 0xFE000000
        self.address = HexAddress(address)
        self.address.byte_change(pos, value, 'subtract')
        result = self.address.value
        expected = 0xfdffff01  
        self.assertEqual(result, expected)

    def test_byte_change_subtract_overloads_out_of_range(self):
        pos = 4
        value = -0x01
        address = 0x00000000
        self.address = HexAddress(address)
        self.assertRaises(NoHexPositionAvailable, self.address.byte_change, pos, value, 'subtract')

    def test_byte_change_add(self):
        pos = 1
        value = 0xff
        
        self.address.byte_change(pos, value)

        result = self.address.value
        expected = 0xfff17638   
        self.assertEqual(result, expected)

    def test_byte_change_add_zeros_print_correctly(self):
        pos = 2
        value = 0x00
        
        self.address.byte_change(pos, value)

        result = self.address.value
        expected = 0x2e007638   
        self.assertEqual(result, expected)


    def test_byte_change_add_overload(self):
        pos = 2
        value = 0x100
        
        self.address.byte_change(pos, value)

        result = self.address.value
        expected = 0x2f007638   
        self.assertEqual(result, expected)

    def test_byte_change_add_overload_propogagetes(self):
        pos = 4
        value = 0x100
        address = 0xFEFFFFFF
        self.address = HexAddress(address)
        self.address.byte_change(pos, value)
        result = self.address.value
        expected = 0xFF000000   
        self.assertEqual(result, expected)

    def test_byte_change_add_overloads_out_of_range(self):
        pos = 4
        value = 0x100
        address = 0xFFFFFFFF
        self.address = HexAddress(address)
        self.assertRaises(NoHexPositionAvailable, self.address.byte_change, pos, value)

    def test_which_add_changed(self):
        pos = 4
        value = 0x100
        address = 0xFEFFFFFF
        self.address = HexAddress(address)
        changed = self.address.byte_change(pos, value)
        expected = [1, 2, 3, 4]
        self.assertEqual(changed, expected)

    def test_which_subtract_changed(self):
        pos = 3
        value = -0x30
        address = 0xfa0000b9
        self.address = HexAddress(address)
        changed = self.address.byte_change(pos, value, 'subtract')
        expected = [1, 2, 3]
        self.assertEqual(changed, expected)

    def test_which_add_changed2(self):
        pos = 4
        value = 0x00
        address = 0xFEFFFFFe
        self.address = HexAddress(address)
        changed = self.address.byte_change(pos, value)
        expected = [4]
        self.assertEqual(changed, expected)

if __name__ == '__main__':
    unittest.main()