import string, random

def encode_base62(num):
    characters = string.digits + string.ascii_letters
    base = len(characters)
    result = []

    while num > 0:
        val = num % base
        result.append(characters[val])
        num = num // base

    return ''.join(result[::-1]) or '0'
