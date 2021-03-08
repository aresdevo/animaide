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

from . import support
from .. import utils
import bpy
from bpy.types import Panel, Menu, UIList, WorkSpaceTool


def key_type_row(layout, name, key_type, icon):
    row = layout.row(align=True)
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='RESTRICT_SELECT_OFF')
    op.type = key_type
    op.selection = True
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='RESTRICT_SELECT_ON')
    op.type = key_type
    op.selection = False
    op = row.operator('anim.aide_set_key_type', text=name, emboss=True, icon=icon)
    op.type = key_type
    op = row.operator('anim.aide_delete_key_type', text='', emboss=True, icon='TRASH')
    op.type = key_type


def handles_select_row(layout, name, icon='NONE', left=False, right=False, point=False, depress=False):
    op = layout.operator('anim.aide_select_key_parts', text=name, emboss=True, icon=icon, depress=depress)
    op.left = left
    op.right = right
    op.point = point


def handles_type_row(context, layout, act_on, name, icon='NONE', handle_type='NONE'):
    subcol = layout.column(align=True)
    if not utils.general.poll(context):
        subcol.active = False
    key_tweak = context.scene.animaide.key_tweak
    # subcol.prop(key_tweak, act_on, text='', icon='LAYER_USED', icon_only=True, emboss=False)
    op = subcol.operator('anim.aide_set_handles_type', text=name, emboss=True, icon=icon)
    op.handle_type = handle_type
    op.act_on = 'SELECTION'
    op.check_ui = True
    subcol.prop(key_tweak, act_on, text='', icon='CHECKMARK', icon_only=True, emboss=False)


class ANIMAIDE_PT_key_manager:
    bl_label = "Key Manager"
    # bl_region_type = 'UI'
    # bl_category = 'AnimAide'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class ANIMAIDE_PT_key_manager_ge(Panel, ANIMAIDE_PT_key_manager):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_key_manager_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_key_manager_de(Panel, ANIMAIDE_PT_key_manager):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_key_manager_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_PT_key_manager_header(Panel, ANIMAIDE_PT_key_manager):
    bl_options = {'HIDE_HEADER'}
    bl_region_type = 'HEADER'
    bl_idname = 'ANIMAIDE_PT_key_manager_header'
    bl_space_type = 'GRAPH_EDITOR'


def move_insert_keys(context, layout):

    if not utils.general.poll(context):
        layout.active = False

    key_tweak = context.scene.animaide.key_tweak

    row = layout.row(align=True)

    op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRACKING_BACKWARDS_SINGLE')
    op.direction = 'LEFT'
    op.amount = key_tweak.frames

    # row.separator()

    op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRACKING_FORWARDS_SINGLE')
    op.direction = 'RIGHT'
    op.amount = key_tweak.frames

    row.separator()

    sub = row.split(factor=0.8, align=True)
    sub.scale_x = .6

    sub.prop(key_tweak, 'frames', text='', slider=False)
    sub.prop(key_tweak, 'amount', text='', icon_only=True, emboss=True)

    row.separator()

    op = row.operator('anim.aide_insert_frames', text='', emboss=True, icon='IMPORT')
    op.amount = key_tweak.frames

    # row.separator()

    op = row.operator('anim.aide_insert_frames', text='', emboss=True, icon='EXPORT')
    op.amount = -key_tweak.frames


class ANIMAIDE_PT_move_keys:
    bl_label = "Move-Insert"
    # bl_region_type = 'UI'
    # bl_category = 'AnimAide'

    def draw(self, context):

        layout = self.layout

        move_insert_keys(context, layout)


class ANIMAIDE_PT_move_keys_ge(Panel, ANIMAIDE_PT_move_keys):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_move_keys_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_move_keys_de(Panel, ANIMAIDE_PT_move_keys):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_move_keys_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_de'


class ANIMAIDE_PT_move_keys_header(Panel, ANIMAIDE_PT_move_keys):
    bl_region_type = 'HEADER'
    bl_idname = 'ANIMAIDE_PT_move_keys_header'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_header'


class ANIMAIDE_PT_key_type:
    bl_label = "Type"
    # bl_region_type = 'UI'
    # bl_category = 'AnimAide'
    # bl_space_type = 'DOPESHEET_EDITOR'
    # bl_region_type = 'HEADER'
    # bl_label = "Key Type"
    # bl_options = {'HIDE_HEADER'}

    def draw(self, context):

        layout = self.layout

        key_type_row(layout, 'Keyframe', 'KEYFRAME', 'KEYTYPE_KEYFRAME_VEC')
        key_type_row(layout, 'Breakdown', 'BREAKDOWN', 'KEYTYPE_BREAKDOWN_VEC')
        key_type_row(layout, 'Jitter', 'JITTER', 'KEYTYPE_JITTER_VEC')
        key_type_row(layout, 'Extreme', 'EXTREME', 'KEYTYPE_EXTREME_VEC')

        layout.label(text='New keys will be:')

        layout.prop(context.scene.tool_settings, 'keyframe_type', text='')


