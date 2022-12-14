import pickle
import os
import bpy
from copy import *
import bmesh


offset = 0x80400000
#edit this to be your directory, blender does not like relative directories
your = "E:/Shit/asset manager" 
infile = your + "/testBins/room0.by"
data = pickle.loads(open(infile, 'rb').read())


vtx = []
gfx = []
txt = []
ctx = []
mtx = []
col = []

def newMaterial(id):

    mat = bpy.data.materials.new(name=str(id))
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(txt[id])
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    return mat

for each in data:
    if each[0] == "vtx":
        vtx = each[1]
    elif each[0] == "gfx":
        gfx = each[1]
    elif each[0] == "txt":
        txt.append(each[1])
    elif each[0] == "mtx":
        mtx = each[1]
    elif each[0] == "ctx":
        ctx = each[1]
    elif each[0] == "col":
        col = each[1]



name = "obj"    
mesh = bpy.data.meshes.new(name)
object = bpy.data.objects.new(name, mesh)
bpy.context.collection.objects.link(object)

verts = []
scalar = 100.0
for each in vtx:
    newX = each["x"] / scalar
    newY = -each["z"] / scalar
    newZ = each["y"] / scalar
    verts.append([newX, newY, newZ])


i = 0
while i < len(txt):
    object.data.materials.append(newMaterial(i))
    i += 1

#find copies
#i = 0
#copyFind = deepcopy(verts)
#while i < len(copyFind):
#    one = copyFind[i]
#    j = i + 1
#    while j < len(copyFind):
#        two = copyFind[j]
#        if two == one:
#            copyFind[j] = "copy of " + str(i)
#        j += 1
#    i += 1
#for each in copyFind:
#    print(each)





faces = []
bank = []
materialIndex = 0
materialAssigns = []
materials = []

for each in gfx:
    if each[0] == "G_SETTIMG":
        found = False
        for check in materials:
            if each == check:
                found = True
                break
        if found:
            continue
        materials.append(each)
i = 0
while i < len(ctx):
    if ctx[i]["type"] == "pal":
        txt.insert(i, None)
    i += 1


for each in gfx:
    if each[0] == "G_VTX":
        toStart = int(each[1][3], 16)
        number = hex(each[2][3]).replace("0x", "") + hex(each[3][3]).replace("0x", "")
        number = bin(int(number, 16)).replace("0b", "")
        while len(number) < 16:
            number = "0" + number
        nov = ""
        length = ""

        i = 0
        while i < 6:
            nov += number[i]
            i += 1
        length = number.replace(nov, "", 1)

        nov = int(nov, 2)
        length = int(length, 2)
        
        if length != (nov * 0x10) - 1:
            #that means its not right!!!!!!!!
            print("bad.")
        val = int(each[4][3], 16) - offset
        val /= 0x10



        while len(bank) < toStart + nov:
            bank.append(0)
        
        fill = 0
        while fill < nov:
            bank[toStart + fill] = int(val) + fill
            fill += 1


        #print(bank)
        #print([toStart, nov, length, val])
        
    elif each[0] == "G_TRI1":
        vert1 = int(each[2][3] / 0x2)
        vert2 = int(each[3][3] / 0x2)
        vert3 = int(each[4][3] / 0x2)
        get1 = bank[vert1]
        get2 = bank[vert2]
        get3 = bank[vert3]
        send = [get1, get2, get3]
        faces.append(send)
        materialAssigns.append([len(faces) - 1, materialIndex])
    elif each[0] == "G_SETTIMG":
        i = 0
        while i < len(materials):
            if materials[i] == each:
                materialIndex = i
                break
            i += 1



mesh.from_pydata(verts, [], faces)

bpy.context.view_layer.objects.active = object
mesher = object.data
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesher)
toAssign = [face for face in mesh.polygons]
bpy.context.tool_settings.mesh_select_mode = [False, False, True]

i = 0
bm.faces.ensure_lookup_table()
while i < len(bm.faces):
    bm.faces[i].select = True
    get = materialAssigns[i][1]
    while txt[get] == None:
        get -= 1
    s = 0
    back = 0
    #print(str(get) + " before")
    while s < get:
        if txt[s] == None:
            back += 1
        s += 1
    get -= back
    #print(str(get) + " after")
    object.active_material_index = get
    bpy.ops.object.material_slot_assign()
    bm.faces[i].select = False
    i += 1
bpy.ops.uv.unwrap()
uv_layer = bm.loops.layers.uv.verify()
i = 0
while i < len(bm.faces):
    f = bm.faces[i]
    getVerts = faces[i]
    s = 0
    for l in f.loops:
        v = vtx[getVerts[s]]
        zoink = 32768.0 / 8.0
        txtx = v["txtX"] / zoink
        txty = v["txtY"] / zoink
        l[uv_layer].uv[0] = txtx
        l[uv_layer].uv[1] = txty
        print("x: " + str(l[uv_layer].uv[0]))
        print("y: " + str(l[uv_layer].uv[1]))
        s += 1
        print(v)
        #l[uv_layer].uv = (l[uv_layer].uv[0], l[uv_layer].uv[1] + 1)
    i += 1

bpy.ops.object.mode_set(mode='OBJECT')
    #object.active_material_index = each[1]
    #mesh.faces[each[0]].select = True
    #bpy.ops.object.material.slot_assign()


#dont bother calculating the true value in this script unless its really easy
#do it in a forward py, not in blender
backVtx = []
for vertex in mesh.vertices:
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
    dict["x"] = round(vertex.co.x * scalar)
    dict["y"] = round(vertex.co.z * scalar)
    dict["z"] = round(-vertex.co.y * scalar)
    backVtx.append(dict)





#cleanup cleanup (everybody do your share)
bpy.context.view_layer.objects.active = object
merge_threshold = 0.05 # here you can define Merge By Distance threshold
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold = merge_threshold)
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_interior_faces()
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')