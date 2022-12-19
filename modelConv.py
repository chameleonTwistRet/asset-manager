import struct
import os


offset = 0x80400000
infile = os.getcwd() + "/testBins/room0.bin"
byt = open(infile, 'rb').read()



byteLimit = {
    "1": 128,
    "2": 32768,
    "4": 2147483648,
}

def floatToHex(input):
    return hex(struct.unpack('<I', struct.pack('<f', input))[0]).replace("0x", "").upper()

def hexToFloat(input):
    return struct.unpack('!f', bytes.fromhex(input))[0]

def hexToNum(input, limit, signed):
    inter = int(input, 16)
    maxer = byteLimit[str(limit)] * 2
    halfer = byteLimit[str(limit)]
    if signed:
        while inter >= halfer:
            inter -= maxer
        while inter < -halfer:
            inter += maxer
    else:
        while inter >= maxer:
            inter -= maxer
        while inter < -maxer:
            inter += maxer
    return inter

def numToHex(input, limit, header = False):
    base = hex(input)
    if base[0] == "-":
        #neg
        sub = ""
        while len(sub) < limit * 2:
            sub += "F"
        sub = hex(int(sub, 16) + 1)
        base = hex(int(sub, 16) + int(base, 16))
    end = base.replace("0x", "").upper()
    while len(end) < limit * 2:
        end = "0" + end
    if header:
        end = "0x" + end
    return end


def bytesToStrings(nerd):
    dataS = ""
    i = 0
    while i < len(nerd):
        ayte = hex(int(nerd[i])).replace("0x", "").zfill(2).upper()
        dataS += ayte
        i += 1
    return dataS

new = bytesToStrings(byt)

def hexToFormat(bin):
    i = 0
    mode = "vtx"
    sections = []
    hold = ""
    while i < len(new):
        width = 0x8
        it = 0
        get = ""
        while it < width:
            get += new[it + i]
            it += 1
        if get == "01040040":
            sections.append([mode, hold])
            hold = ""
            mode = "gfx"
        elif get == "B8000000":
            if mode == "gfx" or mode == "vtx":
                sections.append([mode, hold])
                hold = ""
                mode = "txt"
            elif mode == "txt":
                sections.append([mode, hold])
                hold = ""
        hold += get
        i += width
    sections.append([mode, hold])
    hold = ""
    i = 0
    while i < len(sections):
        if sections[i][0] == "vtx":
            print(sections[i][1])
            s = 0
            mtx = "" 
            augh = 0x40 * 4
            l = len(sections[i][1]) - augh
            while s < augh:
                mtx += sections[i][1][l + s]
                s += 1
            sections[i][1] = sections[i][1].replace(mtx, "")
            sections.insert(i + 1, ["mtx", mtx])
        sections[i][1] = sections[i][1].replace("B800000000000000", "")
        i += 1

    return sections

sectors = hexToFormat(new)

def vtxToDict(vtx):
    dict = {
        #type, byte size, signed
        "x": [int, 2, True],
        "y": [int, 2, True],
        "z": [int, 2, True],
        "flag": [bool, 2, False],
        "txtX": [int, 2, True],
        "txtY":[int, 2, True],
        "r": [int, 1, False],
        "g": [int, 1, False],
        "b": [int, 1, False],
        "a": [int, 1, False],
    }
    vtxGroup = []
    i = 0
    while i < len(vtx):
        width = 0x10 * 2
        key = 0
        vert = dict.copy()
        while key < len(dict.keys()):
            ops = list(dict.values())[key]
            getPrev = 0
            s = 0
            while s < key:
                ops2 = list(dict.values())[s]
                getPrev += ops2[1]
                s += 1
            opSize = ops[1]
            s = 0
            numberStr = ""
            value = -1
            while s < opSize * 2:
                numberStr += vtx[i + s + (getPrev * 2)]
                s += 1
            if ops[0] == int or ops[0] == bool:
                value = hexToNum(numberStr, opSize, ops[2])
            elif ops[0] == float:
                value = hexToFloat(numberStr)
            vert[list(dict.keys())[key]] = value
            key += 1
        vtxGroup.append(vert)
        i += width
    return ["vtx", vtxGroup]
def gfxToDict(gfx, mode):
    dict = {}
    #https://hack64.net/wiki/doku.php?id=f3dex
    if mode == "f3dex":
        dict = {
            "01": [
            "G_MTX",
            [0x1, "bit", ["projection", "load", "push"], 0x0],
            [0x2, None],
            [0x4, "hex", "addr", 0x0],],
        }
    elif mode == "f3dex2":
        dict = {
            #type, byte size, signed
            "matrix": [int, 2, True],
            "y": [int, 2, True],
            "z": [int, 2, True],
            "flag": [bool, 2, False],
            "txtX": [int, 2, True],
            "txtY":[int, 2, True],
            "r": [int, 1, False],
            "g": [int, 1, False],
            "b": [int, 1, False],
            "a": [int, 1, False],
        }
    commands = []
    i = 0
    while i < len(gfx):
        width = 0x8 * 2
        s = 0
        get = ""
        while s < width:
            get += gfx[i + s]
            s += 1
        
        operator = get[0] + get[1]
        args = get
        yoink = []
        if operator in list(dict.keys()):
            yoink = dict[operator].copy()
        else:
            i += width
            continue

        assign = 1
        at = 0x1 * 2
        while assign < len(yoink):
            if yoink[assign][1] == None:
                at += yoink[assign][0] * 2
                assign += 1
                continue
            s = 0
            get = ""
            while s < yoink[assign][0] * 2:
                get += args[at + s]
                s += 1
            if yoink[assign][1] != "hex":
                yoink[assign][3] = hexToNum(get, yoink[assign][0], False)
            else:
                yoink[assign][3] = get
            at += yoink[assign][0] * 2
            assign += 1



        commands.append(yoink)
        i += width


    return ["gfx", commands]


blender = []
for each in sectors:
    if each[0] == "vtx":
        blender.append(vtxToDict(each[1]))
    elif each[0] == "gfx":
        blender.append(gfxToDict(each[1], "f3dex"))
print(blender)