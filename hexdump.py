# -*- coding: utf-8 -*-
import sys
import string
import codecs
import string

"""
Created on Jan 31 20:18:43 2019

@author: Aaron_Quang
"""
# python -i is REPL

def checkBegin():
    # print("Number of Args: ", len(sys.argv))
    # print("Args: " , str(sys.argv))
    # print("File name is: ", str(sys.argv[1]))
    if (len(sys.argv) < 2 or len(sys.argv) > 4):
        print("Usage: hexdump.py [Filename] \nAdditionally, capture using: hexdump.py [Filename] > [NewFile]")
        sys.exit()
    print('')

def printableAscii(byte):
    byte.strip()
    data = byte.decode('ascii','replace')
    returnStr = ''
    for c in data:
        if ord(c) < 127 and ord(c) > 31:
            # print(c, end=' ')
            returnStr += c
        else: 
            returnStr += '.'
    if (len(returnStr) != len(byte)):
        print("ERROR: Missing character on next line!")
    return returnStr

def hexSplit(str):
    return [str[i:i+2] for i in range(2, len(str)-1, 2)]

def readFile(filename):
    with open(filename, 'rb') as f:
        address = 0
        x = f.read(16)
        while(x):
            stringAd = format(address, '08x')
            hexed = ''
            
            data = hexSplit(str(codecs.encode(x, 'hex')))
            # print(len(data))
            for i in range(0, len(data)):
                address += 1
                hexed += data[i]
                hexed += ' '
                if (i == 7): hexed += ' '

            bracket = printableAscii(x)

            # print(len(hexed))
            while len(hexed) < 49:
                hexed += ' '
            
            yield '{}  {} |{}|'.format(stringAd, ''.join(hexed), bracket)
            # address += 1
            x = f.read(16)
            if (not x):
                stringAd = format(address, '08x')
                yield '{}'.format(stringAd)



# checkBegin()
count = 0
for line in readFile(sys.argv[1]):
    print(line)
# sys.exit()