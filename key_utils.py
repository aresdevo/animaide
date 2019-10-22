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


def set_type(objects, kind):
    '''
    Sets key type
    '''

    if kind == 'KEYFRAME' or kind == 'BREAKDOWN' or kind == 'JITTER':

        if objects is None:
            return

        for obj in objects:
            action = obj.animation_data.action

            for fcurve in action.fcurves:

                # if fcurve.select is False:
                #     continue
                #
                # if fcurve.hide is True:
                #     continue

                selected_keys = get_selected(fcurve)

                if not selected_keys:
                    continue

                for index in selected_keys:
                    key = fcurve.keyframe_points[index]
                    print(kind)
                    key.type = kind


def move_right_left(objects, amount, direction='RIGHT', lock=True):
    '''
    move keys horizontaly
    '''

    if objects is None:
        return

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if not fcurve.select or fcurve.hide:
                continue

            selected_keys = get_selected(fcurve)

            if not selected_keys:
                current_index = on_current_frame(fcurve)
                current_key = fcurve.keyframe_points[current_index]
                left_neighbor, right_neighbor = get_frame_neighbors(fcurve)
                # left_key, right_key, left_neighbor, right_neighbor = \
                #     first_and_last_selected(fcurve, neighbors=True)

                if current_key is None:
                    if direction == 'LEFT':
                        key = right_neighbor
                        key.co.x = bpy.context.scene.frame_current
                    if direction == 'RIGHT':
                        key = left_neighbor
                        key.co.x = bpy.context.scene.frame_current
                else:
                    if lock is True:
                        if direction == 'LEFT' and left_neighbor is not None:
                            if current_key.co.x - amount <= left_neighbor.co.x:
                                return
                        if direction == 'RIGHT' and right_neighbor is not None:
                            if current_key.co.x + amount >= right_neighbor.co.x:
                                return
                    move(fcurve, current_key, amount, direction)
            else:
                if lock is True:
                    left_neighbor, right_neighbor = get_selected_neigbors(fcurve, selected_keys)
                    left_key, right_key = first_and_last_selected(fcurve, selected_keys)

                    if direction == 'LEFT' and left_neighbor is not None:
                        print('left_key ', left_key.co.x)
                        print('left_margin', left_neighbor.co.x)
                        if left_key.co.x - amount <= left_neighbor.co.x:
                            return

                    if direction == 'RIGHT' and right_neighbor is not None:
                        print('right_key ', right_key.co.x)
                        print('right_margin', right_neighbor.co.x)
                        if right_key.co.x + amount >= right_neighbor.co.x:
                            return
                for index, key in selected_keys:
                    move(fcurve, key, amount, direction)

            fcurve.update()


def move(fcurve, key, amount, direction='RIGHT'):
    '''
    moves keys
    '''

    # left_neighbor, right_neighbor = get_current_key_neighbors(fcurve, key.co.x)
    selected_keys = get_selected(fcurve)
    left_neighbor, right_neighbor = get_selected_neigbors(fcurve, selected_keys)

    if direction == 'UP':
        key.co.y = key.co.y + amount

    elif direction == 'DOWN':
        key.co.y = key.co.y - amount

    elif direction == 'LEFT':
        key.co.x = key.co.x - int(amount)
        if left_neighbor is not None:
            if key.co.x == left_neighbor.co.x:
                key.co.x = key.co.x - int(amount) - 1
            if key.co.x < left_neighbor.co.x:
                key = swap(key, left_neighbor)
        bpy.context.scene.frame_current = key.co.x

    elif direction == 'RIGHT':
        key.co.x = key.co.x + int(amount)
        if right_neighbor is not None:
            if key.co.x == right_neighbor.co.x:
                key.co.x = key.co.x + int(amount) + 1
            if key.co.x > right_neighbor.co.x:
                key = swap(key, right_neighbor)
        bpy.context.scene.frame_current = key.co.x


