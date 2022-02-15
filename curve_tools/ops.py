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
import os
import math

# import utils.general
# import utils.key
from . import support
from .. import utils, prefe
# from .utils import curve, key
from bpy.props import StringProperty, FloatProperty, EnumProperty
from bpy.types import Operator


# ---------------  TOOLS  ------------------


class ANIMAIDE_OT:
    """Slider Operators Preset"""
    bl_options = {'UNDO_GROUPED'}

    # slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=1.0)
    # op_context: StringProperty(default='INVOKE_DEFAULT', options={'SKIP_SAVE'})
    op_context: EnumProperty(
        items=[('INVOKE_DEFAULT', 'Slider', 'Execute as slider', '', 1),
               ('EXEC_DEFAULT', 'Steps', 'Execute as steps', '', 2)],
        name="Mode",
        options={'SKIP_SAVE'},
        default='INVOKE_DEFAULT'
    )

    tool_type = None

    def __init__(self):
        self.cursor_keys = []
        self.display_info = ''
        pass

    def __del__(self):
        pass

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):
        return

    def add_key(self, context, fcurve):
        # if context.area.type == 'GRAPH_EDITOR':
        #     bpy.ops.graph.keyframe_insert(type='ALL')
        #     support.get_globals(context)
        #     bpy.ops.graph.select_all(action='DESELECT')
        # else:
        #     bpy.ops.anim.keyframe_insert_menu(type='Available')
        #     support.get_globals(context)

        keys = fcurve.keyframe_points
        cur_frame = context.scene.frame_current
        y = fcurve.evaluate(cur_frame)
        # keys.insert(cur_frame, y)
        utils.key.insert_key(keys, cur_frame, y)
        support.get_globals(context)

    def reset_tool_factor(self, context):
        tool = context.scene.animaide.tool
        tool.show_factor = False
        tool.factor = 0.0
        tool.factor_overshoot = 0.0
        context.window.cursor_set("DEFAULT")
        context.window.workspace.status_text_set(None)
        context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        # bpy.ops.wm.redraw_timer()
        # bpy.data.window_managers['WinMan'].windows.update()
        # bpy.data.window_managers['WinMan'].update_tag()

    def start(self, context, event):
        self.activated = True
        # context.scene.animaide.tool.show_factor = True
        self.init_mouse_x = event.mouse_x

    def end(self, context):
        self.activated = False
        # context.scene.animaide.tool.show_factor = False
        self.reset_tool_factor(context)
        return {'FINISHED'}

    def modal(self, context, event):
        tool = context.scene.animaide.tool
        info_tool = tool.selector.title().replace('_', ' ')
        info_factor = int(utils.clamp((self.factor * 100), -100, 100))

        # context.window.workspace.status_text_set()
        self.display_info = f"{info_tool}: {info_factor:3d}%               " \
                            f"MOUSE-RB: Exit {info_tool} mode"

        context.window.cursor_set("SCROLL_X")
        tool.show_factor = True

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # if tool.flip:
                if self.pref.tool_on_release:
                    return self.end(context)
                else:
                    self.start(context, event)

            elif event.value == 'RELEASE':
                # if tool.flip:
                if self.pref.tool_on_release:
                    self.start(context, event)
                else:
                    return self.end(context)

        if event.type == 'MOUSEMOVE' and self.activated:  # Use
            # context.window.workspace.status_text_set(self.display_info)

            tool_from_zero = (event.mouse_x - self.init_mouse_x) / 100
            self.factor = tool_from_zero

            tool.factor = tool_from_zero
            tool.factor_overshoot = tool_from_zero

            self.execute(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            support.reset_original(context)

            self.reset_tool_factor(context)

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'factor', text='', slider=True)

    def invoke(self, context, event):
        preferences = bpy.context.preferences
        self.pref = preferences.addons[prefe.addon_name].preferences
        animaide = context.scene.animaide
        tool = animaide.tool

        # if tool.flip:
        if self.pref.tool_on_release:
            self.start(context, event)
        else:
            self.activated = False
            tool.show_factor = False
            self.init_mouse_x = 0

        self.warning = 'No keys selected or under the cursor. You need auto-key to add values'

        # The select operator(s) are bugged, and can fail to update selected keys, so
        # When you change the frame, then select keys, the previous keys will stay marked as selected
        utils.key.update_keyframe_points(context)

        if self.op_context == 'EXEC_DEFAULT':
            return self.execute(context)

        tool.factor = 0.0
        tool.factor_overshoot = 0.0
        # self.slope = tool.slope
        self.phase = tool.noise_phase

        # self.init_mouse_x = event.mouse_x

        tool.area = context.area.type

        if context.area.type == 'VIEW_3D':
            tool.selector_3d = self.tool_type
            tool.unselected_fcurves = True
        else:
            tool.selector = self.tool_type
            tool.unselected_fcurves = False

        # left_frame, right_frame = support.set_ref_marker(context)

        support.get_globals(context)

        # if support.global_values['are_keys_selected']:
        #     animaide.tool.keys_under_cursor = False
        # else:
        #     animaide.tool.keys_under_cursor = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIMAIDE_OT_ease_to_ease(Operator, ANIMAIDE_OT):
    """Transition selected or current keys from the neighboring\n""" \
    """ones in a "S" shape manner (ease-in and ease-out simultaneously).\n""" \
    """It doesn't take into consideration the current key values.\n"""

    bl_idname = "anim.aide_ease_to_ease"
    bl_label = "Ease To Ease"

    tool_type = 'EASE_TO_EASE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            local_y = self.right_neighbor['y'] - self.left_neighbor['y']
            local_x = self.right_neighbor['x'] - self.left_neighbor['x']

            if local_x == 0:
                return

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                x = k.co.x - self.left_neighbor['x']

                factor = utils.clamp(self.factor, self.min_value, self.max_value)
                frame_ratio = x / local_x
                transition = support.s_curve(frame_ratio, xshift=-factor)
                new_value = self.left_neighbor['y'] + local_y * transition
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_ease(Operator, ANIMAIDE_OT):
    """Transition selected or current keys from the neighboring\n""" \
    """ones in a "C" shape manner (ease-in or ease-out). It doesn't\n""" \
    """take into consideration the current key values."""

    bl_idname = "anim.aide_ease"
    bl_label = "Ease"

    tool_type = 'EASE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            local_y = self.right_neighbor['y'] - self.left_neighbor['y']
            local_x = self.right_neighbor['x'] - self.left_neighbor['x']
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            flipflop = abs(factor)

            if local_x == 0:
                return

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                x = k.co.x - self.left_neighbor['x']

                frame_ratio = x / local_x
                if factor > 0:
                    shift = - 1
                else:
                    shift = 0
                slope = 1 + (5 * flipflop)
                ease_y = support.s_curve(frame_ratio, slope=slope, width=2, height=2, xshift=shift, yshift=shift)
                new_value = self.left_neighbor['y'] + local_y * ease_y
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_blend_ease(Operator, ANIMAIDE_OT):
    """Blend selected or current keys to the ease-in or ease-out\n""" \
    """curve using the neighboring keys."""

    bl_idname = "anim.aide_blend_ease"
    bl_label = "Blend Ease"

    tool_type = 'BLEND_EASE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            local_x = self.right_neighbor['x'] - self.left_neighbor['x']
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            flipflop = abs(factor)

            if local_x == 0:
                return

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                x = k.co_ui.x - self.left_neighbor['x']

                frame_ratio = x / local_x
                if factor > 0:
                    shift = - 1
                else:
                    shift = 0
                source = self.original_values[index]['y']
                if factor > 0:
                    delta = self.right_neighbor['y'] - source
                    base = source
                else:
                    delta = source - self.left_neighbor['y']
                    base = self.left_neighbor['y']
                slope = flipflop * 5
                ease_y = support.s_curve(frame_ratio, slope=slope, width=2, height=2, xshift=shift, yshift=shift)
                new_value = base + delta * ease_y
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_blend_neighbor(Operator, ANIMAIDE_OT):
    """Blend selected or current keys to the value of the neighboring\n""" \
    """left or right keys."""

    bl_idname = "anim.aide_blend_neighbor"
    bl_label = "Blend Neighbor"

    tool_type = 'BLEND_NEIGHBOR'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(abs(self.factor), 0, self.max_value)
            for index in self.selected_keys:
                if self.factor < 0:
                    delta = self.left_neighbor['y'] - self.original_values[index]['y']
                else:
                    delta = self.right_neighbor['y'] - self.original_values[index]['y']
                k = self.fcurve.keyframe_points[index]
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_blend_infinite(Operator, ANIMAIDE_OT):
    """Blend selected or current keys to the slant of neighboring\n""" \
    """left or right keys."""

    bl_idname = "anim.aide_blend_infinite"
    bl_label = "Blend infinite"

    tool_type = 'BLEND_INFINITE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(abs(self.factor), self.min_value, self.max_value)
            left_far = self.global_fcurve.get('left_far')
            right_far = self.global_fcurve.get('right_far')

            if self.factor < 0 and left_far:
                o = left_far['y'] - self.left_neighbor['y']
                a = left_far['x'] - self.left_neighbor['x']
            elif self.factor >= 0 and right_far:
                o = right_far['y'] - self.right_neighbor['y']
                a = right_far['x'] - self.right_neighbor['x']
            else:
                a = 1
                o = 1

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                if self.factor < 0:
                    new_a = k.co_ui.x - self.left_neighbor['x']
                    refe = self.left_neighbor['y']
                else:
                    new_a = k.co_ui.x - self.right_neighbor['x']
                    refe = self.right_neighbor['y']

                if a == 0:
                    new_o = 0
                else:
                    new_o = new_a * o / a

                delta = refe + new_o - self.original_values[index]['y']
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_blend_frame(Operator, ANIMAIDE_OT):
    """Blend selected or current keys to the value of the chosen\n""" \
    """left or right frames."""

    bl_idname = "anim.aide_blend_frame"
    bl_label = "Blend Frame"

    tool_type = 'BLEND_FRAME'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            ref = self.global_fcurve['ref_frames']
            factor = utils.clamp(abs(self.factor), 0, self.max_value)
            for index in self.selected_keys:
                if self.factor < 0:
                    delta = ref['left_y'] - self.original_values[index]['y']
                else:
                    delta = ref['right_y'] - self.original_values[index]['y']
                k = self.fcurve.keyframe_points[index]
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_blend_offset(Operator, ANIMAIDE_OT):
    """Shift selected or current keys to the\n""" \
    """value of the chosen left and right frames."""

    bl_idname = "anim.aide_blend_offset"
    bl_label = "Blend Offset"

    tool_type = 'BLEND_OFFSET'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            first_key_index = self.selected_keys[0]
            last_key_index = self.selected_keys[-1]
            if first_key_index is None or last_key_index is None:
                return
            for index in self.selected_keys:
                if factor < 0:
                    delta = self.original_values[first_key_index]['y'] - self.left_neighbor['y']
                else:
                    delta = self.right_neighbor['y'] - self.original_values[last_key_index]['y']
                k = self.fcurve.keyframe_points[index]
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)

        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_tween(Operator, ANIMAIDE_OT):
    """Set lineal relative value of the selected or current keys \n""" \
    """in relationship to the neighboring ones. It doesn't take into\n""" \
    """consideration the current key values."""

    bl_idname = "anim.aide_tween"
    bl_label = "Tween"

    tool_type = 'TWEEN'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            factor_zero_one = (factor+1)/2
            local_y = self.right_neighbor['y'] - self.left_neighbor['y']
            new_value = self.left_neighbor['y'] + local_y * factor_zero_one
            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_push_pull(Operator, ANIMAIDE_OT):
    """Exagerates or decreases the value of the selected or current keys"""

    bl_idname = "anim.aide_push_pull"
    bl_label = "Push Pull"

    tool_type = 'PUSH_PULL'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            factor_zero_two = factor + 1
            local_y = self.right_neighbor['y'] - self.left_neighbor['y']
            local_x = self.right_neighbor['x'] - self.left_neighbor['x']
            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                x = k.co_ui.x - self.left_neighbor['x']
                frame_ratio = x / local_x
                lineal = self.left_neighbor['y'] + local_y * frame_ratio
                delta = self.original_values[index]['y'] - lineal
                new_value = lineal + delta * factor_zero_two
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)
        return

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_smooth(Operator, ANIMAIDE_OT):
    """Averages values of selected keys creating a smoother fcurve"""

    bl_idname = "anim.aide_smooth"
    bl_label = "Smooth"

    tool_type = 'SMOOTH'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                if 'sy' not in self.original_values[index]:
                    continue
                smooth_y = self.original_values[index]['sy']
                if smooth_y == 'book end':
                    delta = 0
                else:
                    delta = self.original_values[index]['y'] - smooth_y
                k.co_ui.y = self.original_values[index]['y'] - delta * factor
        # else:
        #     self.report({'INFO'}, 'Some selected keys needed for this tool')

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_time_offset(Operator, ANIMAIDE_OT):
    """Shift the value in time of selected or current keys """

    bl_idname = "anim.aide_time_offset"
    bl_label = "Time Offset"

    tool_type = 'TIME_OFFSET'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            cycle = self.animaide.clone.cycle

            clone_name = '%s.%d.clone' % (self.fcurve.data_path, self.fcurve.array_index)
            clone = utils.curve.duplicate_from_data(self.fcurves,
                                                    self.global_fcurve,
                                                    clone_name,
                                                    before=cycle,
                                                    after=cycle)

            factor = utils.clamp(self.factor, self.min_value, self.max_value)

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]

                k.co_ui.y = clone.evaluate(k.co.x - 20 * factor)

            self.fcurves.remove(clone)

        # else:
        #     self.report({'INFO'}, 'Some selected keys needed for this tool')

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_wave_noise(Operator, ANIMAIDE_OT):
    """Set random values to the selected or current key \n""" \
    """or set them in a wave pattern."""

    bl_idname = "anim.aide_wave_noise"
    bl_label = "Wave-Noise"

    tool_type = 'WAVE_NOISE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool

            factor = utils.clamp(self.factor, self.min_value, self.max_value)

            if factor > 0:
                clone = utils.curve.duplicate_from_data(self.fcurves,
                                                        self.global_fcurve,
                                                        'animaide')

                phase = self.animaide.tool.noise_phase + self.noise_steps
                scale = self.animaide.tool.noise_scale

                support.add_noise(clone, strength=1, scale=scale, phase=phase)

                for index in self.selected_keys:
                    k = self.fcurve.keyframe_points[index]

                    delta = clone.evaluate(k.co.x) - self.original_values[index]['y']
                    new_value = self.original_values[index]['y'] + delta * factor
                    if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                        k.co.y = new_value
                    else:
                        k.co_ui.y = new_value

                self.fcurves.remove(clone)
            else:
                n = 0
                for index in self.selected_keys:
                    n += 1
                    if n == 1:
                        direction = 1
                    else:
                        direction = -1
                    k = self.fcurve.keyframe_points[index]
                    new_value = self.original_values[index]['y'] + (factor * direction)/5
                    if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                        k.co.y = new_value
                    else:
                        k.co_ui.y = new_value
                    if n == 2:
                        n = 0

        # else:
        #     self.report({'INFO'}, 'Some selected keys needed for this tool')

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_scale_left(Operator, ANIMAIDE_OT):
    """Increase or decrease the value of selected or current keys \n""" \
    """in relationship to the left neighboring one."""

    bl_idname = "anim.aide_scale_left"
    bl_label = "Scale Left"

    tool_type = 'SCALE_LEFT'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                delta = self.original_values[index]['y'] - self.left_neighbor['y']
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_scale_right(Operator, ANIMAIDE_OT):
    """Increase or decrease the value of selected or current keys \n""" \
    """in relationship to the right neighboring one."""

    bl_idname = "anim.aide_scale_right"
    bl_label = "Scale Right"

    tool_type = 'SCALE_RIGHT'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                delta = self.original_values[index]['y'] - self.right_neighbor['y']
                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value

        elif context.scene.tool_settings.use_keyframe_insert_auto:
            context.window.workspace.status_text_set(self.display_info)
            self.add_key(context, self.fcurve)
        # else:
        #     self.report({'INFO'}, self.warning)

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_scale_average(Operator, ANIMAIDE_OT):
    """Increase or decrease the value of selected or current keys \n""" \
    """in relationship to the average point of those affected"""

    bl_idname = "anim.aide_scale_average"
    bl_label = "Scale Average"

    tool_type = 'SCALE_AVERAGE'

    def tool(self, context):

        if self.selected_keys:
            if self.op_context == 'INVOKE_DEFAULT':
                context.window.workspace.status_text_set(self.display_info)

            tool = context.scene.animaide.tool
            factor = utils.clamp(self.factor, self.min_value, self.max_value)
            y = 0
            for index in self.selected_keys:
                y = y + self.original_values[index]['y']
            y_average = y / len(self.selected_keys)

            for index in self.selected_keys:
                k = self.fcurve.keyframe_points[index]
                delta = self.original_values[index]['y'] - y_average

                new_value = self.original_values[index]['y'] + delta * factor
                if tool.sticky_handles and context.area.type == 'GRAPH_EDITOR':
                    k.co.y = new_value
                else:
                    k.co_ui.y = new_value
        # else:
        #     self.report({'INFO'}, 'Some selected keys needed for this tool')

    def execute(self, context):
        return support.to_execute(self, context, self.tool, context)


