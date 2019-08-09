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


from . import cur_utils, key_utils, utils

# Anim_transform global variables

user_preview_range = {}
user_scene_range = {}
user_auto_animate = False


########## Handlers ############


def anim_transform_handlers(scene):
    '''
    Function to be run by the anim_transform Handler
    '''

    # global user_auto_animate

    context = bpy.context

    # user_auto_animate = context.scene.tool_settings.use_keyframe_insert_auto
    #
    context.scene.tool_settings.use_keyframe_insert_auto = False

    selected_objects = context.selected_objects


    # selected_pose_bones = bpy.context.selected_pose_bones
    # usable_bones_names = []


    for obj in selected_objects:

        # obj = context.object
        obj_anim = obj.animation_data

        if obj_anim is None:
            return

        if obj_anim.action.fcurves is None:
            return

        # if obj.type == 'ARMATURE':
        #     usable_bones_names = utils.get_selected_bones_names(obj, selected_pose_bones)

        fcurves = obj_anim.action.fcurves

        for fcurve in fcurves:

            # if obj.type == 'ARMATURE':
                # bone_name = utils.get_bone_name(fcurve, usable_bones_names)

                # if bone_name is None:
                #     continue

            if obj.type == 'ARMATURE':
                split_data_path = fcurve.data_path.split(sep='"')
                bone_name = split_data_path[1]
                bone = obj.data.bones.get(bone_name)

                if bone is None:
                    return

                if bone.hide:
                    return

                if bone.select or bone.parent or bone.children:
                    animation_transform(obj, fcurve)

            else:
                animation_transform(obj, fcurve)

    return


def anim_trans_mask_handlers(scene):
    '''
    function to be run by the mask handler. It will handle the mask dimensions
    '''

    action = None

    if 'animaide' in bpy.data.actions:
        action = bpy.data.actions['animaide']

    if action is None:
        return

    if action.fcurves.items() == []:
        return

    mask = action.fcurves[0]

    modify_anim_trans_mask(mask, mask.keyframe_points)

    return


########## Main tool ############


def animation_transform(obj, fcurve):
    '''
    Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user
    '''

    if fcurve.lock is True:
        return

    if fcurve.group is None:
        return

    if fcurve.group.name == cur_utils.group_name:
        return  # we don't want to select keys on reference fcurves

    mask_curve = None

    if 'animaide' in bpy.data.actions:

        action = bpy.data.actions['animaide']

        if action.fcurves.items() != []:
            mask_curve = action.fcurves[0]

    delta_y = get_anim_transform_delta(obj, fcurve)

    for k in fcurve.keyframe_points:

        if mask_curve is None:
            factor = 1
        else:
            factor = mask_curve.evaluate(k.co.x)

        k.co.y = k.co.y + (delta_y * factor)

    fcurve.update()

    return


def get_anim_transform_delta(obj, fcurve):
    '''
    Determine the transformation change by the user of the current object
    '''

    cur_frame = bpy.context.scene.frame_current

    source = fcurve.evaluate(cur_frame)

    prop = obj.path_resolve(fcurve.data_path)

    try:
        target = prop[fcurve.array_index]
    except TypeError:
        target = prop

    return target - source


########## Mask ############


def set_animaide_action():
    '''
    Creates an "action" called "animaide"
    '''

    if 'animaide' not in bpy.data.actions:
        action = bpy.data.actions.new('animaide')
    else:
        action = bpy.data.actions['animaide']

    return action


def add_animaide_fcurve(action_group, color=(1, 1, 1)):
    '''
    Adds and fcuve in the "animaide" action
    '''

    action = bpy.data.actions['animaide']

    fcurve = action.fcurves.new(data_path='animaide', index=0, action_group=action_group)
    fcurve.color_mode = 'CUSTOM'
    fcurve.color = color

    return fcurve


def add_anim_trans_mask():
    '''
    Add a curve with 4 control pints to an action called "animaide" that would act as a mask for anim_transform
    '''

    store_user_timeline_ranges()

    animaide = bpy.context.scene.animaide

    action = set_animaide_action()

    if action.fcurves.items() == []:
        mask = add_animaide_fcurve(action_group='Magnet')
        keys = mask.keyframe_points
        keys.add(4)
    else:
        action = bpy.data.actions['animaide']
        mask = action.fcurves[0]
        keys = mask.keyframe_points

    modify_anim_trans_mask(mask, keys)

    animaide.anim_transform.use_mask = True

    mask.update()

    return mask


