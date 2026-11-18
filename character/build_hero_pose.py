# Hero pose of the AI Gym Builder mascot (3D Jutsu, bpy 5.2).
# Same body as build_character.py, re-posed: three-quarter stance, arms out
# at the sides with open palms, head tipped down, low camera, 9:16 frame,
# charcoal background. This render is the structure input for the comic
# restyle (Seedream V5 Pro via scene_builder_3d_generate_angles).
import bpy, bmesh, math
from mathutils import Vector

SKIN = (0x22/255, 0xC3/255, 0xD6/255)
SKIN_SHADE = (0x12/255, 0x86/255, 0x96/255)
SHORTS = (0.075, 0.075, 0.08)
SHORTS_SHADE = (0.035, 0.035, 0.04)
TAPE = (0.06, 0.06, 0.065)
BG = (0.10, 0.11, 0.12)

def lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

scene = bpy.context.scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in list(bpy.data.collections):
    bpy.data.collections.remove(coll)
char = bpy.data.collections.new("CHAR_mascot_hero")
scene.collection.children.link(char)

def toon(name, base, shade, stripe=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); ramp = nt.nodes.new("ShaderNodeValToRGB")
    emi = nt.nodes.new("ShaderNodeEmission")
    ramp.color_ramp.interpolation = "CONSTANT"
    e0, e1 = ramp.color_ramp.elements
    e0.position, e0.color = 0.0, (*lin(shade), 1)
    e1.position, e1.color = 0.22, (*lin(base), 1)
    nt.links.new(diff.outputs[0], s2r.inputs[0]); nt.links.new(s2r.outputs["Color"], ramp.inputs[0])
    col = ramp.outputs["Color"]
    if stripe:
        tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ay = nt.nodes.new("ShaderNodeMath"); ay.operation = "ABSOLUTE"
        lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = 0.022
        ax = nt.nodes.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"
        gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.12
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
        nt.links.new(tc.outputs["Object"], sep.inputs[0])
        nt.links.new(sep.outputs["Y"], ay.inputs[0]); nt.links.new(ay.outputs[0], lt.inputs[0])
        nt.links.new(sep.outputs["X"], ax.inputs[0]); nt.links.new(ax.outputs[0], gt.inputs[0])
        nt.links.new(lt.outputs[0], mul.inputs[0]); nt.links.new(gt.outputs[0], mul.inputs[1])
        nt.links.new(mul.outputs[0], mix.inputs["Factor"]); nt.links.new(col, mix.inputs["A"])
        mix.inputs["B"].default_value = (*lin(stripe), 1)
        col = mix.outputs["Result"]
    nt.links.new(col, emi.inputs["Color"]); nt.links.new(emi.outputs[0], out.inputs["Surface"])
    return m

mat_skin = toon("MAT_skin", SKIN, SKIN_SHADE)
mat_shorts = toon("MAT_shorts", SHORTS, SHORTS_SHADE, stripe=SKIN)
mat_tape = toon("MAT_tape", TAPE, TAPE)
mat_eye = toon("MAT_eye", (1, 1, 1), (0.93, 0.93, 0.93))

mb = bpy.data.metaballs.new("HERO_body"); mb.resolution = mb.render_resolution = 0.009; mb.threshold = 0.5
body_ob = bpy.data.objects.new("HERO_body", mb); char.objects.link(body_ob)
E = "ELLIPSOID"

def el(co, r, kind="BALL", s=(1, 1, 1), stiff=2.0):
    e = mb.elements.new(type=kind); e.co = co; e.radius = r; e.stiffness = stiff
    if kind != "BALL":
        e.size_x, e.size_y, e.size_z = s

def sym(co, r, kind="BALL", s=(1, 1, 1), stiff=2.0):
    el(co, r, kind, s, stiff); el((-co[0], co[1], co[2]), r, kind, s, stiff)

def cap(p0, p1, r, mirror=True, stiff=2.0):
    for sx in ((1, -1) if mirror else (1,)):
        a = Vector((p0[0] * sx, p0[1], p0[2])); b = Vector((p1[0] * sx, p1[1], p1[2]))
        e = mb.elements.new(type="CAPSULE"); e.co = (a + b) / 2; e.radius = r; e.stiffness = stiff
        e.size_x = (b - a).length / 2
        e.rotation = Vector((1, 0, 0)).rotation_difference((b - a).normalized())

