import bpy

from . import key_utils, cur_utils, utils

from bpy.props import StringProperty, BoolProperty, EnumProperty, \
    IntProperty, FloatProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, AddonPreferences


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
         'NOISE': 'RNDCURVE',
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
         'NOISE': 'Noise',
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
    animaide = bpy.context.scene.animaide
    cycle_before = animaide.clone_data.cycle_before
    cycle_after = animaide.clone_data.cycle_after

    cur_utils.add_clone(objects, cycle_before, cycle_after)

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
    key_utils.get_sliders_globals()
    self.overshoot = False
    self.modal_switch = False


def toggle_markers(self, context):
    anim = context.scene.animation_data
    fcurves = anim.action.fcurves
    markers = bpy.context.scene.timeline_markers

    names = ['LB', 'LM', 'RM', 'RB']

    if self.use_markers:
        for n in range(4):
            key = fcurves[0].keyframe_points[n]
            utils.add_marker(name_a=names[n][1:],
                             name_b='',
                             side=names[n][:1],
                             frame=key.co.x)
    else:
        for marker in markers:
            if marker.name in names:
                markers.remove(markers[marker.name])

    return


class AnimAideAnimTransform(PropertyGroup):

    active: BoolProperty()

    use_mask: BoolProperty()

    use_markers: BoolProperty(default=True,
                              description='Let you choose to use markers for the mask',
                              update=toggle_markers)

    mask_margin_l: IntProperty(default=0,
                          description="Margin for the mask")
    mask_blend_l: IntProperty(default=0, max=0,
                         description="Fade value for the left margin")
    mask_margin_r: IntProperty(default=0,
                          description="Margin for the mask")
    mask_blend_r: IntProperty(default=0, min=0,
                         description="Fade value for the right margin")

    interp: EnumProperty(
        items=[('LINEAR', ' ', 'Linear transition', 'IPO_LINEAR', 1),
               ('SINE', ' ', 'Sine transition', 'IPO_SINE', 2),
               ('CUBIC', ' ', 'Cubic transition', 'IPO_CUBIC', 3),
               ('QUART', ' ', 'Quart transition', 'IPO_QUART', 4),
               ('QUINT', ' ', 'Quint transition', 'IPO_QUINT', 5)],
        name="Interpolation",
        default='SINE'
    )

    easing: EnumProperty(
        items=[('EASE_IN', 'ease in', 'ease in', 'IPO_EASE_IN', 1),
               ('EASE_IN_OUT', 'ease in-out', 'ease in-out', 'IPO_EASE_IN_OUT', 2),
               ('EASE_OUT', 'ease out', 'ease out', 'IPO_EASE_OUT', 3)],
        name="Easing",
        default='EASE_IN_OUT'
    )


class AnimAideClone(PropertyGroup):

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
        default='NONE'
    )

    cycle_after: EnumProperty(
        items=cycle_options,
        name='Before',
        default='NONE'
    )


class AnimSlider(PropertyGroup):

    use_markers: BoolProperty(default=True,
                              description='Let you choose to use markers for the reference frames')

    min_value: FloatProperty(default=-1)

    max_value: FloatProperty(default=1)

    index: IntProperty(default=-1)

    modal_switch: BoolProperty()

    slope: FloatProperty(default=2.0,
                         min=1.0,
                         max=10.0,
                         description='Determine how sharp the trasition is')

    overshoot: BoolProperty(update=update_overshoot,
                            description='Allows for higher values')

    left_ref_frame: IntProperty()

    right_ref_frame: IntProperty()

    selector: EnumProperty(
        items=[('EASE', names['EASE'], 'S shape transition', icons['EASE'], 1),
               ('EASE_IN_OUT', names['EASE_IN_OUT'], 'C shape transition', icons['EASE_IN_OUT'], 2),
               ('BLEND_EASE', names['BLEND_EASE'], 'From current to C shape', icons['BLEND_EASE'], 3),
               ('BLEND_NEIGHBOR', names['BLEND_NEIGHBOR'], 'From current to neighbors', icons['BLEND_NEIGHBOR'], 4),
               ('BLEND_FRAME', names['BLEND_FRAME'], 'From current to set frames', icons['BLEND_FRAME'], 5),
               ('BLEND_OFFSET', names['BLEND_OFFSET'], 'Offset key values to neighbors', icons['BLEND_OFFSET'], 6),
               ('PUSH_PULL', names['PUSH_PULL'], 'Overshoots key values', icons['PUSH_PULL'], 7),
               ('SCALE_AVERAGE', names['SCALE_AVERAGE'], 'Scale to average value', icons['SCALE_AVERAGE'], 8),
               ('SCALE_LEFT', names['SCALE_LEFT'], 'Scale anchor to left neighbor', icons['SCALE_LEFT'], 9),
               ('SCALE_RIGHT', names['SCALE_RIGHT'], 'Scale anchor to right neighbor', icons['SCALE_RIGHT'], 10),
               ('SMOOTH', names['SMOOTH'], 'Smooths out fcurve keys', icons['SMOOTH'], 11),
               ('NOISE', names['NOISE'], 'add random values to keys', icons['NOISE'], 12),
               ('TIME_OFFSET', names['TIME_OFFSET'], 'Slide fcurve in time without afecting keys frame value', icons['TIME_OFFSET'], 13),
               ('TWEEN', names['TWEEN'], 'Sets key value using neighbors as reference', icons['TWEEN'], 14)],
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


class AnimAideScene(PropertyGroup):
    anim_transform: PointerProperty(type=AnimAideAnimTransform)
    clone: PointerProperty(type=AnimAideClone)
    slider: PointerProperty(type=AnimSlider)
    slider_slots: CollectionProperty(type=AnimSlider)


# class AnimAideObject(PropertyGroup):
#     magnet: PointerProperty(type=AnimAideMagnet)


class myPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    view_3d: BoolProperty(
        name="3D View",
        default=True,
    )

    sliders: BoolProperty(
        name="Sliders",
        default=True,
    )

    magnet: BoolProperty(
        name="Magnet",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        # layout.label(text="Choose the area where the sliders will be:")
        layout.prop(self, "sliders", text="Use Sliders")
        layout.prop(self, "anim_transform", text="Use AnimTransform")
        layout.prop(self, "view_3d", text="Side panel in the '3D View' instead of the 'Graph Editor'")


def space_type_pref():

    preferences = bpy.context.preferences
    pref = preferences.addons[__package__].preferences

    if pref.view_3d:
        space_type = 'VIEW_3D'
    else:
        space_type = 'GRAPH_EDITOR'

    return space_type


def set_props():
    bpy.types.Scene.animaide = PointerProperty(type=AnimAideScene)
    # bpy.types.Object.animaide = PointerProperty(type=AnimAideObject)

def del_props():
    del bpy.types.Scene.animaide

