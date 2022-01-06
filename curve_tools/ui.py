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
from . import support
from .. import utils
from bpy.types import Panel, Menu, UIList, WorkSpaceTool, GizmoGroup


def step_button(layout, tool, factor, icon='',
                text='', emboss=True, active=True,
                operator_context='EXEC_DEFAULT'):

    layout.active = active

    layout.operator_context = operator_context

    buttons = dict(operator='anim.aide_%s' % str(tool.selector).lower(),
                  text=text, emboss=emboss)
    if icon:
        buttons['icon'] = icon

    step = layout.operator(**buttons)

    step.factor = factor
    # if getattr(step, 'slope', None):
    #     step.slope = tool.slope
    if getattr(step, 'phase', None):
        step.phase = tool.noise_phase

    step.op_context = operator_context

    # bpy.context.window.workspace.status_text_set(None)


def blend_button(layout, fac, text='', icon='NONE'):
    op = layout.operator('anim.aide_blend_neighbor', text=text, icon=icon)
    op.op_context = 'EXEC_DEFAULT'
    op.factor = fac


def reference_frames(context, layout, expand):
    tool = context.scene.animaide.tool

    if tool.selector == 'BLEND_FRAME':

        row = layout.row(align=True)
        # row.label(text='Referece frames:')

        left_frame, right_frame = support.set_ref_marker(context)

        row = layout.row(align=True)
        row.scale_y = .7

        col = row.column(align=False)
        col.scale_x = .3
        col.label(text='L:')

        # left reference botton
        col = row.column(align=False)
        left_ref_frame = col.operator("anim.aide_get_ref_frame", text=str(left_frame), emboss=True)
        left_ref_frame.side = 'L'

        col = row.column(align=False)
        col.scale_x = .3
        col.label(text='R:')

        # right reference button
        col = row.column(align=False)
        right_ref_frame = col.operator("anim.aide_get_ref_frame", text=str(right_frame), emboss=True)
        right_ref_frame.side = 'R'

        # layout.prop(tool, 'use_markers', text='Use markers', toggle=False)


def steps(context, layout, tool, expand):

    # -------- Steps -----------

    # box = layout.box()
    row = layout.row(align=True)
    row.scale_y = .6
    row.active = True
    row.operator_context = 'EXEC_DEFAULT'

    # left overshoot extra buttons
    if tool.overshoot:
        for f in [-2, -1.5]:
            step_button(row, tool, factor=f, text=' ', icon='')

    # left end button
    step_button(row, tool, factor=-1, text='-1',
                icon='NONE', emboss=True, active=True)

    # left buttons
    for f in [-0.75, -0.5, -0.25]:
        step_button(row, tool, factor=f, text=' ', icon='')

    # Center Button
    step_button(row, tool, factor=0, text='0',
                icon='NONE', emboss=True, active=True)

    # right buttons
    for f in [0.25, 0.5, 0.75]:
        step_button(row, tool, factor=f, text=' ', icon='')

    # right end button
    step_button(row, tool, factor=1, text='1',
                icon='NONE', emboss=True, active=True)

    # right overshoot extra buttons
    if tool.overshoot:
        for f in [1.5, 2]:
            step_button(row, tool, factor=f, text=' ', icon='')

    # -------- selector -----------

    if expand:
        selected = utils.general.get_items(context, any_mode=True)
        # row = box.row(align=True)
        row = layout.row(align=True)
        if not selected:
            row.active = False
        if context.area.type == 'VIEW_3D':
            row.prop(tool, 'selector_3d', text='')
        else:
            row.prop(tool, 'selector', text='')
        row.prop(tool, 'overshoot', text='', toggle=1, invert_checkbox=False, icon='SNAP_INCREMENT')


def tool_button(context, layout_type, tool_type=''):
    area = context.area.type
    tool = context.scene.animaide.tool

    if tool.overshoot is False:
        rango = 'factor'
    else:
        rango = 'factor_overshoot'

    if area == 'VIEW_3D':
        selector = tool.selector_3d
    else:
        selector = tool.selector

    if tool_type == '':
        same_type = True
        tool_type = str(selector).lower()
        # On this alternative the button will be whatever option is on the selector
    else:
        same_type = (str(selector).lower() == tool_type)
        # Checks if the tool button matches the option in the selector

    if tool.show_factor and same_type and area == tool.area:
        layout_type.prop(tool, rango, text='', slider=True)
        # substitute the button with a slider of the factor
    else:
        layout_type.operator('anim.aide_%s' % tool_type, emboss=True)