def remove_anim_trans_mask():
    '''
    Removes the fcurve and action that are been used as a mask for anim_transform
    '''

    scene = bpy.context.scene
    animaide = scene.animaide

    if animaide.anim_transform.use_mask is False:
        return

    if 'animaide' not in bpy.data.actions.keys():
        return

    fcurves = bpy.data.actions['animaide'].fcurves

    fcurves.remove(fcurves[0])

    animaide.anim_transform.use_mask = False

    reset_timeline_ranges()


def modify_anim_trans_mask(mask_curve, keys):
    '''
    Modify the position of the fcurve 4 control points that is been used as mask to anim_transform
    '''

    animaide = bpy.context.scene.animaide

    left_margin = animaide.anim_transform.mask_margin_l
    left_blend = animaide.anim_transform.mask_blend_l
    right_margin = animaide.anim_transform.mask_margin_r
    right_blend = animaide.anim_transform.mask_blend_r
    interp = animaide.anim_transform.interp
    easing = animaide.anim_transform.easing

    # when the value of the left_margin is higher than the right_margin then the left_margin becomes
    # the right_margin

    always_left = left_margin
    always_right = right_margin

    if left_margin > right_margin:
        always_left = right_margin
        always_right = left_margin

    if left_blend > 0:
        left_blend = 0

    if right_blend < 0:
        right_blend = 0

    keys[0].co.x = always_left + left_blend
    keys[0].co.y = 0
    keys[1].co.x = always_left
    keys[1].co.y = 1
    keys[2].co.x = always_right
    keys[2].co.y = 1
    keys[3].co.x = always_right + right_blend
    keys[3].co.y = 0

    set_timeline_ranges(left_blend=keys[0].co.x,
                        left_margin=keys[1].co.x,
                        right_margin=keys[2].co.x,
                        right_blend=keys[3].co.x)

    easing_b = easing

    if easing == 'EASE_IN':
        easing_b = 'EASE_OUT'

    if easing == 'EASE_OUT':
        easing_b = 'EASE_IN'

    keys[0].interpolation = interp
    keys[0].easing = easing
    keys[1].interpolation = 'LINEAR'
    keys[1].easing = 'EASE_IN_OUT'
    keys[2].interpolation = interp
    keys[2].easing = easing_b

    mask_curve.lock = True
    mask_curve.select = True


# -------- For mask interface -------


def set_timeline_ranges(left_blend, left_margin, right_margin, right_blend):
    '''
    Use the timeline playback and preview ranges to represent the mask
    '''

    scene = bpy.context.scene
    scene.use_preview_range = True

    scene.frame_preview_start = left_blend
    scene.frame_start = left_margin
    scene.frame_end = right_margin
    scene.frame_preview_end = right_blend


def reset_timeline_ranges():
    '''
    Resets the timeline playback and preview ranges to what the user had it as
    '''

    scene = bpy.context.scene

    scene.frame_preview_start = user_preview_range['start']
    scene.frame_preview_end = user_preview_range['end']
    scene.use_preview_range = user_preview_range['use']
    scene.frame_start = user_scene_range['start']
    scene.frame_end = user_scene_range['end']


def store_user_timeline_ranges():
    '''
    Stores the timeline playback and preview ranges
    '''

    scene = bpy.context.scene

    user_preview_range['start'] = scene.frame_preview_start
    user_preview_range['end'] = scene.frame_preview_end
    user_preview_range['use'] = scene.use_preview_range
    user_scene_range['start'] = scene.frame_start
    user_scene_range['end'] = scene.frame_end


########## Functions for Operators ############


def poll(context):
    '''
    Poll for all the anim_transform related operators
    '''

    objects = context.selected_objects
    obj = context.object
    # space = context.area.spaces.active.type
    area = context.area.type
    # return obj is not None and area == 'GRAPH_EDITOR' and anim is not None
    # return obj is not None and obj.animation_data is not None
    return objects is not None

