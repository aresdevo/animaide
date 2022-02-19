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
    "version": (1, 0, 38_2),
    "blender": (2, 93, 0),
    "location": "Graph Editor - Dope Sheet - Timeline - 3D View - sidebar and menu bar",
    "warning": "This addon is still in development.",
    "category": "Animation",
    "doc_url": "https://github.com/aresdevo/animaide#readme",
    "tracker_url": "https://github.com/aresdevo/animaide/issues"
}

import bpy
import atexit
from . import ui, curve_tools, anim_offset, key_manager, prefe, utils
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty, PointerProperty, CollectionProperty, StringProperty
from bpy.types import AddonPreferences, PropertyGroup, Operator


prefe.addon_name = __package__


class AnimAideScene(PropertyGroup):
    clone: PointerProperty(type=curve_tools.props.AnimAideClone)
    tool: PointerProperty(type=curve_tools.props.AnimAideTool)
    anim_offset: PointerProperty(type=anim_offset.props.AnimAideOffset)
    key_tweak: PointerProperty(type=key_manager.props.KeyTweak)


classes = \
    anim_offset.classes + \
    curve_tools.classes + \
    key_manager.classes + \
    ui.menu_classes + \
    prefe.classes + \
    (AnimAideScene,)

@persistent
def load_post_handler(scene):
    # if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
    #     bpy.app.handlers.depsgraph_update_post.remove(support.magnet_handlers)
    utils.remove_message()
    print('init')


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.load_post.append(load_post_handler)

    bpy.types.Scene.animaide = PointerProperty(type=AnimAideScene)

    preferences = bpy.context.preferences
    pref = preferences.addons[prefe.addon_name].preferences

    # bpy.types.TIME_MT_editor_menus.append(curve_tools.ui.draw_bookmarks)

    bpy.types.DOPESHEET_MT_editor_menus.append(ui.draw_menu)
    bpy.types.GRAPH_MT_editor_menus.append(ui.draw_menu)
    bpy.types.VIEW3D_MT_editor_menus.append(ui.draw_menu)
    # bpy.types.TIME_MT_editor_menus.append(ui.draw_menu)

    if pref.key_manager_ui == 'PANEL':
        prefe.add_key_manager_panel()

    if pref.anim_offset_ui == 'PANEL':
        prefe.add_anim_offset_panel()

    if pref.key_manager_ui == 'HEADERS':
        prefe.add_key_manager_header()

    if pref.anim_offset_ui == 'HEADERS':
        prefe.add_anim_offset_header()

    # if pref.info_panel:
    #     for cls in ui.info_classes:
    #         bpy.utils.register_class(cls)

    # atexit.register(utils.remove_message)


def unregister():

    # utils.remove_message()

    preferences = bpy.context.preferences

    pref = preferences.addons[prefe.addon_name].preferences

    bpy.app.handlers.load_post.remove(load_post_handler)

    # bpy.types.TIME_MT_editor_menus.remove(curve_tools.ui.draw_bookmarks)

    bpy.types.DOPESHEET_MT_editor_menus.remove(ui.draw_menu)
    bpy.types.GRAPH_MT_editor_menus.remove(ui.draw_menu)
    bpy.types.VIEW3D_MT_editor_menus.remove(ui.draw_menu)
    # bpy.types.TIME_MT_editor_menus.remove(ui.draw_menu)

    if pref.key_manager_ui == 'PANEL':
        prefe.remove_key_manager_panel()

    if pref.anim_offset_ui == 'PANEL':
        prefe.remove_anim_offset_panel()

    if pref.key_manager_ui == 'HEADERS':
        prefe.remove_key_manager_header()

    if pref.anim_offset_ui == 'HEADERS':
        prefe.remove_anim_offset_header()

    # if pref.info_panel:
    #     for cls in reversed(ui.info_classes):
    #         bpy.utils.unregister_class(cls)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.animaide
