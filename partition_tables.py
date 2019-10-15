import struct
import uuid
import sys


def parse_mbr(mbr_bytes):
    # print(mbr_bytes)
    toReturn = []
    count = 0
    start = 446
    while (count <= 3):
        dictionary = {
            'number' : count,
            'start' : struct.unpack('<I', mbr_bytes[start+8:start+12])[0],
            'end' : struct.unpack('<I', mbr_bytes[start+12:start+16])[0] + struct.unpack('<I', mbr_bytes[start+8:start+12])[0] - 1,
            'type' : hex(mbr_bytes[start+4]),
        }
        if (dictionary['end'] == -1):
            break
        toReturn += [dictionary]
        start += 16
        count += 1

    return toReturn


def parse_gpt(gpt_file, sector_size=512):
    gpt_file.seek(sector_size)
    mbr_bytes = gpt_file.read()
    toReturn = []
    start = 512
    count = 0
    while (count <= 4):
        print()
        # print(mbr_bytes[start:start+16])
        # print(mbr_bytes[start+16:start+32])
        # print(mbr_bytes[start+32:start+48])
        # print(mbr_bytes[start+48:start+64])
        dictionary = {
            'number' : count,
            'start' : struct.unpack('<QQ', mbr_bytes[start+32:start+48])[0],
            'end' : struct.unpack('<QQ', mbr_bytes[start+32:start+48])[1],
            'type' : uuid.UUID(bytes_le = mbr_bytes[start:start+16]),
            'name' : mbr_bytes[start+48:start+128].decode('utf-16-le').strip("\x00").strip('\x02').strip('mer').strip('\x00')
        }
        if (dictionary['start'] == 0):
            break
        print()
        print([dictionary])
        toReturn += [dictionary]
        start += 128
        count += 1
    return toReturn

    # firstPart = {
    #     'number' : 0,
    #     'start' : struct.unpack('<QQ', mbr_bytes[1056:1072])[0],
    #     'end' : struct.unpack('<QQ', mbr_bytes[1056:1072])[1],
    #     'type' : uuid.UUID(bytes_le = mbr_bytes[1024:1040]),
    #     'name' : mbr_bytes[1080:1128].decode('utf-16-le').strip("\x00")
    # }

    # print('First part:', firstPart)


    # secondPart = {
    #     'number' : 1,
    #     'start' : struct.unpack('<QQ', mbr_bytes[1184:1200])[0],
    #     'end' : struct.unpack('<QQ', mbr_bytes[1184:1200])[1],
    #     'type' : uuid.UUID(bytes_le = mbr_bytes[1152:1168]),
    #     'name' : mbr_bytes[1208:1272].decode('utf-16-le').strip("\x00mer").strip("\x00")
    # }
    # print('Second part:', secondPart)


    # thirdPart = {
    #     'number' : 2,
    #     'start' : struct.unpack('<QQ', mbr_bytes[1312:1328])[0],
    #     'end' : struct.unpack('<QQ', mbr_bytes[1312:1328])[1],
    #     'type' : uuid.UUID(bytes_le = mbr_bytes[1280:1296]),
    #     'name' : mbr_bytes[1336:1358].decode('utf-16-le').strip("\x00")
    # }
    # print('Third part:', thirdPart)


    # fourthPart = {
    #     'number' : 3,
    #     'start' : struct.unpack('<QQ', mbr_bytes[1440:1456])[0],
    #     'end' : struct.unpack('<QQ', mbr_bytes[1440:1456])[1],
    #     'type' : uuid.UUID(bytes_le = mbr_bytes[1408:1424]),
    #     'name' : mbr_bytes[1464:1504].decode('utf-16-le').strip("\x00")
    # }


    # print('Fourth part:', fourthPart)
    # print('Hello2u', sys.getsizeof(gpt_file))



    # print([firstPart, secondPart, thirdPart, fourthPart])
    # return [firstPart, secondPart, thirdPart, fourthPart]