import math

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors
# from utils.curve import valid_anim, valid_fcurve, valid_obj
# from utils.curve import poll_fcurve
# from utils import get_items
from .. import utils


global_values = {}


def scale_tools(self, scale_type):
    """Increase or decrease the value of selected keys acording to the "scale_type"
    L = use left neighboring key as anchor
    R = use right neighboring key as anchor
    Anything else =  use the average point as the anchor"""

    factor = utils.clamp(self.factor, self.min_value, self.max_value)

    y = 0
    for index in self.selected_keys:
        y = y + self.original_values[index]['y']
    y_average = y / len(self.selected_keys)

    for index in self.selected_keys:
        k = self.fcurve.keyframe_points[index]

        if scale_type == 'SCALE_LEFT':
            delta = self.original_values[index]['y'] - self.left_neighbor['y']
        elif scale_type == 'SCALE_RIGHT':
            delta = self.original_values[index]['y'] - self.right_neighbor['y']
        elif scale_type == 'SCALE_AVERAGE':
            delta = self.original_values[index]['y'] - y_average
        else:
            delta = self.original_values[index]['y'] - y_average

        k.co_ui.y = self.original_values[index]['y'] + delta * factor

        # utils.key.set_handles(k)


def ease_tools(self, ease_type):

    local_y = self.right_neighbor['y'] - self.left_neighbor['y']
    local_x = self.right_neighbor['x'] - self.left_neighbor['x']

    for index in self.selected_keys:

        k = self.fcurve.keyframe_points[index]
        x = k.co_ui.x - self.left_neighbor['x']
        frame_ratio = x / local_x
        factor = utils.clamp(self.factor, self.min_value, self.max_value)

        flipflop = abs(factor)

        if factor > 0:
            shift = - 1
            xshift = -1 - flipflop/20
        else:
            shift = 0
            xshift = 0 + flipflop/20

        if ease_type == 'EASE_TO_EASE':
            transition = s_curve(frame_ratio, xshift=-factor)
            k.co_ui.y = self.left_neighbor['y'] + local_y * transition

        elif ease_type == 'EASE':
            slope = 1 + (5 * flipflop)
            ease_y = s_curve(frame_ratio, slope=slope, width=2, height=2, xshift=shift, yshift=shift)
            k.co_ui.y = self.left_neighbor['y'] + local_y * ease_y

        elif ease_type == 'BLEND_EASE':

            source = self.original_values[index]['y']

            if factor > 0:
                delta = self.right_neighbor['y'] - source
                base = source
            else:
                delta = source - self.left_neighbor['y']
                base = self.left_neighbor['y']

            slope = flipflop * 5
            ease_y = s_curve(frame_ratio, slope=slope, width=2, height=2, xshift=shift, yshift=shift)
            k.co_ui.y = base + delta * ease_y

        # utils.key.set_handles(k)


def add_noise(fcurve, strength=0.4, scale=1, phase=0):
    """Adds noise modifier to an fcurve"""

    noise = fcurve.modifiers.new('NOISE')

    noise.strength = strength
    noise.scale = scale
    noise.phase = phase
    # fcurve.convert_to_samples(0, 100)
    # fcurve.convert_to_keyframes(0, 100)
    # fcurve.modifiers.remove(noise)


def set_min_max_values(self, context):
    self.animaide = context.scene.animaide
    tool = self.animaide.tool

    if self.op_context == 'EXEC_DEFAULT':
        get_globals(context)

    self.min_value = tool.min_value
    self.max_value = tool.max_value


def to_execute(self, context, function, *args):

    set_min_max_values(self, context)

    objects = utils.get_items(context)

    self.noise_steps = 0

    for obj in objects:

        if not utils.curve.valid_obj(context, obj):
            continue

        self.fcurves = obj.animation_data.action.fcurves

        for fcurve_index, self.fcurve in self.fcurves.items():
            if not utils.curve.poll_fcurve(context, obj, self.fcurve):
                continue

            self.noise_steps += 1

            obj_name = global_values.get(obj.name)
            self.global_fcurve = obj_name.get(fcurve_index)
            self.selected_keys = self.global_fcurve.get('selected_keys')

            if not self.selected_keys:
                continue

            self.original_values = self.global_fcurve.get('original_values')
            self.left_neighbor = self.global_fcurve.get('left_neighbor')
            self.right_neighbor = self.global_fcurve.get('right_neighbor')

            function(*args)

            self.fcurve.update()

    return {'FINISHED'}


