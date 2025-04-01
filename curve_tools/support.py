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

import math
import bpy

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors
# from utils.curve import valid_anim, valid_fcurve, valid_obj
# from utils.curve import poll_fcurve
# from utils import get_items
from .. import utils, prefe


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


def add_shear_curve():
    """Add a curve with 4 control pints to an action called 'animaide' that would act as a mask for anim_offset"""
    action = utils.set_animaide_action()
    fcurves = getattr(action, 'fcurves', None)
    # fcurves = utils.curve.get_all_fcurves(obj)
    if len(fcurves) == 0:
        return utils.curve.new('Shear', 2, key_interp='VECTOR')
    else:
        return fcurves[0]


def set_shear_values(left, right):
    """Modify the position of the fcurve 4 control points that is been used as mask to anim_offset """

    # scene = context.scene
    action = bpy.data.actions.get('animaide')
    curves = getattr(action, 'fcurves', None)

    if curves is not None:
        curve = curves[0]
        keys = curve.keyframe_points

        # left_blend = scene.frame_preview_start
        # left_margin = scene.frame_start
        # right_margin = scene.frame_end
        # right_blend = scene.frame_preview_end

        keys[0].co.x = left
        keys[0].co.y = 0
        keys[1].co.x = right
        keys[1].co.y = 0
        # keys[2].co.x = right_margin
        # keys[2].co.y = 1
        # keys[3].co.x = right_blend
        # keys[3].co.y = 0
        curve.keyframe_points.sort()
        curve.keyframe_points.handles_recalc()


def shear(self, direction):
    if direction == 'left':
        direction = 1
    else:
        direction = 0
    shear_action = utils.set_animaide_action()
    shear_curves = getattr(shear_action, 'fcurves', None)
    shear_curve = add_shear_curve()
    local_y = self.right_neighbor['y'] - self.left_neighbor['y']
    set_shear_values(self.left_neighbor['x'], self.right_neighbor['x'])

    factor = utils.clamp(self.factor, self.min_value, self.max_value)
    shear_curve.keyframe_points[direction].co_ui.y = local_y
    shear_curve.keyframe_points.sort()
    shear_curve.keyframe_points.handles_recalc()

    for index in self.selected_keys:
        k = self.fcurve.keyframe_points[index]
        k.co_ui.y = self.original_keys[index]['y'] + shear_curve.evaluate(k.co.x) * factor

    shear_curves.remove(shear_curve)


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

    global_objs = global_values['objects']

    for obj_name in global_objs:

        global_actions = global_objs[obj_name]['actions']

        self.some_keys_selected = global_objs[obj_name]['keys_are_selected']

        for action_type in global_actions:

            global_fcurves = global_actions[action_type]['curves']
            action = global_actions[action_type]['action']

            if not action:
                continue

            self.fcurves = action.fcurves

            for fcurve_i in global_fcurves:
                    self.fcurve = self.fcurves[fcurve_i]

                    self.global_fcurve = global_fcurves[fcurve_i]

                    self.selected_keys = self.global_fcurve['selected_keys']

                    # self.some_keys_selected = self.global_fcurve['keys_are_selected']

                    self.noise_steps += 1

                    under_cursor = self.global_fcurve['under_cursor']

                    if not self.selected_keys:
                        if self.some_keys_selected:
                            continue
                        elif under_cursor:
                            self.selected_keys = under_cursor
                        elif self.tool_type in ('SMOOTH', 'TIME_OFFSET', 'WAVE_NOISE', 'SCALE_AVERAGE'):
                            self.report({'WARNING'}, "This tool only works on frames with keys")
                            continue

                    self.original_keys = self.global_fcurve['original_keys']
                    self.left_neighbor = self.global_fcurve['left_neighbor']
                    self.right_neighbor = self.global_fcurve['right_neighbor']

                    function(*args)

                    self.fcurve.keyframe_points.sort()
                    self.fcurve.keyframe_points.handles_recalc()

    return {'FINISHED'}


