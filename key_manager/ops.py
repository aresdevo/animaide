import bpy
import os

from . import support
from .. import utils
# from .utils import curve, key
from bpy.props import StringProperty, FloatProperty, EnumProperty
from bpy.types import Operator


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


class AAT_OT_move_key(Operator):
    '''
    Move selected keys'''

    bl_idname = 'animaide.move_key'
    bl_label = "Move Key"
    bl_options = {'REGISTER'}
    amount: FloatProperty(default=1.0)
    direction: EnumProperty(
        items=[('RIGHT', ' ', 'Move right', 'TRIA_RIGHT', 1),
               ('LEFT', ' ', 'Move left', 'TRIA_LEFT', 2),
               ('UP', ' ', 'Move up', 'TRIA_UP', 3),
               ('DOWN', ' ', 'Move down', 'TRIA_DOWN', 4)],
        name="Direction",
        default='RIGHT'
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        objects = context.selected_objects

        utils.key.move_right_left(objects, self.amount, self.direction)

        return {'FINISHED'}


class ANIMAIDE_OT_key_manager_settings(Operator):
    """Shows global options for Curve Tools"""

    bl_idname = "anim.aide_key_manager_settings"
    bl_label = "Key Manager Settings"

    @classmethod
    def poll(cls, context):
        return support.poll(context)

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


classes = (
    ANIMAIDE_OT_key_manager_settings,
)