def swap(key1, key2):
    '''
    Keys1 become key2 and key2 becomes key1
    '''

    def change_selection(keytochange, Bool):
        setattr(keytochange, 'select_control_point', Bool)
        setattr(keytochange, 'select_left_handle', Bool)
        setattr(keytochange, 'select_right_handle', Bool)

    for l in ('x', 'y'):

        k1 = getattr(key1.co, l)
        k2 = getattr(key2.co, l)

        setattr(key1.co, l, k2)
        setattr(key2.co, l, k1)

    if key1.select_control_point is True:
        change_selection(key1, False)
        change_selection(key2, True)

    return key2


def set_frame(key, str):
    '''
    sets the time of the current key to the numeric value of "str"
    if "+" or "-" is used the it will perform the corresponding math operation
    '''

    key_frame = key.co.x
    if str.startswith('+'):
        rest = str[1:]
        if rest.isnumeric():
            return key_frame + int(rest)
    elif str.startswith('-'):
        rest = str[1:]
        if rest.isnumeric():
            return key_frame - int(rest)
    elif str.isnumeric():
        return int[str]
    else:
        return key_frame


def set_value(key, str):
    '''
    sets the value of the current key to the numeric value of "str"
    if "+" or "-" is used the it will perform the corresponding math operation
    '''

    key_value = key.co.y
    if str.startswith('+'):
        rest = str[1:]
        if rest.isnumeric():
            return key_value + float(rest)
    elif str.startswith('-'):
        rest = str[1:]
        if rest.isnumeric():
            return key_value - float(rest)
    elif str.isnumeric():
        return float[str]
    else:
        return key_value


def set_interpolation(objects, interpolation='BEZIER', easing='AUTO', back=2.0, period=1.0, amplitude=4.0):
    '''
    sets interpolation of the selected keys
    '''

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            selected_keys = get_selected(fcurve)

            for index in selected_keys:
                key = fcurve.keyframe_points[index]
                key.interpolation = interpolation
                key.easing = easing
                key.back = back
                key.period = period
                key.amplitude = amplitude


def select_handle(key, left=None, right=None, control_point=None):
    '''
    selects handles of chosen key
    '''

    animaide = bpy.context.scene.animaide
    key_helpers = animaide.key_helpers

    if left is not None:
        key.select_left_handle = left
    if right is not None:
        key.select_right_handle = right
    if control_point is not None:
        print('key_helpers.control_point:', key_helpers.control_point)
        print('control_point --->', control_point)
        if control_point is False:
            print('@@@@@@', key_helpers.tmp_cps)
            key_helpers.tmp_cps.append((0, key))
        # else:
        #     key_helpers['tmp_cps'] = []
        key.select_control_point = control_point


def handles(objects, act_on='ALL', left=None, right=None, control_point=None, handle_type=None):
    '''
    lets you select or unselect either handel or control point of a key
    '''

    animaide = bpy.context.scene.animaide
    key_helpers = animaide.key_helpers

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            # first_key, last_key = first_and_last_selected(fcurve)
            first_key = fcurve.keyframe_points[0]
            last_index = len(fcurve.keyframe_points) - 1
            last_key = fcurve.keyframe_points[last_index]

            selected_keys = get_selected(fcurve)

            print(selected_keys)

            if act_on == 'SELECTION':
                if not selected_keys:
                    if key_helpers.tmp_cps is not []:
                        selected_keys = key_helpers.tmp_cps
                    else:
                        continue

                for index in selected_keys:
                    key = fcurve.keyframe_points[index]
                    print('Selection')
                    if left is not None:
                        select_handle(key, left=left)

                    if right is not None:
                        select_handle(key, right=right)
                    print('key_helpers.control_point in main function:', key_helpers.control_point)
                    print('control_point in main function:', control_point)
                    if control_point is not None:
                        select_handle(key, control_point=control_point)

                    if handle_type is not None:
                        handle_set_type(key, left=left, right=right, handle_type=handle_type)

            elif handle_type is not None:
                kwargs = dict(left=True, right=True, handle_type=handle_type)
                if act_on == 'ALL':
                    for index, key in fcurve.keyframe_points.items():
                        print('all')
                        handle_set_type(key, **kwargs)
                elif act_on == 'FIRST':
                    print('first')
                    handle_set_type(first_key, **kwargs)
                elif act_on == 'LAST':
                    print('last')
                    handle_set_type(last_key, **kwargs)
                elif act_on == 'BOTH':
                    print('both')
                    handle_set_type(last_key, **kwargs)
                    handle_set_type(first_key, **kwargs)

            fcurve.update()


