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
from bpy.props import BoolProperty, EnumProperty, IntProperty
from bpy.types import PropertyGroup


def interpolation_update(self, context):
    blends_action = bpy.data.actions.get('animaide')
    blends_curves = getattr(blends_action, 'fcurves', None)
    if blends_curves:
        keys = blends_curves[0].keyframe_points
        support.mask_interpolation(keys, context)


class AnimAideOffset(PropertyGroup):

    user_preview_start: IntProperty()

    user_preview_end: IntProperty()

    user_preview_use: BoolProperty()

    user_scene_start: IntProperty()

    user_scene_end: IntProperty()

    user_scene_auto: BoolProperty()

    blends: BoolProperty(default=False)

    # end_on_release: BoolProperty(default=False)

    mask_in_use: BoolProperty(default=False)

    fast_mask: BoolProperty(default=False)

    insert_outside_keys: BoolProperty(default=True)

    interp: EnumProperty(
        items=[('LINEAR', ' ', 'Linear transition', 'IPO_LINEAR', 1),
               ('SINE', ' ', 'Curve slope 1', 'IPO_SINE', 2),
               ('CUBIC', ' ', 'Curve slope 3', 'IPO_CUBIC', 3),
               ('QUART', ' ', 'Curve Slope 4', 'IPO_QUART', 4),
               ('QUINT', ' ', 'Curve Slope 5', 'IPO_QUINT', 5)],
        name="Mask Blend Interpolation",
        default='SINE',
        update=interpolation_update
    )

    easing: EnumProperty(
        items=[('EASE_IN', 'Ease in', 'Sets Mask transition type', 'IPO_EASE_IN', 1),
               ('EASE_IN_OUT', 'Ease in-out', 'Sets Mask transition type', 'IPO_EASE_IN_OUT', 2),
               ('EASE_OUT', 'Ease-out', 'Sets Mask transition type', 'IPO_EASE_OUT', 3)],
        name="Mask Blend Easing",
        default='EASE_IN_OUT',
        update=interpolation_update
    )


classes = (
    AnimAideOffset,
)
