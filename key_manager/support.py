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

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors

from .. import utils


last_op = None
external_op = None


def set_type(context, key_type):
    """Sets key type"""

    if key_type == 'KEYFRAME' or key_type == 'BREAKDOWN' or key_type == 'JITTER' or key_type == 'EXTREME':

        objects = context.selected_objects

        if objects is None:
            return

        for obj in objects:
            if not utils.curve.valid_obj(context, obj):
                continue

            some_selected_key = utils.key.some_selected_key(context, obj)

            fcurves = obj.animation_data.action.fcurves

            for fcurve in fcurves:
                if not utils.curve.valid_fcurve(context, obj, fcurve):
                    continue

                selected_keys = utils.key.get_selected_index(fcurve)
                cursor_index = utils.key.on_current_frame(fcurve)

                if selected_keys:
                    for index in selected_keys:
                        key = fcurve.keyframe_points[index]
                        key.type = key_type

                elif not some_selected_key:
                    if cursor_index:
                        key = fcurve.keyframe_points[cursor_index]
                        key.type = key_type

                    else:
                        add_key_type(context, fcurve, key_type)

                fcurve.keyframe_points.sort()
                fcurve.keyframe_points.handles_recalc()


def add_key_type(context, fcurve, key_type):
    keys = fcurve.keyframe_points
    cur_frame = context.scene.frame_current
    left, right = utils.key.get_frame_neighbors(fcurve, cur_frame)
    if left:
        interp = left.interpolation
    elif right:
        interp = right.interpolation
    else:
        interp = 'BEZIER'

    x = cur_frame
    y = fcurve.evaluate(cur_frame)
    key = utils.key.add_key(keys, x, y, select=False)
    key.interpolation = interp
    key.type = key_type

    fcurve.keyframe_points.sort()
    fcurve.keyframe_points.handles_recalc()


def change_frame(context, amount, direction='RIGHT'):
    """move keys horizontally"""

    def can_move(l_limit, r_limit, most_l, most_r):
        if l_limit and most_l != l_limit and most_l + amount <= l_limit:
            return False
        elif r_limit and most_r != r_limit and most_r + amount >= r_limit:
            return False
        else:
            return True

    objects = context.selected_objects

    if not objects:
        return

    if direction == 'LEFT':
        amount = -int(amount)
    else:
        amount = int(amount)

    frames = amount

    some_selected_key = utils.key.some_selected_keys_in_objects(context, objects)

    bounding_box = utils.key.selected_bounding_box(context, objects, some_selected_key)

    most_left = bounding_box[0]
    most_right = bounding_box[1]
    left_limit = bounding_box[2]
    right_limit = bounding_box[3]
    lonely_cursor = bounding_box[4]

    mid = most_left + ((most_right - most_left)/2)

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve in fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            selected_keys = utils.key.get_selected_index(fcurve)

            if selected_keys:
                if not can_move(left_limit, right_limit, most_left, most_right):
                    return
                for index in selected_keys:
                    key = fcurve.keyframe_points[index]
                    key.co.x += amount
                    fcurve.keyframe_points.sort()
                    fcurve.keyframe_points.handles_recalc()
                frames = 0

            elif not some_selected_key:
                index = utils.key.on_current_frame(fcurve)
                if index is not None:
                    if not can_move(left_limit, right_limit, most_left, most_right):
                        return
                    key = fcurve.keyframe_points[index]
                    key.co.x += amount
                    frames = amount
                    fcurve.keyframe_points.sort()
                    fcurve.keyframe_points.handles_recalc()

    if lonely_cursor and not some_selected_key:
        if direction == 'LEFT' and left_limit:
            context.scene.frame_current = int(left_limit)
        elif direction == 'RIGHT' and right_limit:
            context.scene.frame_current = int(right_limit)
    elif some_selected_key:
        context.scene.frame_current = int(mid + amount)
    else:
        context.scene.frame_current += int(frames)


