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
    "name": "AnimSliders",
    "description": "",
    "author": "Ares Deveaux",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Graph Editor > Properties window",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Animation"}

# load and reload submodules
#################################
from . import utils, key_utils, cur_utils, props, ops, ui

# test

classes = (
    # props.AnimAideKeys,
    # props.myPreferences,
    props.AnimAideFCurves,
    props.AnimAideClone,
    props.AnimAideCloneData,
    props.AnimSlider,
    props.AnimSliders,
    ops.AS_OT_add,
    ops.AS_OT_remove,
    ops.AS_OT_settings,
    ops.AS_OT_get_ref_frame,
    ops.AS_OT_sliders,
    ops.AS_OT_clone,
    ops.AS_OT_clone_remove,
    ops.AS_OT_move_key,
    ops.AS_OT_modifier,
    ui.AS_PT_sliders,
    ui.AS_PT_clone
)

# register
##################################


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    props.set_props()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    props.del_props()
