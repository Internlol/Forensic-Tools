import argparse
import struct
import string

def printable(c):
        return (ord(c) > 31 and ord(c) < 127)

def print_strings(file_obj, encoding, min_len):
    # Right now all this function does is print its arguments.
    # You'll need to replace that code with code that actually finds and prints the strings!
#     print(file_obj.name)
#     print(encoding)
#     print(min_len)

        stringR = ''
        if (encoding == 's'):
                x = file_obj.read(1)
                while(x):
                        data = x.decode('utf-8', 'replace')
                        if (printable(data)):
                                stringR += data
                        else:
                                if (len(stringR) >= min_len):
                                        print(stringR)
                                stringR = ''
                        x = file_obj.read(1)
                if (len(stringR) >= min_len):
                        print(stringR)

        elif (encoding == 'l'):
                x = file_obj.read(2)
                while(x):
                        data = x.decode('utf-16-le', 'replace')
                        if (printable(data)):
                                stringR += data
                        else:
                                if (len(stringR) >= min_len):
                                        print(stringR)
                                stringR = ''
                        x = file_obj.read(2)
                if (len(stringR) >= min_len):
                        print(stringR)
                        
        elif (encoding == 'b'):
                x = file_obj.read(2)
                while(x):
                        data = x.decode('utf-16-be', 'replace')
                        if (printable(data)):
                                stringR += data
                        else:
                                if (len(stringR) >= min_len):
                                        print(stringR)
                                stringR = ''
                        x = file_obj.read(2)
                if (len(stringR) >= min_len):
                        print(stringR)
        else: 
                print('Bad encoding.')

def main():
    parser = argparse.ArgumentParser(description='Print the printable strings from a file.')
    parser.add_argument('filename')
    parser.add_argument('-n', metavar='min-len', type=int, default=4,
                        help='Print sequences of characters that are at least min-len characters long')
    parser.add_argument('-e', metavar='encoding', choices=('s', 'l', 'b'), default='s',
                        help='Select the character encoding of the strings that are to be found. ' +
                             'Possible values for encoding are: s = UTF-8, b = big-endian UTF-16, ' +
                             'l = little endian UTF-16.')
    args = parser.parse_args()

    with open(args.filename, 'rb') as f:
        print_strings(f, args.e, args.n)

if __name__ == '__main__':
    main()