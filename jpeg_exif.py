import tags
import struct
import string
import sys


class ExifParseError(Exception):
        
    try: 
        def init(self):
            pass
    except Exception:
        print("Error to parse JPEG for valid EXIF flag.")

def carve(f, start, end):
    # return the bytes
    f.seek(start)
    x = 0
    if (start > end):
        x = f.read(start-end)
    elif(start < end):
        x = f.read(end-start)
    else:
        x = f.read(1)
    f.seek(0)
    return x
    # here is an example that just returns the entire range of bytes:
    # return f.read()

def find_jfif(f, max_length=None):
    # """
    # Return the offsets ((start, end) inclusive pairs) of JFIF-seeming data within f
    # :param f: a file-like object
    # :param max_length: the maximum size of the interval (start, end) to consider
    # :return: a list of offsets
    # """
    # do some stuff
    pairs = []
    # return pairs
    count = 0
    soi = []
    eoi = []
    check = False
    chunk = f.read(1)
    # print(max_length)
    while (chunk):
        # print(chunk)
        if (chunk == b'\xff'):
            check = True
        elif (check):
            if (chunk == b'\xd8'):
                soi += [count-1]
            elif (chunk == b'\xd9'):
                eoi += [count]
            check = False
        count += 1
        chunk = f.read(1)
        
    for i in soi:
        for j in eoi:
            if (i < j):
                if (max_length != None and j-i < max_length):
                    pairs += [(i,j)]
                elif (max_length == None):
                    pairs += [(i, j)]
    return pairs
    
def parse_exif(f):
    # """
    # Return the Exif data from the JFIF file stored in the file-like object f.
    # """
    x = f.read() # x is all bytes
    count = 0
    # find soi, then find EXIF marker
    if (x[count:count+2] == b'\xff\xd8'):
        while (count+2 <= len(x)):
            if (x[count:count+2] == b'\xff\xe1'):
                exif_bytes = x[count:]
                count = 0
                break
            count += 2
    else:
        return 'what do you mean'
    print(exif_bytes[10:12])
    if (exif_bytes[10:12] == b'MM'):
        y = scanBytesBE(exif_bytes)
    elif (exif_bytes[10:12] == b'II'):
        y = scanBytesLE(exif_bytes)
    # print(y)
    return y

def scanBytesBE(exif_bytes):
    toReturn = {}
    string = ''
    bom_bytes = exif_bytes[10:]
    ifd_start = struct.unpack('>I', exif_bytes[14:18])[0]
    entries = struct.unpack('>H', exif_bytes[18:20])[0]
    i = 0
    # print('Entries:', entries)
    while (i < entries):
        temp = int.from_bytes(bom_bytes[ifd_start+2:ifd_start+4], byteorder='big')
        # print(temp)
        if (temp not in tags.TAGS):
            ifd_start += 12
            i += 1
            continue
        # print(temp)
        tag = tags.TAGS[temp]
        fType = struct.unpack('>H', bom_bytes[ifd_start+4:ifd_start+6])[0]
        size = struct.unpack('>I', bom_bytes[ifd_start+6:ifd_start+10])[0]
        offset = struct.unpack('>I', bom_bytes[ifd_start+10:ifd_start+14])[0]
        # print(bom_bytes[ifd_start+10:ifd_start+14])
        # print(tag)
        if (fType == 1): # print('Unsigned byte.')
            string = struct.unpack(">B",bom_bytes[offset:offset+1])
        elif (fType == 2): # print('ASCII string.')
            string = bytes.decode(bom_bytes[offset:offset+size][0:-1])
        elif (fType == 3): # print('Unsigned short')
            if (size <= 4):
                string = int.from_bytes(bom_bytes[ifd_start+10:ifd_start+12], byteorder='big')
            else:
                string = struct.unpack(">%dH" % size, bom_bytes[offset:offset+size*2])[0]
        elif (fType == 4): # print('Unsigned long')
            if (size <= 4):
                string = int.from_bytes(bom_bytes[ifd_start+10:ifd_start+14], byteorder='big')
            else:
                string = struct.unpack(">L",bom_bytes[offset:offset+4])
        elif (fType == 5): # print('Unsigned rational')
            (numerator, denominator)= struct.unpack(">LL",bom_bytes[offset:offset+8])
            string = "%s/%s" % (numerator,denominator)
        elif (fType == 7): # print('Undefined raw.')
            value = struct.unpack(">%dB" % size,bom_bytes[offset:offset+size])
            string = "".join("%.2x" % x for x in value)
        else:
            string = None
        if (tag in toReturn):
            toReturn[tag] += [string]
        else:
            toReturn.update({tag : [string]})
        # print('Before', bom_bytes[ifd_start+2:ifd_start+14])
        ifd_start += 12
        i += 1
        # # print('i:', i, 'Entries: ', entries)
        # print(bom_bytes[ifd_start+2:ifd_start+14])
        if (i == entries and bom_bytes[ifd_start+2:ifd_start+6] != b'\x00\x00\x00\x00'):
            # print(bom_bytes[ifd_start+0:ifd_start+24])
            ifd_start = struct.unpack('>I', bom_bytes[ifd_start+2:ifd_start+6])[0]
            entries = struct.unpack('>H', bom_bytes[ifd_start+0:ifd_start+2])[0]
            i = 0
            # print(bom_bytes[ifd_start+0:ifd_start+24])
            # print(ifd_start, entries)

    # check = struct.unpack('>I', bom_bytes[ifd_start:ifd_start+4])[0]
    # # print(check)
    # # print(bom_bytes[ifd_start+2:ifd_start+6])
    return toReturn


