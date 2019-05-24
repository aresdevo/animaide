import bpy
from . import utils, cur_utils


global_values = {}

# selected_keys_global = {}
# original_keys_info = {}
# all_keys = {}
# ref_frames_global = {}
# smooth_keys_info = {}
# left_neighbor_global = {}
# right_neighbor_global = {}



def set_type(objects, kind):
    if kind == 'KEYFRAME' or kind == 'BREAKDOWN' or kind == 'JITTER':

        print('test')

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
    if objects is None:
        return

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if fcurve.select is False:
                continue

            if fcurve.hide is True:
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
    # left_neighbor, right_neighbor = get_current_key_neighbors(fcurve, key.co.x)
    selected_keys = get_selected(fcurve)
    left_neighbor, right_neighbor = get_selected_neigbors(fcurve, selected_keys)

    if direction == 'UP':
        key.co.y = key.co.y + amount

    if direction == 'DOWN':
        key.co.y = key.co.y - amount

    if direction == 'LEFT':
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

            elif act_on == 'ALL':
                for index, key in fcurve.keyframe_points.items():
                    print('all')
                    if handle_type is not None:
                        handle_set_type(key, left=True, right=True, handle_type=handle_type)

            elif act_on == 'FIRST':
                print('first')
                if handle_type is not None:
                    handle_set_type(first_key, left=True, right=True, handle_type=handle_type)

            elif act_on == 'LAST':
                print('last')
                if handle_type is not None:
                    handle_set_type(last_key, left=True, right=True, handle_type=handle_type)

            elif act_on == 'BOTH':
                print('both')
                if handle_type is not None:
                    handle_set_type(last_key, left=True, right=True, handle_type=handle_type)
                    handle_set_type(first_key, left=True, right=True, handle_type=handle_type)

            fcurve.update()


def handle_manipulate(key, left=None, right=None, length=None):

    if left is not None:
        if left is True:
            if length is not None:
                key.handle_left.length = length

    if right is not None:
        if right is True:
            if length is not None:
                key.handle_right.length = length


def handle_set_type(key, left=True, right=True, handle_type='AUTO_CLAMPED'):
    if left is not None:
        if left is True:
            key.handle_left_type = handle_type

    if left is not None:
        if right is True:
            key.handle_right_type = handle_type


def attach_selection_to_fcurve(fcurve, target_fcurve, factor=1.0, is_gradual=True):

        selected_keys = get_selected(fcurve)

        for index in selected_keys:

            key = fcurve.keyframe_points[index]

            attach_to_fcurve(key, key, target_fcurve, factor=factor, is_gradual=is_gradual)


def attach_to_fcurve(key, source_key, target_fcurve, factor=1.0, is_gradual=True):

    target_y = target_fcurve.evaluate(key.co.x)

    if is_gradual is True:
        key.co.y = utils.gradual(source_key.co.y, target_y, factor=factor)

    else:
        key.co.y = target_y

    print('key "y" value:', key.co.y)


def get_selected(fcurve):
    """
    :return reversable list of complex keys that contains (index, key) on a tuple of the selected keys:
    """
    keys = fcurve.keyframe_points
    keyframe_indexes = []

    if fcurve.group.name == cur_utils.group_name:
        return []  # we don't want to select keys on reference fcurves

    for index, key in keys.items():
        if key.select_control_point:
            keyframe_indexes.append(index)

    return keyframe_indexes


