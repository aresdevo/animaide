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
from bpy.props import BoolProperty, EnumProperty, StringProperty, \
    IntProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup


handle_type_t = [('FREE', 'Free', 'Each handle can be manipulated independently', 'HANDLE_FREE', 1),
                 ('ALIGNED', 'Aligned', 'Handles remain aligned as you modify them', 'HANDLE_ALIGNED', 2),
                 ('VECTOR', 'Vector', 'Each handle points to the adjacent key', 'HANDLE_VECTOR', 3),
                 ('AUTO', 'Auto', 'Automatically adjust both handles to conform the the curve', 'HANDLE_AUTO', 4),
                 ('AUTO_CLAMPED', 'Auto Clamped',
                  'Automatically adjust both handles to conform the curve but'
                  ' flattens it as it gets to picks and valleys',
                  'HANDLE_AUTOCLAMPED', 5)]


interp_t = [('CONSTANT', 'Step', 'Poses hold until the next key', 'IPO_CONSTANT', 1),
            ('LINEAR', 'Linear', 'Gradual linear transition between keys', 'IPO_LINEAR', 2),
            ('BEZIER', 'Bezier', 'Transition between keys is affected by a curve tangents that can be manipulated',
             'IPO_BEZIER', 3),
            ('EASE', 'Ease', 'Preset of ease in and out curves with different level of strength and shapes',
             'IPO_EASE_IN_OUT', 4)]


strength_t = [('SINE', 'Sinusoidal', 'Options of ease mode to apply to keys', 'IPO_SINE', 1),
              ('QUAD', 'Quadratic', 'Options of ease mode to apply to keys', 'IPO_QUAD', 2),
              ('CUBIC', 'Cubic', 'Options of ease mode to apply to keys', 'IPO_CUBIC', 3),
              ('QUART', 'Quartic', 'Options of ease mode to apply to keys', 'IPO_QUART', 4),
              ('QUINT', 'Quintic', 'Options of ease mode to apply to keys', 'IPO_QUINT', 5),
              ('EXPO', 'Exponential', 'Options of ease mode to apply to keys', 'IPO_EXPO', 6),
              ('CIRC', 'Circular', 'Options of ease mode to apply to keys', 'IPO_CIRC', 7),
              ('BACK', 'Back', 'Options of ease mode to apply to keys', 'IPO_BACK', 8),
              ('BOUNCE', 'Bounce', 'Options of ease mode to apply to keys', 'IPO_BOUNCE', 9),
              ('ELASTIC', 'Elastic', 'Options of ease mode to apply to keys', 'IPO_ELASTIC', 10)]


easing_t = [('AUTO', 'Auto', 'Auto', 'IPO_EASE_IN_OUT', 1),
            ('EASE_IN', 'Ease in', 'Ease in', 'IPO_EASE_IN', 2),
            ('EASE_OUT', 'Ease-out', 'Ease-out', 'IPO_EASE_OUT', 3),
            ('EASE_IN_OUT', 'Ease in-out', 'Ease in-out', 'IPO_EASE_IN_OUT', 4)]


key_type_t = [('KEYFRAME', 'Keyframe', 'Normal keys in Blender', 'KEYTYPE_KEYFRAME_VEC', 1),
              ('BREAKDOWN', 'Breakdown', 'Usually used for in-between poses', 'KEYTYPE_BREAKDOWN_VEC', 2),
              ('JITTER', 'Jitter', 'Usually used for keys that happens in rapid succession', 'KEYTYPE_JITTER_VEC', 3),
              ('EXTREME', 'Extreme', 'Usually used for those key poses with the most vital' 
               ' information for the animation', 'KEYTYPE_EXTREME_VEC', 4)]


act_on_t = [('FIRST', 'First key', 'Preset of key groups', ' ', 1),
            ('LAST', 'Last key', 'Preset of key groups', ' ', 2),
            ('BOTH', 'First and last keys', 'Preset of key groups', ' ', 3),
            ('ALL', 'Every key', 'Preset of key groups', ' ', 4)]


amount_t = [('2', '2', 'Preset amounts to choose from', '', 1),
            ('3', '3', 'Preset amounts to choose from', '', 2),
            ('4', '4', 'Preset amounts to choose from', '', 3),
            ('5', '5', 'Preset amounts to choose from', '', 4),
            ('10', '10', 'Preset amounts to choose from', '', 5),
            ('20', '20', 'Preset amounts to choose from', '', 6),
            ('50', '50', 'Preset amounts to choose from', '', 7),
            ('100', '100', 'Preset amounts to choose from', '', 8)]


def update_handle_type(self, context):
    support.set_handles_type(context, handle_type=self.handle_type, check_ui=True)


def update_act_on(self, context):
    # support.set_handles_interp(context, act_on=self.act_on, interp=self.interp)
    support.set_handles_type(context, act_on=self.act_on, handle_type=self.handle_type, check_ui=False)


def interp_update(self, context):
    if self.interp == 'EASE':
        strength_update(self, context)
    else:
        support.set_handles_interp(context, interp=self.interp)


def easing_update(self, context):
    # if self.interp == 'EASE':
    support.set_handles_interp(context, easing=self.easing)


def strength_update(self, context):
    # if self.interp == 'EASE':
    support.set_handles_interp(context, strength=self.strength)


def amount_update(self, context):
    self.frames = int(self.amount)


class KeyTweak(PropertyGroup):

    panel_pref: StringProperty(default='PANEL')

    frames: IntProperty(default=1, min=1)

    left: BoolProperty(default=False)
    right: BoolProperty(default=False)
    point: BoolProperty(default=False)

    handle_type: EnumProperty(
        items=handle_type_t,
        name="Handle_type",
        default='AUTO_CLAMPED',
        update=update_handle_type
    )

    act_on: EnumProperty(
        items=act_on_t,
        name="Act-on",
        default='ALL',
        update=update_act_on
    )

    interp: EnumProperty(
        items=interp_t,
        name="Interpolation",
        default='BEZIER',
        update=interp_update
    )

    strength: EnumProperty(
        items=strength_t,
        name="Ease Strength",
        default='SINE',
        update=strength_update
    )

    easing: EnumProperty(
        items=easing_t,
        name="Ease Mode",
        default='AUTO',
        update=easing_update
    )

    amount: EnumProperty(
        items=amount_t,
        name="Presets",
        default='2',
        update=amount_update
    )


classes = (
    KeyTweak,
)
