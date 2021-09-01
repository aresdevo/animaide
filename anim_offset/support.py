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

# from utils.key import global_values
from .. import utils, prefe

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

    external_op = context.active_operator

    if context.scene.tool_settings.use_keyframe_insert_auto or \
            (context.mode != "OBJECT" and context.mode != "POSE"):

        anim_offset = scene.animaide.anim_offset
        if anim_offset.mask_in_use:
            remove_mask(context)
            reset_timeline_mask(context)

        bpy.app.handlers.depsgraph_update_post.remove(magnet_handlers)
        utils.remove_message()
        return

    animaide = context.scene.animaide
    anim_offset = animaide.anim_offset

    preferences = context.preferences
    pref = preferences.addons[prefe.addon_name].preferences

    if context.scene.animaide.anim_offset.mask_in_use:
        cur_frame = context.scene.frame_current
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

        for fcurve in getattr(action, 'fcurves', list()):
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

            keys = fcurve.keyframe_points
            cur_index = utils.key.on_current_frame(fcurve)
            delta_y = get_delta(context, obj, fcurve)

            if not cur_index:
                cur_frame = context.scene.frame_current
                y = fcurve.evaluate(cur_frame) + delta_y
                # keys.insert(cur_frame, y)
                utils.key.insert_key(keys, cur_frame, y)
                # utils.key.add_key(keys, x, y, select=False)
            else:
                key = keys[cur_index]
                key.co_ui.y += delta_y


def magnet(context, obj, fcurve):
    """Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user """

    scene = context.scene

    if fcurve.lock:
        return

    if getattr(fcurve.group, 'name', None) == 'animaide':
        return  # we don't want to select keys on reference fcurves

    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)

    delta_y = get_delta(context, obj, fcurve)

    for k in fcurve.keyframe_points:
        if not context.scene.animaide.anim_offset.mask_in_use:
            factor = 1
        elif scene.frame_start <= k.co.x <= scene.frame_end:
            factor = 1
        elif blends_curves is not None and len(blends_curves) > 0:
            blends_curve = blends_curves[0]
            factor = blends_curve.evaluate(k.co.x)
        else:
            factor = 0

        k.co_ui.y = k.co_ui.y + (delta_y * factor)

    fcurve.update()

    return


def get_delta(context, obj, fcurve):
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


