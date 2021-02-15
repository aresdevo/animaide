import math

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors
# from utils.curve import valid_anim, valid_fcurve, valid_obj
# from utils.curve import poll_fcurve
# from utils import get_items
from .. import utils


global_values = {}


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

    self.noise_steps = 0

    objects = utils.get_items(context)

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        stored_obj = global_values.get(obj.name)

        self.some_keys_selected = global_values.get('keys_are_selected')

        self.fcurves = obj.animation_data.action.fcurves

        for self.fcurve_index, self.fcurve in self.fcurves.items():
            if not utils.curve.valid_fcurve(context, obj, self.fcurve):
                continue

            self.noise_steps += 1

            self.global_fcurve = stored_obj.get(self.fcurve_index)
            self.selected_keys = self.global_fcurve.get('selected_keys')

            under_cursor = self.global_fcurve.get('under_cursor')

            if not self.selected_keys:
                if self.some_keys_selected:
                    continue
                elif under_cursor:
                    self.selected_keys = under_cursor
                elif self.tool_type in ('SMOOTH', 'TIME_OFFSET', 'WAVE_NOISE', 'SCALE_AVERAGE'):
                    self.report({'WARNING'}, "This tool only works on frames with keys")
                    continue

            self.original_values = self.global_fcurve.get('original_values')
            self.left_neighbor = self.global_fcurve.get('left_neighbor')
            self.right_neighbor = self.global_fcurve.get('right_neighbor')

            # fcurve_key_added = function(*args)
            function(*args)

            # if fcurve_key_added:
            #     self.cursor_keys.append(fcurve_key_added)

            self.fcurve.update()

    return {'FINISHED'}


def reset_original(context):
    """Set selected keys to the values in the global variables"""

    objects = utils.get_items(context)

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if not utils.curve.valid_fcurve(context, obj, fcurve):
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

    keys_are_selected = False

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        fcurves = obj.animation_data.action.fcurves
        curves = {}

        for fcurve_index, fcurve in fcurves.items():
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            # level 2 variables
            curve_items = {}
            keyframes = []
            under_cursor = []
            values = {}
            every_key = []
            left_neighbor = None
            right_neighbor = None

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                # stores coordinate of every key
                handles = {'l': key.handle_left.y, 'r': key.handle_right.y}
                co = {'x': key.co_ui.x, 'y': key.co_ui.y}
                values[key_index] = co
                values[key_index]['handles'] = handles

                # stores every key
                every_key.append(key_index)

                # if animaide.tool.keys_under_cursor:
                index = utils.key.on_current_frame(fcurve)
                if index is not None:
                    under_cursor = [index]
                    # left_neighbor, right_neighbor = utils.key.get_frame_neighbors(fcurve, frame=None, clamped=False)
                if key.select_control_point and context.area.type != 'VIEW_3D':
                    # stores only selected keys
                    keyframes.append(key_index)
                    keys_are_selected = True
                    # find smooth values (average) of the original keys

                    # key = fcurve.keyframe_points[key_index]

                    if key_index - 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        prevkey_value = key.co_ui.y
                        co = {'x': key.co_ui.x, 'y': key.co_ui.y}
                        curve_items['first_key'] = co
                    else:
                        prevkey_value = fcurve.keyframe_points[key_index - 1].co_ui.y

                    if key_index + 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        nextkey_value = key.co_ui.y
                        co = {'x': key.co_ui.x, 'y': key.co_ui.y}
                        curve_items['last_key'] = co
                    else:
                        nextkey_value = fcurve.keyframe_points[key_index + 1].co_ui.y

                    # smooth = (prevkey_value + key.co_ui.y + nextkey_value) / 3
                    smooth = (prevkey_value + nextkey_value) / 2
                    values[key_index]['sy'] = smooth

            if keyframes:
                # left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, keyframes)
                # left_far, right_far = utils.key.get_neigbors_of_neighbors(fcurve, keyframes)
                left_neighbor, left_index, right_neighbor, right_index = utils.key.get_selected_neigbors(
                    fcurve, keyframes, return_index=True)
                left_far, key = utils.key.get_selected_neigbors(fcurve, left_index)
                key, right_far = utils.key.get_selected_neigbors(fcurve, right_index)
                # first_key, last_key = utils.key.first_and_last_selected(fcurve, keyframes)

            # if selected:
            #     # Store selected keys
                curve_items['selected_keys'] = keyframes
            else:
                if under_cursor:
                    # left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, under_cursor)
                    # left_far, right_far = utils.key.get_neigbors_of_neighbors(fcurve, under_cursor)
                    left_neighbor, left_index, right_neighbor, right_index = utils.key.get_selected_neigbors(
                        fcurve, under_cursor, return_index=True)
                    left_far, key = utils.key.get_selected_neigbors(fcurve, left_index)
                    key, right_far = utils.key.get_selected_neigbors(fcurve, right_index)
                else:
                    cur_frame = context.scene.frame_current
                    # left_neighbor, right_neighbor = utils.key.get_frame_neighbors(fcurve, cur_frame)
                    left_neighbor, left_index, right_neighbor, right_index = utils.key.get_frame_neighbors(
                        fcurve, cur_frame, return_index=True)
                    left_far, key = utils.key.get_selected_neigbors(fcurve, left_index)
                    key, right_far = utils.key.get_selected_neigbors(fcurve, right_index)

                curve_items['selected_keys'] = None
                curve_items['first_key'] = None
                curve_items['last_key'] = None

            if left_neighbor is None:
                curve_items['left_neighbor'] = None
            else:
                # stores coordinates of left neighboring key
                co = {'x': left_neighbor.co_ui.x, 'y': left_neighbor.co_ui.y}
                curve_items['left_neighbor'] = co

            if right_neighbor is None:
                curve_items['right_neighbor'] = None
            else:
                # stores coordinates of right neighboring key
                co = {'x': right_neighbor.co_ui.x, 'y': right_neighbor.co_ui.y}
                curve_items['right_neighbor'] = co

            if left_far is None:
                curve_items['left_far'] = None
            else:
                # stores coordinates of left neighboring key
                co = {'x': left_far.co_ui.x, 'y': left_far.co_ui.y}
                curve_items['left_far'] = co

            if right_far is None:
                curve_items['right_far'] = None
            else:
                # stores coordinates of right neighboring key
                co = {'x': right_far.co_ui.x, 'y': right_far.co_ui.y}
                curve_items['right_far'] = co

            # if original:
            # stores original values of every key
            curve_items['original_values'] = values
            curve_items['every_key'] = every_key
            curve_items['under_cursor'] = under_cursor

            # if left_frame is not None or right_frame is not None:
            left_frame, right_frame = set_ref_marker(context)
            frames = {'left_y': fcurve.evaluate(left_frame),
                      'right_y': fcurve.evaluate(right_frame)}

            curve_items['ref_frames'] = frames

            curves[fcurve_index] = curve_items
            # curves['keys_selected'] = keys_selected

        global_values[obj.name] = curves
        global_values['keys_are_selected'] = keys_are_selected

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