def get_sliders_globals(selected=True, original=True, left_frame=None, right_frame=None):
    """
    :return reversable list of complex keys that contains (index, key) on a tuple of the selected keys:
    """

    objects = bpy.context.selected_objects

    for obj in objects:
        anim = obj.animation_data
        if anim is None:
            continue
        if anim.action.fcurves is None:
            continue
        fcurves = obj.animation_data.action.fcurves

        curves = {}

        for fcurve_index, fcurve in fcurves.items():
            curve_items = {}

            if fcurve.select is False:
                continue

            if fcurve.hide is True:
                continue

            if fcurve.group.name == cur_utils.group_name:
                continue  # we don't want to select keys on reference fcurves

            keyframes = []
            values = {}
            every_key = []

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                co = {'x': key.co.x, 'y': key.co.y}
                values[key_index] = co

                every_key.append(key_index)

                if key.select_control_point:
                    keyframes.append(key_index)

            prevkey_value = None

            for key_index in keyframes:
                key = fcurve.keyframe_points[key_index]

                if key_index - 1 not in keyframes:
                    prevkey_value = 'book end'

                if key_index + 1 not in keyframes:
                    nextkey_value = 'book end'
                else:
                    nextkey_value = fcurve.keyframe_points[key_index + 1].co.y

                if prevkey_value == 'book end' or nextkey_value == 'book end':
                    values[key_index]['sy'] = 'book end'
                    prevkey_value = key.co.y
                else:
                    smooth = (prevkey_value + key.co.y + nextkey_value)/3
                    values[key_index]['sy'] = smooth
                    prevkey_value = smooth

            if not keyframes:
                index = on_current_frame(fcurve)
                left_neighbor, right_neighbor = get_frame_neighbors(fcurve, frame=None, clamped=False)
                keyframes = [index]
            else:
                left_neighbor, right_neighbor = get_selected_neigbors(fcurve, keyframes)

            if selected:
                curve_items['selected_keys'] = keyframes

                co = {'x': left_neighbor.co.x, 'y': left_neighbor.co.y}
                curve_items['left_neighbor'] = co
                co = {'x': right_neighbor.co.x, 'y': right_neighbor.co.y}
                curve_items['right_neighbor'] = co

            if original:
                curve_items['original_values'] = values
                curve_items['every_key'] = every_key

            if left_frame is not None or left_frame is not None:
                frames = {'left_y': fcurve.evaluate(left_frame),
                          'right_y': fcurve.evaluate(right_frame)}
                curve_items['ref_frames'] = frames

            curves[fcurve_index] = curve_items

        global_values[obj.name] = curves

    return


def get_ref_frame_globals(left_ref_frame, right_ref_frame):

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


def get_magnet_globals(object):

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

            fcurve.update()

    return


def first_and_last_selected(fcurve, keyframes):
    """
    Given a list of keys it returns the first and last keys.
    If an fcurve is supplied just the keys of that curve are taken into consideration
    """

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
    selected_keys = get_selected(fcurve)
    if selected_keys is not None:
        for index in selected_keys:
            key = fcurve.keyframe_points[index]
            key.handle_right_type = mode
            key.handle_left_type = mode


def delete(objects, kind=None):
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
    for index, key in keyframes:
        key.co.y = reference_key.co.y


def flatten(objects, side):
    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if fcurve.group.name == cur_utils.group_name:
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
    current_index = None
    cur_frame = bpy.context.scene.frame_current
    for index, key in fcurve.keyframe_points.items():
        if key.co.x == cur_frame:
            current_index = index
    return current_index


def get_selected_neigbors(fcurve, keyframes):
    if not keyframes:
        index = on_current_frame(fcurve)
        if index is None:
            return
        keyframes = [index]

    left_neighbor = None
    right_neighbor = None
    every_key = fcurve.keyframe_points
    first_index = keyframes[0]
    if keyframes[0] is None:
        return left_neighbor, right_neighbor
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
    left_neighbor = fcurve.keyframe_points[utils.floor(index - 1, 0)]
    right_neighbor = fcurve.keyframe_points[utils.ceiling(index + 1, len(fcurve.keyframe_points) - 1)]

    # if clamped is False:
    #     if left_neighbor == fcurve.keyframe_points[0]:
    #         left_neighbor = None
    #     if right_neighbor == fcurve.keyframe_points[len(fcurve.keyframe_points) - 1]:
    #         right_neighbor = None

    return left_neighbor, right_neighbor


def get_frame_neighbors(fcurve, frame=None, clamped=False):
    if frame is None:
        frame = bpy.context.scene.frame_current
    fcurve_keys = fcurve.keyframe_points
    left_neighbor = fcurve_keys[0]
    right_neighbor = fcurve_keys[len(fcurve_keys)-1]

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


