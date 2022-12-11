import struct #for floats
from PyQt5.QtCore import *
from tkinter import filedialog#if there is a better alternative for this i would love to hear it
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from math import *
import os

currMode = None
compressedMode = False
compressedType = ""
dim = [960, 540]
doopaDat = bytes()

byteLimit = {
    "1": 128,
    "2": 32768,
    "4": 2147483648,
}
roomObject = {
    "x": float,
    "y": float,
    "z": float,
    "xScale": float,
    "yScale": float,
    "zScale": float,
    "unk_14": int,
    "hurts": int,
    "unk_20": int,
    "unk_24": int,
    "unk_28": float,
    "unk_2C": float,
    "unk_30": float,
    "unk_34": int,
    "unk_38": int,
    "unk_3C": int,
    "unk_40": int,
    "unk_44": int,
    "unk_48": int,
    "unk_4C": int,
    "objectId": int,
    "unk_54": int,
    "unk_58": int,
    "unk_5C": int,
    "unk_60": int,
    "unk_64": int,
    "unk_68": int,
    "unk_6C": int,
    "collisionMode": int,
    "existant": int,
    "unk_78": int,
    "unk_7C": int,
    "unk_80": int,
    "unk_84": int,
    "unk_88": int,
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

def mapToHex(map):
    result = ""
    for row in map:
        for c in row:
            result += numToHex(c, 4)
    return result

def hexToMap(hex, width, per):
    DestLength = per * 2
    i = 0
    j = 0
    map = []
    row = []
    curr = 0
    while curr < len(hex):
        get = ""
        while len(get) < DestLength:
            get += hex[len(get) + (i * DestLength)]
        number = hexToNum(get, per, True)
        row.append(number)
        i += 1
        if i >= width * (j + 1):
            map.append(row)
            row = []
            j += 1
        curr = (i * DestLength)
    while row != []:
        map.append(row)
        row = []
    return map

def openFile(path):
    filepath = filedialog.askopenfilename(initialdir = path,
        filetypes=[("Binary File", "*.bin"),]
    )
    if not filepath:
        return
    print("opened")
    return open(filepath, 'rb').read()

def bytesToStrings(nerd):
    dataS = ""
    i = 0
    while i < len(nerd):
        ayte = hex(int(nerd[i])).replace("0x", "").zfill(2).upper()
        dataS += ayte
        i += 1
    return dataS

def hexToRoom(input, object):
    newRoom = roomObject.copy()
    i = 0
    while i < len(newRoom.keys()):
        s = i * 8
        receive = ""
        while s < (i + 1) * 8:
            receive += input[s + (object * (0x8C * 2))]
            s += 1
        conv = None
        key = list(newRoom.keys())[i]
        value = list(newRoom.values())[i]
        if value == float:
            conv = hexToFloat(receive)
        elif value == int:
            conv = hexToNum(receive, 4, True)
        newRoom[key] = conv
        i += 1
    return newRoom


#print(hexToMap(boip, 3, 4))
#print(mapToHex(hexToMap(boip, 3, 4)))
print(hexToFloat("44960000"))
print(floatToHex(hexToFloat("44960000")))






# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asset Manager")

        self.currRoomObj = 0

        widget = QWidget()
        self.load = QPushButton(widget)
        self.load.setText("Load")
        self.load.clicked.connect(self.loadFile)
        self.load.move(0, 0)
        self.load.resize(QSize(80, 20))

        self.loadType = QComboBox(widget)
        self.loadType.addItems(["Binary", "Image", "Model", "Sound", "Animation", "String", "Asset Type"])
        self.loadType.activated[str].connect(self.typeSelect)
        self.loadType.move(80, 0)
        self.loadType.resize(QSize(80, 20))

        self.extBox = QComboBox(widget)
        self.extBox.addItems(["N/A"])
        self.extBox.activated[str].connect(self.extSelect)
        self.extBox.move(160, 0)
        self.extBox.resize(QSize(80, 20))

        self.compressed = QCheckBox(widget)
        self.compressed.toggled.connect(self.compressCheck)
        self.compressed.move(240, 0)
        self.compressed.resize(QSize(20, 20))

        self.compressions = QComboBox(widget)
        self.compressions.setEnabled(compressedMode)
        self.compressions.addItems(["inflate"])
        self.compressions.activated[str].connect(self.compressionSelect)
        self.compressions.move(260, 0)
        self.compressions.resize(QSize(80, 20))

        self.compressionExt = QComboBox(widget)
        self.compressionExt.setEnabled(compressedMode)
        self.compressionExt.addItems(["N/A"])
        self.compressionExt.activated[str].connect(self.compressionExtSelect)
        self.compressionExt.move(340, 0)
        self.compressionExt.resize(QSize(120, 20))


        #placeholder path, pls ignore
        self.displayPath = os.getcwd() + "//funster.png"
        self.imgDisplay = QPixmap(self.displayPath)
        self.image = QLabel(widget)
        self.image.setPixmap(self.imgDisplay)
        self.image.move(0, 20)
        self.image.hide()

        self.hexLines = int(dim[1] / 20)
        self.hexChars = 16
        self.hexCharSize = 14

        getWidth = ceil(self.hexChars * self.hexCharSize)


        self.hexEdit = QPlainTextEdit(widget)
        self.hexEdit.move(512, 0)
        self.hexEdit.resize(QSize(getWidth, 20 * self.hexLines))

        self.hexConv = QPlainTextEdit(widget)
        self.hexConv.move(512 + getWidth, 0)
        self.hexConv.resize(QSize(getWidth, 20 * self.hexLines))

        self.roomSpin = QSpinBox(widget)
        self.roomSpin.move(512 - 50, 0)
        self.roomSpin.resize(QSize(50, 20))
        self.roomSpin.valueChanged.connect(self.roomSpinChange)


        widgets = [
            #QDateEdit,
            #QDateTimeEdit,
            #QDial,
            #QDoubleSpinBox,
            #QFontComboBox,
            #QLCDNumber,
            QLabel,
            #QProgressBar,
            #QPushButton,
            #QRadioButton,
            #QSlider,
            #QSpinBox,
            #QTimeEdit,
        ]


        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)
        self.setFixedSize(dim[0], dim[1])
    def loadFile(self):
        if currMode == "":
            return
        doopaDat = openFile(os.getcwd())
        self.hexEdit.clear()
        self.hexConv.clear()
        self.hexEdit.insertPlainText(bytesToStrings(doopaDat))


        
    def typeSelect(self, text):
        currMode = text
        i = self.extBox.maxVisibleItems()
        while i > 0:
            self.extBox.removeItem(i - 1)
            i -= 1
        place = []
        if currMode == "Binary":
            place = ["None", "UTC", "Shift-JIS"]
        elif currMode == "Image":
            place = ["RGBA16", "RGBA32", "IA16", "IA8", "IA4", "I8", "I4", "CI8", "CI4", "1bpp"]
        elif currMode == "Model":
            place = ["No UV", "UV"]
        elif currMode == "Asset Type":
            place = ["Room",]
        self.extBox.addItems(place)
        if len(place) == 0:
            self.extBox.addItem("N/A")
    def extSelect(self, text):
        if text == "UTC":
            print('j')
        if text == "Room":
            self.hexConv.clear()
            self.roomSpin.setMaximum(floor(len(self.hexEdit.toPlainText()) / (0x8C * 2)) - 1)
            getR = hexToRoom(self.hexEdit.toPlainText(), self.currRoomObj)
            i = 0
            while i < len(getR.keys()):
                app = list(getR.keys())[i] + ": " + str(list(getR.values())[i]) + "\n"
                self.hexConv.insertPlainText(app)
                i += 1
    def compressCheck(self, checked):
        compressedMode = checked
        self.compressions.setEnabled(checked)
        self.compressionExt.setEnabled(checked)
        if not checked:
            compressedType = ""
    def compressionSelect(self, text): 
        i = self.compressionExt.maxVisibleItems()
        while i > 0:
            self.compressionExt.removeItem(i - 1)
            i -= 1
        place = []
        if text == "inflate":
            place = ["Low / None (78 01)", "Default (78 9C)", "Best (78 DA)"]
        self.compressionExt.addItems(place)
        if len(place) == 0:
            self.compressionExt.addItem("N/A")
    def compressionExtSelect(self, text):
        if text != "N/A":
            compressedType = text
    def roomSpinChange(self, value):
        self.currRoomObj = value


        

app = QApplication([])
window = MainWindow()
window.show()

app.exec()
