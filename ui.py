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

from bpy.types import Panel, Menu
from .curve_tools.ui import blend_button


# class ANIMAIDE_PT_help:
#     bl_label = "Help"
#     bl_region_type = 'UI'
#     bl_category = 'AnimAide'
#     bl_options = {'DEFAULT_CLOSED'}
#
#     def draw(self, context):
#
#         layout = self.layout
#
#         row = layout.row(align=True)
#
#         row.operator('anim.aide_manual', text='', icon='HELP', emboss=False)
#         row.operator('anim.aide_demo', text='', icon='FILE_MOVIE', emboss=False)


# class ANIMAIDE_PT_info:
#     bl_label = "Info"
#     bl_region_type = 'UI'
#     bl_category = 'AnimAide'
#
#     def draw(self, context):
#
#         layout = self.layout
#
#         layout.label(text='-Anim-offset and Key-manager')
#         layout.label(text='can now be put on the headers')
#         layout.label(text='instead of the panels.')
#         layout.label(text='-that and other preferences are')
#         layout.label(text='now located in the addon tab')
#         layout.label(text='in Blender Preferences.')
#         layout.label(text='Because of that Blender')
#         layout.label(text='will remember them after')
#         layout.label(text='you quit.')
#         layout.label(text='-This info panel can also')
#         layout.label(text='be removed in the addon')
#         layout.label(text='preferences.')
#         layout.label(text='Find more information at:')
#         layout.label(text='https://github.com/aresdevo/animaide')


# class ANIMAIDE_PT_info_3d(Panel, ANIMAIDE_PT_info):
#     bl_idname = 'ANIMAIDE_PT_info_3d'
#     bl_space_type = 'VIEW_3D'
#
#
# class ANIMAIDE_PT_info_ge(Panel, ANIMAIDE_PT_info):
#     bl_idname = 'ANIMAIDE_PT_info_ge'
#     bl_space_type = 'GRAPH_EDITOR'
#
#
# class ANIMAIDE_PT_info_de(Panel, ANIMAIDE_PT_info):
#     bl_idname = 'ANIMAIDE_PT_info_de'
#     bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_MT_operators(Menu):
    bl_idname = 'ANIMAIDE_MT_menu_operators'
    bl_label = "AnimAide"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.area.type == 'VIEW_3D':
            layout.menu('ANIMAIDE_MT_curve_tools', text='On Frame Curve Tools')
            layout.separator()
            layout.menu('ANIMAIDE_MT_anim_offset')

        elif context.area.type == 'DOPESHEET_EDITOR':
            layout.operator('wm.call_menu_pie', text="Pie AnimOffset").name = 'ANIMAIDE_MT_pie_anim_offset'
            layout.menu('ANIMAIDE_MT_anim_offset')
            layout.menu('ANIMAIDE_MT_anim_offset_mask')

        elif context.area.type == 'GRAPH_EDITOR':
            layout.menu('ANIMAIDE_MT_curve_tools_pie')
            layout.menu('ANIMAIDE_MT_curve_tools')
            layout.menu('ANIMAIDE_MT_tweak')
            layout.separator()
            layout.operator('wm.call_menu_pie', text="Pie AnimOffset").name = 'ANIMAIDE_MT_pie_anim_offset'
            layout.menu('ANIMAIDE_MT_anim_offset')
            layout.menu('ANIMAIDE_MT_anim_offset_mask')


def draw_menu(self, context):
    if context.mode == 'OBJECT' or context.mode == 'POSE':
        layout = self.layout
        layout.menu('ANIMAIDE_MT_menu_operators')


menu_classes = (
    ANIMAIDE_MT_operators,
)

# info_classes = (
#     ANIMAIDE_PT_info_3d,
#     ANIMAIDE_PT_info_ge,
#     ANIMAIDE_PT_info_de,
# )
