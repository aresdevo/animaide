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
from . import utils, cur_utils


global_values = {}


def get_selected(fcurve):
    '''
    Creates a list of selected keys index
    '''

    keys = fcurve.keyframe_points
    keyframe_indexes = []

    if getattr(fcurve.group, 'name', None) == cur_utils.group_name:
        return []  # we don't want to select keys on reference fcurves

    for index, key in keys.items():
        if key.select_control_point:
            keyframe_indexes.append(index)

    return keyframe_indexes


def valid_anim(obj):
    '''
    checks if the obj has an active action
    '''

    anim = obj.animation_data
    action = getattr(anim, 'action', None)
    fcurves = getattr(action, 'fcurves', None)

    return bool(fcurves)


def valid_fcurve(fcurve):
    '''
    Validates an fcurve to see if it can be used with animaide
    '''

    animaide = bpy.context.scene.animaide
    if animaide.slider.affect_non_selected_fcurves is False:
        if fcurve.select is False:
            return False

    if fcurve.lock or fcurve.hide:
        return False
    elif getattr(fcurve.group, 'name', None) == cur_utils.group_name:
        return False  # we don't want to select keys on reference fcurves
    else:
        return True


def set_handle(key, side, delta):

    handle = getattr(key, 'handle_%s' % side, None)
    handle_type = getattr(key, 'handle_%s_type' % side, None)

    if handle_type == 'FREE' or handle_type == 'ALIGNED':
        handle.y = key.co.y - delta


def set_handles(key, lh_delta, rh_delta):
    set_handle(key, 'left', lh_delta)
    set_handle(key, 'right', rh_delta)


def get_sliders_globals(selected=True, original=True, left_frame=None, right_frame=None):
    '''
    Gets all the global values needed to work with the sliders
    '''

    context = bpy.context
    animaide = context.scene.animaide

    if context.space_data.dopesheet.show_only_selected:
        objects = context.selected_objects
    else:
        objects = bpy.data.objects

    for obj in objects:

        if not valid_anim(obj):
            continue

        # Level 1 variables
        # if object.type == 'ARMATURE':
        #     bones = context.selected_pose_bones

        fcurves = obj.animation_data.action.fcurves
        curves = {}

        for fcurve_index, fcurve in fcurves.items():
            # print('fcurve: ', fcurve_index)

            if not valid_fcurve(fcurve):
                continue

            # level 2 variables
            curve_items = {}
            keyframes = []
            values = {}
            every_key = []

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                # stores coordinate of every key
                handles = {'l': key.handle_left.y, 'r': key.handle_right.y}
                co = {'x': key.co.x, 'y': key.co.y}
                values[key_index] = co
                values[key_index]['handles'] = handles

                # stores every key
                every_key.append(key_index)

                # stores only selected keys
                if key.select_control_point:
                    keyframes.append(key_index)

                    # find smooth values (average) of the original keys
            # for key_index in keyframes:

                    key = fcurve.keyframe_points[key_index]

                    if key_index - 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        prevkey_value = key.co.y
                    else:
                        prevkey_value = fcurve.keyframe_points[key_index - 1].co.y

                    if key_index + 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        nextkey_value = key.co.y
                    else:
                        nextkey_value = fcurve.keyframe_points[key_index + 1].co.y

                    # smooth = (prevkey_value + key.co.y + nextkey_value) / 3
                    smooth = (prevkey_value + nextkey_value) / 2
                    values[key_index]['sy'] = smooth

            if keyframes:
                left_neighbor, right_neighbor = get_selected_neigbors(fcurve, keyframes)
            else:
                # what to do if no key is selected

                if animaide.slider.affect_non_selected_keys is True:
                    index = on_current_frame(fcurve)
                    if index is None:
                        keyframes = []
                        left_neighbor = None
                        right_neighbor = None
                    else:
                        keyframes = [index]
                        left_neighbor, right_neighbor = get_frame_neighbors(fcurve, frame=None, clamped=False)
                else:
                    keyframes = []
                    left_neighbor = None
                    right_neighbor = None

            if selected:
                # Store selected keys
                curve_items['selected_keys'] = keyframes

            if left_neighbor is None:
                curve_items['left_neighbor'] = None
            else:
                # stores coordinates of left neighboring key
                co = {'x': left_neighbor.co.x, 'y': left_neighbor.co.y}
                curve_items['left_neighbor'] = co

            if right_neighbor is None:
                curve_items['right_neighbor'] = None
            else:
                # stores coordinates of right neighboring key
                co = {'x': right_neighbor.co.x, 'y': right_neighbor.co.y}
                curve_items['right_neighbor'] = co

            if original:
                # stores original values of every key
                curve_items['original_values'] = values
                curve_items['every_key'] = every_key

            if left_frame is not None or right_frame is not None:
                frames = {'left_y': fcurve.evaluate(left_frame),
                          'right_y': fcurve.evaluate(right_frame)}
                curve_items['ref_frames'] = frames

            curves[fcurve_index] = curve_items

        global_values[obj.name] = curves

    return


