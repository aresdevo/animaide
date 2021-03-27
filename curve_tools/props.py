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


menu_items = [('BLEND_EASE', 'Blend Ease', 'From current to C shape', '', 1),
              ('BLEND_FRAME', 'Blend Frame', 'From current to set frames', '', 2),
              ('BLEND_INFINITE', 'Blend Infinite', 'Adds or adjust keys to conform to the adjacent slope', '', 3),
              ('BLEND_NEIGHBOR', 'Blend Neighbor', 'From current to neighbors', '', 4),
              ('BLEND_OFFSET', 'Blend Offset', 'Offset key values to neighbors', '', 5),

              ('EASE', 'Ease', 'C shape transition', '', 6),
              ('EASE_TO_EASE', 'Ease To Ease', 'S shape transition', '', 7),

              ('SCALE_AVERAGE', 'Scale Average', 'Scale to average value', '', 8),
              ('SCALE_LEFT', 'Scale Left', 'Scale anchor to left neighbor', '', 9),
              ('SCALE_RIGHT', 'Scale Right', 'Scale anchor to right neighbor', '', 10),

              ('SMOOTH', 'Smooth', 'Smooths out fcurve keys', '', 11),
              ('PUSH_PULL', 'Push Pull', 'Overshoots key values', '', 12),

              ('TIME_OFFSET', 'Time Offset', 'Slide fcurve in time without afecting keys frame value', '', 13),
              ('TWEEN', 'Tween', 'Sets key value using neighbors as reference', '', 14),
              ('WAVE_NOISE', 'Wave-Noise', 'add wave or random values to keys', '', 15)]


menu_items_3d = [('BLEND_FRAME', 'Blend Frame', 'From current to set frames', '', 1),
                 ('BLEND_INFINITE', 'Blend Infinite', 'Adds or adjust keys to conform to the adjacent slope', '', 2),
                 ('BLEND_NEIGHBOR', 'Blend Neighbor', 'From current to neighbors', '', 3),

                 ('SCALE_LEFT', 'Scale Left', 'Scale anchor to left neighbor', '', 4),
                 ('SCALE_RIGHT', 'Scale Right', 'Scale anchor to right neighbor', '', 5),

                 ('PUSH_PULL', 'Push Pull', 'Overshoots key values', '', 6),

                 ('TIME_OFFSET', 'Time Offset', 'Slide fcurve in time without afecting keys frame value', '', 7),
                 ('TWEEN', 'Tween', 'Sets key value using neighbors as reference', '', 8)]


def update_clone_move(self, context):

    objects = context.selected_objects

    utils.curve.move_clone(objects)

    return


def update_overshoot(self, context):
    # change values when overshoot property is changed

    if self.overshoot:
        self.min_value = -2.0
        self.max_value = 2.0
    else:
        self.min_value = -1.0
        self.max_value = 1.0


def update_selector(self, context):
    # change values when selector property is changed

    support.get_globals(context)
    # self.overshoot = False
    self.show_factor = False


def toggle_tool_markers(self, context):
    if self.use_markers:
        if self.left_ref_frame > 0:
            utils.add_marker(name='', side='L', frame=self.left_ref_frame)

        if self.right_ref_frame > 0:
            utils.add_marker(name='', side='R', frame=self.right_ref_frame)
    else:
        for side in ['L', 'R']:
            utils.remove_marker(
                side=side)

    return


class AnimAideClone(PropertyGroup):

    move_factor: FloatProperty(default=0.0,
                               min=-2.0,
                               max=2.0,
                               update=update_clone_move)

    cycle_options = [('NONE', 'None', '', '', 1),
                     ('REPEAT', 'Repeat', '', '', 2),
                     ('REPEAT_OFFSET', 'Repeat with Offset', '', '', 3),
                     ('MIRROR', 'Mirrored', '', '', 4)]

    cycle: EnumProperty(
        items=cycle_options,
        name='Before',
        default='REPEAT_OFFSET'
    )

    # cycle_after: EnumProperty(
    #     items=cycle_options,
    #     name='Before',
    #     default='REPEAT_OFFSET'
    # )


class AnimAideFrameBookmark(PropertyGroup):
    frame: IntProperty()
    name: StringProperty()


class AnimAideTool(PropertyGroup):

    use_markers: BoolProperty(default=True,
                              description='use markers for the reference frames',
                              update=toggle_tool_markers)

    # unselected_fcurves: BoolProperty(default=False,
    #                                  description='Affect unselected fcurves')

    keys_under_cursor: BoolProperty(default=False,
                                    description='Affect unselected keys when cursor is over them')

    min_value: FloatProperty(default=-1)

    max_value: FloatProperty(default=1)

    show_factor: BoolProperty()

    flip: BoolProperty(default=True,
                       description='Changes how the tools modal work')

    expand: BoolProperty(default=False,
                         name='Expand',
                         description='Toggle between compact and expanded modes for the Tools')

    expand_3d: BoolProperty(default=False,
                            name='Expand',
                            description='Toggle between compact and expanded modes for the Tools')

    area: StringProperty()

    noise_phase: IntProperty(default=1,
                             min=1,
                             max=10,
                             description='Change noise shape')

    noise_scale: FloatProperty(default=1.0,
                               min=.01,
                               max=2,
                               description='Change noise scale')

    # slope: FloatProperty(default=1.0,
    #                      min=1.0,
    #                      max=10.0,
    #                      description='Determine how sharp the trasition is')

    overshoot: BoolProperty(update=update_overshoot,
                            name='Overshoot',
                            description='Allows for higher values')

    sticky_handles: BoolProperty(default=False,
                                 name='Sticky Handles',
                                 description='If On key points will be modified independetly\n' \
                                 'from its handles if the interpolation is "Free"\n' \
                                 'or "Aligned"')

    left_ref_frame: IntProperty()

    right_ref_frame: IntProperty()

    selector: EnumProperty(
        items=menu_items,
        name="Ease Tool Selector",
        default='EASE_TO_EASE',
        update=update_selector
    )

    selector_3d: EnumProperty(
        items=menu_items_3d,
        name="Ease Tool Selector",
        default='BLEND_NEIGHBOR',
        update=update_selector
    )

    factor: FloatProperty(default=0.0,
                          min=-1.0,
                          max=1.0
                          )

    factor_overshoot: FloatProperty(default=0.0,
                                    min=-2.0,
                                    max=2.0
                                    )

    frame_bookmarks: CollectionProperty(type=AnimAideFrameBookmark)

    bookmark_index: IntProperty()


classes = (
    AnimAideClone,
    AnimAideFrameBookmark,
    AnimAideTool,
)
