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


curve_node_mapping = {}
global_values = {}


def myNodeTree():
    if 'AnimAideTemp' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('AnimAideTemp', 'ShaderNodeTree')
        # ng.fake_user = True
    return bpy.data.node_groups['AnimAideTemp'].nodes


def myCurveData(curve_name):
    if curve_name not in curve_node_mapping:
        cn = myNodeTree().new('ShaderNodeRGBCurve')
        curve_node_mapping[curve_name] = cn.name
    return myNodeTree()[curve_node_mapping[curve_name]]


def magnet(context):
    """Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user """

    selected_objects = context.selected_objects

    animaide = context.scene.animaide

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)
        fcurves = getattr(action, 'fcurves', list())

        stored_obj = global_values.get(obj.name)

        if stored_obj is None:
            continue

        for fcurve_index, fcurve in fcurves.items():
            if not utils.curve.valid_fcurve(context, obj, fcurve):
                continue

            # if fcurve.data_path.endswith("rotation_mode"):
            #     continue   #added exception

            if fcurve.lock:
                return

            global_fcurve = stored_obj.get(fcurve_index)
            original_values = global_fcurve.get('original_values')
            selected_keys = global_fcurve.get('selected_keys')
            first_key = global_fcurve.get('first_key')
            last_key = global_fcurve.get('last_key')
            box_width = last_key['x'] - first_key['x']
            box_height = last_key['y'] - first_key['y']

            # ng = bpy.data.node_groups['AnimAideTemp']
            # mapping = ng.nodes['RGB Curves'].mapping
            # curve = mapping.curves[0]

            if animaide.sculptor.switch is True:
                for index in selected_keys:
                    k = fcurve.keyframe_points[index]
                    # key_y = mapping.evaluate(curve, k.co.x/box_width)
                    key_y = 0
                    k.co_ui.y = original_values[index]['y'] + key_y * box_height

            fcurve.update()
    return


def get_globals(context):
    """Gets all the global values needed to work with the curve_tools"""

    global global_values

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
            values = {}

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                # stores coordinate of every key
                co = {'x': key.co_ui.x, 'y': key.co_ui.y}
                values[key_index] = co

                if key.select_control_point:
                    # stores only selected keys
                    keyframes.append(key_index)
                    keys_are_selected = True

                curve_items['last_key'] = co

                if key_index - 1 not in keyframes:
                    curve_items['first_key'] = co

            if keyframes:
                curve_items['selected_keys'] = keyframes
            else:
                curve_items['selected_keys'] = None

            # if original:
            # stores original values of every key
            curve_items['original_values'] = values

            curves[fcurve_index] = curve_items
            # curves['keys_selected'] = keys_selected

        global_values[obj.name] = curves
        global_values['keys_are_selected'] = keys_are_selected

    return
