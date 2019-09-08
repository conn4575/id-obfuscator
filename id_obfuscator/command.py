#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import random
import string

import click

from ._util import generate_prime

lowercase = string.ascii_lowercase
uppercase = string.ascii_uppercase
lowercase36 = string.ascii_lowercase + string.digits
uppercase36 = string.ascii_uppercase + string.digits
base62 = string.ascii_lowercase + string.ascii_uppercase + string.digits
urlsafe_base64 = base62 + '_-'
readable_base47 = base62.translate({ord(c): None for c in 'iI1sSzZ2oO0vVwW'})

base_available = {
    "base62": base62,
    "base64": urlsafe_base64,
    "readable47": readable_base47,
    "lowercase": lowercase,
    "uppercase": uppercase,
    "lowercase36": lowercase36,
    "uppercase36": uppercase36,
}


@click.command(help='生成一组给混淆器需要的随机初始参数')
@click.option('bits', '--bit', '-b', default=32, type=int, help='混淆算法需要支持的最大数的位数')
@click.option('base', '--base', '-B', default='base62', type=click.Choice(list(base_available.keys())), help='使用内置的字母表')
@click.option('alphabet', '--alphabet', type=str, help='可用的字母表，默认使用 base62')
def spark(bits, base, alphabet):
    prime = generate_prime(bits)
    random_int = random.getrandbits(bits)
    if not alphabet:
        alphabet = base_available.get(base, base62)
    population = list(set(alphabet))
    random.shuffle(population)
    print("Bit length: {}\nPrime: {}\nSalt_int: {}\nAlphabet: {}".format(
        bits, prime, random_int, ''.join(population)
    ))


@click.group()
def cli():
    pass


cli.add_command(spark)

if __name__ == '__main__':
    cli()
