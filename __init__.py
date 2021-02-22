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

# Addon Info
bl_info = {
    "name": "AnimAide",
    "description": "Helpful tools to manipulate keys on f-curves",
    "author": "Ares Deveaux",
    "version": (1, 0, 1),
    "blender": (2, 91, 0),
    "location": "Graph Editor - Dope Sheet - Timeline - 3D View - sidebar and menu bar",
    "warning": "This addon is still in development.",
    "category": "Animation",
    "wiki_url": "https://github.com/aresdevo/animaide",
    "tracker_url": "https://github.com/aresdevo/animaide/issues"
}

import bpy
from . import ui, curve_tools, anim_offset, key_manager, utils
from bpy.props import BoolProperty, EnumProperty, PointerProperty, CollectionProperty, StringProperty
from bpy.types import AddonPreferences, PropertyGroup, Operator


pref = ''


class Preferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = 'animaide'

    def key_manager_update(self, context):
        global pref
        # panel_pref = context.scene.animaide.key_tweak.panel_pref
        if self.key_manager_ui == pref:
            return

        if self.key_manager_ui == 'HEADERS':
            bpy.types.TIME_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset)
            bpy.types.GRAPH_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)
            bpy.types.DOPESHEET_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)
            for cls in key_manager.ui.header_classes:
                bpy.utils.register_class(cls)
            bpy.types.TIME_MT_editor_menus.append(key_manager.ui.draw_key_manager)
            bpy.types.TIME_MT_editor_menus.append(anim_offset.ui.draw_anim_offset)
            bpy.types.DOPESHEET_MT_editor_menus.append(key_manager.ui.draw_key_manager)
            bpy.types.DOPESHEET_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)
            bpy.types.GRAPH_MT_editor_menus.append(key_manager.ui.draw_key_interpolation)
            bpy.types.GRAPH_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)
            for cls in key_manager.ui.panel_classes:
                bpy.utils.unregister_class(cls)

            pref = self.key_manager_ui

        elif self.key_manager_ui == 'PANEL':
            for cls in key_manager.ui.panel_classes:
                bpy.utils.register_class(cls)
            for cls in key_manager.ui.header_classes:
                bpy.utils.unregister_class(cls)
            bpy.types.TIME_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
            bpy.types.DOPESHEET_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
            bpy.types.GRAPH_MT_editor_menus.remove(key_manager.ui.draw_key_interpolation)

            pref = self.key_manager_ui

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

    def info_panel_update(self, context):
        if self.info_panels:
            for cls in ui.info_classes:
                bpy.utils.register_class(cls)
        else:
            for cls in reversed(ui.info_classes):
                bpy.utils.unregister_class(cls)

    key_manager_ui: EnumProperty(
        items=[('PANEL', 'Panel', 'Choose if you want "Key Manager" on a panel', '', 1),
               ('HEADERS', 'Headers', 'Choose if you want "Key Manager" tools on headers', '', 2)],
        name="Ease Mode",
        default='PANEL',
        update=key_manager_update
    )

    tool_on_release: BoolProperty(default=True,
                                  description='Changes how the tools modal work')

    ct_use_markers: BoolProperty(default=True,
                              description='use markers for the reference frames',
                              update=toggle_tool_markers)

    ao_fast_offset: BoolProperty(default=False)

    info_panels: BoolProperty(default=True,
                              update=info_panel_update)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.prop(self, "key_manager_ui", text="Key Manager on")
        col = layout.column(heading='Curve Tools')
        col.prop(self, 'tool_on_release', text='Activate on mouse release', toggle=False)
        col.prop(self, 'ct_use_markers', text='Use markers', toggle=False)
        col = layout.column(heading='Anim Offset')
        col.prop(self, 'ao_fast_offset', text='Fast calculation', toggle=False)
        col = layout.column(heading='Info')
        col.prop(self, 'info_panels', text='Panels', toggle=False)


