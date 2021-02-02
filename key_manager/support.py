import bpy

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors

from .. import utils


handle_type = [('FREE', ' ', 'Free', 'HANDLE_FREE', 1),
               ('ALIGNED', ' ', 'Aligned', 'HANDLE_ALIGNED', 2),
               ('VECTOR', ' ', 'Vector', 'HANDLE_VECTOR', 3),
               ('AUTO', ' ', 'Auto', 'HANDLE_AUTO', 4),
               ('AUTO_CLAMPED', ' ', 'Auto Clamped', 'HANDLE_AUTOCLAMPED', 5)]


interp = [('CONSTANT', 'Constant', 'Constant', 'IPO_CONSTANT', 1),
          ('LINEAR', 'Linear', 'Linear', 'IPO_LINEAR', 2),
          ('BEZIER', 'Bezier', 'Bezier', 'IPO_BEZIER', 3),
          ('EASE', 'Ease', 'Ease', 'IPO_EASE_IN_OUT', 4)]


strength = [('SINE', 'Sinusoidal', 'Sinusoidal', 'IPO_SINE', 1),
            ('QUAD', 'Quadratic', 'Quadratic', 'IPO_QUAD', 2),
            ('CUBIC', 'Cubic', 'Cubic', 'IPO_CUBIC', 3),
            ('QUART', 'Quartic', 'Quartic', 'IPO_QUART', 4),
            ('QUINT', 'Quintic', 'Quintic', 'IPO_QUINT', 5),
            ('EXPO', 'Exponential', 'Exponential', 'IPO_EXPO', 6),
            ('CIRC', 'Circular', 'Circular', 'IPO_CIRC', 7),
            ('BACK', 'Back', 'Back', 'IPO_BACK', 8),
            ('BOUNCE', 'Bounce', 'Bounce', 'IPO_BOUNCE', 9),
            ('ELASTIC', 'Elastic', 'Elastic', 'IPO_ELASTIC', 10)]


easing = [('AUTO', 'Auto', 'Auto', 'IPO_EASE_IN_OUT', 1),
          ('EASE_IN', 'Ease in', 'Ease in', 'IPO_EASE_IN', 2),
          ('EASE_OUT', 'Ease-out', 'Ease-out', 'IPO_EASE_OUT', 3),
          ('EASE_IN_OUT', 'Ease in-out', 'Ease in-out', 'IPO_EASE_IN_OUT', 4)]


key_type = [('KEYFRAME', ' ', 'Keyframe', 'KEYTYPE_KEYFRAME_VEC', 1),
            ('BREAKDOWN', ' ', 'Breakdown', 'KEYTYPE_BREAKDOWN_VEC', 2),
            ('JITTER', ' ', 'Jitter', 'KEYTYPE_JITTER_VEC', 3),
            ('EXTREME', ' ', 'Extreme', 'KEYTYPE_EXTREME_VEC', 4)]


act_on = [('FIRST', 'First', 'First', ' ', 1),
          ('LAST', 'Last', 'Last', ' ', 2),
          ('BOTH', 'Both', 'Both', ' ', 3),
          ('ALL', 'All', 'All', ' ', 4)]


tmp_points = {}


def set_type(context, kind):
    """Sets key type"""

    if kind == 'KEYFRAME' or kind == 'BREAKDOWN' or kind == 'JITTER' or kind == 'EXTREME':

        objects = context.selected_objects

        if objects is None:
            return

        for obj in objects:
            if not utils.curve.valid_anim(obj):
                continue
            fcurves = obj.animation_data.action.fcurves

            for fcurve in fcurves:

                if not utils.curve.valid_fcurve(context, fcurve):
                    continue

                selected_keys = utils.key.get_selected_index(fcurve)

                if not selected_keys:
                    continue

                for index in selected_keys:
                    key = fcurve.keyframe_points[index]
                    key.type = kind
                fcurve.update()


