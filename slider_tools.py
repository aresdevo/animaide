import bpy


from . import utils, key_utils, cur_utils


fcurve = None
global_fcurve = None
selected_keys = None
original_values = None
left_neighbor = None
right_neighbor = None
min_value = None
max_value = None


def ease(factor, slope):

    clamped_factor = utils.clamp(-factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']
        try:
            key_ratio = 1 / (local_x / x)
        except:
            key_ratio = 0

        clamped_move = utils.clamp(clamped_factor, minimum=key_ratio - 1, maximum=key_ratio)

        ease_y = cur_utils.s_curve(key_ratio, slope=slope, xshift=clamped_move)

        k.co.y = left_neighbor['y'] + local_y * ease_y


def ease_in_out(factor, slope):

    clamped_factor = utils.clamp(factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    new_slope = 1 + ((slope * 2) * abs(clamped_factor))

    if factor < 0:
        height = 2
        width = 2
        yshift = 0
        xshift = 0
    else:
        height = 2
        width = 2
        xshift = -1
        yshift = -1

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']
        try:
            key_ratio = 1 / (local_x / x)
        except:
            key_ratio = 0

        ease_y = cur_utils.s_curve(key_ratio,
                                   slope=new_slope,
                                   width=width,
                                   height=height,
                                   xshift=xshift,
                                   yshift=yshift)

        k.co.y = left_neighbor['y'] + local_y * ease_y.real


def blend_neighbor(factor):

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if factor < 0:
            delta = left_neighbor['y'] - original_values[index]['y']
        else:
            delta = right_neighbor['y'] - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_frame(factor, left_y_ref, right_y_ref):

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if factor < 0:
            delta = left_y_ref - original_values[index]['y']
        else:
            delta = right_y_ref - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_ease(factor, slope):

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']

        if factor < 0:
            clamped_factor = utils.clamp(1 + factor * 2, min_value, max_value)
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0
            ease_y = cur_utils.s_curve(key_ratio,
                                       slope=1 + (slope),  # self.slope * 2,
                                       width=2,
                                       height=2,
                                       xshift=0,
                                       yshift=0)
        else:
            clamped_factor = utils.clamp(1 - factor * 2, min_value, max_value)
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0
            ease_y = cur_utils.s_curve(key_ratio,
                                       slope=1 + (slope),  # self.slope * 2,
                                       width=2,
                                       height=2,
                                       xshift=-1,
                                       yshift=-1)

        clamped_move = utils.clamp(clamped_factor,
                                   minimum=key_ratio - 1,
                                   maximum=key_ratio)

        blend = cur_utils.s_curve(key_ratio,
                                  slope=1.3,
                                  # xshift=clamped_move)
                                  width=2,
                                  height=2,
                                  xshift=clamped_move - 1,
                                  yshift=-1)

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        delta = (left_neighbor['y'] + local_y * ease_y.real) - original_values[index]['y']

        # k.co.y = original_values[index]['y'] + delta * blend.real
        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_offset(factor):

    clamped_factor = utils.clamp(factor, min_value, max_value)

    first_key_index = selected_keys[0]
    last_key_index = selected_keys[-1]

    if first_key_index is None or last_key_index is None:
        return

    if clamped_factor > 0:
        delta = right_neighbor['y'] - original_values[last_key_index]['y']
    else:
        delta = original_values[first_key_index]['y'] - left_neighbor['y']

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = original_values[index]['y'] + delta * clamped_factor


def tween(factor):

    clamped_factor = utils.clamp(factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    delta = local_y / 2
    mid = left_neighbor['y'] + delta

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = mid + delta * clamped_factor


def push_pull(factor):

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        average_y = key_utils.linear_y(left_neighbor, right_neighbor, k)
        delta = original_values[index]['y'] - average_y

        k.co.y = original_values[index]['y'] + delta * clamped_factor * 2


def smooth(factor):

    # factor = (self.factor/2) + 0.5

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if 'sy' not in original_values[index]:
            continue

        smooth_y = original_values[index]['sy']

        if smooth_y == 'book end':
            delta = 0
        else:
            delta = original_values[index]['y'] - smooth_y

        k.co.y = original_values[index]['y'] - delta * clamped_factor


def time_offset(factor, fcurves):

    # factor = (self.factor/2) + 0.5
    animaide = bpy.context.scene.animaide
    cycle_before = animaide.clone.cycle_before
    cycle_after = animaide.clone.cycle_after

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone = cur_utils.duplicate_from_data(fcurves,
                                          global_fcurve,
                                          clone_name,
                                          before=cycle_before,
                                          after=cycle_after)

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = clone.evaluate(k.co.x - 20 * clamped_factor)

    fcurves.remove(clone)


def noise(factor, fcurves, fcurve_index):

    # factor = (self.factor/2) + 0.5
    # animaide = bpy.context.scene.animaide

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone = cur_utils.duplicate_from_data(fcurves,
                                          global_fcurve,
                                          clone_name)

    cur_utils.add_noise(clone, strength=1, scale=0.5, phase=fcurve_index * left_neighbor['y'])

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        delta = clone.evaluate(k.co.x) - original_values[index]['y']
        k.co.y = original_values[index]['y'] + delta * clamped_factor

    fcurves.remove(clone)


def scale(factor, scale_type):

    clamped_factor = utils.clamp(factor, min_value, max_value)

    y = 0
    for index in selected_keys:
        y = y + original_values[index]['y']
    y_average = y / len(selected_keys)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        if scale_type == 'L':
            delta = original_values[index]['y'] - left_neighbor['y']
        elif scale_type == 'R':
            delta = right_neighbor['y'] - original_values[index]['y']
        else:
            delta = original_values[index]['y'] - y_average

        k.co.y = original_values[index]['y'] + delta * clamped_factor