import bpy
import os

# from utils.key import global_values
from .. import utils

# Anim_transform global variables

user_preview_range = {}
user_scene_range = {}
global_values = {}
last_op = None

# ---------- Main Tool ------------


def magnet_handlers(scene):
    """Function to be run by the anim_offset Handler"""
    global last_op

    context = bpy.context

    external_op = bpy.context.active_operator

    animaide = context.scene.animaide
    anim_offset = animaide.anim_offset

    if bpy.context.scene.animaide.anim_offset.mask_in_use:
        left_margin = scene.frame_start
        right_margin = scene.frame_end
        cur_frame = bpy.context.scene.frame_current
        if cur_frame < left_margin or cur_frame > right_margin:
            if anim_offset.insert_outside_keys:
                autokey = True
            else:
                autokey = False
            context.scene.tool_settings.use_keyframe_insert_auto = autokey
            return

    # Doesn't refresh if fast mask is selected:
    # Each time an operator is used is a different one, so this tests
    # if any transform on an object is steel been applied
    if external_op is last_op and anim_offset.fast_mask:
        return
    last_op = bpy.context.active_operator

    context.scene.tool_settings.use_keyframe_insert_auto = False

    selected_objects = context.selected_objects

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)

        for fcurve in getattr(action, 'fcurves', list()):
            # ######### Not sure we need this part ##########
            # if obj.type == 'ARMATURE':
            #     split_data_path = fcurve.data_path.split(sep='"')
            #     bone_name = split_data_path[1]
            #     bone = obj.data.bones.get(bone_name)
            #
            #     if not bone:
            #         return
            #
            #     if bone.select or bone.parent or bone.children:
            #         magnet(obj, fcurve, scene)
            # else:
            magnet(obj, fcurve, scene)

    return


def magnet(obj, fcurve, scene):
    """Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user"""

    if fcurve.lock:
        return

    if getattr(fcurve.group, 'name', None) == 'animaide':
        return  # we don't want to select keys on reference fcurves

    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    delta_y = get_delta(obj, fcurve)

    for k in fcurve.keyframe_points:
        if not bpy.context.scene.animaide.anim_offset.mask_in_use:
            factor = 1
        elif scene.frame_start <= k.co.x <= scene.frame_end:
            factor = 1
        elif blends_curves is not None and len(blends_curves) > 0:
            blends_curve = blends_curves[0]
            factor = blends_curve.evaluate(k.co.x)
        else:
            factor = 0

        k.co.y = k.co.y + (delta_y * factor)

    fcurve.update()

    return


def get_delta(obj, fcurve):
    """Determine the transformation change by the user of the current object"""

    cur_frame = bpy.context.scene.frame_current
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
    if len(keys) is 0:
        keys.add(4)

    blends_curve.lock = True
    blends_curve.select = True
    blends_curve.update() # check if I need to add irmita's key function
    return blends_curve


def remove_mask():
    """Removes the fcurve and action that are been used as a mask for anim_offset"""

    anim_offset = bpy.context.scene.animaide.anim_offset
    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    anim_offset.mask_in_use = False
    if blends_curves is not None and len(blends_curves) > 0:
        blends_curves.remove(blends_curves[0])
        reset_timeline_mask()

    return


def set_blend_values():
    """Modify the position of the fcurve 4 control points that is been used as mask to anim_offset"""

    scene = bpy.context.scene
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

        mask_interpolation(keys)


def mask_interpolation(keys):
    anim_offset = bpy.context.scene.animaide.anim_offset
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


def set_timeline_ranges(left_blend, left_margin, right_margin, right_blend):
    """Use the timeline playback and preview ranges to represent the mask"""

    scene = bpy.context.scene
    scene.use_preview_range = True

    scene.frame_preview_start = left_blend
    scene.frame_start = left_margin
    scene.frame_end = right_margin
    scene.frame_preview_end = right_blend


def reset_timeline_mask():
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = bpy.context.scene
    anim_offset = scene.animaide.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use
    scene.frame_start = anim_offset.user_scene_start
    scene.frame_end = anim_offset.user_scene_end
    # scene.tool_settings.use_keyframe_insert_auto = anim_offset.user_scene_auto


def reset_timeline_blends():
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = bpy.context.scene
    anim_offset = scene.animaide.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use


def store_user_timeline_ranges():
    """Stores the timeline playback and preview ranges"""

    scene = bpy.context.scene
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
    return objects is not None and area == 'GRAPH_EDITOR' or area == 'DOPESHEET_EDITOR'


def get_anim_offset_globals(object):
    """Get global values for the anim_offset"""

    anim = object.animation_data
    if anim is None:
        return
    if anim.action.fcurves is None:
        return

    fcurves = object.animation_data.action.fcurves

    curves = {}

    for fcurve_index, fcurve in fcurves.items():

        if fcurve.lock is True:
            continue

        cur_frame = bpy.context.scene.frame_current
        cur_frame_y = fcurve.evaluate(cur_frame)

        values = {'x': cur_frame, 'y': cur_frame_y}

        curves[fcurve_index]['current_frame'] = values

    global_values[object.name] = curves