def insert_frames(context, amount):
    """insert frames between keys"""

    def can_move(meta, margen):
        if meta and meta != margen and margen + amount <= meta:
            return False
        else:
            return True

    objects = context.selected_objects

    if not objects:
        return

    current_frame = context.scene.frame_current

    some_selected_key = utils.key.some_selected_keys_in_objects(context, objects)

    bounding_box = utils.key.selected_bounding_box(context, objects, some_selected_key)

    most_left = bounding_box[0]
    most_right = bounding_box[1]
    left_limit = bounding_box[2]
    right_limit = bounding_box[3]
    lonely_cursor = bounding_box[4]

    def displace_keys(anchor_frame):
        for key in fcurve.keyframe_points:
            if key.co_ui.x <= anchor_frame:
                continue

            if key.co_ui.x + amount <= anchor_frame:
                break

            key.co_ui.x += amount

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        some_selected_key = utils.key.some_selected_key(context, obj)

        fcurves = obj.animation_data.action.fcurves

        for fcurve in fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            selected_keys = utils.key.get_selected_index(fcurve)

            if selected_keys:
                if not can_move(most_right, right_limit):
                    return
                for selected_i in selected_keys:
                    selected_k = fcurve.keyframe_points[selected_i]
                    displace_keys(selected_k.co_ui.x)
                    # displace_keys(most_left)
            elif not some_selected_key:
                if not can_move(current_frame, right_limit):
                    return
                displace_keys(current_frame)

            fcurve.keyframe_points.sort()
            fcurve.keyframe_points.handles_recalc()


def set_handles_type(context, act_on='SELECTION', handle_type='NONE', check_ui=True):
    """lets you select or unselect either handle or control point of a key"""

    objects = context.selected_objects

    if handle_type == 'NONE':
        return

    for obj in objects:
        if not utils.curve.valid_obj(context, obj, check_ui=check_ui):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve, check_ui=check_ui):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            some_selected_key = utils.key.some_selected_key(context, obj)

            key_tweak = context.scene.animaide.key_tweak

            first_key = fcurve.keyframe_points[0]
            last_index = len(fcurve.keyframe_points) - 1
            last_key = fcurve.keyframe_points[last_index]
            kwargs = dict(left=True, right=True, handle_type=handle_type)

            if act_on == 'SELECTION' and selected_keys_index:
                for index in selected_keys_index:
                    key = fcurve.keyframe_points[index]
                    handle_type_asignment(key,
                                          left=key.select_left_handle,
                                          right=key.select_right_handle,
                                          handle_type=handle_type)

            elif act_on == 'ALL':
                for index, key in fcurve.keyframe_points.items():
                    # set_handles_interp(context, interp=key_tweak.interp)
                    handle_type_asignment(key, **kwargs)
            elif act_on == 'FIRST':
                handle_type_asignment(first_key, **kwargs)
            elif act_on == 'LAST':
                handle_type_asignment(last_key, **kwargs)
            elif act_on == 'BOTH':
                handle_type_asignment(last_key, **kwargs)
                handle_type_asignment(first_key, **kwargs)

            fcurve.keyframe_points.sort()
            fcurve.keyframe_points.handles_recalc()


def select_key_parts(context,  left=False, right=False, point=False):
    """lets you select or unselect either handle or control point of a key"""

    global last_op

    last_op = external_op

    objects = context.selected_objects

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            # if not selected_keys_index and fcurve_index in tmp_points.keys():
            #     selected_keys_index = tmp_points[fcurve_index]
            #     tmp_points[fcurve_index] = []

            if selected_keys_index:
                # tmp_points[fcurve_index] = selected_keys_index
                for index in selected_keys_index:
                    key = fcurve.keyframe_points[index]

                    if left:
                        handle_buttons(context, key, left=True, point=False, right=False)

                    elif right:
                        handle_buttons(context, key, left=False, point=False, right=True)

                    elif point:
                        handle_buttons(context, key, left=True, point=False, right=True)

                    else:
                        handle_buttons(context, key, left=True, point=True, right=True)


def assign_interp(key, interp, easing, strength):
    if interp == 'EASE':
        interp = 'NONE'

    if interp != 'NONE':
        key.interpolation = interp

    if strength != 'NONE':
        key.interpolation = strength

    if easing != 'NONE':
        key.easing = easing


def set_handles_interp(context, act_on='SELECTION', interp='NONE', easing='NONE', strength='NONE', check_ui=True):
    """lets you select or unselect either handle or control point of a key"""

    objects = context.selected_objects

    for obj in objects:
        if not utils.curve.valid_obj(context, obj, check_ui=check_ui):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve, check_ui=check_ui):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            if selected_keys_index and act_on == 'SELECTION':
                for index in selected_keys_index:
                    key = fcurve.keyframe_points[index]
                    assign_interp(key, interp, easing, strength)

            if act_on == 'ALL':
                for index, key in fcurve.keyframe_points.items():
                    assign_interp(key, interp, easing, strength)

            fcurve.keyframe_points.sort()
            fcurve.keyframe_points.handles_recalc()


