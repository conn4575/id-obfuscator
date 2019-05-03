#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from .int_obfuscator import DEFAULT_SIZE, IntObfuscator


def _reorder(string, salt):
    """Reorders `string` according to `salt`."""
    len_salt = len(salt)

    if len_salt != 0:
        string = list(string)
        index, integer_sum = 0, 0
        for i in range(len(string) - 1, 0, -1):
            integer = ord(salt[index])
            integer_sum += integer
            j = (integer + index + integer_sum) % i
            string[i], string[j] = string[j], string[i]
            index = (index + 1) % len_salt
        string = ''.join(string)

    return string


def _hash(num: int, alphabet: str):
    if num == 0:
        return alphabet[0]
    alpha_len = len(alphabet)
    arr = []
    while num:
        num, rem = divmod(num, alpha_len)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def _unhash(hashed: str, alphabet: str):
    if not hashed:
        return None
    alpha_map = {c: i for i, c in enumerate(alphabet)}
    rt = 0
    alpha_len = len(alphabet)
    for _s in hashed:
        if _s not in alpha_map:
            return None
        rt = rt * alpha_len + alpha_map[_s]
    return rt


class StrObfuscator:
    def __init__(self, prime: int, salt_int: int, alphabet: str, size=DEFAULT_SIZE):
        self._alphabet = alphabet
        self._len_alphabet = len(alphabet)
        self._salt_str = _hash(salt_int, alphabet)
        self._salt_int = salt_int
        self._int_obfuscator = IntObfuscator(prime, salt_int, size)

    def encode(self, num):
        int_encoded = self._int_obfuscator.encode(num)
        return self._encode_str(int_encoded)

    def decode(self, encoded: str):
        """
        restore the number from the encoded string.
        :param encoded:
        :return: return None if 'encoded' can not convert to its original number.
        """
        if not isinstance(encoded, str) or not encoded:
            return None
        int_encoded = self._decode_str(encoded)
        if not int_encoded:
            return None
        int_origin = self._int_obfuscator.decode(int_encoded)
        if int_origin is None:
            return None
        str_encoded = self.encode(int_origin)
        return int_origin if str_encoded == encoded else None

    def _decode_str(self, encoded: str):
        lottery = encoded[0]
        salt = (lottery + self._salt_str + self._alphabet)[:self._len_alphabet]
        alpha = _reorder(self._alphabet, salt)
        return _unhash(encoded[1:], alpha)

    def _encode_str(self, num: int):
        encoded = lottery = self._alphabet[num % self._len_alphabet]
        salt = (lottery + self._salt_str + self._alphabet)[:self._len_alphabet]
        alpha = _reorder(self._alphabet, salt)
        return encoded + _hash(num, alpha)