class ANIMAIDE_PT_curve_tools:
    bl_label = "Curve Tools"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        animaide = context.scene.animaide
        tool = animaide.tool
        clone = animaide.clone

        layout = self.layout

        box = layout.box()
        col = box.column(align=True)

        selected = utils.general.get_items(context, any_mode=True)

        if context.area.type == 'VIEW_3D':
            expand = tool.expand_3d
            expand_text = 'expand_3d'
            selector_text = 'selector_3d'
        else:
            expand = tool.expand
            expand_text = 'expand'
            selector_text = 'selector'

        if not expand:
            subrow = col.row(align=True)

            if not selected:
                subrow.active = False
            subrow.prop(tool, expand_text, text='', icon='RIGHTARROW', emboss=True, icon_only=True)
            tool_button(context, subrow)
            subrow.prop(tool, 'overshoot', text='', toggle=1, invert_checkbox=False, icon='SNAP_INCREMENT')
            subrow.prop_menu_enum(tool, selector_text, text='', icon='FCURVE')
            # subrow.prop(tool, 'selector', text='', icon='FCURVE', icon_only=True)
        else:
            col.prop(tool, expand_text, text='', icon='DOWNARROW_HLT', emboss=True)
            if context.area.type != 'VIEW_3D':
                tool_button(context, col, 'blend_ease')
            tool_button(context, col, 'blend_frame')
            tool_button(context, col, 'blend_infinite')
            tool_button(context, col, 'blend_neighbor')
            if context.area.type != 'VIEW_3D':
                tool_button(context, col, 'blend_offset')
                col.separator()
                tool_button(context, col, 'ease')
                tool_button(context, col, 'ease_to_ease')
            col.separator()
            if context.area.type != 'VIEW_3D':
                tool_button(context, col, 'scale_average')
            tool_button(context, col, 'scale_left')
            tool_button(context, col, 'scale_right')
            col.separator()
            if context.area.type != 'VIEW_3D':
                tool_button(context, col, 'smooth')
            tool_button(context, col, 'push_pull')
            tool_button(context, col, 'time_offset')
            tool_button(context, col, 'tween')
            if context.area.type != 'VIEW_3D':
                tool_button(context, col, 'wave_noise')

        steps(context, box, tool, expand)

        layout.use_property_split = True
        layout.use_property_decorate = False

        if context.area.type == 'GRAPH_EDITOR':
            layout.prop(tool, 'sticky_handles', text='Sticky handles')

        if tool.selector == 'TIME_OFFSET':

            layout.prop(clone, 'cycle', text='Cicle Options')

        reference_frames(context, layout, expand)


class ANIMAIDE_PT_curve_tools_ge(Panel, ANIMAIDE_PT_curve_tools):
    bl_idname = 'ANIMAIDE_PT_curve_tools_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_curve_tools_de(Panel, ANIMAIDE_PT_curve_tools):
    bl_idname = 'ANIMAIDE_PT_curve_tools_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_PT_curve_tools_3d(Panel, ANIMAIDE_PT_curve_tools):
    bl_label = "On Frame Curve Tools"
    bl_idname = 'ANIMAIDE_PT_curve_tools_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_UL_frame_bookmarks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        bookmark = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row.prop(bookmark, "name", text="", emboss=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            row.alignment = 'CENTER'
            row.label(text="", icon_value=icon)


class ANIMAIDE_PT_frame_bookmarks:
    bl_label = "Frame Bookmarks"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        animaide = context.scene.animaide
        tool = animaide.tool

        row = layout.row(align=False)
        row.template_list("ANIMAIDE_UL_frame_bookmarks", "", tool, "frame_bookmarks", tool, "bookmark_index")
        col = row.column(align=True)
        col.operator('anim.aide_add_bookmark', text='', emboss=True, icon='ADD')
        col.operator('anim.aide_delete_bookmark', text='', emboss=True, icon='REMOVE')
        col.separator()
        op = col.operator('anim.aide_push_bookmark', text='', emboss=True, icon='EVENT_L')
        op.side = 'L'
        op = col.operator('anim.aide_push_bookmark', text='', emboss=True, icon='EVENT_R')
        op.side = 'R'


class ANIMAIDE_PT_frame_bookmarks_ge(Panel, ANIMAIDE_PT_frame_bookmarks):
    bl_idname = 'ANIMAIDE_PT_frame_bookmarks_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_curve_tools_ge'


class ANIMAIDE_PT_frame_bookmarks_3d(Panel, ANIMAIDE_PT_frame_bookmarks):
    bl_idname = 'ANIMAIDE_PT_frame_bookmarks_3d'
    bl_space_type = 'VIEW_3D'
    bl_parent_id = 'ANIMAIDE_PT_curve_tools_3d'


# class ANIMAIDE_PT_frame_bookmarks_de(Panel, ANIMAIDE_PT_frame_bookmarks):
#     bl_idname = 'ANIMAIDE_PT_frame_bookmarks_de'
#     bl_space_type = 'DOPESHEET_EDITOR'
#     # bl_parent_id = 'ANIMAIDE_PT_curve_tools_de'