def reset_original():
    """Set selected keys to the values in the global variables"""

    global_objs = global_values['objects']

    for obj_name in global_objs:

        global_actions = global_objs[obj_name]['actions']

        for action_type in global_actions:

            global_fcurves = global_actions[action_type]['curves']
            action = global_actions[action_type]['action']

            if not action:
                continue

            for fcurve_i in global_fcurves:
                fcurve = action.fcurves[fcurve_i]

                global_fcurve = global_fcurves[fcurve_i]

                selected_keys = global_fcurve['selected_keys']
                original_keys = global_fcurve['original_keys']

                if not original_keys:
                    continue

                if not selected_keys:
                    continue

                for index in selected_keys:
                    if index is None:
                        continue
                    k = fcurve.keyframe_points[index]
                    k.co_ui.y = original_keys[index]['y']
                    handles = original_keys[index]['handles']
                    k.handle_left.y = handles.get('l')
                    k.handle_right.y = handles.get('r')

                fcurve.keyframe_points.sort()
                fcurve.keyframe_points.handles_recalc()

    return


def get_globals(context):
    """Gets all the global values needed to work with the curve_tools"""

    global global_values
    objects = utils.get_items(context)
    keys_are_selected = False
    obj_actions = {}

    for obj in objects:
        if not utils.curve.valid_obj(context, obj):
            continue

        actions = utils.get_all_actions(obj)

        if not actions:
            continue

        global_action_type = {}
        global_action_data = {}

        for action_data in actions:
            action = action_data['action']

            if not action:
                continue

            action_type = action_data['type']
            fcurves = action.fcurves

            if not fcurves:
                continue

            global_curve_data = {}

            # Allows selection in dope sheet to work in graph editor
            for fcurve_index, fcurve in fcurves.items():
                fcurve.select = True

            for fcurve_index, fcurve in fcurves.items():
                if not utils.curve.valid_fcurve(context, obj, fcurve, action_type=action_type):
                    continue

                curve_items = {}
                keyframes = []
                under_cursor = []
                values = {}
                every_key = []
                last_index = 0

                keys = fcurve.keyframe_points
                if not keys:
                    continue

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
                    if key.select_control_point and context.area.type != 'VIEW_3D':
                        # stores only selected keys
                        keyframes.append(key_index)
                        keys_are_selected = True

                        # find smooth values (average) of the original keys

                        values[key_index]['book_end'] = False
                        curve_items['last_key'] = co
                        last_index = key_index

                        if key_index - 1 not in keyframes:
                            values[key_index]['book_end'] = True
                            curve_items['first_key'] = co

                values[last_index]['book_end'] = True

                if keyframes:
                    left_neighbor, left_index, right_neighbor, right_index = utils.key.get_selected_neigbors(
                        fcurve, keyframes, return_index=True)
                    left_far, key = utils.key.get_selected_neigbors(fcurve, left_index)
                    key, right_far = utils.key.get_selected_neigbors(fcurve, right_index)

                    # Store selected keys
                    curve_items['selected_keys'] = keyframes
                else:
                    if under_cursor:
                        left_neighbor, left_index, right_neighbor, right_index = utils.key.get_selected_neigbors(
                            fcurve, under_cursor, return_index=True)
                        left_far, key = utils.key.get_selected_neigbors(fcurve, left_index)
                        key, right_far = utils.key.get_selected_neigbors(fcurve, right_index)
                    else:
                        cur_frame = context.scene.frame_current
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

                # stores original values of every key
                curve_items['original_keys'] = values
                curve_items['every_key'] = every_key
                curve_items['under_cursor'] = under_cursor

                left_frame, right_frame = set_ref_marker(context)
                frames = {'left_y': fcurve.evaluate(left_frame),
                          'right_y': fcurve.evaluate(right_frame)}

                curve_items['ref_frames'] = frames

                global_curve_data[fcurve_index] = curve_items
            if global_curve_data:
                global_action_type[action_type] = {'curves': global_curve_data,
                                                   'action': action}
        if global_action_type:
            obj_actions[obj.name] = {'actions': global_action_type,
                                     'keys_are_selected': keys_are_selected}
    global_values = {'objects': obj_actions}
    return


def set_ref_marker(context):
    preferences = context.preferences
    pref = preferences.addons[prefe.addon_name].preferences
    tool = context.scene.animaide.tool
    # if tool.use_markers:
    if pref.ct_use_markers:
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