def reset_original():
    '''
    Set selected keys to the values in the global variables
    '''

    context = bpy.context

    if context.space_data.dopesheet.show_only_selected is True:
        objects = context.selected_objects
    else:
        objects = context.scene.objects

    for obj in objects:

        if not valid_anim(obj):
            continue

        visible = obj.visible_get()

        if not context.space_data.dopesheet.show_hidden and not visible:
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if not poll_fcurve(context, obj, fcurve):
                continue

            global_fcurve = global_values[obj.name][fcurve_index]

            selected_keys = global_fcurve['selected_keys']
            original_values = global_fcurve['original_values']

            if not selected_keys:
                index = on_current_frame(fcurve)
                if index is None:
                    continue
                selected_keys = [index]

            for index in selected_keys:
                if index is None:
                    continue
                k = fcurve.keyframe_points[index]
                k.co.y = original_values[index]['y']
                k.handle_left.y = original_values[index]['handles']['l']
                k.handle_right.y = original_values[index]['handles']['r']

            fcurve.update()

    return


def on_current_frame(fcurve):
    '''
    returns the index of the key in the current frame
    '''
    current_index = None
    cur_frame = bpy.context.scene.frame_current
    for index, key in fcurve.keyframe_points.items():
        if key.co.x == cur_frame:
            current_index = index
    return current_index


def get_selected_neigbors(fcurve, keyframes):
    '''
    Get the left and right neighboring keys of the selected keys
    '''

    left_neighbor = None
    right_neighbor = None

    if not keyframes:
        index = on_current_frame(fcurve)
        if index is None:
            return left_neighbor, right_neighbor
        keyframes = [index]

    every_key = fcurve.keyframe_points
    # if keyframes.items() == []:
    #     return left_neighbor, right_neighbor
    first_index = keyframes[0]
    i = len(keyframes) - 1
    last_index = keyframes[i]

    if first_index == 0:
        # print('no more keys to the left')
        left_neighbor = every_key[first_index]

    elif first_index > 0:
        left_neighbor = every_key[first_index - 1]

    if last_index == len(fcurve.keyframe_points) - 1:
        # print('no more keys to the right')
        right_neighbor = every_key[last_index]

    elif last_index < len(fcurve.keyframe_points) - 1:
        right_neighbor = every_key[last_index + 1]

    return left_neighbor, right_neighbor


def get_frame_neighbors(fcurve, frame=None, clamped=False):
    '''
    Get neighboring keys of a frame
    '''
    if frame is None:
        frame = bpy.context.scene.frame_current
    fcurve_keys = fcurve.keyframe_points
    left_neighbor = fcurve_keys[0]
    right_neighbor = fcurve_keys[len(fcurve_keys) - 1]

    for key in fcurve.keyframe_points:
        dif = key.co.x - frame
        if dif < 0:
            left = key
            if left.co.x > left_neighbor.co.x:
                left_neighbor = left
        elif dif > 0:
            right = key
            if right.co.x < right_neighbor.co.x:
                right_neighbor = right

    if clamped is False:
        if left_neighbor.co.x == frame:
            left_neighbor = None
        if right_neighbor.co.x == frame:
            right_neighbor = None

    return left_neighbor, right_neighbor


def linear_y(left_neighbor, right_neighbor, key):
    big_adjacent = right_neighbor['x'] - left_neighbor['x']
    big_oposite = right_neighbor['y'] - left_neighbor['y']
    if big_adjacent == 0:
        return
    tangent = big_oposite / big_adjacent

    adjacent = key.co.x - left_neighbor['x']
    oposite = tangent * adjacent
    return left_neighbor['y'] + oposite


def poll_fcurve(context, obj, fcurve):
    if not valid_fcurve(fcurve):
        return

    if (obj.type == 'ARMATURE'):
        # bone_name = utils.get_bone_name(fcurve, usable_bones_names)
        # bone_name = utils.get_bone_name(obj, fcurve)
        #

        if getattr(fcurve.group, 'name', None) == 'Object Transforms':
            # When animating an object, by default its fcurves grouped with this name.
            return
        elif not fcurve.group:
            transforms = (
                'location', 'rotation_euler', 'scale',
                'rotation_quaternion', 'rotation_axis_angle',
                '[\"',  # custom property
            )
            if fcurve.data_path.startswith(transforms):
                # fcurve belongs to the  object, so skip it
                return

        # if fcurve.group.name not in bones_names:
            # return

        split_data_path = fcurve.data_path.split(sep='"')
        bone_name = split_data_path[1]
        bone = obj.data.bones.get(bone_name)

        only_selected = context.space_data.dopesheet.show_only_selected

        if bone is None or bone.hide or (only_selected and not bone.select):
            return

        # if bone_name is None:
            # return

    if getattr(fcurve.group, 'name', None) == cur_utils.group_name:
        return  # we don't want to select keys on reference fcurves

    return True
