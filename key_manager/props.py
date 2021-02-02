import bpy
from . import support
from .. import utils
from bpy.props import BoolProperty, EnumProperty, StringProperty, \
    IntProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup


def update_free(self, context):
    support.set_handles_type(context, act_on=self.free_act_on, handle_type='FREE')


def update_aligned(self, context):
    support.set_handles_type(context, act_on=self.aligned_act_on,handle_type='ALIGNED')


def update_vector(self, context):
    support.set_handles_type(context, act_on=self.vector_act_on, handle_type='VECTOR')


def update_auto(self, context):
    support.set_handles_type(context, act_on=self.auto_act_on, handle_type='AUTO')


def update_auto_clamped(self, context):
    support.set_handles_type(context, act_on=self.auto_clamped_act_on, handle_type='AUTO_CLAMPED')


def interp_update(self, context):
    if self.interp == 'EASE':
        strength_update(self, context)
    else:
        support.set_handles_interp(context, interp=self.interp)


def easing_update(self, context):
    # if self.interp == 'EASE':
    support.set_handles_interp(context,  easing=self.easing)


def strength_update(self, context):
    # if self.interp == 'EASE':
    support.set_handles_interp(context, strength=self.strength)


class KeyTweak(PropertyGroup):

    frame_change: IntProperty(default=1, min=1)
    value_change: FloatProperty(default=0.1, min=0.0)

    left: BoolProperty(default=False)
    right: BoolProperty(default=False)
    point: BoolProperty(default=True)

    act_on: EnumProperty(
        items=support.act_on,
        name="Act-on",
        default='ALL',
    )

    free_act_on: EnumProperty(
        items=support.act_on,
        name="Free Act-on",
        default='ALL',
        update=update_free
    )

    aligned_act_on: EnumProperty(
        items=support.act_on,
        name="Aligned Act-on",
        default='ALL',
        update=update_aligned
    )

    vector_act_on: EnumProperty(
        items=support.act_on,
        name="Vector Act-on",
        default='ALL',
        update=update_vector
    )

    auto_act_on: EnumProperty(
        items=support.act_on,
        name="Auto Act-on",
        default='ALL',
        update=update_auto
    )

    auto_clamped_act_on: EnumProperty(
        items=support.act_on,
        name="Auto Clamped Act-on",
        default='ALL',
        update=update_auto_clamped
    )

    handle_type: EnumProperty(
        items=support.handle_type,
        name="Handle Type",
        default='AUTO_CLAMPED'
    )

    interp: EnumProperty(
        items=support.interp,
        name="Interpolation",
        default='BEZIER',
        update=interp_update
    )

    strength: EnumProperty(
        items=support.strength,
        name="Ease Strength",
        default='SINE',
        update=strength_update
    )

    easing: EnumProperty(
        items=support.easing,
        name="Ease Mode",
        default='AUTO',
        update=easing_update
    )


classes = (
    KeyTweak,
)