def reset_original(context):
    """Set selected keys to the values in the global variables"""

    objects = utils.get_items(context)

    for obj in objects:

        if not utils.curve.valid_anim(obj):
            continue

        visible = obj.visible_get()

        if context.area.type != 'VIEW_3D':
            if not context.space_data.dopesheet.show_hidden and not visible:
                continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if not utils.curve.poll_fcurve(context, obj, fcurve):
                continue

            obj_name = global_values.get(obj.name)
            global_fcurve = obj_name.get(fcurve_index)

            selected_keys = global_fcurve.get('selected_keys')
            original_values = global_fcurve.get('original_values')

            if not original_values:
                continue

            if not selected_keys:
                index = utils.key.on_current_frame(fcurve)
                if index is None:
                    continue
                selected_keys = [index]

            for index in selected_keys:
                if index is None:
                    continue
                k = fcurve.keyframe_points[index]
                k.co_ui.y = original_values[index].get('y')
                handles = original_values[index].get('handles')
                k.handle_left.y = handles.get('l')
                k.handle_right.y = handles.get('r')

            fcurve.update()

    return


def get_globals(context):
    """Gets all the global values needed to work with the curve_tools"""

    animaide = context.scene.animaide

    objects = utils.get_items(context)

    # are_keys_selected = False

    for obj in objects:

        if not utils.curve.valid_anim(obj):
            continue

        # Level 1 variables
        # if object.type == 'ARMATURE':
        #     bones = context.selected_pose_bones

        fcurves = obj.animation_data.action.fcurves
        curves = {}

        for fcurve_index, fcurve in fcurves.items():

            if not utils.curve.valid_fcurve(context, fcurve):
                continue

            # level 2 variables
            curve_items = {}
            keyframes = []
            values = {}
            every_key = []
            left_neighbor = None
            right_neighbor = None

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                # stores coordinate of every key
                handles = {'l': key.handle_left.y, 'r': key.handle_right.y}
                co_ui = {'x': key.co_ui.x, 'y': key.co_ui.y}
                values[key_index] = co_ui
                values[key_index]['handles'] = handles

                # stores every key
                every_key.append(key_index)

                if animaide.tool.keys_under_cursor:
                    index = utils.key.on_current_frame(fcurve)
                    if index is not None:
                        keyframes = [index]
                        # left_neighbor, right_neighbor = utils.key.get_frame_neighbors(fcurve, frame=None, clamped=False)
                elif key.select_control_point:
                    # stores only selected keys
                    keyframes.append(key_index)
                    # are_keys_selected = True
                    # find smooth values (average) of the original keys

                    # key = fcurve.keyframe_points[key_index]

                    if key_index - 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        prevkey_value = key.co_ui.y
                        co_ui = {'x': key.co_ui.x, 'y': key.co_ui.y}
                        curve_items['first_key'] = co_ui
                    else:
                        prevkey_value = fcurve.keyframe_points[key_index - 1].co_ui.y

                    if key_index + 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        nextkey_value = key.co_ui.y
                        co_ui = {'x': key.co_ui.x, 'y': key.co_ui.y}
                        curve_items['last_key'] = co_ui
                    else:
                        nextkey_value = fcurve.keyframe_points[key_index + 1].co_ui.y

                    # smooth = (prevkey_value + key.co_ui.y + nextkey_value) / 3
                    smooth = (prevkey_value + nextkey_value) / 2
                    values[key_index]['sy'] = smooth

            if keyframes:
                left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, keyframes)
                # first_key, last_key = utils.key.first_and_last_selected(fcurve, keyframes)

            # if selected:
            #     # Store selected keys
                curve_items['selected_keys'] = keyframes
            else:
                curve_items['first_key'] = None
                curve_items['last_key'] = None

            if left_neighbor is None:
                curve_items['left_neighbor'] = None
            else:
                # stores coordinates of left neighboring key
                co_ui = {'x': left_neighbor.co_ui.x, 'y': left_neighbor.co_ui.y}
                curve_items['left_neighbor'] = co_ui

            if right_neighbor is None:
                curve_items['right_neighbor'] = None
            else:
                # stores coordinates of right neighboring key
                co_ui = {'x': right_neighbor.co_ui.x, 'y': right_neighbor.co_ui.y}
                curve_items['right_neighbor'] = co_ui

            # if original:
            # stores original values of every key
            curve_items['original_values'] = values
            curve_items['every_key'] = every_key

            # if left_frame is not None or right_frame is not None:
            left_frame, right_frame = set_ref_marker(context)
            frames = {'left_y': fcurve.evaluate(left_frame),
                      'right_y': fcurve.evaluate(right_frame)}

            curve_items['ref_frames'] = frames

            curves[fcurve_index] = curve_items
            # curves['keys_selected'] = keys_selected

        global_values[obj.name] = curves
        # global_values['are_keys_selected'] = are_keys_selected

    return


