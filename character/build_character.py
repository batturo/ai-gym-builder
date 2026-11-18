# Builds the AI Gym Builder mascot in Blender (3D Jutsu runtime, bpy 5.2).
# Original character: muscular calisthenics build, flat cyan-teal skin,
# bald rounded head with a squared jaw, two white oval eyes, no mouth/nose,
# black shorts with a cyan side stripe, black wrist tape.
# Rendered as a flat 2D comic: two-tone cel shading + Freestyle ink outlines.
import bpy, bmesh, math
from mathutils import Vector

SKIN = (0x22/255, 0xC3/255, 0xD6/255)
SKIN_SHADE = (0x12/255, 0x86/255, 0x96/255)
SHORTS = (0.075, 0.075, 0.08)
SHORTS_SHADE = (0.035, 0.035, 0.04)
TAPE = (0.06, 0.06, 0.065)
BG = (0.91, 0.895, 0.87)

def srgb_to_lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

scene = bpy.context.scene
# clean scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in list(bpy.data.collections):
    bpy.data.collections.remove(coll)

char = bpy.data.collections.new("CHAR_mascot")
scene.collection.children.link(char)

# ---------- toon materials ----------
def toon_mat(name, base, shade, stripe=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    emi = nt.nodes.new("ShaderNodeEmission")
    ramp.color_ramp.interpolation = "CONSTANT"
    e0, e1 = ramp.color_ramp.elements
    e0.position, e0.color = 0.0, (*srgb_to_lin(shade), 1)
    e1.position, e1.color = 0.22, (*srgb_to_lin(base), 1)
    nt.links.new(diff.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs["Color"], ramp.inputs[0])
    col = ramp.outputs["Color"]
    if stripe:
        # vertical stripe along the side seam of the shorts (|y| small, |x| large)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
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
        nt.links.new(mul.outputs[0], mix.inputs["Factor"])
        nt.links.new(col, mix.inputs["A"])
        mix.inputs["B"].default_value = (*srgb_to_lin(stripe), 1)
        col = mix.outputs["Result"]
    nt.links.new(col, emi.inputs["Color"])
    nt.links.new(emi.outputs[0], out.inputs["Surface"])
    return m

mat_skin = toon_mat("MAT_skin", SKIN, SKIN_SHADE)
mat_shorts = toon_mat("MAT_shorts", SHORTS, SHORTS_SHADE, stripe=SKIN)
mat_tape = toon_mat("MAT_tape", TAPE, TAPE)
mat_eye = toon_mat("MAT_eye", (1, 1, 1), (0.93, 0.93, 0.93))

# ---------- metaball body ----------
def metaball(name, res=0.009, thr=0.6):
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res
    mb.render_resolution = res
    mb.threshold = thr
    ob = bpy.data.objects.new(name, mb)
    char.objects.link(ob)
    return ob, mb

def el(mb, co, r, kind="BALL", s=(1, 1, 1), stiff=2.0):
    e = mb.elements.new(type=kind)
    e.co = co
    e.radius = r
    e.stiffness = stiff
    if kind != "BALL":
        e.size_x, e.size_y, e.size_z = s
    return e

def sym(mb, co, r, kind="BALL", s=(1, 1, 1), stiff=2.0):
    x, y, z = co
    el(mb, (x, y, z), r, kind, s, stiff)
    el(mb, (-x, y, z), r, kind, s, stiff)

def seg(mb, p0, p1, r0, r1, n, mirror=True):
    for i in range(n + 1):
        t = i / n
        p = Vector(p0).lerp(Vector(p1), t)
        r = r0 + (r1 - r0) * t
        if mirror:
            sym(mb, tuple(p), r)
        else:
            el(mb, tuple(p), r)

def cap(mb, p0, p1, r, mirror=True, stiff=2.0):
    for sx in ((1, -1) if mirror else (1,)):
        a = Vector((p0[0] * sx, p0[1], p0[2])); b = Vector((p1[0] * sx, p1[1], p1[2]))
        e = mb.elements.new(type="CAPSULE")
        e.co = (a + b) / 2
        e.radius = r
        e.stiffness = stiff
        e.size_x = (b - a).length / 2
        e.rotation = Vector((1, 0, 0)).rotation_difference((b - a).normalized())

body_ob, B = metaball("HERO_body", thr=0.5)
E = "ELLIPSOID"
# torso core
el(B, (0, 0, 0.98), 0.17, E, (1.25, 0.85, 1.0))
el(B, (0, 0, 1.09), 0.16, E, (1.1, 0.8, 1.0))
el(B, (0, 0, 1.23), 0.18, E, (1.25, 0.82, 1.0))
el(B, (0, 0, 1.37), 0.19, E, (1.5, 0.85, 0.9))
# pecs, abs, obliques (soft so they blend into the torso)
sym(B, (0.08, -0.06, 1.37), 0.12, E, (1.1, 0.55, 0.7), stiff=1.4)
for z in (1.08, 1.16, 1.24):
    sym(B, (0.04, -0.085, z), 0.06, E, (1.0, 0.5, 0.75), stiff=1.2)
sym(B, (0.125, -0.035, 1.12), 0.08, E, (0.8, 0.8, 1.5), stiff=1.3)
# lats, traps
sym(B, (0.145, 0.03, 1.28), 0.11, E, (0.8, 0.8, 1.5), stiff=1.5)
sym(B, (0.08, 0.02, 1.49), 0.09, stiff=1.5)
# neck
cap(B, (0, 0, 1.49), (0, 0.005, 1.62), 0.085, mirror=False)
# head: rounded dome + broader lower jaw
el(B, (0, 0.005, 1.70), 0.155, E, (0.85, 0.92, 1.05))
el(B, (0, -0.01, 1.635), 0.105, E, (0.92, 0.85, 0.62))
# arms
sym(B, (0.235, 0, 1.445), 0.13)                      # deltoids
cap(B, (0.235, 0, 1.44), (0.33, 0, 1.17), 0.075)    # upper arm
cap(B, (0.33, 0, 1.17), (0.40, 0, 0.95), 0.062)     # forearm
cap(B, (0.40, 0, 0.95), (0.425, -0.005, 0.83), 0.058)  # hand
sym(B, (0.29, -0.03, 1.30), 0.085, E, (1, 1, 1.5), stiff=1.6)  # biceps
sym(B, (0.30, 0.03, 1.31), 0.08, E, (1, 1, 1.5), stiff=1.6)    # triceps
sym(B, (0.35, -0.01, 1.10), 0.08, E, (1, 1, 1.4), stiff=1.6)   # forearm muscle
# hips, glutes
sym(B, (0.10, 0, 0.93), 0.13)
sym(B, (0.085, 0.07, 0.95), 0.12, stiff=1.6)
# legs
cap(B, (0.10, 0, 0.93), (0.115, 0, 0.50), 0.12)     # thigh
sym(B, (0.115, 0, 0.50), 0.09)                       # knee
cap(B, (0.115, 0, 0.50), (0.115, 0.01, 0.09), 0.08) # shin
sym(B, (0.115, -0.025, 0.70), 0.12, E, (1, 1, 1.6), stiff=1.6)  # quads
sym(B, (0.12, 0.03, 0.34), 0.09, E, (1, 1, 1.5), stiff=1.6)     # calves
cap(B, (0.115, 0.0, 0.05), (0.115, -0.12, 0.03), 0.06)          # feet

def to_mesh(ob, mat):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    name = ob.name
    data = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.metaballs.remove(data)
    new = bpy.data.objects.new(name, me)
    char.objects.link(new)
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    return new

body = to_mesh(body_ob, mat_skin)
bm = bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
for _ in range(6):
    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.normal_update()
bm.to_mesh(body.data); bm.free()

# shorts: the body's own hip/thigh surface, trimmed and pushed outward
sm = body.data.copy(); sm.name = "HERO_shorts"
sm.materials.clear(); sm.materials.append(mat_shorts)
bm = bmesh.new(); bm.from_mesh(sm)
g = bm.verts[:] + bm.edges[:] + bm.faces[:]
bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, 1.065), plane_no=(0, 0, 1), clear_outer=True)
g = bm.verts[:] + bm.edges[:] + bm.faces[:]
bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, 0.64), plane_no=(0, 0, 1), clear_inner=True)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if abs(v.co.x) > 0.27], context="VERTS")
bm.normal_update()
for v in bm.verts:
    push = 0.022 + (0.012 * (0.72 - v.co.z) / 0.08 if v.co.z < 0.72 else 0.0)
    v.co += v.normal * push
