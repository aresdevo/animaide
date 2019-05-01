import bpy

from . import key_utils, cur_utils

from bpy.props import StringProperty, BoolProperty, EnumProperty, \
    IntProperty, FloatProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup


icons = {'EASE': 'IPO_EASE_IN_OUT',
         'EASE_IN_OUT': 'ANIM_DATA',
         'BLEND_EASE': 'TRACKING',
         'BLEND_NEIGHBOR': 'TRACKING_FORWARDS',
         'BLEND_FRAME': 'TRACKING_FORWARDS_SINGLE',
         'BLEND_OFFSET': 'CURVE_PATH',
         'PUSH_PULL': 'UV_SYNC_SELECT',
         'SCALE_AVERAGE': 'FULLSCREEN_EXIT',
         'SCALE_LEFT': 'IMPORT',
         'SCALE_RIGHT': 'EXPORT',
         'SMOOTH': 'SMOOTHCURVE',
         'TIME_OFFSET': 'CENTER_ONLY',
         'TWEEN': 'DRIVER_DISTANCE'}


names = {'EASE': 'Ease',
         'EASE_IN_OUT': 'Ease In Out',
         'BLEND_EASE': 'Blend Ease',
         'BLEND_NEIGHBOR': 'Blend Neighbor',
         'BLEND_FRAME': 'Blend Frame',
         'BLEND_OFFSET': 'Blend Offset',
         'PUSH_PULL': 'Push Pull',
         'SCALE_AVERAGE': 'Scale Average',
         'SCALE_LEFT': 'Scale Left',
         'SCALE_RIGHT': 'Scale Right',
         'SMOOTH': 'Smooth',
         'TIME_OFFSET': 'Time Offset',
         'TWEEN': 'Tween'}


def update_clone_move(self, context):
    """
     for internal use
    """
    objects = context.selected_objects

    cur_utils.move_clone(objects)

    print("In update func...")
    return


def update_clone(self, context):
    """
     for internal use
    """
    objects = context.selected_objects
    animsliders = bpy.context.scene.animsliders
    cycle_before = animsliders.clone_data.cycle_before
    cycle_after = animsliders.clone_data.cycle_after

    cur_utils.create_clone(objects, cycle_before, cycle_after)

    print("In update func...")
    return


def update_overshoot(self, context):
    if self.overshoot:
        self.min_value = -2.0
        self.max_value = 2.0
    else:
        self.min_value = -1.0
        self.max_value = 1.0


def update_selector(self, context):
    """
     for internal use
    """
    key_utils.get_selected_global()
    self.overshoot = False
    self.modal_switch = False


class AnimAideKeys(PropertyGroup):
    # index: IntProperty(default=-1)
    x: IntProperty()
    y: FloatProperty()


class AnimAideFCurves(PropertyGroup):
    data_path: StringProperty()
    parent_obj: StringProperty()
    index: IntProperty(default=-1)
    # original_keys_info: PointerProperty(type=AnimAideKeys)


class AnimAideClone(PropertyGroup):
    #
    fcurve: PointerProperty(type=AnimAideFCurves)
    original_fcurve: PointerProperty(type=AnimAideFCurves)


class AnimAideCloneData(PropertyGroup):
    #
    clones: CollectionProperty(type=AnimAideClone)
    move_factor: FloatProperty(default=0.0,
                               min=-2.0,
                               max=2.0,
                               update=update_clone_move)

    cycle_options = [('NONE', 'None', '', '', 1),
                    ('REPEAT', 'Repeat', '', '', 2),
                    ('REPEAT_OFFSET', 'Repeat with Offset', '', '', 3),
                    ('MIRROR', 'Mirrored', '', '', 4)]

    cycle_before: EnumProperty(
        items=cycle_options,
        name='Before',
        default='NONE',
        update=update_clone
    )

    cycle_after: EnumProperty(
        items=cycle_options,
        name='Before',
        default='NONE',
        update=update_clone
    )


