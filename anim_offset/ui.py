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
# from .utils import key
from bpy.types import Panel, Menu


class ANIMAIDE_PT:
    bl_label = "Anim Offset"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        anim_offset = context.scene.animaide.anim_offset

        layout = self.layout

        # layout.label(text='Now Anim Offset buttons')
        # layout.label(text='are in the timeline')
        # layout.label(text='header next to Animaide')
        # layout.label(text='menu')

        row = layout.row(align=True)

        if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
            row.operator("anim.aide_deactivate_anim_offset", text='Deactivate', depress=True, icon='OVERLAY')
        else:
            row.operator("anim.aide_activate_anim_offset", text='Activate', icon='OVERLAY')

        row.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)

        row = layout.row(align=True)

        if context.area.type != 'VIEW_3D':
            mask_in_use = context.scene.animaide.anim_offset.mask_in_use
            if mask_in_use:
                name = 'Modify Mask'
                depress = True

            else:
                name = 'Mask'
                depress = False

            row.operator("anim.aide_add_anim_offset_mask", text=name, depress=depress, icon='SELECT_SUBTRACT')
            row.operator("anim.aide_delete_anim_offset_mask", text='', icon='TRASH')
            if mask_in_use:
                layout.label(text='Mask blend interpolation:')
                row = layout.row(align=True)
                row.prop(anim_offset, 'easing', text='', icon_only=False)
                row.prop(anim_offset, 'interp', text='', expand=True)


class ANIMAIDE_PT_anim_offset_3d(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_PT_anim_offset_ge(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_anim_offset_de(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_MT_anim_offset(Menu):
    bl_idname = 'ANIMAIDE_MT_anim_offset'
    bl_label = "Anim Offset"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.operator('anim.aide_activate_anim_offset', text='On')
        layout.operator('anim.aide_deactivate_anim_offset', text='Off')


class ANIMAIDE_MT_anim_offset_mask(Menu):
    bl_idname = 'ANIMAIDE_MT_anim_offset_mask'
    bl_label = "Anim Offset Mask"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_add_anim_offset_mask', text='Add/Modify')
            layout.operator('anim.aide_delete_anim_offset_mask', text='Delete')


class ANIMAIDE_MT_pie_anim_offset(Menu):
    bl_idname = "ANIMAIDE_MT_pie_anim_offset"
    bl_label = "AnimOffset"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator('anim.aide_activate_anim_offset', text='AnimOffset Without Mask')
        pie.operator('anim.aide_add_anim_offset_mask', text='Add AnimOffset Mask')
        pie.operator('anim.aide_delete_anim_offset_mask', text='Delete AnimOffset Mask')
        pie.operator('anim.aide_deactivate_anim_offset', text='Deactivate AnimOffset')


class ANIMAIDE_PT_preferences(Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Anim Offset Settings"
    bl_options = {'HIDE_HEADER'}

    # @classmethod
    # def poll(cls, context):
    #     return support.magnet_handlers in bpy.app.handlers.depsgraph_update_post

    def draw(self, context):
        anim_offset = context.scene.animaide.anim_offset

        layout = self.layout

        # if support.magnet_handlers not in bpy.app.handlers.depsgraph_update_post:
        #     layout.active = False

        mask_in_use = context.scene.animaide.anim_offset.mask_in_use
        if not mask_in_use:
            layout.active = False

        # layout.label(text='Settings')
        # layout.separator()
        # layout.prop(anim_offset, 'end_on_release', text='masking ends on mouse release')
        # layout.prop(anim_offset, 'fast_mask', text='Fast offset calculation')
        # if context.area.type != 'VIEW_3D':
        layout.prop(anim_offset, 'insert_outside_keys', text='Auto Key outside margins')
        layout.separator()
        layout.label(text='Mask blend interpolation:')
        row = layout.row(align=True)
        if not mask_in_use:
            row.active = False
        row.prop(anim_offset, 'easing', text='', icon_only=False)
        row.prop(anim_offset, 'interp', text='', expand=True)


def draw_anim_offset(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.separator()

    if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        row.operator("anim.aide_deactivate_anim_offset", text='', depress=True, icon='PROP_ON')
    else:
        row.operator("anim.aide_activate_anim_offset", text='', icon='PROP_ON')


def draw_anim_offset_mask(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.separator()

    if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        row.operator("anim.aide_deactivate_anim_offset", text='', depress=True, icon='PROP_ON')
    else:
        row.operator("anim.aide_activate_anim_offset", text='', icon='PROP_ON')

    mask_in_use = context.scene.animaide.anim_offset.mask_in_use
    if mask_in_use:
        row.operator("anim.aide_delete_anim_offset_mask", text='', depress=True, icon='SELECT_SUBTRACT')
        op = row.operator("anim.aide_add_anim_offset_mask", text='', icon='GREASEPENCIL')
        op.sticky = True
        sub = row.row(align=True)
        sub.active = True
    else:
        row.operator("anim.aide_add_anim_offset_mask", text='', icon='SELECT_SUBTRACT')
        sub = row.row(align=True)
        sub.active = False

    sub.popover(panel="ANIMAIDE_PT_preferences", text="")


classes = (
    # ANIMAIDE_PT_anim_offset_3d,
    # ANIMAIDE_PT_anim_offset_ge,
    # ANIMAIDE_PT_anim_offset_de,
    ANIMAIDE_MT_anim_offset,
    ANIMAIDE_MT_anim_offset_mask,
    ANIMAIDE_MT_pie_anim_offset,
    ANIMAIDE_PT_preferences,
)
