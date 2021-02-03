import bpy
from . import support
from .. import utils
from bpy.props import BoolProperty, EnumProperty, StringProperty, \
    IntProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup


menu_items = [('EASE_TO_EASE', 'Ease To Ease', 'S shape transition', '', 1),
              ('EASE', 'Ease', 'C shape transition', '', 2),
              ('BLEND_EASE', 'Blend Ease', 'From current to C shape', '', 3),
              ('BLEND_NEIGHBOR', 'Blend Neighbor', 'From current to neighbors', '', 4),
              ('BLEND_FRAME', 'Blend Frame', 'From current to set frames', '', 5),
              ('BLEND_OFFSET', 'Blend Offset', 'Offset key values to neighbors', '', 6),
              ('TWEEN', 'Tween', 'Sets key value using neighbors as reference', '', 7),
              ('PUSH_PULL', 'Push Pull', 'Overshoots key values', '', 8),
              ('SCALE_LEFT', 'Scale Left', 'Scale anchor to left neighbor', '', 9),
              ('SCALE_AVERAGE', 'Scale Average', 'Scale to average value', '', 10),
              ('SCALE_RIGHT', 'Scale Right', 'Scale anchor to right neighbor', '', 11),
              ('SMOOTH', 'Smooth', 'Smooths out fcurve keys', '', 12),
              ('WAVE_NOISE', 'Wave-Noise', 'add wave or random values to keys', '', 13),
              ('TIME_OFFSET', 'Time Offset', 'Slide fcurve in time without afecting keys frame value', '', 14)]


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

    expand: BoolProperty(default=True,
                         description='Toggle between compact and expanded modes for the Tools')

    expand_3d: BoolProperty(default=True)

    area: StringProperty()

    noise_phase: IntProperty(default=1,
                             min=1,
                             max=10,
                             description='Change noise shape')

    noise_scale: FloatProperty(default=1.0,
                               min=.01,
                               max=2,
                               description='Change noise scale')

    slope: FloatProperty(default=1.0,
                         min=1.0,
                         max=10.0,
                         description='Determine how sharp the trasition is')

    overshoot: BoolProperty(update=update_overshoot,
                            description='Allows for higher values')

    left_ref_frame: IntProperty()

    right_ref_frame: IntProperty()

    selector: EnumProperty(
        items=menu_items,
        name="Ease Tool Selector",
        default='EASE_TO_EASE',
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