class AnimSlider(PropertyGroup):

    min_value: FloatProperty(default=-1)

    max_value: FloatProperty(default=1)

    index: IntProperty(default=-1)

    modal_switch: BoolProperty()

    slope: FloatProperty(default=2.0,
                       min=1.0,
                       max=10.0)

    overshoot: BoolProperty(update=update_overshoot)

    left_ref_frame: IntProperty()

    right_ref_frame: IntProperty()

    selector: EnumProperty(
        items=[('EASE', names['EASE'], '', icons['EASE'], 1),
               ('EASE_IN_OUT', names['EASE_IN_OUT'], '', icons['EASE_IN_OUT'], 2),
               ('BLEND_EASE', names['BLEND_EASE'], '', icons['BLEND_EASE'], 3),
               ('BLEND_NEIGHBOR', names['BLEND_NEIGHBOR'], '', icons['BLEND_NEIGHBOR'], 4),
               ('BLEND_FRAME', names['BLEND_FRAME'], '', icons['BLEND_FRAME'], 5),
               ('BLEND_OFFSET', names['BLEND_OFFSET'], '', icons['BLEND_OFFSET'], 6),
               ('PUSH_PULL', names['PUSH_PULL'], '', icons['PUSH_PULL'], 7),
               ('SCALE_AVERAGE', names['SCALE_AVERAGE'], '', icons['SCALE_AVERAGE'], 8),
               ('SCALE_LEFT', names['SCALE_LEFT'], '', icons['SCALE_LEFT'], 9),
               ('SCALE_RIGHT', names['SCALE_RIGHT'], '', icons['SCALE_RIGHT'], 10),
               ('SMOOTH', names['SMOOTH'], '', icons['SMOOTH'], 11),
               ('TIME_OFFSET', names['TIME_OFFSET'], '', icons['TIME_OFFSET'], 12),
               ('TWEEN', names['TWEEN'], '', icons['TWEEN'], 13)],
        name="Ease Slider Selector",
        default='EASE',
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

    # factor_stepped: EnumProperty(
    #     items=[('-1.000', ' ', '', 'RADIOBUT_OFF', 1),
    #            ('-0.750', ' ', '', '', 2),
    #            ('-0.500', ' ', '', '', 3),
    #            ('-0.250', ' ', '', '', 4),
    #            ('0.000', ' ', '', 'NODE_MATERIAL', 5),
    #            ('0.250', ' ', '', '', 6),
    #            ('0.500', ' ', '', '', 7),
    #            ('0.750', ' ', '', '', 8),
    #            ('1.000', '', '', 'RADIOBUT_OFF', 9)],
    #     name="Factor Stepped",
    #     default='0.000',
    #     update=prop_utils.update_stepped
    # )
    #
    # factor_stepped_overshoot: EnumProperty(
    #     items=[('-1.300', ' ', '', '', 1),
    #            ('-1.150', ' ', '', '', 2),
    #            ('-1.000', ' ', '', 'RADIOBUT_OFF', 3),
    #            ('-0.750', ' ', '', '', 4),
    #            ('-0.500', ' ', '', '', 5),
    #            ('-0.250', ' ', '', '', 6),
    #            ('0.000', ' ', '', 'NODE_MATERIAL', 7),
    #            ('0.250', ' ', '', '', 8),
    #            ('0.500', ' ', '', '', 9),
    #            ('0.750', ' ', '', '', 10),
    #            ('1.000', ' ', '', 'RADIOBUT_OFF', 11),
    #            ('1.150', ' ', '', '', 12),
    #            ('1.300', '', '', '', 13)],
    #     name="Factor Stepped Overshoot",
    #     default='0.000',
    #     update=prop_utils.update_stepped
    # )


class AnimSliders(PropertyGroup):
    clone_data: PointerProperty(type=AnimAideCloneData)
    item: PointerProperty(type=AnimSlider)
    slots: CollectionProperty(type=AnimSlider)


def set_props():
    bpy.types.Scene.animsliders = PointerProperty(type=AnimSliders)

def del_props():
    del bpy.types.Scene.animsliders

