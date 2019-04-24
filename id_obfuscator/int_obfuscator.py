#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ._util import modinv, is_prime

DEFAULT_SIZE = 32


class IntObfuscator:
    def __init__(self, prime: int, salt_int: int, size=DEFAULT_SIZE):
        """

        :param prime: a prime required by this arithmetic，it should be large enough。
        :param salt_int: A string influencing the confusion result
        :param size: the max bit length it can confuse, default 32
        """
        divisor = 2 ** size
        if prime <= 0 or not is_prime(prime):
            raise ValueError("{} must be prime")
        if salt_int <= 0:
            raise ValueError("salt_int should be positive")
        self._prime = prime
        self._inverse = modinv(prime, divisor)
        self._salt_int = salt_int
        self._size = size
        self.__max = 2 ** size - 1

    def encode(self, value: int):
        # when value is 0, the result is salt_int,it will expose our salt
        if value <= 0 or value > self.__max:
            raise ValueError(
                'value must be positive integer and less than 2**{}，current value is {}'.format(self._size, value))
        return ((value * self._prime) & self.__max) ^ self._salt_int

    def decode(self, num: int):
        if 0 <= num <= self.__max and num != self._salt_int:
            return ((num ^ self._salt_int) * self._inverse) & self.__max
        else:
            return None
