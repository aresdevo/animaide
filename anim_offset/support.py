# licence
'''
Copyright (C) 2018 Ares Deveaux


Created by Ares Deveaux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import os
import mathutils as mu
import math

# from utils.key import global_values
from .. import utils, prefe

# Anim_transform global variables

# user_preview_range = {}
# user_scene_range = {}
global_values = {}
last_op = None
current_copy = [None]
frozen_current = None

# ---------- Main Tool ------------


def magnet_handlers(scene):
    """Function to be run by the anim_offset Handler"""

    global last_op

    context = bpy.context
    # scene = context.scene

    external_op = context.active_operator

    if scene.tool_settings.use_keyframe_insert_auto or \
            (context.mode != "OBJECT" and context.mode != "POSE"):

        anim_offset = scene.animaide.anim_offset
        if anim_offset.mask_in_use:
            remove_mask(context)
            reset_timeline_mask(context)

        bpy.app.handlers.depsgraph_update_post.remove(magnet_handlers)
        utils.remove_message()
        return

    animaide = scene.animaide
    anim_offset = animaide.anim_offset

    preferences = context.preferences
    pref = preferences.addons[prefe.addon_name].preferences

    if scene.animaide.anim_offset.mask_in_use:
        cur_frame = scene.frame_current
        if cur_frame < scene.frame_start or cur_frame > scene.frame_end:
            if anim_offset.insert_outside_keys:
                add_keys(context)
            return

    # Doesn't refresh if fast mask is selected:
    # Each time an operator is used is a different one, so this tests
    # if any transform on an object is steel been applied

    # if external_op is last_op and anim_offset.fast_mask:
    if external_op is last_op and pref.ao_fast_offset:
        return
    last_op = context.active_operator

    # context.scene.tool_settings.use_keyframe_insert_auto = False

    selected_objects = context.selected_objects

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)
        fcurves = getattr(action, 'fcurves', list())

        for fcurve in fcurves:

            # ######## Not sure we need this ############
            # if obj.type == 'ARMATURE':
            #     split_data_path = fcurve.data_path.split(sep='"')
            #     bone_name = split_data_path[1]
            #     bone = obj.data.bones.get(bone_name)
            #
            #     if bone is None or bone.hide:
            #         return
            #
            #     if bone.select or bone.parent or bone.children:
            #         magnet(context, obj, fcurve)
            # else:
            magnet(context, obj, fcurve)

    return


def add_keys(context):
    selected_objects = context.selected_objects

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)

        for fcurve in getattr(action, 'fcurves', list()):
            scene = context.scene
            anim_offset = scene.animaide.anim_offset

            if fcurve.lock:
                return

            if getattr(fcurve.group, 'name', None) == 'animaide':
                return  # we don't want to select keys on reference fcurves

            # if context.scene.animaide.anim_offset.mask_in_use:
            #     cur_frame = context.scene.frame_current
            #     if cur_frame < scene.frame_start or cur_frame > scene.frame_end:
            # if anim_offset.insert_outside_keys:
            # if context.area.type == 'GRAPH_EDITOR':
            #     bpy.ops.graph.keyframe_insert(type='ALL')
            # else:
            # bpy.ops.anim.keyframe_insert_menu(type='Available')

            kfps = fcurve.keyframe_points
            cur_index = utils.key.on_current_frame(fcurve)
            delta_y = get_delta(context, obj, fcurve)

            if not cur_index:
                cur_frame = context.scene.frame_current
                y = fcurve.evaluate(cur_frame) + delta_y
                # keys.insert(cur_frame, y)
                utils.key.insert_key(kfps, cur_frame, y)
                # utils.key.add_key(keys, x, y, select=False)
            else:
                kfp = kfps[cur_index]
                kfp.co_ui.y += delta_y


def magnet(context, obj, fcurve):
    """Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user """

    global current_copy, frozen_current

    scene = context.scene

    if fcurve.lock:
        return

    if getattr(fcurve.group, 'name', None) == 'animaide':
        return  # we don't want to select keys on reference fcurves

    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    # delta = get_delta(context, obj, fcurve)

    # frames = global_values[obj.name]['frames']
    cur_frame = context.scene.frame_current
    current_matrix = obj.matrix_local

    if cur_frame != current_copy[0]:
        frozen_current = current_matrix.to_4x4()
        modify_global(obj)

    current_copy = [cur_frame]

    if current_matrix != frozen_current:
        use_matrix = True
    else:
        use_matrix = False

    # for frame in frames:
    #     if frame > cur_frame:
    #         frame_matrix = global_values[obj.name]["kfp_matrix"][frame]
    #         matrix = obj.matrix_local @ frozen_current.inverted() @ frame_matrix

    for kfp in fcurve.keyframe_points:

        # if kfp.co.x > cur_frame:

        if use_matrix:
            frame_matrix = global_values[obj.name]["kfp_matrix"][kfp.co.x]
            # matrix = current_matrix @ frozen_current.inverted() @ frame_matrix
            matrix = None
        else:
            matrix = None

        delta = get_delta(context, obj, fcurve, kfp.co.x, matrix)

        print(f'delta: {delta}')

        if not context.scene.animaide.anim_offset.mask_in_use:
            factor = 1
        elif scene.frame_start <= kfp.co.x <= scene.frame_end:
            factor = 1
        elif blends_curves is not None and len(blends_curves) > 0:
            blends_curve = blends_curves[0]
            factor = blends_curve.evaluate(kfp.co.x)
        else:
            factor = 0

        kfp.co_ui.y = kfp.co_ui.y + (delta * factor)
        # print(f'kfp.co.y: {kfp.co.y}')

    fcurve.update()

    return


def get_frame_vector(kind, frame, channels):
    func = getattr(mu, kind)
    values = []
    if kind == "Vector" or kind == "Euler":
        n = 3
    elif kind == "Quaternion":
        n = 4
    else:
        n = 0

    for n in range(n):
        # values.append(channels[n].keyframe_points[time].co.y)
        values.append(channels[n].evaluate(frame))

    return func(values)


def get_frame_matrix(frame, channels):

    posx = 0
    posy = 0
    posz = 0
    rotx = 0
    roty = 0
    rotz = 0
    rotw = 0
    scax = 0
    scay = 0
    scaz = 0

    for c in channels:
        if c.data_path == 'location':
            # vec = matrix.to_translation()[c.array_index]
            if c.array_index == 0:
                # posx = vec
                posx = c.evaluate(frame)
            elif c.array_index == 1:
                # posy = vec
                posy = c.evaluate(frame)
            elif c.array_index == 2:
                # posz = vec
                posz = c.evaluate(frame)

        if c.data_path == 'rotation_euler':
            # vec = matrix.to_euler()[c.array_index]
            if c.array_index == 0:
                # rotx = vec
                rotx = c.evaluate(frame)
            elif c.array_index == 1:
                # roty = vec
                roty = c.evaluate(frame)
            elif c.array_index == 2:
                # rotz = vec
                rotz = c.evaluate(frame)

        if c.data_path == 'rotation_quaternion':
            # vec = matrix.to_quaternion()[c.array_index]
            if c.array_index == 0:
                # rotw = vec
                rotw = c.evaluate(frame)
            elif c.array_index == 1:
                # rotx = vec
                rotx = c.evaluate(frame)
            elif c.array_index == 2:
                # roty = vec
                roty = c.evaluate(frame)
            elif c.array_index == 3:
                # rotz = vec
                rotz = c.evaluate(frame)

        if c.data_path == 'scale':
            # vec = matrix.to_scale()[c.array_index]
            if c.array_index == 0:
                # scax = vec
                scax = c.evaluate(frame)
            elif c.array_index == 1:
                # scay = vec
                scay = c.evaluate(frame)
            elif c.array_index == 2:
                # scaz = vec
                scaz = c.evaluate(frame)

    # create a location matrix
    mat_loc = mu.Matrix.Translation((posx, posy, posz))

    # create an identitiy matrix
    mat_scax = mu.Matrix.Scale(scax, 4, (1, 0, 0))
    mat_scay = mu.Matrix.Scale(scay, 4, (0, 1, 0))
    mat_scaz = mu.Matrix.Scale(scaz, 4, (0, 0, 1))

    # create a rotation matrix
    mat_rotx = mu.Matrix.Rotation(math.radians(rotx), 4, 'X')
    mat_roty = mu.Matrix.Rotation(math.radians(roty), 4, 'Y')
    mat_rotz = mu.Matrix.Rotation(math.radians(rotz), 4, 'Z')

    # combine transformations
    mat_rot = mat_rotz @ mat_roty @ mat_rotx
    mat_sca = mat_scax @ mat_scay @ mat_scaz
    mat_out = mat_loc @ mat_rot @ mat_sca

    return mat_out


def get_delta_old(context, obj, fcurve):
    """Determine the transformation change by the user of the current object"""

    cur_frame = context.scene.frame_current
    curve_value = fcurve.evaluate(cur_frame)

    try:
        prop = obj.path_resolve(fcurve.data_path)
    except:
        prop = None

    if prop:
        try:
            target = prop[fcurve.array_index]
        except TypeError:
            target = prop
        return target - curve_value
    else:
        return 0


def get_delta(context, obj, fcurve, frame, matrix):
    """Determine the transformation change by the user of the current object"""

    index = fcurve.array_index
    data_path = fcurve.data_path
    print(f'data_path: {data_path}')

    cur_frame = context.scene.frame_current

    if matrix:
        if data_path == 'location':
            prop = matrix.to_translation()[index]
            # new_vector = vecs[0]
        elif data_path == 'rotation_euler':
            prop = matrix.to_euler()[index]
            # new_vector = vecs[1].to_euler()
        elif data_path == 'rotation_quaternion':
            prop = matrix.to_quaternion()[index]
        else:
            prop = matrix.to_scale()
        # if frame < cur_frame:
        #     return 0
    else:
        try:
            prop = obj.path_resolve(data_path)
        except:
            prop = None

    # print(f'vector: {vector}')

    if prop:
        curve_value = fcurve.evaluate(cur_frame)
        try:
            target = prop[index]
        except TypeError:
            target = prop
        return target - curve_value
    else:
        return 0


def get_globals(context):
    global global_values
    selected_objects = context.selected_objects
    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)
        fcurves = getattr(action, 'fcurves', list())
        channels = action.groups['Object Transforms'].channels
        frames = utils.key.frame_summary(fcurves)

        mat = {}
        for fr in frames:
            mat[fr] = get_frame_matrix(fr, channels).to_4x4()

        data = {"kfp_matrix": mat, "frames": frames}
        global_values[obj.name] = data
    print(f'global_values: {global_values}')


def modify_global(obj, start=None):
    global global_values
    action = getattr(obj.animation_data, 'action', None)
    channels = action.groups['Object Transforms'].channels
    frames = global_values[obj.name]['frames']

    for fr in frames:
        if start and fr > start:
            continue
        global_values[obj.name]['kfp_matrix'][fr] = get_frame_matrix(fr, channels).to_4x4()


# ----------- Mask -----------


def set_animaide_action():
    """Creates an "action" called 'animaide'"""

    blends_action = bpy.data.actions.get('animaide')

    if blends_action is None:
        return bpy.data.actions.new('animaide')

    return


def add_animaide_fcurve(action_group, color=(1, 1, 1)):
    """Adds and fcuve in the 'animaide' action"""

    blends_action = bpy.data.actions.get('animaide')

    if blends_action is None:
        return

    if len(blends_action.fcurves) == 0:
        blends_curve = blends_action.fcurves.new(data_path='animaide', index=0, action_group=action_group)
        blends_curve.color_mode = 'CUSTOM'
        blends_curve.color = color
    else:
        blends_curve = blends_action.fcurves[0]

    return blends_curve


def add_blends():
    """Add a curve with 4 control pints to an action called 'animaide' that would act as a mask for anim_offset"""

    set_animaide_action()
    blends_curve = add_animaide_fcurve(action_group='Magnet')
    keys = blends_curve.keyframe_points
    if len(keys) == 0:
        keys.add(4)

    blends_curve.lock = True
    blends_curve.select = True
    blends_curve.update() # check if I need to add irmita's key function
    return blends_curve


def remove_mask(context):
    """Removes the fcurve and action that are been used as a mask for anim_offset"""

    anim_offset = context.scene.animaide.anim_offset
    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    anim_offset.mask_in_use = False
    if blends_curves is not None and len(blends_curves) > 0:
        blends_curves.remove(blends_curves[0])
        # reset_timeline_mask(context)

    return


def set_blend_values(context):
    """Modify the position of the fcurve 4 control points that is been used as mask to anim_offset """

    scene = context.scene
    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    if blends_curves is not None:
        blend_curve = blends_curves[0]
        keys = blend_curve.keyframe_points

        left_blend = scene.frame_preview_start
        left_margin = scene.frame_start
        right_margin = scene.frame_end
        right_blend = scene.frame_preview_end

        keys[0].co.x = left_blend
        keys[0].co.y = 0
        keys[1].co.x = left_margin
        keys[1].co.y = 1
        keys[2].co.x = right_margin
        keys[2].co.y = 1
        keys[3].co.x = right_blend
        keys[3].co.y = 0

        mask_interpolation(keys, context)


def mask_interpolation(keys, context):
    anim_offset = context.scene.animaide.anim_offset
    interp = anim_offset.interp
    easing = anim_offset.easing

    oposite = None

    if easing == 'EASE_IN':
        oposite = 'EASE_OUT'
    elif easing == 'EASE_OUT':
        oposite = 'EASE_IN'
    elif easing == 'EASE_IN_OUT':
        oposite = 'EASE_IN_OUT'

    keys[0].interpolation = interp
    keys[0].easing = easing
    keys[1].interpolation = 'LINEAR'
    keys[1].easing = 'EASE_IN_OUT'
    keys[2].interpolation = interp
    keys[2].easing = oposite


# -------- For mask interface -------


def set_timeline_ranges(context, left_blend, left_margin, right_margin, right_blend):
    """Use the timeline playback and preview ranges to represent the mask"""

    scene = context.scene
    scene.use_preview_range = True

    scene.frame_preview_start = left_blend
    scene.frame_start = left_margin
    scene.frame_end = right_margin
    scene.frame_preview_end = right_blend


def reset_timeline_mask(context):
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = context.scene
    anim_offset = scene.animaide.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use
    scene.frame_start = anim_offset.user_scene_start
    scene.frame_end = anim_offset.user_scene_end
    # scene.tool_settings.use_keyframe_insert_auto = anim_offset.user_scene_auto


def reset_timeline_blends(context):
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = context.scene
    anim_offset = scene.animaide.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use


def store_user_timeline_ranges(context):
    """Stores the timeline playback and preview ranges"""

    scene = context.scene
    anim_offset = scene.animaide.anim_offset

    anim_offset.user_preview_start = scene.frame_preview_start
    anim_offset.user_preview_end = scene.frame_preview_end
    anim_offset.user_preview_use = scene.use_preview_range
    anim_offset.user_scene_start = scene.frame_start
    anim_offset.user_scene_end = scene.frame_end
    # anim_offset.user_scene_auto = scene.tool_settings.use_keyframe_insert_auto


# ---------- Functions for Operators ------------


def poll(context):
    """Poll for all the anim_offset related operators"""

    objects = context.selected_objects
    area = context.area.type
    return objects is not None and area == 'GRAPH_EDITOR' or area == 'DOPESHEET_EDITOR' or area == 'VIEW_3D'


def get_anim_offset_globals(context, obj):
    """Get global values for the anim_offset"""

    anim = obj.animation_data
    if anim is None:
        return
    if anim.action.fcurves is None:
        return

    fcurves = obj.animation_data.action.fcurves

    curves = {}

    for fcurve_index, fcurve in fcurves.items():

        if fcurve.lock is True:
            continue

        cur_frame = context.scene.frame_current
        cur_frame_y = fcurve.evaluate(cur_frame)

        values = {'x': cur_frame, 'y': cur_frame_y}

        curves[fcurve_index]['current_frame'] = values

    global_values[obj.name] = curves


