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
from .. import utils
from bpy.types import Panel, Menu, UIList, WorkSpaceTool, GizmoGroup


class ANIMAIDE_PT_curve_sculptor:
    bl_label = "Curve Sculptor"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        animaide = context.scene.animaide
        sculptor = animaide.sculptor

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(sculptor, 'influence', text='Influence')
        layout.prop(sculptor, 'switch', text='On')
        # layout.template_curve_mapping(support.myCurveData('TestOne'), "mapping")


# class FalloffPanel(BrushPanel):
#     bl_label = "Falloff"
#     bl_options = {'DEFAULT_CLOSED'}
#
#     @classmethod
#     def poll(cls, context):
#         if not super().poll(context):
#             return False
#         settings = cls.paint_settings(context)
#         return (settings and settings.brush and settings.brush.curve)
#
#     def draw(self, context):
#         layout = self.layout
#         settings = self.paint_settings(context)
#         mode = self.get_brush_mode(context)
#         brush = settings.brush
#
#         if brush is None:
#             return
#
#         col = layout.column(align=True)
#         row = col.row(align=True)
#         row.prop(brush, "curve_preset", text="")
#
#         if brush.curve_preset == 'CUSTOM':
#             layout.template_curve_mapping(brush, "curve", brush=True)
#
#             col = layout.column(align=True)
#             row = col.row(align=True)
#             row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
#             row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
#             row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
#             row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
#             row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
#             row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'
#
#         if mode in {'SCULPT', 'PAINT_VERTEX', 'PAINT_WEIGHT'} and brush.sculpt_tool != 'POSE':
#             col.separator()
#             row = col.row(align=True)
#             row.use_property_split = True
#             row.use_property_decorate = False
#             row.prop(brush, "falloff_shape", expand=True)


class ANIMAIDE_PT_curve_sculptor_ge(Panel, ANIMAIDE_PT_curve_sculptor):
    bl_idname = 'ANIMAIDE_PT_curve_sculptor_ge'
    bl_space_type = 'GRAPH_EDITOR'


classes = (
    ANIMAIDE_PT_curve_sculptor_ge,
)