class ANIMAIDE_OT_tools_settings(Operator):
    """Shows global options for Curve Tools"""

    bl_idname = "anim.aide_tools_settings"
    bl_label = "Tools Settings"

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def draw(self, context):
        animaide = context.scene.animaide
        tool = animaide.tool

        layout = self.layout

        layout.label(text='Settings')
        layout.separator()
        # layout.prop(tool, 'overshoot', text='overshoot', toggle=False)
        # layout.prop(tool, 'keys_under_cursor', text='Only keys under cursor', toggle=False)
        layout.prop(tool, 'flip', text='Activates on release', toggle=False)

        col = layout.column(align=False)
        if tool.selector == 'BLEND_FRAME':
            col.active = True
        else:
            col.active = False
        col.prop(tool, 'use_markers', text='Use markers', toggle=False)

        # col = layout.column(align=False)
        # if tool.selector == 'EASE_TO_EASE' or tool.selector == 'EASE':
        #     col.active = True
        # else:
        #     col.active = False
        # col.label(text='Ease slope')
        # col.prop(tool, 'slope', text='', slider=False)

        # if tool.selector == 'NOISE':
        #     layout.label(text='Noise settings')
        #     layout.prop(tool, 'noise_phase', text='Phase', slider=True)
        #     layout.prop(tool, 'noise_scale', text='Scale', slider=True)


