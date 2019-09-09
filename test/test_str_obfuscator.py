#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import itertools
import string

import pytest

from id_obfuscator import StrObfuscator, FixedLengthStrObfuscator


class TestStrEncode:
    def test_uniqueness(self):
        obfuscator = StrObfuscator(151, 156, "abcd", 8)
        d = {}
        for i in range(1, 2 ** 8):
            s = obfuscator.encode(i)
            origin = obfuscator.decode(s)
            assert origin == i
            assert s not in d, "repeat {} -> {}, {}".format(s, d[s], i)
            d[s] = i

    def test_invalid_str(self):
        obfuscator = StrObfuscator(151, 156, "abcd", 8)
        assert obfuscator.decode("abcd") is None
        assert obfuscator.decode("eeee") is None
        assert obfuscator.decode(" ") is None
        assert obfuscator.decode("") is None

    def test_all_invalid_permutations(self):
        alphabet = 'abcd'
        obfuscator = StrObfuscator(151, 156, alphabet, 16)
        valid = {obfuscator.encode(i): i for i in range(1, 2 ** 16)}
        for s in self._all_product(alphabet, 9):
            if s in valid:
                continue
            decode = obfuscator.decode(s)
            assert decode is None, "error: {} -> {}".format(s, decode)

    def test_stability(self):
        obfuscator = StrObfuscator(151, 156, "abcd", 8)
        target = 243
        s = obfuscator.encode(target)
        for _ in range(1000):
            assert obfuscator.encode(target) == s

    def _all_product(self, alphabet, max_len):
        for i in range(1, max_len + 1):
            replacement = itertools.product(alphabet, repeat=i)
            for char_tuple in replacement:
                yield ''.join(char_tuple)


class TestFixLengthStrObfuscator:
    def test_constructor(self):
        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8)
        assert obfuscator._fixed_length == 7
        assert len(obfuscator._padding_alphabet) == 1
        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, fixed_length=0)
        assert obfuscator._fixed_length == 7
        assert len(obfuscator._padding_alphabet) == 1
        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, padding_alphabet='')
        assert obfuscator._fixed_length == 7
        assert len(obfuscator._padding_alphabet) == 1

        obfuscator = FixedLengthStrObfuscator(151, 156, string.ascii_letters + string.digits, 32,padding_alphabet="_=")
        assert obfuscator._fixed_length == 7
        assert len(obfuscator._padding_alphabet) == 2
        obfuscator = FixedLengthStrObfuscator(151, 156, string.ascii_letters + string.digits, 32)
        assert obfuscator._fixed_length == 7
        assert len(obfuscator._padding_alphabet) == 6

        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, fixed_length=12)
        assert obfuscator._fixed_length == 12
        assert len(obfuscator._padding_alphabet) == 1

        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, padding_alphabet='ABCD')
        assert obfuscator._fixed_length == 5
        assert len(obfuscator._padding_alphabet) == 4

        with pytest.raises(ValueError):
            FixedLengthStrObfuscator(151, 156, "abcd", 8, fixed_length=4)

        with pytest.raises(ValueError):
            FixedLengthStrObfuscator(151, 156, "abcd", 8, padding_alphabet='aBCD')

    def test_encode(self):
        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, padding_alphabet="ABCD")
        assert obfuscator.encode(1) == 'dbcDA'
        assert obfuscator.encode(79) == 'baaCA'
        assert obfuscator.encode(245) == 'daccD'
        assert obfuscator.encode(125) == 'dbacD'
        assert obfuscator.encode(146) == 'cdbbd'
        assert obfuscator.encode(222) == 'ccdad'

    def test_decode(self):
        obfuscator = FixedLengthStrObfuscator(151, 156, "abcd", 8, padding_alphabet="ABCD")
        for i in range(1, 2 ** 8):
            encoded = obfuscator.encode(i)
            num2 = obfuscator.decode(encoded)
            assert len(encoded) == 5
            assert num2 == i, "decode failed: {} -> {} -> {}".format(i, encoded, num2)