def handle_manipulate(key, left=None, right=None, length=None):
    '''
    set length of a key handles
    '''

    if length is None:
        return

    if left is True:
        key.handle_left.length = length

    if right is True:
        key.handle_right.length = length


def handle_set_type(key, left=True, right=True, handle_type='AUTO_CLAMPED'):
    '''
    set "type" of a key handles
    '''

    if left is True:
        key.handle_left_type = handle_type

    if right is True:
        key.handle_right_type = handle_type


def attach_selection_to_fcurve(fcurve, target_fcurve, factor=1.0, is_gradual=True):
    '''
    Match "y" value of selected keys to the value o target_fcurve
    '''

    selected_keys = get_selected(fcurve)

    for index in selected_keys:

        key = fcurve.keyframe_points[index]

        attach_to_fcurve(key, key, target_fcurve, factor=factor, is_gradual=is_gradual)


def attach_to_fcurve(key, source_key, target_fcurve, factor=1.0, is_gradual=True):
    '''
    Match "y" value of a key to the value o target_fcurve
    '''

    target_y = target_fcurve.evaluate(key.co.x)

    if is_gradual is True:
        key.co.y = utils.gradual(source_key.co.y, target_y, factor=factor)

    else:
        key.co.y = target_y

    # print('key "y" value:', key.co.y)


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

            if not keyframes:
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

            else:
                left_neighbor, right_neighbor = get_selected_neigbors(fcurve, keyframes)

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


def get_ref_frame_globals(left_ref_frame, right_ref_frame):
    '''
    Get global values for the reference frames
    '''

    objects = bpy.context.selected_objects

    for obj in objects:
        anim = obj.animation_data
        if anim is None:
            continue
        if anim.action.fcurves is None:
            continue
        fcurves = obj.animation_data.action.fcurves

        curves = {}
        ref_frames = {}

        for fcurve_index, fcurve in fcurves.items():
            frames = {}

            if fcurve.select is False:
                continue

            if fcurve.lock is True:
                continue

            if fcurve.hide is True:
                continue

            frames['left_y'] = fcurve.evaluate(left_ref_frame)
            frames['right_y'] = fcurve.evaluate(right_ref_frame)

            curves[fcurve_index]['ref_frames'] = frames

        if curves != {}:
            global_values[obj.name] = curves


def get_anim_transform_globals(object):
    '''
    Get global values for the anim_transform
    '''

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


def reset_original():
    '''
    Set selected keys to the values in the global variables
    '''

    objects = bpy.context.selected_objects

    for obj in objects:
        anim = obj.animation_data
        if anim is None:
            pass
        if anim.action.fcurves is None:
            pass
        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():

            if fcurve.select is False:
                continue

            if fcurve.lock is True:
                continue

            if fcurve.hide is True:
                continue

            selected_keys = global_values[obj.name][fcurve_index]['selected_keys']
            original_values = global_values[obj.name][fcurve_index]['original_values']

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


def first_and_last_selected(fcurve, keyframes):
    '''
    Given a list of keys it returns the first and last keys.
    If an fcurve is supplied just the keys of that curve are taken into consideration
    '''

    every_key = fcurve.keyframe_points

    if not keyframes:
        index = on_current_frame(fcurve)
        if index is None:
            return
        keyframes = [index]

    print('keyframes', keyframes)

    first_index = keyframes[0]
    print('first index', first_index)
    first_key = every_key[first_index]

    # i = len(keyframes) - 1
    last_index = keyframes[-1]
    print('last index', last_index)
    last_key = every_key[last_index]

    return first_key, last_key


def set_mode(fcurve, mode='AUTO_CLAMPED'):
    '''
    Sets the handle type of the selected keys
    '''
    selected_keys = get_selected(fcurve)
    if selected_keys is not None:
        for index in selected_keys:
            key = fcurve.keyframe_points[index]
            key.handle_right_type = mode
            key.handle_left_type = mode