# torso (unchanged)
el((0, 0, 0.98), 0.17, E, (1.25, 0.85, 1.0)); el((0, 0, 1.09), 0.16, E, (1.1, 0.8, 1.0))
el((0, 0, 1.23), 0.18, E, (1.25, 0.82, 1.0)); el((0, 0, 1.37), 0.19, E, (1.5, 0.85, 0.9))
sym((0.08, -0.06, 1.37), 0.12, E, (1.1, 0.55, 0.7), stiff=1.4)
for z in (1.08, 1.16, 1.24):
    sym((0.04, -0.085, z), 0.06, E, (1.0, 0.5, 0.75), stiff=1.2)
sym((0.125, -0.035, 1.12), 0.08, E, (0.8, 0.8, 1.5), stiff=1.3)
sym((0.145, 0.03, 1.28), 0.11, E, (0.8, 0.8, 1.5), stiff=1.5)
sym((0.08, 0.02, 1.49), 0.09, stiff=1.5)
# neck + head tipped slightly forward/down
cap((0, 0, 1.49), (0, -0.015, 1.62), 0.085, mirror=False)
el((0, -0.02, 1.695), 0.155, E, (0.85, 0.92, 1.05))
el((0, -0.035, 1.63), 0.105, E, (0.92, 0.85, 0.62))
# arms out at the sides, elbows soft, palms open and forward
sym((0.235, 0, 1.445), 0.13)
cap((0.235, 0, 1.44), (0.42, -0.03, 1.24), 0.075)
cap((0.42, -0.03, 1.24), (0.56, -0.07, 1.07), 0.062)
cap((0.29, -0.045, 1.39), (0.38, -0.05, 1.28), 0.078, stiff=1.6)   # biceps
cap((0.29, 0.02, 1.40), (0.39, 0.015, 1.29), 0.072, stiff=1.6)     # triceps
cap((0.43, -0.045, 1.22), (0.50, -0.06, 1.13), 0.072, stiff=1.6)   # forearm
sym((0.615, -0.085, 1.035), 0.075, E, (1.25, 0.45, 0.85))          # open palm
cap((0.585, -0.11, 1.06), (0.62, -0.14, 1.09), 0.03)                # thumb
# hips, legs (unchanged)
sym((0.10, 0, 0.93), 0.13); sym((0.085, 0.07, 0.95), 0.12, stiff=1.6)
cap((0.10, 0, 0.93), (0.115, 0, 0.50), 0.12); sym((0.115, 0, 0.50), 0.09)
cap((0.115, 0, 0.50), (0.115, 0.01, 0.09), 0.08)
sym((0.115, -0.025, 0.70), 0.12, E, (1, 1, 1.6), stiff=1.6)
sym((0.12, 0.03, 0.34), 0.09, E, (1, 1, 1.5), stiff=1.6)
cap((0.115, 0.0, 0.05), (0.115, -0.12, 0.03), 0.06)

dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(body_ob.evaluated_get(dg))
bpy.data.objects.remove(body_ob, do_unlink=True); bpy.data.metaballs.remove(mb)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
for _ in range(6):
    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.normal_update(); bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = True
me.materials.append(mat_skin)
body = bpy.data.objects.new("HERO_body", me); char.objects.link(body)

sm = me.copy(); sm.name = "HERO_shorts"; sm.materials.clear(); sm.materials.append(mat_shorts)
bm = bmesh.new(); bm.from_mesh(sm)
g = bm.verts[:] + bm.edges[:] + bm.faces[:]
bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, 1.065), plane_no=(0, 0, 1), clear_outer=True)
g = bm.verts[:] + bm.edges[:] + bm.faces[:]
bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, 0.64), plane_no=(0, 0, 1), clear_inner=True)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if abs(v.co.x) > 0.27], context="VERTS")
bm.normal_update()
for v in bm.verts:
    v.co += v.normal * (0.026 + (0.014 * (0.72 - v.co.z) / 0.08 if v.co.z < 0.72 else 0.0))