bm.to_mesh(sm); bm.free()
shorts = bpy.data.objects.new("HERO_shorts", sm)
char.objects.link(shorts)
shorts.modifiers.new("thickness", "SOLIDIFY").thickness = 0.006

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()

def surface(origin, direction):
    hit, loc, nrm, idx, ob, mtx = scene.ray_cast(dg, Vector(origin), Vector(direction))
    return (loc, nrm) if hit else (None, None)

# ---------- eyes ----------
for sx in (1, -1):
    loc, nrm = surface((sx * 0.042, -1.0, 1.715), (0, 1, 0))
    me = bpy.data.meshes.new("eye")
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    bm.to_mesh(me); bm.free()
    eye = bpy.data.objects.new("HERO_eye_%s" % ("L" if sx > 0 else "R"), me)
    char.objects.link(eye)
    eye.location = loc + nrm * 0.002 if loc else (sx * 0.042, -0.1, 1.715)
    eye.scale = (0.018, 0.006, 0.026)
    eye.rotation_mode = "QUATERNION"
    if nrm is not None:
        eye.rotation_quaternion = Vector((0, -1, 0)).rotation_difference(nrm)
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat_eye)

# ---------- wrist tape ----------
for sx in (1, -1):
    a = Vector((sx * 0.384, 0, 1.0)); b = Vector((sx * 0.406, 0, 0.93))
    axis = (b - a).normalized()
    mid = (a + b) / 2
    loc, _ = surface(mid + Vector((sx * 0.3, 0, 0)), (-sx, 0, 0))
    rad = (abs(loc.x - mid.x) + 0.003) if loc else 0.045
    me = bpy.data.meshes.new("tape")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=32, radius1=rad, radius2=rad, depth=0.05)
    bm.to_mesh(me); bm.free()
    tape = bpy.data.objects.new("HERO_tape_%s" % ("L" if sx > 0 else "R"), me)
    char.objects.link(tape)
    tape.location = mid
    tape.rotation_mode = "QUATERNION"
    tape.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(axis)
    tape.modifiers.new("thick", "SOLIDIFY").thickness = 0.006
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat_tape)

