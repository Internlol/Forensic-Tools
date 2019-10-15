import struct
import sys

def asciiD(inputByte):
    byte = inputByte.decode('ascii', 'ignore')
    returnStr = ''
    for c in byte:
        if ord(c) < 127 and ord(c) > 31:
            returnStr += c
    return returnStr.strip()

def findRange(inputFile, offset):
    num = struct.unpack("<H",inputFile[offset+19:offset+21])[0] - 1
    if (num == 0 or num == -1):
        num = struct.unpack("<L", inputFile[offset+34:offset+38])[0] - 1
    return num

# x is inputfile
def oemName(x, offset):
    return asciiD(x[offset+3:offset+16])

def volumeID(x, offset):
    return x[offset+39:offset+43][::-1].hex()

def volumeLabel(x, offset):
    return asciiD(x[offset+43:offset+54])

def fsTypeLabel(x, offset):
    return asciiD(x[offset+54:offset+62])

def findReserved(x, offset):
    return struct.unpack('<H', x[offset+14:offset+16])[0] - 1

def dataArea(x, offset):
    return struct.unpack('<H', x[22:24])[0] * 2 + 1

def as_le_unsigned(b):
    table = {1: 'B', 2: 'H', 4: 'L', 8: 'Q'}
    return struct.unpack('<' + table[len(b)], b)[0]