def delete(objects, kind=None):
    '''
    Deletes keys if they match the type in "kind"
    '''
    # selected_keys = get_selected(fcurve, reverse=False)
    # selected_keys.sort(reverse=True)
    if objects is None:
        return

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            # if fcurve.select is False:
            #     continue
            #
            # if fcurve.hide is True:
            #     continue

            keys = fcurve.keyframe_points
            index = 0
            for n in range(len(keys)):
                if index > len(keys) - 1:
                    break

                print('index: ', index)
                key = keys[index]

                print('selected: ', key.select_control_point)

                if key.select_control_point is False:
                    print('not selected')
                    index += 1
                    continue

                print('kind: ', kind)
                print('key.type: ', key.type)

                if kind is None:
                    print('delete for None')
                    obj.keyframe_delete(fcurve.data_path,
                                        fcurve.array_index,
                                        key.co.x,
                                        fcurve.group.name)
                elif \
                        kind == 'KEYFRAME' or \
                        kind == 'BREAKDOWN' or \
                        kind == 'JITTER':
                    if key.type == kind:
                        print('delete for ', kind)
                        obj.keyframe_delete(fcurve.data_path,
                                            fcurve.array_index,
                                            key.co.x,
                                            fcurve.group.name)
                    else:
                        index += 1
                fcurve.update()


def copy_value(keyframes, reference_key):
    '''
    Copy value of "referece_key" to "keyframes"
    '''
    for index, key in keyframes:
        key.co.y = reference_key.co.y


def flatten(objects, side):
    '''
    Match the value of the selected keys to the neighboring key to the "side"
    '''
    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if getattr(fcurve.group, 'name', None) == cur_utils.group_name:
                continue  # we don't want to add to the list the helper curves we have created

            if fcurve.select is False:
                continue

            selected_keys = get_selected(fcurve)

            if not selected_keys:
                index = on_current_frame(fcurve)
                selected_keys = [index]

            left_neighbor, right_neighbor = get_selected_neigbors(fcurve, selected_keys)

            if side == 'LEFT':
                # this fixes the problem of the fist key moving (just happens with this one)
                # if selected_keys[0][1] != fcurve.keyframe_points[0]:
                #     copy_value(selected_keys, left_neighbor)  # if there is no key on the left then it uses itself
                # else:
                copy_value(selected_keys, fcurve.keyframe_points[0])

            elif side == 'RIGHT':
                copy_value(selected_keys, right_neighbor)

            fcurve.update()


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


def get_index_neighbors(fcurve, index, clamped=False):
    '''
    Get the neighboring keys of a key given index
    '''
    left_neighbor = fcurve.keyframe_points[utils.floor(index - 1, 0)]
    right_neighbor = fcurve.keyframe_points[utils.ceiling(index + 1, len(fcurve.keyframe_points) - 1)]

    # if clamped is False:
    #     if left_neighbor == fcurve.keyframe_points[0]:
    #         left_neighbor = None
    #     if right_neighbor == fcurve.keyframe_points[len(fcurve.keyframe_points) - 1]:
    #         right_neighbor = None

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


def calculate_delta(key, previous_key, next_key):

    frames_gap = abs(next_key.co.x - previous_key.co.x)  # frames between keys
    key_pos = abs(key.co.x - previous_key.co.x)  # frame position of the key in question

    if frames_gap == 0:  # not to devided by zero
        return 0
    if key_pos == 0:
        return 0.25     # in the case of the fist or last key
    else:
        return ((key_pos * 100) / frames_gap) / 100


def switch_aim(aim, factor):
    if factor < 0.5:
        aim = aim * -1
    return aim


def set_direction(factor, left_key, right_key):
    if factor < 0:
        next_key = left_key
        previous_key = right_key
    else:
        next_key = right_key
        previous_key = left_key

    return previous_key, next_key


def linear_y(left_neighbor, right_neighbor, key):
    big_adjacent = right_neighbor['x'] - left_neighbor['x']
    big_oposite = right_neighbor['y'] - left_neighbor['y']
    if big_adjacent == 0:
        return
    tangent = big_oposite/big_adjacent

    adjacent = key.co.x - left_neighbor['x']
    oposite = tangent * adjacent
    return left_neighbor['y'] + oposite