# ---------- sheet layout: front + rear instances ----------
lc = bpy.context.view_layer.layer_collection.children[char.name]
lc.exclude = True
for nm, x, rz in (("SHEET_front", -0.56, 0.0), ("SHEET_rear", 0.56, math.pi)):
    inst = bpy.data.objects.new(nm, None)
    inst.instance_type = "COLLECTION"
    inst.instance_collection = char
    inst.location = (x, 0, 0)
    inst.rotation_euler = (0, 0, rz)
    scene.collection.objects.link(inst)

# ---------- camera, light, world, render ----------
cam_data = bpy.data.cameras.new("CAM_sheet")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.45
cam = bpy.data.objects.new("CAM_sheet", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, -10, 0.93)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam

sun_data = bpy.data.lights.new("LGT_key", "SUN")
sun_data.energy = 3.0
sun = bpy.data.objects.new("LGT_key", sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(-20))

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wn = world.node_tree
for n in list(wn.nodes):
    wn.nodes.remove(n)
wout = wn.nodes.new("ShaderNodeOutputWorld")
bg_cam = wn.nodes.new("ShaderNodeBackground"); bg_cam.inputs[0].default_value = (*srgb_to_lin(BG), 1)
bg_amb = wn.nodes.new("ShaderNodeBackground"); bg_amb.inputs[0].default_value = (0.05, 0.05, 0.05, 1)
lp = wn.nodes.new("ShaderNodeLightPath")
wmix = wn.nodes.new("ShaderNodeMixShader")
wn.links.new(lp.outputs["Is Camera Ray"], wmix.inputs[0])
wn.links.new(bg_amb.outputs[0], wmix.inputs[1])
wn.links.new(bg_cam.outputs[0], wmix.inputs[2])
wn.links.new(wmix.outputs[0], wout.inputs["Surface"])

r = scene.render
r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y = 1600, 1440
r.resolution_percentage = 100
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
r.film_transparent = False
r.use_freestyle = True
r.line_thickness_mode = "ABSOLUTE"
r.line_thickness = 3.2
fs = bpy.context.view_layer.freestyle_settings
fs.crease_angle = math.radians(120)
if len(fs.linesets) == 0:
    fs.linesets.new("LS_ink")
for ls in fs.linesets:
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("INK")
    ls.select_by_visibility = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = False
    ls.linestyle.color = (0, 0, 0)
    ls.linestyle.thickness = 3.2
    ls.linestyle.use_length_min = True
    ls.linestyle.length_min = 30.0
try:
    scene.eevee.taa_render_samples = 16
except Exception:
    pass

def render_to(name):
    t = artifacts.file(name=name, media_type="image/png")
    r.filepath = str(t.path)
    r.image_settings.media_type = "IMAGE"
    r.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    t.publish()

render_to("mascot_sheet.png")
dims = body.dimensions
result = {"body_dims": [round(v, 3) for v in dims], "verts": len(body.data.vertices),
          "shorts_verts": len(shorts.data.vertices)}
