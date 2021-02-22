import bpy
import os

from . import support, props
from .. import utils
# from .utils import curve, key
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty, IntProperty
from bpy.types import Operator


class AAT_OT_move_key(Operator):
    """Displace keys based on a predetermined amount"""

    bl_idname = 'anim.aide_move_key'
    bl_label = "Move Key"
    bl_options = {'UNDO_GROUPED'}

    amount: FloatProperty(default=1.0)
    direction: EnumProperty(
        items=[('RIGHT', ' ', 'Move right', 'TRIA_RIGHT', 1),
               ('LEFT', ' ', 'Move left', 'TRIA_LEFT', 2)],
        name="Direction",
        default='RIGHT'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        if self.direction == 'LEFT' or self.direction == 'RIGHT':
            support.change_frame(context, self.amount, self.direction)

        return {'FINISHED'}


class AAT_OT_insert_frames(Operator):
    """Change the amount of frames between keys base on a predetermine amount"""

    bl_idname = 'anim.aide_insert_frames'
    bl_label = "Space between Keys"
    bl_options = {'UNDO_GROUPED'}

    amount: IntProperty(default=1)
    # amount: EnumProperty(
    #     items=support.amount,
    #     name="Amount",
    #     default='3'
    # )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.insert_frames(context, self.amount)

        return {'FINISHED'}


class AAT_OT_set_key_type(Operator):
    """Classify keys by type"""

    bl_idname = 'anim.aide_set_key_type'
    bl_label = "Set Key Type"
    bl_options = {'UNDO_GROUPED'}

    type: EnumProperty(
        items=props.key_type_t,
        name="Key Type",
        default='JITTER'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        if self.type == 'KEYFRAME':
            support.set_type(context, 'KEYFRAME')
        elif self.type == 'BREAKDOWN':
            support.set_type(context, 'BREAKDOWN')
        elif self.type == 'JITTER':
            support.set_type(context, 'JITTER')
        elif self.type == 'EXTREME':
            support.set_type(context, 'EXTREME')

        return {'FINISHED'}


class AAT_OT_delete_key_type(Operator):
    """Remove keys based on the type classification"""

    bl_idname = 'anim.aide_delete_key_type'
    bl_label = "Delete Key Type"
    bl_options = {'UNDO_GROUPED'}

    type: EnumProperty(
        items=props.key_type_t,
        name="Key Type",
        default='JITTER'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.delete_by_type(context, self.type)

        return {'FINISHED'}


class AAT_OT_select_key_type(Operator):
    """Sets the selection of keys based on the type classification"""

    bl_idname = 'anim.aide_select_key_type'
    bl_label = "Key selection Type"
    bl_options = {'UNDO_GROUPED'}

    selection: BoolProperty()

    type: EnumProperty(
        items=props.key_type_t,
        name="Key Type",
        default='JITTER'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.select_by_type(context, kind=self.type, selection=self.selection)

        return {'FINISHED'}


class AAT_OT_set_handles_type(Operator):
    """Sets the type of handle a key has"""

    bl_idname = 'anim.aide_set_handles_type'
    bl_label = "Set Handles Type"
    bl_options = {'UNDO_GROUPED'}

    check_ui: BoolProperty(
        default=True
    )

    handle_type: EnumProperty(
        items=props.handle_type_t,
        name="Handle Type",
        default='AUTO_CLAMPED'
    )

    act_on: EnumProperty(
        items=[('SELECTION', 'Selection', 'Preset', '', 1),
               ('FIRST', 'First key', 'Preset', '', 2),
               ('LAST', 'Last key', 'Preset', '', 3),
               ('BOTH', 'First and last keys', 'Preset', '', 4),
               ('ALL', 'Every key', 'Preset', '', 5)],
        name="Act on",
        default='SELECTION'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.set_handles_type(context, act_on=self.act_on, handle_type=self.handle_type, check_ui=self.check_ui)

        return {'FINISHED'}


class AAT_OT_select_key_parts(Operator):
    """Sets the selection status of of the corresponding key part"""

    bl_idname = 'anim.aide_select_key_parts'
    bl_label = "Select Key Part"
    bl_options = {'UNDO_GROUPED'}

    left: BoolProperty()
    right: BoolProperty()
    point: BoolProperty()
    handle_type: EnumProperty(
        items=props.handle_type_t,
        name="Handle Type",
        default='AUTO_CLAMPED'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.select_key_parts(
            context,
            left=self.left,
            right=self.right,
            point=self.point
        )

        return {'FINISHED'}


class AAT_OT_set_handles_interp(Operator):
    """Sets the interpolation type of keys"""

    bl_idname = 'anim.aide_set_handles_interp'
    bl_label = "Set Handles Interpolation"
    bl_options = {'UNDO_GROUPED'}

    check_ui: BoolProperty(
        default=True
    )

    interp: EnumProperty(
        items=props.interp_t,
        name="Interpolation",
        default='BEZIER'
    )

    strength: EnumProperty(
        items=[('NONE', '', '', '', 1),
               ('SINE', 'Sinusoidal', 'Options of ease mode to apply to keys', 'IPO_SINE', 2),
               ('QUAD', 'Quadratic', 'Options of ease mode to apply to keys', 'IPO_QUAD', 3),
               ('CUBIC', 'Cubic', 'Options of ease mode to apply to keys', 'IPO_CUBIC', 4),
               ('QUART', 'Quartic', 'Options of ease mode to apply to keys', 'IPO_QUART', 5),
               ('QUINT', 'Quintic', 'Options of ease mode to apply to keys', 'IPO_QUINT', 6),
               ('EXPO', 'Exponential', 'Options of ease mode to apply to keys', 'IPO_EXPO', 7),
               ('CIRC', 'Circular', 'Options of ease mode to apply to keys', 'IPO_CIRC', 8),
               ('BACK', 'Back', 'Options of ease mode to apply to keys', 'IPO_BACK', 9),
               ('BOUNCE', 'Bounce', 'Options of ease mode to apply to keys', 'IPO_BOUNCE', 10),
               ('ELASTIC', 'Elastic', 'Options of ease mode to apply to keys', 'IPO_ELASTIC', 11)],
        name="Ease Strength",
        default='NONE'
    )

    easing: EnumProperty(
        items=[('NONE', '', '', '', 1),
               ('AUTO', 'Auto', 'Auto', 'IPO_EASE_IN_OUT', 2),
               ('EASE_IN', 'Ease in', 'Ease in', 'IPO_EASE_IN', 3),
               ('EASE_OUT', 'Ease-out', 'Ease-out', 'IPO_EASE_OUT', 4),
               ('EASE_IN_OUT', 'Ease in-out', 'Ease in-out', 'IPO_EASE_IN_OUT', 5)],
        name="Ease Mode",
        default='NONE'
    )

    act_on: EnumProperty(
        items=[('SELECTION', 'Selection', 'Preset', '', 1),
               ('FIRST', 'First key', 'Preset', '', 2),
               ('LAST', 'Last key', 'Preset', '', 3),
               ('BOTH', 'First and last keys', 'Preset', '', 4),
               ('ALL', 'Every key', 'Preset', '', 5)],
        name="Act on",
        default='SELECTION'
    )

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):

        support.set_handles_interp(context, act_on=self.act_on, interp=self.interp, easing=self.easing,
                                   strength=self.strength, check_ui=self.check_ui)

        return {'FINISHED'}


# ------- Not used --------


class ANIMAIDE_OT_key_manager_settings(Operator):
    """Shows global options for Curve Tools"""

    bl_idname = "anim.aide_key_manager_settings"
    bl_label = "Key Manager Settings"

    @classmethod
    def poll(cls, context):
        return utils.general.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def draw(self, context):
        animaide = context.scene.animaide
        tool = animaide.tool

        layout = self.layout

        layout.label(text='Settings')
        layout.separator()
        layout.prop(tool, 'overshoot', text='overshoot', toggle=False)
        layout.prop(tool, 'keys_under_cursor', text='Only keys under cursor', toggle=False)
        layout.prop(tool, 'flip', text='Activates on release', toggle=False)

        col = layout.column(align=False)
        if tool.selector == 'BLEND_FRAME':
            col.active = True
        else:
            col.active = False
        col.prop(tool, 'use_markers', text='Use markers', toggle=False)

        col = layout.column(align=False)
        if tool.selector == 'EASE_TO_EASE' or tool.selector == 'EASE':
            col.active = True
        else:
            col.active = False
        col.label(text='Ease slope')
        col.prop(tool, 'slope', text='', slider=False)

        # if tool.selector == 'NOISE':
        #     layout.label(text='Noise settings')
        #     layout.prop(tool, 'noise_phase', text='Phase', slider=True)
        #     layout.prop(tool, 'noise_scale', text='Scale', slider=True)


class ANIMAIDE_OT_modifier(Operator):
    """Add noise to a curve using a modifier"""

    bl_idname = 'anim.aide_fcurve_modifier'
    bl_label = "Modifier"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        objects = context.selected_objects
        for obj in objects:
            action = obj.animation_data.action

            for curve in action.fcurves:
                if curve.select is not True:
                    continue
                noise = curve.modifiers.new('NOISE')

                noise.strength = 5
                noise.scale_tools = 3
                curve.convert_to_samples(0, 100)
                curve.convert_to_keyframes(0, 100)
                curve.modifiers.remove(noise)
        return {'FINISHED'}


class ANIMAIDE_OT_path(Operator):
    bl_idname = 'anim.aide_path'
    bl_label = "Path"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = context.object
        fcurves = obj.animation_data.action.fcurves
        utils.curve.create_path(context, fcurves)


class AAT_OT_clone(Operator):
    '''
    Creates a clone of an fcurve'''

    bl_idname = 'animaide.fcurve_clone'
    bl_label = "Clone Fcurve"
    bl_options = {'REGISTER'}
    # cycle_before: StringProperty()
    # cycle_after: StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        animaide = context.scene.animaide
        cycle_before = animaide.clone.cycle_before
        cycle_after = animaide.clone.cycle_after

        objects = context.selected_objects

        utils.curve.add_clone(objects, cycle_before, cycle_after)

        return {'FINISHED'}


class AAT_OT_clone_remove(Operator):
    '''
    Removes a clone of an fcurve'''

    bl_idname = 'animaide.remove_clone'
    bl_label = "Remove Clone"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        objects = context.selected_objects

        utils.curve.remove_helpers(objects)

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'FINISHED'}


classes = (
    AAT_OT_move_key,
    AAT_OT_insert_frames,
    AAT_OT_set_key_type,
    AAT_OT_delete_key_type,
    AAT_OT_select_key_type,
    AAT_OT_set_handles_type,
    AAT_OT_select_key_parts,
    AAT_OT_set_handles_interp,
)