class ANIMAIDE_OT_add_bookmark(Operator):
    """Adds a frame to the list for latter use as reference"""

    bl_idname = 'anim.aide_add_bookmark'
    bl_label = "Add Bookmark"
    bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        animaide = context.scene.animaide
        tool = animaide.tool
        bookmarks = tool.frame_bookmarks
        current_frame = context.scene.frame_current
        name = 'frame %s' % current_frame

        frame = bookmarks.get(name)

        if frame is None:
            bookmark = bookmarks.add()
            tool.bookmark_index = len(bookmarks) - 1
            bookmark.frame = current_frame
            bookmark.name = name

        return {'FINISHED'}


class ANIMAIDE_OT_delete_bookmark(Operator):
    """Delete frame from the list """

    bl_idname = 'anim.aide_delete_bookmark'
    bl_label = "Delete Bookmark"
    bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        animaide = context.scene.animaide
        tool = animaide.tool
        bookmarks = tool.frame_bookmarks
        index = tool.bookmark_index
        bookmarks.remove(index)

        return {'FINISHED'}


class ANIMAIDE_OT_push_bookmark(Operator):
    """Pushes the bookmarked frame to be used as reference frame"""

    bl_idname = 'anim.aide_push_bookmark'
    bl_label = "Push Bookmark"
    bl_options = {'UNDO_GROUPED'}

    side: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        preferences = context.preferences
        pref = preferences.addons[prefe.addon_name].preferences
        animaide = context.scene.animaide
        tool = animaide.tool
        index = tool.bookmark_index
        bookmark = tool.frame_bookmarks[index]
        frame = bookmark.frame
        context.scene.frame_current = frame

        # if tool.use_markers:
        if pref.ct_use_markers:
            utils.add_marker(name='', side=self.side, frame=frame)
        elif self.side == 'L':
            tool.left_ref_frame = frame
        else:
            tool.right_ref_frame = frame

        return {'FINISHED'}