bm.to_mesh(sm); bm.free()
shorts = bpy.data.objects.new("HERO_shorts", sm); char.objects.link(shorts)
shorts.modifiers.new("thickness", "SOLIDIFY").thickness = 0.006

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
for sx in (1, -1):
    hit, loc, nrm, *_ = scene.ray_cast(dg, Vector((sx * 0.042, -1.0, 1.70)), Vector((0, 1, 0)))
    em = bpy.data.meshes.new("eye")
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0); bm.to_mesh(em); bm.free()
    eye = bpy.data.objects.new("HERO_eye", em); char.objects.link(eye)
    eye.location = loc + nrm * 0.002 if hit else (sx * 0.042, -0.12, 1.70)
    eye.scale = (0.018, 0.006, 0.026)
    eye.rotation_mode = "QUATERNION"
    if hit:
        eye.rotation_quaternion = Vector((0, -1, 0)).rotation_difference(nrm)
    for p in em.polygons:
        p.use_smooth = True
    em.materials.append(mat_eye)

for sx in (1, -1):
    a = Vector((sx * 0.53, -0.062, 1.105)); b = Vector((sx * 0.57, -0.073, 1.06))
    tm = bpy.data.meshes.new("tape")
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=32, radius1=0.047, radius2=0.047, depth=0.05)
    bm.to_mesh(tm); bm.free()
    tape = bpy.data.objects.new("HERO_tape", tm); char.objects.link(tape)
    tape.location = (a + b) / 2
    tape.rotation_mode = "QUATERNION"
    tape.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((b - a).normalized())
    tape.modifiers.new("thick", "SOLIDIFY").thickness = 0.006
    tm.materials.append(mat_tape)

root = bpy.data.objects.new("RIG_root", None); scene.collection.objects.link(root)
root.rotation_euler = (0, 0, math.radians(-25))
for ob in char.objects:
    ob.parent = root

cd = bpy.data.cameras.new("CAM_hero"); cd.lens = 50; cd.sensor_fit = "AUTO"
cam = bpy.data.objects.new("CAM_hero", cd); scene.collection.objects.link(cam)
cam.location = (0.05, -3.3, 0.78)
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (Vector((0, 0, 1.08)) - cam.location).to_track_quat("-Z", "Y")
scene.camera = cam

sun = bpy.data.objects.new("LGT_key", bpy.data.lights.new("LGT_key", "SUN"))
sun.data.energy = 3.0; scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(-35))

world = scene.world or bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
wn = world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
wout = wn.nodes.new("ShaderNodeOutputWorld")
bgc = wn.nodes.new("ShaderNodeBackground"); bgc.inputs[0].default_value = (*lin(BG), 1)
bga = wn.nodes.new("ShaderNodeBackground"); bga.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
lp = wn.nodes.new("ShaderNodeLightPath"); wmix = wn.nodes.new("ShaderNodeMixShader")
wn.links.new(lp.outputs["Is Camera Ray"], wmix.inputs[0])
wn.links.new(bga.outputs[0], wmix.inputs[1]); wn.links.new(bgc.outputs[0], wmix.inputs[2])
wn.links.new(wmix.outputs[0], wout.inputs["Surface"])

r = scene.render
r.engine = "BLENDER_EEVEE"; r.resolution_x, r.resolution_y = 1080, 1920; r.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "None"
r.film_transparent = False
r.use_freestyle = True; r.line_thickness_mode = "ABSOLUTE"; r.line_thickness = 3.0
fs = bpy.context.view_layer.freestyle_settings
if len(fs.linesets) == 0:
    fs.linesets.new("LS_ink")
for ls in fs.linesets:
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("INK")
    ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = False
    ls.linestyle.color = (0, 0, 0); ls.linestyle.thickness = 3.0
    ls.linestyle.use_length_min = True; ls.linestyle.length_min = 30.0
try:
    scene.eevee.taa_render_samples = 16
except Exception:
    pass

t = artifacts.file(name="mascot_hero.png", media_type="image/png")
r.filepath = str(t.path); r.image_settings.media_type = "IMAGE"; r.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True); t.publish()
result = {"body_dims": [round(v, 3) for v in body.dimensions]}