class AnimAideScene(PropertyGroup):
    clone: PointerProperty(type=curve_tools.props.AnimAideClone)
    tool: PointerProperty(type=curve_tools.props.AnimAideTool)
    anim_offset: PointerProperty(type=anim_offset.props.AnimAideOffset)
    key_tweak: PointerProperty(type=key_manager.props.KeyTweak)


op_classes = \
    anim_offset.props.classes + \
    anim_offset.ops.classes + \
    curve_tools.props.classes + \
    curve_tools.ops.classes + \
    key_manager.props.classes + \
    key_manager.ops.classes + \
    (AnimAideScene,)


ui_classes = \
    curve_tools.ui.classes + \
    anim_offset.ui.classes + \
    ui.menu_classes


def register():

    global pref

    for cls in op_classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.animaide = PointerProperty(type=AnimAideScene)

    bpy.utils.register_class(Preferences)

    preferences = bpy.context.preferences
    pref = preferences.addons['animaide'].preferences

    if pref.key_manager_ui == 'PANEL':
        key_manager_ui_classes = ui_classes + key_manager.ui.panel_classes
    else:
        key_manager_ui_classes = ui_classes + key_manager.ui.header_classes

    for cls in key_manager_ui_classes:
        bpy.utils.register_class(cls)

    if pref.info_panels:
        for cls in ui.info_classes:
            bpy.utils.register_class(cls)

    # bpy.types.TIME_MT_editor_menus.append(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        bpy.types.TIME_MT_editor_menus.append(key_manager.ui.draw_key_manager)
    # bpy.types.TIME_MT_editor_menus.append(curve_tools.ui.draw_bookmarks)
    bpy.types.TIME_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)

    bpy.types.DOPESHEET_MT_editor_menus.append(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        bpy.types.DOPESHEET_MT_editor_menus.append(key_manager.ui.draw_key_manager)
    bpy.types.DOPESHEET_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)

    # bpy.types.GRAPH_MT_key.append(draw_graph_menu)
    bpy.types.GRAPH_MT_editor_menus.append(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        # bpy.types.GRAPH_MT_editor_menus.append(key_manager.ui.draw_key_manager)
        bpy.types.GRAPH_MT_editor_menus.append(key_manager.ui.draw_key_interpolation)
    bpy.types.GRAPH_MT_editor_menus.append(anim_offset.ui.draw_anim_offset_mask)

    bpy.types.VIEW3D_MT_editor_menus.append(ui.draw_menu)


def unregister():

    global pref

    preferences = bpy.context.preferences
    pref = preferences.addons['animaide'].preferences

    if pref.key_manager_ui == 'PANEL':
        key_manager_ui_classes = ui_classes + key_manager.ui.panel_classes
    else:
        key_manager_ui_classes = ui_classes + key_manager.ui.header_classes

    for cls in reversed(key_manager_ui_classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(op_classes):
        bpy.utils.unregister_class(cls)

    if pref.info_panels:
        for cls in reversed(ui.info_classes):
            bpy.utils.unregister_class(cls)

    # bpy.types.TIME_MT_editor_menus.remove(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        bpy.types.TIME_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
    # bpy.types.TIME_MT_editor_menus.remove(curve_tools.ui.draw_bookmarks)
    bpy.types.TIME_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)

    bpy.types.DOPESHEET_MT_editor_menus.remove(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        bpy.types.DOPESHEET_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
    bpy.types.DOPESHEET_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)

    # bpy.types.GRAPH_MT_key.remove(draw_graph_menu)
    bpy.types.GRAPH_MT_editor_menus.remove(ui.draw_menu)
    if pref.key_manager_ui == 'HEADERS':
        # bpy.types.GRAPH_MT_editor_menus.remove(key_manager.ui.draw_key_manager)
        bpy.types.GRAPH_MT_editor_menus.remove(key_manager.ui.draw_key_interpolation)
    bpy.types.GRAPH_MT_editor_menus.remove(anim_offset.ui.draw_anim_offset_mask)

    bpy.types.VIEW3D_MT_editor_menus.remove(ui.draw_menu)

    bpy.utils.unregister_class(Preferences)

    del bpy.types.Scene.animaide
