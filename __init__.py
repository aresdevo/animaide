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
from . import ui, curve_tools, anim_offset, key_manager
from bpy.props import BoolProperty, EnumProperty, PointerProperty, CollectionProperty
from bpy.types import AddonPreferences, PropertyGroup


class myPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = 'animaide'

    tools: BoolProperty(
        name="Sliders",
        default=True,
    )

    offset: BoolProperty(
        name="AnimOffset",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "tools", text="Use curveTools")
        layout.prop(self, "offset", text="Use animOffset")


def draw_graph_menu(self, context):
    layout = self.layout
    layout.menu('ANIMAIDE_MT_menu_operators')


class AnimAideScene(PropertyGroup):
    clone: PointerProperty(type=curve_tools.props.AnimAideClone)
    tool: PointerProperty(type=curve_tools.props.Tool)
    anim_offset: PointerProperty(type=anim_offset.props.AnimAideAnimOffset)

# key_manager.classes + \
classes = \
    anim_offset.classes + \
    curve_tools.classes + \
    ui.classes + \
    (AnimAideScene,)

# classes = \
#     curve_tools.props.classes + \
#     curve_tools.ops.classes + \
#     ops.classes + \
#     ui.classes + \
#     curve_tools.ui.classes + \
#     anim_offset.classes + \
#     (AnimAideScene,)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.GRAPH_MT_key.append(draw_graph_menu)
    bpy.types.GRAPH_MT_editor_menus.append(draw_graph_menu)

    bpy.types.DOPESHEET_MT_editor_menus.append(draw_graph_menu)

    bpy.types.TIME_MT_editor_menus.append(draw_graph_menu)

    bpy.types.VIEW3D_MT_editor_menus.append(draw_graph_menu)

    # bpy.utils.register_class(myPreferences)

    bpy.types.Scene.animaide = PointerProperty(type=AnimAideScene)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # bpy.types.GRAPH_MT_key.remove(draw_graph_menu)
    bpy.types.GRAPH_MT_editor_menus.remove(draw_graph_menu)

    bpy.types.DOPESHEET_MT_editor_menus.remove(draw_graph_menu)

    bpy.types.TIME_MT_editor_menus.remove(draw_graph_menu)

    # bpy.utils.unregister_class(myPreferences)

    del bpy.types.Scene.animaide
