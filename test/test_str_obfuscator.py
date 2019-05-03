#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import itertools

from id_obfuscator import StrObfuscator


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

    def _all_product(self, alphabet, max_len):
        for i in range(1, max_len + 1):
            replacement = itertools.product(alphabet, repeat=i)
            for char_tuple in replacement:
                yield ''.join(char_tuple)
