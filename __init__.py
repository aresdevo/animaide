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
    # props.AnimAideFCurves,
    props.AnimAideClone,
    # props.AnimAideCloneData,
    props.AnimSlider,
    props.AnimAide,
    ops.AAT_OT_add_slider,
    ops.AAT_OT_remove_slider,
    ops.AAT_OT_settings,
    ops.AAT_OT_get_ref_frame,
    ops.AAT_OT_sliders,
    ops.AAT_OT_ease,
    ops.AAT_OT_ease_in_out,
    ops.AAT_OT_blend_neighbor,
    ops.AAT_OT_blend_frame,
    ops.AAT_OT_blend_ease,
    ops.AAT_OT_blend_offset,
    ops.AAT_OT_tween,
    ops.AAT_OT_push_pull,
    ops.AAT_OT_smooth,
    ops.AAT_OT_noise,
    ops.AAT_OT_time_offset,
    ops.AAT_OT_scale_average,
    ops.AAT_OT_scale_left,
    ops.AAT_OT_scale_right,
    # ops.AAT_OT_clone,
    # ops.AAT_OT_clone_remove,
    # ops.AAT_OT_move_key,
    # ops.AAT_OT_modifier,
    ui.AAT_PT_sliders,
    # ui.AAT_PT_clone
)

# register
##################################

# store keymaps here to access after registration
addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    props.set_props()

    # # handle the keymap
    # wm = bpy.context.window_manager
    # # Note that in background mode (no GUI available), keyconfigs are not available either, so we have to check this
    # # to avoid nasty errors in background case.
    # kc = wm.keyconfigs.addon
    # if kc:
    #     km = wm.keyconfigs.addon.keymaps.new(name='Slider', space_type='GRAPH_EDITOR')
    #     kmi = km.keymap_items.new(ops.AAT_OT_sliders.bl_idname, 'ONE', 'PRESS')
    #     # kmi.properties.total = 4
    #     addon_keymapseymaps.append((km, kmi))


def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    # for km, kmi in addon_keymaps:
    #     km.keymap_items.remove(kmi)
    # addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    props.del_props()