def set_ref_marker(context):
    tool = context.scene.animaide.tool
    if tool.use_markers:
        markers = context.scene.timeline_markers
        left = 0
        right = 0
        for marker in markers:
            if marker.get('side') == 'L':
                left = marker.frame
            elif marker.get('side') == 'R':
                right = marker.frame
    else:
        left = tool.left_ref_frame
        right = tool.right_ref_frame

    return left, right


def s_curve(x, slope=2.0, width=1.0, height=1.0, xshift=0.0, yshift=0.0):
    """Formula for 'S' curve"""
    curve = height * ((x - xshift) ** slope / ((x - xshift) ** slope + (width - (x - xshift)) ** slope)) + yshift
    if x > xshift + width:
        curve = height + yshift
    elif x < xshift:
        curve = yshift
    return curve

    # return height * ((x - xshift) ** slope / ((x - xshift) ** slope + (width - (x - xshift)) ** slope)) + yshift


def sine_curve(x, height=1.0, width=1.0, xshift=0.0, yshift=0.0):
    curve = height / 2 * math.sin(width * math.pi * (x - xshift + 1.5) + (yshift * 2) + 1)
    if x > xshift + width or x < xshift:
        curve = height + yshift
    return curve


def u_curve(x, slope=2, height=1, width=1, reverse_width=1, xshift=0, yshift=0):
    curve = height * (((reverse_width / width) * (x - xshift)) ** slope) + yshift
    if x > xshift + width:
        curve = height + yshift
    elif x < xshift:
        curve = yshift
    return curve


def ramp_curve(x, slope=2.0, height=1.0, yshift=0.0, width=1.0, xshift=0.0, invert=False):
    """Formula for ease-in or ease-out curve"""

    if invert:
        slope = 1 / slope

    return height * (((1 / width) * (x - xshift)) ** slope) + yshift
    # return height * ((((x-xshift)/width)**slope)+yshift)


def to_linear_curve(left_neighbor, right_neighbor, selected_keys, factor=1):
    """Lineal transition between neighbors"""

    local_y = right_neighbor.y - left_neighbor.y
    local_x = right_neighbor.x - left_neighbor.x
    ratio = local_y / local_x
    for k in selected_keys:
        x = k.co_ui.x - left_neighbor.co_ui.x
        average_y = ratio * x + left_neighbor.y
        delta = average_y - k.co_ui.y
        k.co_ui.y = k.co_ui.y + (delta * factor)


def linear_y(key, left_neighbor, right_neighbor):
    big_adjacent = right_neighbor['x'] - left_neighbor['x']
    big_oposite = right_neighbor['y'] - left_neighbor['y']
    if big_adjacent == 0:
        return
    tangent = big_oposite / big_adjacent

    adjacent = key.co_ui.x - left_neighbor['x']
    oposite = tangent * adjacent
    return left_neighbor['y'] + oposite


