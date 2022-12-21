
from sys import argv
from math import ceil
import png
from itertools import zip_longest

def iter_image_indexes(
    width, height, bytes_per_x=1, bytes_per_y=1, flip_h=False, flip_v=False
):
    w = int(width * bytes_per_x)
    h = int(height * bytes_per_y)

    xrange = (
        range(w - ceil(bytes_per_x), -1, -ceil(bytes_per_x))
        if flip_h
        else range(0, w, ceil(bytes_per_x))
    )
    yrange = (
        range(h - ceil(bytes_per_y), -1, -ceil(bytes_per_y))
        if flip_v
        else range(0, h, ceil(bytes_per_y))
    )

    for y in yrange:
        for x in xrange:
            yield x, y, (y * w) + x
# RRRRRGGG GGBBBBBA
def unpack_color(data):
    s = int.from_bytes(data[0:2], "big")
    r = (s >> 11) & 0x1F
    g = (s >> 6) & 0x1F
    b = (s >> 1) & 0x1F
    a = (s & 1) * 0xFF

    r = ceil(0xFF * (r / 31))
    g = ceil(0xFF * (g / 31))
    b = ceil(0xFF * (b / 31))

    return r, g, b, a


def iter_in_groups(iterable, n, fillvalue=None):
    items = [iter(iterable)] * n
    return zip_longest(*items, fillvalue=fillvalue)

def parse_palette(data):
    palette = []
    i = 0
    width = 0x2
    while i < len(data):
        palette.append(unpack_color(data[i : i + width]))
        i += width
    return palette


def IMGPARSE(mode, infile, outfile, width, height, palette = None):
    width = int(width)
    height = int(height)
    bData = open(infile, 'rb').read()
    pData = None
    if palette != None:
        pData = open(palette, 'rb').read()
    destPath = outfile
    if mode == "rgba32":
        img = bData
        w = png.Writer(width, height, greyscale=False, alpha=True)
        with open(destPath, "wb") as f:
            w.write_array(f,img)
    elif mode == "rgba16":
        img = bytearray()
        for x, y, i in iter_image_indexes(width, height, 2, 1, False, False):
            img += bytes(unpack_color(bData[i:]))
        w = png.Writer(width, height, greyscale=False, alpha=True)
        with open(destPath, "wb") as f:
            w.write_array(f,img)
    elif mode == "i4":
        img = bytearray()
        for x, y, i in iter_image_indexes(width, height, 0.5, 1, False, False):
            b = bData[i]

            i1 = (b >> 4) & 0xF
            i2 = b & 0xF

            i1 = ceil(0xFF * (i1 / 15))
            i2 = ceil(0xFF * (i2 / 15))

            img += bytes((i1, i2))
        w = png.Writer(
            width, height, greyscale=True
        )
        with open(destPath, "wb") as f:
            w.write_array(f, img)
    elif mode == "i8":
        img = bData
        w = png.Writer(
            width, height, greyscale=True
        )
        with open(destPath, "wb") as f:
            w.write_array(f, img)
    elif mode == "ia4":
        img = bytearray()
        for x, y, i in iter_image_indexes(width, height, 0.5, 1, False, False):
            b = bData[i]

            h = (b >> 4) & 0xF
            l = b & 0xF

            i1 = (h >> 1) & 0xF
            a1 = (h & 1) * 0xFF
            i1 = ceil(0xFF * (i1 / 7))

            i2 = (l >> 1) & 0xF
            a2 = (l & 1) * 0xFF
            i2 = ceil(0xFF * (i2 / 7))

            img += bytes((i1, a1, i2, a2))
        w = png.Writer(width, height, greyscale=True, alpha=True)
        with open(destPath, "wb") as f:
            w.write_array(f,img)
    elif mode == "ia8":
        img = bytearray()
        for x, y, i in iter_image_indexes(width, height, False, False):
            b = bData[i]

            i = (b >> 4) & 0xF
            a = b & 0xF

            i = ceil(0xFF * (i / 15))
            a = ceil(0xFF * (a / 15))

            img += bytes((i, a))
        w = png.Writer(width, height, greyscale=True, alpha=True)
        with open(destPath, "wb") as f:
            w.write_array(f,img)
    elif mode == "ia16":
        img = bData
        w = png.Writer(width, height, greyscale=True, alpha=True)
        with open(destPath, "wb") as f:
            w.write_array(f,img)
    elif mode == "ci4":
        img = bytearray()
        for x, y, i in iter_image_indexes(width, height, 0.5, 1, False, False):
            img.append(bData[i] >> 4)
            img.append(bData[i] & 0xF)
        palette = parse_palette(pData)
        w = png.Writer(
            width=width, height=height, palette=palette
        )
        with open(destPath, "wb") as f:
            w.write_array(f, img)
    elif mode == "ci8":
        img = bData
        palette = parse_palette(pData)
        w = png.Writer(
            width=width, height=height, palette=palette
        )
        with open(destPath, "wb") as f:
            w.write_array(f, img)
    return (destPath)


if __name__ == "__main__":
    if len(argv) < 5:
        print("usage: build.py MODE INFILE OUTFILE [--flip-x] [--flip-y]")
        exit(1)
    IMGPARSE(*argv[1:])