class ANIMAIDE_OT_get_ref_frame(Operator):
    """Sets a refernce frame that will be use by the BLEND FRAME\n""" \
    """tool. The one at the left sets the left reference, and the\n""" \
    """one on the right sets the right reference"""

    bl_idname = 'anim.aide_get_ref_frame'
    bl_label = "Get Reference Frames"
    bl_options = {'UNDO_GROUPED'}

    side: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        preferences = context.preferences
        pref = preferences.addons[prefe.addon_name].preferences

        animaide = context.scene.animaide

        tool = animaide.tool

        current_frame = bpy.context.scene.frame_current

        if self.side == 'L':
            tool.left_ref_frame = current_frame

        if self.side == 'R':
            tool.right_ref_frame = current_frame

        # if tool.use_markers:
        if pref.ct_use_markers:
            utils.add_marker(name='', side=self.side, frame=current_frame)

        return {'FINISHED'}


class ANIMAIDE_OT_modifier(Operator):
    """Add noise to a curve using a modifier"""

    bl_idname = 'anim.aide_fcurve_modifier'
    bl_label = "Modifier"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        objects = context.selected_objects
        for obj in objects:
            action = obj.animation_data.action

            for curve in action.fcurves:
                if curve.select is not True:
                    continue
                noise = curve.modifiers.new('NOISE')

                noise.strength = 5
                noise.scale_tools = 3
                curve.convert_to_samples(0, 100)
                curve.convert_to_keyframes(0, 100)
                curve.modifiers.remove(noise)
        return {'FINISHED'}


class ANIMAIDE_OT_path(Operator):
    bl_idname = 'anim.aide_path'
    bl_label = "Path"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.object
        fcurves = obj.animation_data.action.fcurves
        utils.curve.create_path(context, fcurves)


classes = (
    ANIMAIDE_OT_tools_settings,
    ANIMAIDE_OT_get_ref_frame,
    ANIMAIDE_OT_push_bookmark,
    ANIMAIDE_OT_add_bookmark,
    ANIMAIDE_OT_delete_bookmark,
    ANIMAIDE_OT_ease_to_ease,
    ANIMAIDE_OT_ease,
    ANIMAIDE_OT_blend_ease,
    ANIMAIDE_OT_blend_neighbor,
    ANIMAIDE_OT_blend_frame,
    ANIMAIDE_OT_blend_offset,
    ANIMAIDE_OT_push_pull,
    ANIMAIDE_OT_scale_average,
    ANIMAIDE_OT_scale_left,
    ANIMAIDE_OT_scale_right,
    ANIMAIDE_OT_smooth,
    ANIMAIDE_OT_wave_noise,
    ANIMAIDE_OT_time_offset,
    ANIMAIDE_OT_tween,
    ANIMAIDE_OT_blend_infinite,
)
