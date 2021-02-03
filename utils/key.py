import bpy

from .. import utils


def attach_selection_to_fcurve(fcurve, target_fcurve, factor=1.0, is_gradual=True):
    """Match 'y' value of selected keys to the value o target_fcurve"""

    selected_keys = get_selected_index(fcurve)

    for index in selected_keys:

        key = fcurve.keyframe_points[index]

        attach_to_fcurve(key, key, target_fcurve, factor=factor, is_gradual=is_gradual)


def attach_to_fcurve(key, source_key, target_fcurve, factor=1.0, is_gradual=True):
    """Match 'y' value of a key to the value o target_fcurve"""

    target_y = target_fcurve.evaluate(key.co.x)

    if is_gradual is True:
        key.co.y = utils.gradual(source_key.co.y, target_y, factor=factor)

    else:
        key.co.y = target_y


def get_selected_index(fcurve):
    """Creates a list of selected keys index"""

    keys = fcurve.keyframe_points
    keyframe_indexes = []
    if getattr(fcurve.group, 'name', None) == utils.curve.group_name:
        return []  # we don't want to select keys on reference fcurves

    for index, key in keys.items():
        if key.select_control_point or key.select_left_handle or key.select_right_handle:
            keyframe_indexes.append(index)

    return keyframe_indexes


def some_selected_key(context):
    objects = context.selected_objects
    for obj in objects:
        action = obj.animation_data.action
        for fcurve in action.fcurves:
            keys = fcurve.keyframe_points
            for key in keys:
                if key.select_control_point:
                    return True


def set_handle(key, side, delta):

    handle = getattr(key, 'handle_%s' % side, None)
    handle_type = getattr(key, 'handle_%s_type' % side, None)

    if handle_type == 'FREE' or handle_type == 'ALIGNED':
        handle.y = key.co.y - delta


def set_handles(key):
    lh_delta = key.co.y - key.handle_left.y
    rh_delta = key.co.y - key.handle_right.y
    set_handle(key, 'left', lh_delta)
    set_handle(key, 'right', rh_delta)


def first_and_last_selected(fcurve, keyframes):
    """Given a list of keys it returns the first and last keys.
    If an fcurve is supplied just the keys of that curve are taken into consideration"""

    every_key = fcurve.keyframe_points

    if not keyframes:
        index = on_current_frame(fcurve)
        if index is None:
            return
        keyframes = [index]

    first_index = keyframes[0]
    first_key = every_key[first_index]

    # i = len(keyframes) - 1
    last_index = keyframes[-1]
    last_key = every_key[last_index]

    return first_key, last_key


def on_current_frame(fcurve):
    """returns the index of the key in the current frame"""

    current_index = None
    cur_frame = bpy.context.scene.frame_current
    for index, key in fcurve.keyframe_points.items():
        if key.co.x == cur_frame:
            current_index = index
    return current_index


def get_selected_neigbors(fcurve, keyframes):
    """Get the left and right neighboring keys of the selected keys"""

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
        left_neighbor = every_key[first_index]

    elif first_index > 0:
        left_neighbor = every_key[first_index - 1]

    if last_index == len(fcurve.keyframe_points) - 1:
        right_neighbor = every_key[last_index]

    elif last_index < len(fcurve.keyframe_points) - 1:
        right_neighbor = every_key[last_index + 1]

    return left_neighbor, right_neighbor


def get_index_neighbors(fcurve, index, clamped=False):
    """Get the neighboring keys of a key given index"""

    left_neighbor = fcurve.keyframe_points[utils.floor(index - 1, 0)]
    right_neighbor = fcurve.keyframe_points[utils.ceiling(index + 1, len(fcurve.keyframe_points) - 1)]

    # if clamped is False:
    #     if left_neighbor == fcurve.keyframe_points[0]:
    #         left_neighbor = None
    #     if right_neighbor == fcurve.keyframe_points[len(fcurve.keyframe_points) - 1]:
    #         right_neighbor = None

    return left_neighbor, right_neighbor


def get_frame_neighbors(fcurve, frame=None, clamped=False):
    """Get neighboring keys of a frame"""

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


def update_keyframe_points(context):
    # The select operator(s) are bugged, and can fail to update selected keys, so

    area = context.area.type
    if area != 'GRAPH_EDITOR':
        context.area.type = 'GRAPH_EDITOR'

    snap = context.space_data.auto_snap
    context.space_data.auto_snap = 'NONE'

    bpy.ops.transform.transform()

    context.space_data.auto_snap = snap
    if area != 'GRAPH_EDITOR':
        context.area.type = area


