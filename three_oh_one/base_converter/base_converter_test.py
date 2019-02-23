import unittest
from base_converter import BaseConverter

FULL_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'
FULL_ALPHABET_NO_UNDERSCORE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
ALPHANUMERIC = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
ALPHANUMERIC_LOWERCASE = '0123456789abcdefghijklmnopqrstuvwxyz'

class TestBaseConverter(unittest.TestCase):
    def test_int_to_int_conversion(self):
        converter = BaseConverter(FULL_ALPHABET)
        results = []
        for i in range(0, 10000):
            result = converter.int_to_str(i)
            self.assertFalse(result in results) # check for uniqueness
            self.assertEqual(converter.str_to_int(result), i)
            results.append(result)

    def test_int_to_int_conversion_with_bytes(self):
        converter = BaseConverter(FULL_ALPHABET)
        for i in range(0, 10000):
            self.assertEqual(
                converter.str_to_int(
                    converter.bytes_to_str(
                        converter.str_to_bytes(
                            converter.int_to_str(i)
                        )
                    )
                ),
                i
            )

    def test_int_to_str(self):
        converter = BaseConverter(FULL_ALPHABET)
        self.assertEqual(converter.int_to_str(1), '0')
        self.assertEqual(converter.int_to_str(66), '00')
        self.assertEqual(converter.int_to_str(11), 'a')
        self.assertEqual(converter.int_to_str(37), 'A')
        self.assertEqual(converter.int_to_str(129), '0_')

    def test_str_to_int(self):
        converter = BaseConverter(FULL_ALPHABET)
        self.assertEqual(converter.str_to_int('0'), 1)
        self.assertEqual(converter.str_to_int('00'), 66)
        self.assertEqual(converter.str_to_int('a'), 11)
        self.assertEqual(converter.str_to_int('A'), 37)
        self.assertEqual(converter.str_to_int('0_'), 129)

    def test_str_to_bytes(self):
        converter = BaseConverter(FULL_ALPHABET)
        with self.assertRaises(ValueError):
            converter.int_to_str(-1)

if __name__ == '__main__':
    unittest.main()