def scanBytesLE(exif_bytes):
    toReturn = {}
    string = ''
    bom_bytes = exif_bytes[10:]
    ifd_start = struct.unpack('<I', exif_bytes[14:18])[0]
    entries = struct.unpack('<H', exif_bytes[18:20])[0]
    i = 0
    # print('Entries:', entries)
    while (i < entries):
        temp = int.from_bytes(bom_bytes[ifd_start+2:ifd_start+4], byteorder='little')
        # print(temp)
        if (temp not in tags.TAGS):
            ifd_start += 12
            i += 1
            continue
        # print(temp)
        tag = tags.TAGS[temp]
        fType = struct.unpack('<H', bom_bytes[ifd_start+4:ifd_start+6])[0]
        size = struct.unpack('<I', bom_bytes[ifd_start+6:ifd_start+10])[0]
        offset = struct.unpack('<I', bom_bytes[ifd_start+10:ifd_start+14])[0]
        # print(bom_bytes[ifd_start+10:ifd_start+14])
        # print(tag)
        if (fType == 1): # print('Unsigned byte.')
            string = struct.unpack("<B",bom_bytes[offset:offset+1])
        elif (fType == 2): # print('ASCII string.')
            string = bytes.decode(bom_bytes[offset:offset+size][0:-1])
        elif (fType == 3): # print('Unsigned short')
            if (size <= 4):
                string = int.from_bytes(bom_bytes[ifd_start+10:ifd_start+12], byteorder='little')
            else:
                string = struct.unpack("<%dH" % size, bom_bytes[offset:offset+size*2])[0]
        elif (fType == 4): # print('Unsigned long')
            if (size <= 4):
                string = int.from_bytes(bom_bytes[ifd_start+10:ifd_start+14], byteorder='little')
            else:
                string = struct.unpack("<L",bom_bytes[offset:offset+4])
        elif (fType == 5): # print('Unsigned rational')
            (numerator, denominator)= struct.unpack("<LL",bom_bytes[offset:offset+8])
            string = "%s/%s" % (numerator,denominator)
        elif (fType == 7): # print('Undefined raw.')
            value = struct.unpack("<%dB" % size,bom_bytes[offset:offset+size])
            string = "".join("%.2x" % x for x in value)
        else:
            string = None
        if (tag in toReturn):
            toReturn[tag] += [string]
        else:
            toReturn.update({tag : [string]})
        # print('Before', bom_bytes[ifd_start+2:ifd_start+14])
        ifd_start += 12
        i += 1
        # # print('i:', i, 'Entries: ', entries)
        # print(bom_bytes[ifd_start+2:ifd_start+14])
        if (i == entries and bom_bytes[ifd_start+2:ifd_start+6] != b'\x00\x00\x00\x00'):
            # print(bom_bytes[ifd_start+0:ifd_start+24])
            ifd_start = struct.unpack('<I', bom_bytes[ifd_start+2:ifd_start+6])[0]
            entries = struct.unpack('<H', bom_bytes[ifd_start+0:ifd_start+2])[0]
            i = 0
            # print(bom_bytes[ifd_start+0:ifd_start+24])
            print(ifd_start, entries)

    # check = struct.unpack('>I', bom_bytes[ifd_start:ifd_start+4])[0]
    # # print(check)
    # # print(bom_bytes[ifd_start+2:ifd_start+6])
    return toReturn