class ANIMAIDE_PT_key_type_ge(Panel, ANIMAIDE_PT_key_type):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_key_type_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_key_type_de(Panel, ANIMAIDE_PT_key_type):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_key_type_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_de'


class ANIMAIDE_PT_key_type_header(Panel, ANIMAIDE_PT_key_type):
    bl_region_type = 'HEADER'
    bl_idname = 'ANIMAIDE_PT_key_type_header'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_header'


class ANIMAIDE_PT_key_interp:
    bl_label = "Interpolation"
    # bl_region_type = 'UI'
    # bl_category = 'AnimAide'

    # bl_space_type = 'DOPESHEET_EDITOR'
    # bl_region_type = 'HEADER'
    # bl_label = "Key Interpolation"
    # bl_options = {'HIDE_HEADER'}

    def draw(self, context):

        # if context.area.type == 'GRAPH_EDITOR':

        support.external_op = context.active_operator

        layout = self.layout

        key_tweak = context.scene.animaide.key_tweak

        if not utils.general.poll(context):
            layout.active = False

        row = layout.row(align=True)

        row.prop(key_tweak, 'interp', text='')

        # layout.separator()

        if key_tweak.interp == 'CONSTANT':

            op = row.operator('anim.aide_set_handles_interp',
                                 text='',
                                 emboss=True, icon='CHECKMARK')
            op.interp = 'CONSTANT'
            op.strength = 'NONE'
            op.easing = 'NONE'
            op.act_on = 'ALL'
            op.check_ui = False

        elif key_tweak.interp == 'LINEAR':

            op = row.operator('anim.aide_set_handles_interp',
                                 text='',
                                 emboss=True, icon='CHECKMARK')
            op.interp = 'LINEAR'
            op.strength = 'NONE'
            op.easing = 'NONE'
            op.act_on = 'ALL'
            op.check_ui = False

        elif key_tweak.interp == 'BEZIER':

            key_tweak = context.scene.animaide.key_tweak
            row.prop(key_tweak, 'handle_type', icon_only=True)
            row.prop(key_tweak, 'act_on', text='', icon='CHECKMARK', icon_only=True)

            subrow = layout.row(align=True)

            subrow.label(text='Handle selection:')

            subrow = layout.row(align=True)

            if support.external_op and support.external_op != support.last_op:
                if support.external_op.name == 'Box Select':
                    left = True
                    point = True
                    right = True
                else:
                    left = False
                    point = True
                    right = False
            else:
                if key_tweak.left:
                    left = True
                else:
                    left = False

                if key_tweak.point:
                    point = True
                else:
                    point = False

                if key_tweak.right:
                    right = True
                else:
                    right = False

            handles_select_row(subrow, 'Left', left=True, depress=left)
            handles_select_row(subrow, '', icon='DECORATE_KEYFRAME', point=point, depress=point)
            handles_select_row(subrow, 'Right', right=True, depress=right)

            subrow = layout.row(align=True)

            subrow.prop(context.space_data, 'pivot_point', text='')

        elif key_tweak.interp == 'EASE':

            row.prop(key_tweak, 'strength', text='', icon_only=True)
            row.prop(key_tweak, 'easing', text='', icon_only=True)

            op = row.operator('anim.aide_set_handles_interp',
                                 text='',
                                 emboss=True, icon='CHECKMARK')
            op.interp = 'EASE'
            op.easing = key_tweak.easing
            op.strength = key_tweak.strength
            op.act_on = 'ALL'
            op.check_ui = False


class ANIMAIDE_PT_key_interp_ge(Panel, ANIMAIDE_PT_key_interp):
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_idname = 'ANIMAIDE_PT_key_interp_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_key_interp_header(Panel, ANIMAIDE_PT_key_interp):
    bl_region_type = 'HEADER'
    bl_idname = 'ANIMAIDE_PT_key_interp_header'
    bl_space_type = 'GRAPH_EDITOR'
    # bl_parent_id = 'ANIMAIDE_PT_key_manager_header'


def draw_key_interpolation(self, context):
    layout = self.layout
    row = layout.row(align=False)
    row.popover(panel="ANIMAIDE_PT_key_interp_header", text="", icon='FORCE_HARMONIC')
    # row.separator()


def draw_key_manager(self, context):
    layout = self.layout
    row = layout.row(align=False)
    row.popover(panel="ANIMAIDE_PT_key_manager_header", text="", icon='CON_ACTION')
    if context.area.type == 'GRAPH_EDITOR':
        row.popover(panel="ANIMAIDE_PT_key_interp_header", text="", icon='FORCE_HARMONIC')
    # row.separator()


panel_classes = (
    ANIMAIDE_PT_key_manager_ge,
    ANIMAIDE_PT_key_manager_de,
    ANIMAIDE_PT_move_keys_ge,
    ANIMAIDE_PT_move_keys_de,
    ANIMAIDE_PT_key_type_ge,
    ANIMAIDE_PT_key_type_de,
    ANIMAIDE_PT_key_interp_ge,
)


header_classes = (
    ANIMAIDE_PT_key_manager_header,
    ANIMAIDE_PT_move_keys_header,
    ANIMAIDE_PT_key_type_header,
    ANIMAIDE_PT_key_interp_header,
)
