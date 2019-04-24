#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pytest

from id_obfuscator import IntObfuscator


class TestEncode:
    def test_encode(self):
        obfuscator = IntObfuscator(151, 156, 8)
        assert obfuscator.encode(255) == 245
        obfuscator.encode(123)

        with pytest.raises(ValueError):
            obfuscator.encode(256)
        with pytest.raises(ValueError):
            obfuscator.encode(0)

    def test_decode(self):
        obfuscator = IntObfuscator(151, 156, 8)
        assert obfuscator.decode(245) == 255
        assert obfuscator.decode(255) == 21

        assert obfuscator.decode(156) is None
        assert obfuscator.decode(256) is None
        assert obfuscator.decode(-1) is None

    def test_encode_uniqueness(self):
        obfuscator = IntObfuscator(38113, 42168, 16)
        record = {}
        for num in range(1, 2 ** 16):
            encoded = obfuscator.encode(num)
            num2 = obfuscator.decode(encoded)
            assert num2 == num
            assert encoded not in record, 'repeat {}|{} --> {} '.format(num, record[encoded], encoded)
            record[encoded] = num