def handle_buttons(context, key, left, point, right):
    key_tweak = context.scene.animaide.key_tweak

    key.select_left_handle = left
    key.select_right_handle = right
    key.select_control_point = point

    key_tweak.left = left
    key_tweak.right = right
    key_tweak.point = point


def handle_type_asignment(key, left=True, right=True, handle_type='AUTO_CLAMPED'):
    """set 'type' of a key handles"""

    if left:
        key.handle_left_type = handle_type

    if right:
        key.handle_right_type = handle_type


def delete_by_type(context, key_type):
    """Deletes keys if they match the type in 'kind'"""

    objects = context.selected_objects

    if objects is None:
        return

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            selected_keys = utils.key.get_selected_index(fcurve)
            cursor_index = utils.key.on_current_frame(fcurve)

            # if not utils.curve.valid_fcurve(context, fcurve):
            #     continue

            keys = fcurve.keyframe_points

            for index, key in keys.items():

                if selected_keys and not key.select_control_point:
                    continue

                while key.type == key_type and key.select_control_point:
                    print('fcurve.data_path: ', fcurve.data_path)
                    print('fcurve.array_index: ', fcurve.array_index)
                    print('key.co_ui.x: ', key.co_ui.x)
                    print('fcurve.group.name: ', fcurve.group.name)
                    obj.keyframe_delete(fcurve.data_path,
                                        index=fcurve.array_index,
                                        frame=key.co_ui.x,
                                        group=fcurve.group.name)

            fcurve.keyframe_points.sort()
            fcurve.keyframe_points.handles_recalc()

            # utils.key.select_by_type(fcurve, kind)
        # if context.area.type == 'GRAPH_EDITOR':
        #     bpy.ops.graph.delete()
        # elif context.area.type == 'DOPESHEET':
        #     bpy.ops.action.delete()

    # context.area.tag_redraw()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    # bpy.ops.wm.redraw_timer()
    # bpy.data.window_managers['WinMan'].windows.update()
    # bpy.data.window_managers['WinMan'].update_tag()


def select_by_type(context, kind, selection=True):
    """Selects or unselects keys if they match the type in 'kind'"""

    objects = context.selected_objects

    if objects is None:
        return

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            # if getattr(fcurve.group, 'name', None) == utils.curve.group_name:
            #     return []  # we don't want to select keys on reference fcurves

            keys = fcurve.keyframe_points

            for index, key in keys.items():
                if key.type == kind:
                    # key.select_control_point = selection
                    handle_buttons(context, key, selection, selection, selection)

    # context.area.tag_redraw()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    # bpy.ops.wm.redraw_timer()
    # bpy.data.window_managers['WinMan'].windows.update()
    # bpy.data.window_managers['WinMan'].update_tag()


# ----------- Not used -----------


def add_samples(fcurve, reference_fcurve, frequency=1):
    """Add keys to an fcurve with the given frequency"""

    key_list = fcurve.keyframe_points

    selected_keys = utils.key.get_selected_index(fcurve)
    first_key, last_key = utils.key.first_and_last_selected(fcurve, selected_keys)

    amount = int(abs(last_key.co_ui.x - first_key.co_ui.x) / frequency)
    frame = first_key.co_ui.x

    for n in range(amount):
        target = reference_fcurve.evaluate(frame)
        key_list.insert(frame, target)
        frame += frequency

    target = reference_fcurve.evaluate(last_key.co_ui.x)
    key_list.insert(last_key.co_ui.x, target)


def swap(key1, key2):
    """Keys1 become key2 and key2 becomes key1"""

    def change_selection(keytochange, Bool):
        setattr(keytochange, 'select_control_point', Bool)
        setattr(keytochange, 'select_left_handle', Bool)
        setattr(keytochange, 'select_right_handle', Bool)

    for l in ('x', 'y'):

        k1 = getattr(key1.co, l)
        k2 = getattr(key2.co, l)

        setattr(key1.co, l, k2)
        setattr(key2.co, l, k1)

    if key1.select_control_point:
        change_selection(key1, False)
        change_selection(key2, True)

    return key2


def set_frame(key, str):
    """sets the time of the current key to the numeric value of 'str'
    if '+' or '-' is used then it will perform the corresponding math operation"""

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
        return int(str)
    else:
        return key_frame


def set_value(key, str):
    """sets the value of the current key to the numeric value of 'str'
    if '+' or '-' is used the it will perform the corresponding math operation"""

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
        return float(str)
    else:
        return key_value


def copy_value(keyframes, reference_key):
    """Copy value of 'reference_key' to 'keyframes'"""

    for index, key in keyframes:
        key.co_ui.y = reference_key.co.y