def change_value(context, amount, direction='UP'):
    """move keys verticaly"""

    objects = context.selected_objects

    if objects is None:
        return

    if direction == 'DOWN':
        amount = -amount

    some_selected_key = utils.key.some_selected_key(context)

    for obj in objects:
        if not utils.curve.valid_anim(obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve in fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            selected_keys = utils.key.get_selected_index(fcurve)
            current_index = utils.key.on_current_frame(fcurve)

            if selected_keys:
                for index in selected_keys:
                    if index is None:
                        continue
                    key = fcurve.keyframe_points[index]
                    key.co.y += amount
                    fcurve.update()
            elif current_index and not some_selected_key:
                key = fcurve.keyframe_points[current_index]
                key.co.y += amount


def change_frame(context, amount, direction='RIGHT'):
    """move keys horizontally"""

    def cant_move(l_neighbor, r_neighbor, l_key, r_key):
        if l_neighbor is not None and l_key.co.x + amount <= l_neighbor.co.x:
            return False
        elif r_neighbor is not None and r_key.co.x + amount >= r_neighbor.co.x:
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

    some_selected_key = utils.key.some_selected_key(context)
    frames = amount

    for obj in objects:

        if not utils.curve.valid_anim(obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve in fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            selected_keys = utils.key.get_selected_index(fcurve)

            if selected_keys:
                left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, selected_keys)
                left_key, right_key = utils.key.first_and_last_selected(fcurve, selected_keys)
                if not cant_move(left_neighbor, right_neighbor, left_key, right_key):
                    return
                for index in selected_keys:
                    if index is None:
                        continue
                    key = fcurve.keyframe_points[index]
                    key.co.x += amount
                    fcurve.update()
                frames = 0

            elif not some_selected_key:
                left_neighbor, right_neighbor = utils.key.get_frame_neighbors(fcurve)
                current_index = utils.key.on_current_frame(fcurve)
                if current_index:
                    key = fcurve.keyframe_points[current_index]
                    if not cant_move(left_neighbor, right_neighbor, key, key):
                        return
                    key.co.x += amount
                    fcurve.update()
                    # context.scene.frame_current += amount
                    frames = amount
                else:
                    if direction == 'LEFT':
                        right_neighbor.co.x = context.scene.frame_current
                    elif direction == 'RIGHT':
                        left_neighbor.co.x = context.scene.frame_current
                    frames = 0
                    fcurve.update()

    context.scene.frame_current += frames


def set_handles_type(context, act_on='SELECTION', handle_type='NONE'):
    """lets you select or unselect either handle or control point of a key"""

    objects = context.selected_objects

    for obj in objects:
        if not utils.curve.valid_anim(obj):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            # first_key, last_key = first_and_last_selected(fcurve)
            # first_key = fcurve.keyframe_points[0]
            # last_index = len(fcurve.keyframe_points) - 1
            # last_key = fcurve.keyframe_points[last_index]
            if selected_keys_index:
                first_key = fcurve.keyframe_points[selected_keys_index[0]]
                last_index = len(selected_keys_index) - 1
                last_key = fcurve.keyframe_points[selected_keys_index[last_index]]

                if act_on == 'SELECTION':
                    for index in selected_keys_index:
                        key = fcurve.keyframe_points[index]
                        handle_type_asignment(key,
                                              left=key.select_left_handle,
                                              right=key.select_right_handle,
                                              handle_type=handle_type)

                elif handle_type != 'NONE':
                    kwargs = dict(left=True, right=True, handle_type=handle_type)
                    if act_on == 'ALL':
                        for index, key in fcurve.keyframe_points.items():
                            handle_type_asignment(key, **kwargs)
                    elif act_on == 'FIRST':
                        handle_type_asignment(first_key, **kwargs)
                    elif act_on == 'LAST':
                        handle_type_asignment(last_key, **kwargs)
                    elif act_on == 'BOTH':
                        handle_type_asignment(last_key, **kwargs)
                        handle_type_asignment(first_key, **kwargs)

                fcurve.update()


def select_key_parts(context, left=False, right=False, point=False):
    """lets you select or unselect either handle or control point of a key"""

    global tmp_points

    objects = context.selected_objects

    for obj in objects:
        if not utils.curve.valid_anim(obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            if not selected_keys_index and fcurve_index in tmp_points.keys():
                selected_keys_index = tmp_points[fcurve_index]
                tmp_points[fcurve_index] = []

            if selected_keys_index:
                tmp_points[fcurve_index] = selected_keys_index
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


def set_handles_interp(context, interp='NONE', easing='NONE', strength='NONE'):
    """lets you select or unselect either handle or control point of a key"""

    objects = context.selected_objects

    for obj in objects:
        if not utils.curve.valid_anim(obj):
            continue

        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            selected_keys_index = utils.key.get_selected_index(fcurve)

            for index in selected_keys_index:
                key = fcurve.keyframe_points[index]
                if interp != 'NONE':
                    key.interpolation = interp
                if easing != 'NONE':
                    key.easing = easing
                if strength != 'NONE':
                    key.interpolation = strength

            fcurve.update()


def handle_buttons(context, key, left, point, right):
    key_tweak = context.scene.animaide.key_tweak

    if length is None:
        return

    if left is True:
        key.handle_left.length = length

def handle_type_asignment(key, left=True, right=True, handle_type='AUTO_CLAMPED'):
    """set 'type' of a key handles"""

    if left:
        key.handle_left_type = handle_type

    if right:
        key.handle_right_type = handle_type


def delete_by_type(context, kind=None):
    """Deletes keys if they match the type in 'kind'"""

    objects = context.selected_objects

    if objects is None:
        return

    for obj in objects:
        if not utils.curve.valid_anim(obj):
            continue
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            keys = fcurve.keyframe_points
            for index, key in keys.items():
                if not kind:
                    obj.keyframe_delete(fcurve.data_path,
                                        fcurve.array_index,
                                        key.co_ui.x,
                                        fcurve.group.name)
                else:
                    while key.type == kind:
                        obj.keyframe_delete(fcurve.data_path,
                                            fcurve.array_index,
                                            key.co_ui.x,
                                            fcurve.group.name)
            fcurve.update()

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
        if not utils.curve.valid_anim(obj):
            continue
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            if getattr(fcurve.group, 'name', None) == utils.curve.group_name:
                return []  # we don't want to select keys on reference fcurves

            keys = fcurve.keyframe_points

            for index, key in keys.items():
                if key.type == kind:
                    key.select_control_point = selection

    # context.area.tag_redraw()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
    # bpy.ops.wm.redraw_timer()
    # bpy.data.window_managers['WinMan'].windows.update()
    # bpy.data.window_managers['WinMan'].update_tag()


def poll(context):
    """Poll used on all the slider operators"""

    # selected = get_items(context, any_mode=True)
    #
    # area = context.area.type
    # return bool((area == 'GRAPH_EDITOR' or
    #              area == 'DOPESHEET_EDITOR' or
    #              area == 'VIEW_3D') and
    #             selected)

    return True


# ----------- Not used -----------


def calculate_delta(key, previous_key, next_key):

    frames_gap = abs(next_key.co_ui.x - previous_key.co_ui.x)  # frames between keys
    key_pos = abs(key.co_ui.x - previous_key.co_ui.x)  # frame position of the key in question

    if frames_gap == 0:  # not to devided by zero
        return 0
    if key_pos == 0:
        return 0.25     # in the case of the fist or last key
    else:
        return ((key_pos * 100) / frames_gap) / 100


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


def set_direction(factor, left_key, right_key):
    if factor < 0:
        next_key = left_key
        previous_key = right_key
    else:
        next_key = right_key
        previous_key = left_key

    return previous_key, next_key


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
    """Copy value of 'referece_key' to 'keyframes'"""

    for index, key in keyframes:
        key.co_ui.y = reference_key.co.y


def flatten(objects, side):
    """Match the value of the selected keys to the neighboring key to the 'side'"""

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:

            if getattr(fcurve.group, 'name', None) == utils.curve.group_name:
                continue  # we don't want to add to the list the helper curves we have created

            if fcurve.select is False:
                continue

            selected_keys = utils.key.get_selected_index(fcurve)

            if not selected_keys:
                index = utils.key.on_current_frame(fcurve)
                selected_keys = [index]

            left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, selected_keys)

            if side == 'LEFT':
                # this fixes the problem of the fist key moving (just happens with this one)
                # if selected_keys[0][1] != fcurve.keyframe_points[0]:
                #     copy_value(selected_keys, left_neighbor)  # if there is no key on the left then it uses itself
                # else:
                copy_value(selected_keys, fcurve.keyframe_points[0])

            elif side == 'RIGHT':
                copy_value(selected_keys, right_neighbor)

            fcurve.update()


def select_handle(key, index, left=None, right=None, control_point=None):
    """selects handles of chosen key"""

    global tmp_points

    if left is not None:
        key.select_left_handle = left
    if right is not None:
        key.select_right_handle = right
    if control_point is not None:
        if not control_point:
            tmp_points.append((index, key))
        else:
            tmp_points = []
        key.select_control_point = control_point


def handle_manipulate(key, left=None, right=None, length=None):
    """set length of a key handles"""

    key.select_left_handle = left
    key.select_right_handle = right
    key.select_control_point = point

    key_tweak.left = left
    key_tweak.right = right
    key_tweak.point = point


    if right is True:
        key.handle_right.length = length
