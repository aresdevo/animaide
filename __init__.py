import bpy

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
    "description": "",
    "author": "Ares Deveaux",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "Graph Editor > Sidebar",
    "warning": "This addon is still in development.",
    "category": "Animation",
    "wiki_url": "https://github.com/aresdevo/animaide",
    "tracker_url": "https://github.com/aresdevo/animaide/issues"
}

# load and reload submodules
#################################
from . import utils, key_utils, cur_utils, magnet, props, ops, ui

classes = props.classes + ops.classes + ui.classes


# register
##################################


def draw_graph_menu(self, context):
    layout = self.layout
    layout.menu('AAT_MT_menu_operators')



def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.GRAPH_MT_key.append(draw_graph_menu)

    props.set_props()


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.GRAPH_MT_key.remove(draw_graph_menu)

    props.del_props()

    if magnet.anim_transform_handlers in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(magnet.anim_transform_handlers)

    if magnet.anim_trans_mask_handlers in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(magnet.anim_trans_mask_handlers)
