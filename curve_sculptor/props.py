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
    IntProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup


def toggle(self, context):
    if self.switch:
        support.get_globals(context)
        print('globals: ', support.global_values)


class AnimAideSculptor(PropertyGroup):

    influence_options = [('MIRROR', 'Mirrored', '', '', 1),
                         ('TOP', 'Top', '', '', 2),
                         ('BOTTOM', 'Bottom', '', '', 3),
                         ('TOP_BOTTOM', 'Top-Bottom', '', '', 4),
                         ('CONSTANT', 'Constant', '', '', 5)]

    influence: EnumProperty(
        items=influence_options,
        name='Influence',
        default='MIRROR'
    )

    switch: BoolProperty(default=False,
                         update=toggle)

    factor: FloatProperty(default=0.0,
                          min=-1.0,
                          max=1.0
                          )


classes = (
    AnimAideSculptor,
)
