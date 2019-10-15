import struct


def encode(codepoint):
    # encode takes a codepoint (an `int`) and returns a `bytes` object
    # print("{0:b}".format(codepoint))
    if codepoint < 128:
        return bytes([codepoint])

    elif codepoint <= 0x7FF:
        print(bin(codepoint))
        extract1 = (codepoint & 0b0000011111000000) << 2
        # print(bin(extract1))
        extract2 = codepoint & 0b111111
        extract = 0b1100000010000000 | extract1 | extract2
        # print ('Bits for extract: ', end = '')
        # print(bin(extract))
        return extract.to_bytes(2, 'big')

    elif codepoint <= 0xFFFF:
        extract1 = (codepoint & 0b1111000000000000) << 4
        extract2 = (codepoint & 0b111111000000) << 2
        extract3 = codepoint & 0b111111
        extract = 0b111000001000000010000000 | extract1 | extract2 | extract3
        # print(bin(extract))
        return extract.to_bytes(3, 'big')

    elif codepoint <= 0x1FFFFF:
        extract1 = (codepoint & 0b111000000000000000000) << 6
        extract2 = (codepoint & 0b111111000000000000) << 4
        extract3 = (codepoint & 0b111111000000) << 2
        extract4 = (codepoint & 0b111111)
        extract = 0b11110000100000001000000010000000 | extract1 | extract2 | extract3 | extract4
        return extract.to_bytes(4, 'big')
        


def decode(bytes_object):
    # decode takes a `bytes` object and returns a codepoint (an `int`)
    # print(len(bytes_object))
    bint = int.from_bytes(bytes_object, byteorder = 'big', signed = True)
    # print(bint)
    extract = 0
    if len(bytes_object) <= 1:
        extract = bint & 0b1111111

    elif len(bytes_object) <= 2:
        extract1 = (bint & 0b1111100000000) >> 2
        extract2 = bint & 0b111111
        extract = extract1 | extract2

    elif len(bytes_object) <= 3:
        extract1 = (bint & 0b11110000000000000000) >> 4
        extract2 = (bint & 0b11111100000000) >> 2
        extract3 = bint & 0b111111
        extract = extract1 | extract2 | extract3

    elif len(bytes_object) <= 4:
        extract1 = (bint & 0b111000000000000000000000000) >> 6
        extract2 = (bint & 0b1111110000000000000000) >> 4
        extract3 = (bint & 0b11111100000000) >> 2
        extract4 = bint & 0b111111
        extract = extract1 | extract2 | extract3 | extract4

    return extract

# print(0b1100001010000000.to_bytes(2, 'big'))
# print(encode(4096))
# print(encode(16384)) 
# b'\xf0\x90\x80\x81'

# print('Should be: ', end = '')
# print(decode(b'\xe1\x80\x80'))
# print(decode(b'\xe4\x80\x80'))

def main():
    pass

if __name__ == '__main__':
    main()