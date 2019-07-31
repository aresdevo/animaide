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
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Graph Editor > Side Panel",
    "warning": "This addon is still in development.",
    "category": "Animation"},
    "wiki_url": "https://github.com/aresdevo/animaide",
    "tracker_url": "https://github.com/aresdevo/animaide/issues"
}

# load and reload submodules
#################################
from . import utils, key_utils, cur_utils, magnet, props, ops, ui

classes = props.classes + ops.classes + ui.classes

# register
##################################

# store keymaps here to access after registration


addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')

        kmi = km.keymap_items.new('wm.call_menu_pie', 'ONE', 'PRESS', alt=True)
        kmi.properties.name = 'AAT_MT_pie_menu_a'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('wm.call_menu_pie', 'TWO', 'PRESS', alt=True)
        kmi.properties.name = 'AAT_MT_pie_menu_b'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.ease_to_ease', 'ONE', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.tween', 'ONE', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.ease', 'TWO', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_ease', 'TWO', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_neighbor', 'THREE', 'PRESS')
        kmi.properties.op_context = 'INVOKE_DEFAULT'
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_neighbor', 'MINUS', 'PRESS')
        kmi.properties.op_context = 'EXEC_DEFAULT'
        kmi.properties.factor = -0.15
        kmi.properties.slope = 1
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_neighbor', 'EQUAL', 'PRESS')
        kmi.properties.op_context = 'EXEC_DEFAULT'
        kmi.properties.factor = 0.15
        kmi.properties.slope = 1
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_neighbor', 'MINUS', 'PRESS')
        kmi.shift = True
        kmi.properties.op_context = 'EXEC_DEFAULT'
        kmi.properties.factor = -1
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_neighbor', 'EQUAL', 'PRESS')
        kmi.shift = True
        kmi.properties.op_context = 'EXEC_DEFAULT'
        kmi.properties.factor = 1
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_frame', 'THREE', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.push_pull', 'FOUR', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.scale_average', 'FOUR', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.scale_left', 'FIVE', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.scale_right', 'FIVE', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.smooth', 'SIX', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.noise', 'SIX', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.time_offset', 'SEVEN', 'PRESS')
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new('animaide.blend_offset', 'SEVEN', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    props.set_props()

    register_keymaps()


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    props.del_props()

    unregister_keymaps()

