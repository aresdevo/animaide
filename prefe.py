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
from . import anim_offset, key_manager, utils, ui
from bpy.props import BoolProperty, EnumProperty
from bpy.types import AddonPreferences, PropertyGroup

key_manager_pref = ''
anim_offset_pref = ''
addon_name = __package__


def add_key_manager_header():
    global key_manager_pref
    for cls in key_manager.ui.header_classes:
        bpy.utils.register_class(cls)
    bpy.types.TIME_MT_editor_menus.append(key_manager.ui.draw_key_manager)
    bpy.types.DOPESHEET_MT_editor_menus.append(key_manager.ui.draw_key_manager)
    bpy.types.GRAPH_MT_editor_menus.append(key_manager.ui.draw_key_manager)
    key_manager_pref = 'HEADERS'


def remove_key_manager_header():
    global key_manager_pref
    for cls in key_manager.ui.header_classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TIME_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
    bpy.types.DOPESHEET_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
    bpy.types.GRAPH_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
    key_manager_pref = ''


def add_key_manager_panel():
    global key_manager_pref
    for cls in key_manager.ui.panel_classes:
        bpy.utils.register_class(cls)
    key_manager_pref = 'PANEL'


def remove_key_manager_panel():
    global key_manager_pref
    for cls in key_manager.ui.panel_classes:
        bpy.utils.unregister_class(cls)
    key_manager_pref = ''


def add_anim_offset_panel():
    global anim_offset_pref
    for cls in anim_offset.ui.panel_classes:
        bpy.utils.register_class(cls)
    anim_offset_pref = 'PANEL'


def remove_anim_offset_panel():
    global anim_offset_pref
    for cls in anim_offset.ui.panel_classes:
        bpy.utils.unregister_class(cls)
    anim_offset_pref = ''


def add_anim_offset_header():
    global anim_offset_pref
    bpy.types.TIME_MT_editor_menus.append(anim_offset.ui.draw_anim_offset)
    bpy.types.DOPESHEET_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)
    bpy.types.GRAPH_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)
    anim_offset_pref = 'HEADERS'


def remove_anim_offset_header():
    global anim_offset_pref
    bpy.types.TIME_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset)
    bpy.types.GRAPH_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)
    bpy.types.DOPESHEET_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)
    anim_offset_pref = ''


class Preferences(AddonPreferences):
    bl_idname = addon_name

    def key_manager_update(self, context):
        global key_manager_pref

        if self.key_manager_ui == key_manager_pref:
            return

        if self.key_manager_ui == 'HEADERS':
            remove_key_manager_panel()
            if self.anim_offset_ui == 'HEADERS':
                remove_anim_offset_header()
            add_key_manager_header()
            if self.anim_offset_ui == 'HEADERS':
                add_anim_offset_header()

        elif self.key_manager_ui == 'PANEL':
            remove_key_manager_header()
            add_key_manager_panel()

    def anim_offset_update(self, context):
        global anim_offset_pref

        if self.anim_offset_ui == anim_offset_pref:
            return

        if self.anim_offset_ui == 'HEADERS':
            remove_anim_offset_panel()
            add_anim_offset_header()

        elif self.anim_offset_ui == 'PANEL':
            remove_anim_offset_header()
            add_anim_offset_panel()

    def toggle_tool_markers(self, context):
        tool = context.scene.animaide.tool

        if self.ct_use_markers:
            if tool.left_ref_frame > 0:
                utils.add_marker(name='', side='L', frame=tool.left_ref_frame)

            if tool.right_ref_frame > 0:
                utils.add_marker(name='', side='R', frame=tool.right_ref_frame)
        else:
            for side in ['L', 'R']:
                utils.remove_marker(
                    side=side)
        return

    # def info_panel_update(self, context):
    #     if self.info_panel:
    #         for cls in ui.info_classes:
    #             bpy.utils.register_class(cls)
    #     else:
    #         for cls in reversed(ui.info_classes):
    #             bpy.utils.unregister_class(cls)

    key_manager_ui: EnumProperty(
        items=[('PANEL', 'Panel', 'Choose if you want "Key Manager" on a panel', '', 1),
               ('HEADERS', 'Headers', 'Choose if you want "Key Manager" tools on headers', '', 2)],
        name="Key Manager",
        default='PANEL',
        update=key_manager_update
    )

    anim_offset_ui: EnumProperty(
        items=[('PANEL', 'Panel', 'Choose if you want "Anim Offset" on a panel', '', 1),
               ('HEADERS', 'Headers', 'Choose if you want "Anim Offset" tools on headers', '', 2)],
        name="Anim Offset",
        default='HEADERS',
        update=anim_offset_update
    )

    tool_on_release: BoolProperty(default=True,
                                  description='Changes how the tools modal work')

    ct_use_markers: BoolProperty(default=True,
                                 description='use markers for the reference frames',
                                 update=toggle_tool_markers)

    ao_fast_offset: BoolProperty(default=False)

    # info_panel: BoolProperty(default=True,
    #                          update=info_panel_update)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(self, "anim_offset_ui", text="Anim Offset on")
        layout.prop(self, "key_manager_ui", text="Key Manager on")
        col = layout.column(heading='Curve Tools')
        col.prop(self, 'tool_on_release', text='Activate on mouse release', toggle=False)
        col.prop(self, 'ct_use_markers', text='Use markers', toggle=False)
        col = layout.column(heading='Anim Offset')
        col.prop(self, 'ao_fast_offset', text='Fast calculation', toggle=False)
        # col = layout.column(heading='Info')
        # col.prop(self, 'info_panel', text='Panel', toggle=False)


classes = (
    Preferences,
)
