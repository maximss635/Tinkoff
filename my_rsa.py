from builtins import pow


def my_rsa_encrypt(s, key):
    buffer = bytearray()
    e, n = key[0], key[1]

    for c in s:
        crypted_symbol = pow(ord(c), e, n)
        #print(crypted_symbol)

        crypted_bytes = crypted_symbol.to_bytes(8, byteorder='big')
        buffer += bytearray(crypted_bytes)

    return buffer


def my_rsa_decrypt(bytes, key):
    decrypted_data = ''
    d, n = key[0], key[1]

    for i in range(len(bytes) // 8):
        crypted_sym = 0
        for j in range(8):
            crypted_sym = crypted_sym * 256 + bytes[i*8 + j]

        decrypted_sym = chr(pow(crypted_sym, d, n))
        decrypted_data += decrypted_sym

    return decrypted_data
