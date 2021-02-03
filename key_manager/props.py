import bpy
from . import support
from .. import utils
from bpy.props import BoolProperty, EnumProperty, StringProperty, \
    IntProperty, FloatProperty, CollectionProperty
from bpy.types import PropertyGroup


def update_free(self, context):
    support.set_handles_type(context, act_on=self.free_act_on, handle_type='FREE')
    self.free_act_on = 'SELECTION'


def update_aligned(self, context):
    support.set_handles_type(context, act_on=self.aligned_act_on,handle_type='ALIGNED')
    self.free_act_on = 'SELECTION'


def update_vector(self, context):
    support.set_handles_type(context, act_on=self.vector_act_on, handle_type='VECTOR')
    self.free_act_on = 'SELECTION'


def update_auto(self, context):
    support.set_handles_type(context, act_on=self.auto_act_on, handle_type='AUTO')
    self.free_act_on = 'SELECTION'


def update_auto_clamped(self, context):
    support.set_handles_type(context, act_on=self.auto_clamped_act_on, handle_type='AUTO_CLAMPED')
    self.free_act_on = 'SELECTION'


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


def amount_update(self, context):
    self.frame_change = int(self.amount)


class KeyTweak(PropertyGroup):

    frame_change: IntProperty(default=1, min=1)
    value_change: FloatProperty(default=0.1, min=0.0)

    left: BoolProperty(default=False)
    right: BoolProperty(default=False)
    point: BoolProperty(default=True)

    act_on: EnumProperty(
        items=support.act_on_t,
        name="Act-on",
        default='SELECTION',
    )

    free_act_on: EnumProperty(
        items=support.act_on_t,
        name="Free Act-on",
        default='SELECTION',
        update=update_free
    )

    aligned_act_on: EnumProperty(
        items=support.act_on_t,
        name="Aligned Act-on",
        default='SELECTION',
        update=update_aligned
    )

    vector_act_on: EnumProperty(
        items=support.act_on_t,
        name="Vector Act-on",
        default='SELECTION',
        update=update_vector
    )

    auto_act_on: EnumProperty(
        items=support.act_on_t,
        name="Auto Act-on",
        default='SELECTION',
        update=update_auto
    )

    auto_clamped_act_on: EnumProperty(
        items=support.act_on_t,
        name="Auto Clamped Act-on",
        default='SELECTION',
        update=update_auto_clamped
    )

    handle_type: EnumProperty(
        items=support.handle_type_t,
        name="Handle Type",
        default='AUTO_CLAMPED'
    )

    interp: EnumProperty(
        items=support.interp_t,
        name="Interpolation",
        default='BEZIER',
        update=interp_update
    )

    strength: EnumProperty(
        items=support.strength_t,
        name="Ease Strength",
        default='SINE',
        update=strength_update
    )

    easing: EnumProperty(
        items=support.easing_t,
        name="Ease Mode",
        default='AUTO',
        update=easing_update
    )

    amount: EnumProperty(
        items=support.amount_t,
        name="Amount",
        default='2',
        update=amount_update
    )


classes = (
    KeyTweak,
)
