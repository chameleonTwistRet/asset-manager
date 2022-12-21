import struct
import os
from copy import *
import pickle
import pngToBin
import binToPng


offset = 0x80400000
name = "room0"
root = os.getcwd() + "/"
path = root + "testBins/"
infile = path + name + ".bin"
context = path + name + "ctx.txt"
outfile = path + name + ".by"
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
    while i < len(bin):
        width = 0x8
        it = 0
        get = ""
        while it < width:
            get += bin[it + i]
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
    sections.append(["col", hold])
    hold = ""
    i = 0
    while i < len(sections):
        if sections[i][0] == "vtx":
            print(sections[i][1])
            s = 0
            mtx = "" 
            augh = 0x40 * 2
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
        vert = deepcopy(dict)
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
                num = i + s + (getPrev * 2)
                numberStr += vtx[num]
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
            "E7": [
            "G_RDPPIPESYNC",],
            "BA": [
            "G_SetOtherMode_H",
            [0x1, None],
            [0x1, "bit", "amount", 0x0],
            [0x1, "bit", "affected", 0x0],
            [0x4, "hex", "mode-bits", 0x0],],
            "BB": [
            "G_TEXTURE",
            [0x1, None],
            [0x1, "bit", "mmLevels&tile", 0x0],
            [0x1, "bit", "tileFlag", 0x0],
            [0x2, "hex", "scalingS", 0x0],
            [0x2, "hex", "scalingT", 0x0],],
            "FD": [
            "G_SETTIMG",
            [0x1, "bit", "textureBitandFormat", 0x0],
            [0x2, None],
            [0x4, "hex", "addr", 0x0],],
            "F4": [
            "G_LOADTILE",
            [0x1, "bit", "sTopLeft", 0x0],
            [0x1, "bit", "sTopLeft&tTopLeft", 0x0],
            [0x1, "bit", "tTopLeft", 0x0],
            [0x1, "bit", "descriptor", 0x0],
            [0x1, "bit", "sbottomRight", 0x0],
            [0x1, "bit", "sBottomRight&tBottomRight", 0x0],
            [0x1, "bit", "tBottomRight", 0x0], ],
            "F2": [
            "G_SETTILESIZE",
            [0x1, "bit", "sTopLeft", 0x0],
            [0x1, "bit", "sTopLeft&tTopLeft", 0x0],
            [0x1, "bit", "tTopLeft", 0x0],
            [0x1, "bit", "descriptor", 0x0],
            [0x1, "bit", "width - 1 << 2", 0x0],
            [0x1, "bit", "both", 0x0],
            [0x1, "bit", "swidth - 1 << 2", 0x0], ],
            "04": [
            "G_VTX",
            [0x1, "hex", "whereToStart", 0x0],
            [0x1, "bit", "number1", 0x0],
            [0x1, "bit", "number2", 0x0],
            [0x4, "hex", "addr", 0x0], ],
            "BF": [
            "G_TRI1",
            [0x4, None],
            [0x1, "int", "vert1", 0x0],
            [0x1, "int", "vert2", 0x0],
            [0x1, "int", "vert3", 0x0], ],
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
            yoink = deepcopy(dict[operator])
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
def getImgContext(ctx):
    arr = []
    get = open(ctx, 'r').readlines()
    for each in get:
        boink = each.split(",")
        dict = {}
        if len(boink) > 2:
            dict = {
                "name": boink[0].strip(),
                "type": boink[1].strip(),
                "width": int(boink[2]),
                "height": int(boink[3]),
                "id": int(boink[4].replace("\n", "")),
            }
        else:
            dict = {
                "name": boink[0].strip(),
                "type": boink[1].replace("\n", "").strip(),
            }
        arr.append(dict)
    return arr


def txtToBin(txt, ctx, at):
    g = bytes.fromhex(txt)
    binFile = root + ctx[at]["name"] + ".bin"
    if ctx[at]["type"] == "pal":
        binFile = binFile.replace(".bin", ".pal.bin")
    with open(binFile, 'wb') as file:
        file.write(g)
    at += 1
    return [binFile, 1]
def binToImg(bin, ctx, at):
    toUp = 1
    pngFile = root + ctx[at]["name"] + ".png"
    type = ctx[at]["type"]
    width = ctx[at]["width"]
    height = ctx[at]["height"]
    palette = None
    if type.startswith("ci"):#ci split
        toUp = 2
        palette = bins[at + 1]
    exe = ["binToPng.py", type, "'" + bin + "'", "'" + pngFile + "'", str(width), str(height)]
    binToPng.IMGPARSE(type, bin, pngFile, width, height, palette)
    return [pngFile, toUp]

ctx = getImgContext(context)
bins = []
currentlyAT = 0
for each in sectors:
    if each[0] == "txt":
        s = txtToBin(each[1], ctx, currentlyAT)
        bins.append(s[0])
        currentlyAT += s[1]
blender = []
#vtx and gfx to blender
for each in sectors:
    if each[0] == "vtx":
        blender.append(vtxToDict(each[1]))
    elif each[0] == "gfx":
        blender.append(gfxToDict(each[1], "f3dex"))
#txt to blender (its really weird)
currentlyAT = 0
while currentlyAT < len(bins):
    s = binToImg(bins[currentlyAT], ctx, currentlyAT)
    blender.append(["txt", s[0]])
    currentlyAT += s[1]
blender.append(["ctx", ctx])
with open(outfile, 'wb') as file:
    pickle.dump(blender, file)
for each in bins:
    os.remove(each)