# class ANIMAIDE_PT_frame_bookmarks_3d(Panel, ANIMAIDE_PT_frame_bookmarks):
#     bl_idname = 'ANIMAIDE_PT_frame_bookmarks_3d'
#     bl_space_type = 'VIEW_3D'
#     bl_parent_id = 'ANIMAIDE_PT_curve_tools_3d'


class ANIMAIDE_MT_curve_tools(Menu):
    bl_idname = 'ANIMAIDE_MT_curve_tools'
    bl_label = "Curve Tools"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_blend_ease')
        layout.operator('anim.aide_blend_frame')
        layout.operator('anim.aide_blend_infinite')
        layout.operator('anim.aide_blend_neighbor')
        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_blend_offset')

            layout.operator('anim.aide_ease')
            layout.operator('anim.aide_ease_to_ease')

            layout.operator('anim.aide_scale_average')
        layout.operator('anim.aide_scale_left')
        layout.operator('anim.aide_scale_right')

        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_smooth')
        layout.operator('anim.aide_push_pull')
        layout.operator('anim.aide_time_offset')
        layout.operator('anim.aide_tween')
        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_wave_noise')


class ANIMAIDE_MT_tweak(Menu):
    bl_idname = 'ANIMAIDE_MT_tweak'
    bl_label = "Tweak"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        blend_button(layout, -0.10, text="Tweak Left")
        blend_button(layout, 0.10, text="Tweak Right")
        blend_button(layout, -1, text="Match Left")
        blend_button(layout, 1, text="Match Right")


class ANIMAIDE_MT_curve_tools_pie(Menu):
    bl_idname = 'ANIMAIDE_MT_curve_tools_pie'
    bl_label = "Pie Curve Tools"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.operator('wm.call_menu_pie', text="Group A").name = 'ANIMAIDE_MT_pie_curve_tools_a'
        layout.operator('wm.call_menu_pie', text="Group B").name = 'ANIMAIDE_MT_pie_curve_tools_b'


class ANIMAIDE_MT_pie_curve_tools_a(Menu):
    bl_idname = "ANIMAIDE_MT_pie_curve_tools_a"
    bl_label = "Curve Tools A"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("anim.aide_ease_to_ease")
        pie.operator("anim.aide_tween")
        pie.operator("anim.aide_blend_ease")
        pie.operator("anim.aide_ease")
        pie.operator("anim.aide_blend_neighbor")
        pie.operator("anim.aide_scale_average")
        pie.operator("anim.aide_push_pull")
        pie.operator("anim.aide_blend_frame")


class ANIMAIDE_MT_pie_curve_tools_b(Menu):
    bl_idname = "ANIMAIDE_MT_pie_curve_tools_b"
    bl_label = "Curve Tools B"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("anim.aide_scale_left")
        pie.operator("anim.aide_scale_right")
        pie.operator("anim.aide_wave_noise")
        pie.operator("anim.aide_smooth")
        pie.operator("anim.aide_blend_offset")
        pie.operator("anim.aide_time_offset")
        pie.operator('anim.aide_blend_infinite')


class ANIMAIDE_MT_pie_curve_tools_3d(Menu):
    bl_idname = "ANIMAIDE_MT_pie_curve_tools_3d"
    bl_label = "Curve Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("anim.aide_tween")
        pie.operator("anim.aide_blend_neighbor")
        pie.operator("anim.aide_push_pull")
        pie.operator("anim.aide_blend_frame")
        pie.operator("anim.aide_scale_left")
        pie.operator("anim.aide_scale_right")
        pie.operator("anim.aide_time_offset")
        pie.operator('anim.aide_blend_infinite')


def draw_bookmarks(self, context):
    layout = self.layout
    row = layout.row(align=False)
    row.popover(panel="ANIMAIDE_PT_frame_bookmarks_ge", text="", icon='BOOKMARKS')
    row.separator()


classes = (
    ANIMAIDE_PT_curve_tools_ge,
    # ANIMAIDE_PT_curve_tools_de,
    ANIMAIDE_PT_curve_tools_3d,
    ANIMAIDE_UL_frame_bookmarks,
    ANIMAIDE_PT_frame_bookmarks_ge,
    # ANIMAIDE_PT_frame_bookmarks_de,
    ANIMAIDE_PT_frame_bookmarks_3d,
    ANIMAIDE_MT_pie_curve_tools_a,
    ANIMAIDE_MT_pie_curve_tools_b,
    ANIMAIDE_MT_pie_curve_tools_3d,
    ANIMAIDE_MT_curve_tools,
    ANIMAIDE_MT_tweak,
    ANIMAIDE_MT_curve_tools_pie
)
