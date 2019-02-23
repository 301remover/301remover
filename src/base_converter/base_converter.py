import math

class BaseConverter:
    def __init__(self, alphabet):
        self._alphabet = ' ' + alphabet
        self._alphabet_dict = dict((c, v) for v, c in enumerate(self._alphabet))
        self._alphabet_len = len(self._alphabet)

    def int_to_str(self, num: int) -> str:
        if num < 0:
            raise ValueError('num must be a positive integer')

        encoding = ""
        while num:
            num, rem = divmod(num, self._alphabet_len)
            encoding = self._alphabet[rem] + encoding
        return encoding

    def str_to_int(self, string: str) -> int:
        num = 0
        for char in string:
            num = num * self._alphabet_len + self._alphabet_dict[char]
        return num

    def str_to_bytes(self, string: str):
        num = self.str_to_int(string)
        length = int(math.ceil(num.bit_length() / 8))
        return num.to_bytes(length, byteorder='big')

    def bytes_to_str(self, bytestr):
        return self.int_to_str(int.from_bytes(bytestr, byteorder='big'))
