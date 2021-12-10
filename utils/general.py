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
import blf

# from curve_tools.support import get_items


def gradual(key_y, target_y, delta=1.0, factor=0.15):
    """Gradualy transition the value of key_y to target_y"""
    step = abs(key_y - target_y) * (delta * factor)

    if target_y > key_y:
        return key_y + step

    else:
        return key_y - step


def clamp(value, minimum, maximum, to_none=False):
    """Take a value and if it goes beyond the minimum and maximum it would replace it with those."""

    if value <= minimum:
        if to_none is True:
            return None
        else:
            return minimum

    if value >= maximum:
        if to_none is True:
            return None
        else:
            return maximum

    return value


def floor(value, minimum, to_none=False):
    """Take the value and if it goes lower than the minimum it would replace it with it"""
    if value < minimum:
        if to_none is True:
            return None
        else:
            return minimum

    return value


def ceiling(value, maximum, to_none=False):
    """Take the value and if it goes over the maximum it would replace it with it"""
    if value > maximum:
        if to_none is True:
            return None
        else:
            return maximum

    return value


def toggle(to_toggle, value_a, value_b):
    """Change 'to_toggle' to one of the tow values it doesn't have at the moment"""
    if to_toggle == value_a:
        return value_b
    elif to_toggle == value_b:
        return value_a


def add_marker(name, side, frame=0, overwrite=True):
    """add reference frames marker"""

    animaide = bpy.context.scene.animaide
    use_markers = animaide.tool.use_markers

    if not use_markers:
        return

    name = f'{side}{name}'

    markers = bpy.context.scene.timeline_markers
    if overwrite:
        remove_marker(side)
    marker = markers.new(name=name, frame=frame)
    marker['side'] = side
    return marker


def modify_marker(marker, name='SAME', frame='SAME'):
    if name != 'SAME':
        marker.name = name

    if frame != 'SAME':
        marker.frame = frame


def remove_marker(side):
    """Removes reference frame markers"""

    markers = bpy.context.scene.timeline_markers

    for marker in markers:
        if marker.get('side') == side:
            markers.remove(marker)
    return


def switch_aim(aim, factor):
    if factor < 0.5:
        aim = aim * -1
    return aim


def poll(context):
    """Poll used on all the slider operators"""

    selected = get_items(context, any_mode=True)

    area = context.area.type
    return bool((area == 'GRAPH_EDITOR' or
                area == 'DOPESHEET_EDITOR' or
                area == 'VIEW_3D') and
                selected)


def get_items(context, any_mode=False):
    """returns objects"""
    if any_mode:
        if context.mode == 'OBJECT':
            selected = context.selected_objects
        elif context.mode == 'POSE':
            selected = context.selected_pose_bones
        else:
            selected = None
    else:
        selected = context.selected_objects

    if context.area.type == 'VIEW_3D':
        return selected
    elif context.space_data.dopesheet.show_only_selected:
        return selected
    else:
        return bpy.data.objects


text_handle = None
pref_autosave = None
dopesheet_color = None
graph_color = None
nla_color = None


def add_message(message):

    global text_handle, dopesheet_color, graph_color, nla_color, pref_autosave
    if text_handle is None:
        pref_autosave = bpy.context.preferences.use_preferences_save
        dopesheet_color = bpy.context.preferences.themes[0].dopesheet_editor.space.header[:]
        graph_color = bpy.context.preferences.themes[0].graph_editor.space.header[:]
        nla_color = bpy.context.preferences.themes[0].nla_editor.space.header[:]

    warning_color = (0.5, 0.3, 0.2, 1)
    bpy.context.preferences.use_preferences_save = False

    def draw_text_callback(info):
        font_id = 0
        # draw some text
        bpy.context.preferences.themes[0].dopesheet_editor.space.header = warning_color
        bpy.context.preferences.themes[0].nla_editor.space.header = warning_color
        bpy.context.preferences.themes[0].graph_editor.space.header = warning_color
        blf.position(font_id, 5, 80, 0)
        blf.size(font_id, 30, 72)
        blf.color(font_id, 1, 1, 1, .5)
        blf.draw(font_id, info)

    if text_handle is None:
        text_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_text_callback, (message,),
            'WINDOW', 'POST_PIXEL')


def remove_message():
    global text_handle

    bpy.types.SpaceView3D.draw_handler_remove(text_handle, 'WINDOW')
    text_handle = None

    if pref_autosave is not None:
        bpy.context.preferences.use_preferences_save = pref_autosave
    if dopesheet_color is not None:
        bpy.context.preferences.themes[0].dopesheet_editor.space.header = dopesheet_color
    if graph_color is not None:
        bpy.context.preferences.themes[0].nla_editor.space.header = graph_color
    if nla_color is not None:
        bpy.context.preferences.themes[0].graph_editor.space.header = nla_color
