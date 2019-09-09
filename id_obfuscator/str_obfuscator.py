#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import math

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
        if not alphabet:
            raise ValueError("alphabet can not be empty")
        self._alphabet = alphabet
        self._len_alphabet = len(alphabet)
        self._salt_str = _hash(salt_int, alphabet)
        self._salt_int = salt_int
        self._int_obfuscator = IntObfuscator(prime, salt_int, size)

    def encode(self, num):
        return self.__encode(num)

    def __encode(self, num):
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
        if int_encoded is None:
            return None
        int_origin = self._int_obfuscator.decode(int_encoded)
        if int_origin is None:
            return None
        str_encoded = self.__encode(int_origin)
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


def _min_fixed_length_for_bits(bit_size: int, alphabet_len: int):
    assert bit_size >= 0
    if bit_size == 0:
        return 0
    m = alphabet_len
    max_value = 2 ** bit_size - 1
    n = 1
    while m < max_value:
        m *= alphabet_len
        n += 1
    return n


class FixedLengthStrObfuscator(StrObfuscator):
    def __init__(self, prime: int, salt_int: int, alphabet: str, size=DEFAULT_SIZE, fixed_length: int = None, padding_alphabet: str = None):
        if padding_alphabet:
            intersection = set(alphabet) & set(padding_alphabet)
            if intersection:
                raise ValueError("'padding_alphabet' contains some characters of 'alphabet': {}".format(''.join(intersection)))
            self._padding_alphabet = padding_alphabet
        else:
            self._padding_alphabet, alphabet = self._pick_padding_alphabet(alphabet)

        if fixed_length:
            min_length = self._min_fixed_length(size, len(alphabet))
            if fixed_length < min_length:
                raise ValueError(
                    "The 'fixed_length' is too small, The minimum length to encode a {}-bit integer using {} letters is {}".format(
                        size, len(alphabet), min_length
                    ))
            self._fixed_length = fixed_length
        else:
            self._fixed_length = self._min_fixed_length(size, len(alphabet))

        super().__init__(prime, salt_int, alphabet, size)

    def encode(self, num):
        return self.__encode(num)

    def __encode(self, num):
        encoded = super().encode(num)
        return self._pad_to_length(encoded)

    def decode(self, encoded: str):
        unpadded = self._remove_padding(encoded)
        return super().decode(unpadded)

    def _pick_padding_alphabet(self, alphabet: str):
        num_padding = int(math.ceil(float(len(alphabet)) / 12))
        return alphabet[:num_padding], alphabet[num_padding:]

    def _pad_to_length(self, encoded: str):
        padding_alpha = self._padding_alphabet
        while len(encoded) < self._fixed_length:
            padding_alpha = _reorder(padding_alpha, encoded)
            encoded += padding_alpha
        return encoded[:self._fixed_length]

    def _min_fixed_length(self, size: int, alphabet_len: int):
        # the first character in the obfuscated string is used for validation and dose not count as a effective character.
        return _min_fixed_length_for_bits(size, alphabet_len) + 1

    def _remove_padding(self, padded: str):
        padding_set = set(self._padding_alphabet)
        chars = (c for c in padded if c not in padding_set)
        return ''.join(chars)