def fsstat_fat16(fat16_file, sector_size=512, offset=0):
    old = offset
    olde = 0
    if (sector_size + offset > 512): olde = 1
    offset = offset * sector_size
    # print('Offset:', offset)
    x = fat16_file.read()
    result = ['FILE SYSTEM INFORMATION',
              '--------------------------------------------',
              'File System Type: FAT16',
              '']

    # then do a few things, .append()ing to result as needed
    
    sectorsPerCluster = x[offset+13]
    
    result += ['OEM Name: {}'.format(oemName(x, offset))]
    result += ['Volume ID: 0x{}'.format(volumeID(x, offset))]
    result += ['Volume Label (Boot Sector): {}'.format(volumeLabel(x, offset))]
    result += ['File System Type Label: {}'.format(fsTypeLabel(x, offset))]
    result += ['']
    result += ['Sectors before file system: {}'.format(as_le_unsigned(x[offset+28:offset+29]))]
    result += ['']
    result += ['File System Layout (in sectors)']
    result += ['Total Range: 0 - {}'.format(findRange(x, offset))]
    result += ['* Reserved: 0 - {}'.format(findReserved(x, offset))]
    result += ['** Boot Sector: {}'.format(offset-offset)]
    result += ['* FAT 0: {} - {}'.format(as_le_unsigned(x[offset+16:offset+18]) - 1, as_le_unsigned(x[offset+22:offset+24]))]
    result += ['* FAT 1: {} - {}'.format(struct.unpack('<H', x[offset+22:offset+24])[0] + 1, struct.unpack('<H', x[offset+22:offset+24])[0]*2)]
    result += ['* Data Area: {} - {}'.format(as_le_unsigned(x[offset+22:offset+24]) * 2 + 1, findRange(x, offset))]
    dirEnd = int(as_le_unsigned(x[offset+17:offset+19])*32/as_le_unsigned(x[offset+11:offset+13])+as_le_unsigned(x[offset+22:offset+24])*2)
    result += ['** Root Directory: {} - {}'.format(as_le_unsigned(x[offset+22:offset+24]) * 2 + 1, dirEnd)]
    result += ['** Cluster Area: {} - {}'.format(dirEnd+1, findRange(x, offset)-olde)]
    if (olde): 
        result += ['** Non-clustered: {} - {}'.format(findRange(x, offset), findRange(x, offset))]
    result += ['']
    result += ['CONTENT INFORMATION']
    result += ['--------------------------------------------']
    result += ['Sector Size: {}'.format(sector_size)]
    result += ['Cluster Size: {}'.format(sector_size*as_le_unsigned(x[offset+16:offset+17]))]
    result += ['Total Cluster Range: {} - {}'.format(2, 2 + int((findRange(x, offset)-dirEnd-2)/sectorsPerCluster))]
    result += ['']
    result += ['FAT CONTENTS (in sectors)']
    result += ['--------------------------------------------']
    # numOfClusters = as_le_unsigned(x[offset+16:offset+17])
    sliced = x[offset+sector_size:]
    newOffset = 4
    start = newOffset + dirEnd - 1 - old
    end = 0
    save = 0
    astart = 0
    aend = 0
    startArr = []
    endArr = []
    while (newOffset < findRange(x, offset) and start < findRange(x, offset) and end < findRange(x, offset)):
        num = as_le_unsigned(sliced[newOffset:newOffset+2])
        if (num == 0):
            start = newOffset + dirEnd - 1
            newOffset += sectorsPerCluster
            continue
        if (num != 65535):
            if (save < num):
                save = num
                astart = start
                aend = newOffset + dirEnd -1
            if (num + 1 == save):
                # what += ['{}-{} ({}) -> {}'.format(astart, aend-1, aend-astart, newOffset+dirEnd+1)]
                if (astart in startArr):
                    startArr = startArr[:-1]
                    endArr = endArr[:-1]
                    # print('- {}-{}'.format(startArr[len(startArr)-1], endArr[len(endArr)-1]))
                startArr += [astart]
                endArr += ['{} ({}) -> {}'.format(aend-1, aend-astart, newOffset+dirEnd+1)]
                # print('1 {}-{}'.format(startArr[len(startArr)-1], endArr[len(endArr)-1]))
                start = aend
                if (start not in startArr and end > start):
                    startArr += [start]
                    endArr += ['{} ({}) -> {}'.format(end, end-start+1, 'EOF')]
                    # print('2 {}-{}'.format(startArr[len(startArr)-1], endArr[len(endArr)-1]))
                    start = end + 1
        elif (num == 65535):
            end = newOffset + dirEnd - 2
            # what += ['{}-{} ({}) -> {}'.format(start, end, end-start+1, 'EOF')]
            if (start not in startArr):
                startArr += [start]
                endArr += ['{} ({}) -> {}'.format(end, end-start+1, 'EOF')]
                # print('3 {}-{}'.format(startArr[len(startArr)-1], endArr[len(endArr)-1]))
            start = end + 1
            # if (newOffset == 16132):
                # print('{}-{} {}'.format(startArr[len(startArr)-1], endArr[len(endArr)-1], appArr[len(appArr)-1]))
        newOffset += sectorsPerCluster
    # startArr.sort()
    # endArr.sort()
    for i in range(0, len(startArr)):
        result += ['{}-{}'.format(startArr[i], endArr[i])]
    # print(newOffset, findRange(x, offset))
    # while (newOffset < findRange(x, offset)):
    #     while (sliced[newOffset+2:newOffset+4] != b'\xff\xff'):
    #         if (sliced[newOffset+2:newOffset+5]==b'' or sliced[newOffset+2:newOffset+5] == b'' or sliced[newOffset+2:newOffset+6] == b'' or sliced[newOffset+2:newOffset+5] == b''):
    #             oldStart = start
    #             oldEnd = newOffset + dirEnd
    #             if (olde): start += 2
    #         if (sliced[newOffset:newOffset+4] == b''):
    #             start = newOffset + dirEnd -1
    #         newOffset += sectorsPerCluster
    #     end = newOffset + dirEnd
    #     point = end+1
    #     if (start != 0 and end != 0 and end > start and '{}-{} ({}) -> {}'.format(start, end, end-start+1, point) not in result):
    #             # print(newOffset, '>', findRange(x, offset), newOffset > findRange(x, offset))
    #             if (end > findRange(x, offset)):
    #                 break
    #             if (oldEnd > 0 and point != 'EOF'):
    #                 result += ['{}-{} ({}) -> {}'.format(oldStart, oldEnd, oldEnd-oldStart+1, point)]
    #                 start = oldEnd + 1
    #                 oldEnd = 0
    #             point = 'EOF'
    #             result += ['{}-{} ({}) -> {}'.format(start, end, end-start+1, point)]
    #     start = newOffset + dirEnd + 3 - old
        # newOffset += sectorsPerCluster
    # for y in result:
    #     print(y)
    # for k in what:
    #     print(k)
    # print(sectorsPerCluster)
    # print('num of clusters:', numOfClusters, 'sectors per cluster:', sectorsPerCluster, 'dirEnd:', dirEnd, 'clusters*sectors:', numOfClusters*sectorsPerCluster)
    return result


def main():
    with open('adams.dd', 'rb') as f:
        for x in fsstat_fat16(f, 512, 0):
            print(x)
    print('')
    print(';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;')
    print('')
    with open('fragmented.dd', 'rb') as f:
        for x in fsstat_fat16(f, 1024, 0):
            print(x)
    print('')
    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    print('')
    with open('spiff.dd', 'rb') as f:
        for x in fsstat_fat16(f, 512, 2):
            print(x)

if __name__ == '__main__':
    main()