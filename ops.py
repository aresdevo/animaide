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


import bpy, os

from . import utils, key_utils, cur_utils, slider_tools, magnet
from bpy.props import StringProperty, EnumProperty, BoolProperty, \
    IntProperty, FloatProperty
from bpy.types import Operator


################  SLIDERS  ###############


class AAT_OT_ease_to_ease(Operator):
    '''
Transition selected keys - or current key - from the neighboring
ones with a "S" shape manner (ease-in and ease-out simultaneously).
It doesn't take into consideration the current key values.

shortcut:   1
pie_menu-1:  (alt-1)'''

    bl_idname = "animaide.ease_to_ease"
    bl_label = "Ease To Ease"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'EASE_TO_EASE'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_ease(Operator):
    '''
Transition selected keys - or current key - from the neighboring
ones with a "C" shape manner (ease-in or ease-out). It doesn't
take into consideration the current key values.

shortcut:   2
pie_menu-1:  (alt-1)'''

    bl_idname = "animaide.ease"
    bl_label = "Ease"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'EASE'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_blend_neighbor(Operator):
    '''
Blend selected keys - or current key - to the value of the neighboring
left and right keys.

shortcut:   3
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.blend_neighbor"
    bl_label = "Blend Neighbor"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'BLEND_NEIGHBOR'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_blend_frame(Operator):
    '''
Blend selected keys - or current key - to the value of the chosen
left and right frames.

shortcut:   shift-3
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.blend_frame"
    bl_label = "Blend Frame"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'BLEND_FRAME'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_blend_ease(Operator):
    '''
Blend selected keys - or current key - to the ease-in or ease-out
curve using the neighboring keys.

shortcut:   shift-2
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.blend_ease"
    bl_label = "Blend Ease"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'BLEND_EASE'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_blend_offset(Operator):
    '''
Blend selected keys - or current key - to the
value of the chosen left and right frames.

shortcut:   shift-7
pie_menu-2: (alt-2)'''

    bl_idname = "animaide.blend_offset"
    bl_label = "Blend Offset"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'BLEND_OFFSET'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_tween(Operator):
    '''
Set lineal relative value of the selected keys - or current key -
in relationship to the neighboring ones. It doesn't take into
consideration the current key values.

shortcut:   shift-1
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.tween"
    bl_label = "Tween"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'TWEEN'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_push_pull(Operator):
    '''
Exagerates or decreases the value of the selected keys
- or current key -

shortcut:   4
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.push_pull"
    bl_label = "Push Pull"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'PUSH_PULL'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_smooth(Operator):
    '''
Averages values of selected keys creating
a smoother fcurve

shortcut:   6
pie_menu-2: (alt-2)'''
    bl_idname = "animaide.smooth"
    bl_label = "Smooth"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'SMOOTH'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_time_offset(Operator):
    '''
Shift the value of selected keys - or current key -
to the ones of the left or right in the same fcurve

shortcut:   7
pie_menu-2: (alt-2)'''
    bl_idname = "animaide.time_offset"
    bl_label = "Time Offset"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'TIME_OFFSET'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_noise(Operator):
    '''
Set random values to the selected keys - or current key -

shortcut:   shift-6
pie_menu-2: (alt-2)'''
    bl_idname = "animaide.noise"
    bl_label = "Noise"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'NOISE'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_scale_left(Operator):
    '''
Increase or decrease the value of selected keys - or current key -
in relationship to the left neighboring one.

shortcut:   5
pie_menu-2: (alt-2)'''
    bl_idname = "animaide.scale_left"
    bl_label = "Scale Left"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'SCALE_LEFT'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_scale_right(Operator):
    '''
Increase or decrease the value of selected keys - or current key -
in relationship to the right neighboring one.

shortcut:   shift-5
pie_menu-2: (alt-2)'''
    bl_idname = "animaide.scale_right"
    bl_label = "Scale Right"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'SCALE_RIGHT'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


class AAT_OT_scale_average(Operator):
    '''
Increase or decrease the value of selected keys - or current key -
in relationship to the average point of those affected.

shortcut:   shift-4
pie_menu-1: (alt-1)'''

    bl_idname = "animaide.scale_average"
    bl_label = "Scale Average"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'SCALE_AVERAGE'

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_tools.looper(self, context)

    def modal(self, context, event):

        return slider_tools.modal(self, context, event)

    def invoke(self, context, event):

        return slider_tools.invoke(self, context, event)


# ------- sliders extra operators ------


class AAT_OT_sliders_settings(Operator):
    '''
Options related to the current tool on the slider'''

    bl_idname = "animaide.sliders_settings"
    bl_label = "Sliders Settings"

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=150)

    def draw(self, context):
        animaide = context.scene.animaide
        if self.slot_index < 0:
            slider = animaide.slider
        else:
            slider = animaide.slider_slots[self.slot_index]

        layout = self.layout
        col = layout.column(align=False)
        col.label(text='Settings')
        col.prop(slider, 'slope', text='Slope', slider=False)
        col.prop(slider, 'overshoot', text='Overshoot', toggle=False)
        if slider.selector == 'BLEND_FRAME':
            col.prop(slider, 'use_markers', text='Use Markers', toggle=False)
        # col.prop(animaide.slider, 'affect_non_selected_frame', text='Not selected frames', toggle=False)


class AAT_OT_global_settings(Operator):
    '''
Options for the entire sliders tool'''

    bl_idname = "animaide.global_settings"
    bl_label = "Global Settings"

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def draw(self, context):
        animaide = context.scene.animaide

        layout = self.layout
        col = layout.column(align=False)
        col.label(text='Settings')
        col.prop(animaide.slider, 'affect_non_selected_fcurves', text='Non-selected fcurves', toggle=False)
        col.prop(animaide.slider, 'affect_non_selected_keys', text='Non-selected keys on frame', toggle=False)


class AAT_OT_add_slider(Operator):
    '''
Add aditional slider to the panel'''

    bl_idname = 'animaide.add_slider'
    bl_label = "add_slider"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        animaide = context.scene.animaide
        slots = animaide.slider_slots
        slot = slots.add()
        slot.index = len(slots) - 1

        return {'FINISHED'}


class AAT_OT_remove_slider(Operator):
    '''
Removes last slider of the list'''

    bl_idname = 'animaide.remove_slider'
    bl_label = "remove_slider"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        animaide = context.scene.animaide
        slots = animaide.slider_slots
        # if len(slots) > 1:
        index = len(slots) - 1
        slots.remove(index)
        slider_tools.remove_marker(index+2)

        return {'FINISHED'}


class AAT_OT_get_ref_frame(Operator):
    '''
Sets a refernce frame that will be use by the BLEND FRAME
slider. The one at the left sets the left reference, and the
one on the right sets the right reference'''

    bl_idname = 'animaide.get_ref_frame'
    bl_label = "get_ref_frames"
    bl_options = {'REGISTER'}

    slot_index: IntProperty(default=-1)
    side: StringProperty()
    # is_collection: BoolProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        animaide = context.scene.animaide

        # if self.slot_index == -1:
        #     slider_num = '1'
        # else:
        #     slider_num = '%s' % (self.slot_index + 2)
        #
        # if self.is_collection:

        if self.slot_index == -1:
            slider = animaide.slider
            slider_num = 1
        else:
            slider = animaide.slider_slots[self.slot_index]
            slider_num = self.slot_index + 2

        current_frame = bpy.context.scene.frame_current

        # if self.is_collection:
        #     slider_num = self.slot_index + 2
        # else:
        #     slider_num = 1

        if self.side == 'L':
            slider.left_ref_frame = current_frame

        if self.side == 'R':
            slider.right_ref_frame = current_frame

        if slider.use_markers:
            slider_tools.add_marker(name_a='F',
                             name_b=slider_num,
                             side=self.side,
                             frame=current_frame)
        else:
            for side in ['L', 'R']:
                slider_tools.remove_marker(name_a='F',
                                    name_b=slider_num,
                                    side=side)
            # utils.remove_marker(slider_num)

        # key_utils.get_ref_frame_globals(slider.left_neighbor, slider.right_neighbor)

        # else:
        #
        #     if self.side == 'L':
        #         item.left_ref_frame = current_frame
        #
        #     if self.side == 'R':
        #         item.right_ref_frame = current_frame
        #
        #     left_ref_frame = item.left_ref_frame
        #     right_ref_frame = item.right_ref_frame
        #     key_utils.get_ref_frame_globals(left_ref_frame, right_ref_frame)

        return {'FINISHED'}


################  ANIM TRANSFORM  ###############


class AAT_OT_create_anim_trans_mask(Operator):
    ''' Adds a mask to the AnimTransform. It determins the influence
over the keys in the object being manipulated in the 3D View'''

    bl_idname = "animaide.create_anim_trans_mask"
    bl_label = "Create Mask"
    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return magnet.poll(context)

    def execute(self, context):
        scene = context.scene
        animaide = scene.animaide

        # key_utils.get_anim_transform_globals(obj)

        cur_frame = bpy.context.scene.frame_current

        animaide.anim_transform.mask_margin_l = cur_frame
        animaide.anim_transform.mask_margin_r = cur_frame
        animaide.anim_transform.mask_blend_l = -5
        animaide.anim_transform.mask_blend_r = 5

        magnet.add_anim_trans_mask()

        # context.scene.tool_settings.use_keyframe_insert_auto = False

        if magnet.anim_trans_mask_handlers not in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.append(magnet.anim_trans_mask_handlers)

        return {'FINISHED'}


class AAT_OT_anim_transform_on(Operator):
    '''Enables AnimTransform. Modify the entire animation
based on the object manipulation in the 3D View.
This tool desables auto-key'''

    bl_idname = "animaide.anim_transform_on"
    bl_label = "Activate"
    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return magnet.poll(context)

    def execute(self, context):
        animaide = context.scene.animaide
        animaide.anim_transform.active = True
        magnet.user_auto_animate = context.scene.tool_settings.use_keyframe_insert_auto
        context.scene.tool_settings.use_keyframe_insert_auto = False
        # context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer()
        # bpy.data.window_managers['WinMan'].windows.update()

        if magnet.anim_transform_handlers not in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.append(magnet.anim_transform_handlers)

        bpy.data.window_managers['WinMan'].update_tag()

        return {'FINISHED'}


class AAT_OT_anim_transform_off(Operator):
    '''Disable AnimTransform. Objects can be animated again'''

    bl_idname = "animaide.anim_transform_off"
    bl_label = "Deactivate"
    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return magnet.poll(context)

    def execute(self, context):
        animaide = context.scene.animaide
        animaide.anim_transform.active = False

        if magnet.anim_transform_handlers in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.remove(magnet.anim_transform_handlers)

        if magnet.anim_trans_mask_handlers in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.remove(magnet.anim_trans_mask_handlers)

        magnet.remove_anim_trans_mask()

        context.scene.tool_settings.use_keyframe_insert_auto = magnet.user_auto_animate
        # context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer()
        # bpy.data.window_managers['WinMan'].windows.update()
        bpy.data.window_managers['WinMan'].update_tag()

        return {'FINISHED'}


class AAT_OT_delete_anim_trans_mask(Operator):
    '''Removes the anim_trans_mask from the scene'''

    bl_idname = "animaide.delete_anim_trans_mask"
    bl_label = "Delete Mask"
    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return magnet.poll(context)

    def execute(self, context):

        if magnet.anim_trans_mask_handlers in bpy.app.handlers.depsgraph_update_pre:
            bpy.app.handlers.depsgraph_update_pre.remove(magnet.anim_trans_mask_handlers)

        magnet.remove_anim_trans_mask()

        return {'FINISHED'}


class AAT_OT_anim_transform_settings(Operator):
    '''
Options related to the anim_transform'''

    bl_idname = "animaide.anim_transform_settings"
    bl_label = "Anim Transform Settings"
    # bl_options = {'REGISTER'}

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return magnet.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=150)

    def draw(self, context):
        animaide = context.scene.animaide

        layout = self.layout

        row = layout.row(align=False)
        row.prop(animaide.anim_transform, 'easing', text='', icon_only=False)
        row = layout.row(align=False)
        row.prop(animaide.anim_transform, 'interp', text=' ', expand=True)
        # row = layout.row(align=False)
        # row.prop(animaide.anim_transform, 'use_markers', text='Use Markers')
        # row.prop(animaide.anim_transform, 'interp', text='', icon_only=False)


################  HELP  ###############


class AAT_OT_help(Operator):
    '''
Shows all the shortuts for the tool'''

    bl_idname = "animaide.help"
    bl_label = "Shortcuts"

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return slider_tools.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def draw(self, context):
        animaide = context.scene.animaide

        layout = self.layout
        col = layout.column(align=False)
        col.label(text='Shortcuts')
        col.label(text='')
        col.label(text='Ease To Ease    (1)')
        col.label(text='Tween           (shift 1)')
        col.label(text='Ease-In-Out     (2)')
        col.label(text='Blend Ease      (shift 2)')
        col.label(text='Blend Neighbor  (3)')
        col.label(text='Blend Frame     (shift 3)')
        col.label(text='Push-Pull       (4)')
        col.label(text='Scale Average   (shift 4)')
        col.label(text='Scale Left      (5)')
        col.label(text='Scale Right     (shift 5)')
        col.label(text='Smooth          (6)')
        col.label(text='Noise           (shift 6)')
        col.label(text='Time Offset     (7)')
        col.label(text='Blend Offset    (shift 7)')
        col.label(text='')
        col.label(text='Toward Left Neighbor    (-)')
        col.label(text='Toward Right Neighbor   (+)')
        col.label(text='')
        col.label(text='To Left Neighbor    (shift -)')
        col.label(text='To Right Neighbor   (shift +)')
        col.label(text='')
        col.label(text='pie_menu-1  (alt 1)')
        col.label(text='pie_menu-2  (alt 2)')


class AAT_OT_manual(Operator):
    '''
Opens Animaide manual'''

    bl_idname = "animaide.manual"
    bl_label = "Manual"

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "readme.html")
        url = 'file://' + path
        bpy.ops.wm.url_open(url=url)
        # bpy.ops.wm.url_open(url="https://github.com/aresdevo/animaide/blob/master/readme.md")
        return {'FINISHED'}


################  OTHER TOOLS  ###############


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

        cur_utils.add_clone(objects, cycle_before, cycle_after)

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

        cur_utils.remove_helpers(objects)

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

        key_utils.move_right_left(objects, self.amount, self.direction)

        return {'FINISHED'}


class AAT_OT_modifier(Operator):
    '''
    Add noise to a curve using a modifier'''

    bl_idname = 'animaide.fcurve_modifier'
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
                noise.scale = 3
                curve.convert_to_samples(0, 100)
                curve.convert_to_keyframes(0, 100)
                curve.modifiers.remove(noise)
        return {'FINISHED'}


# Variable to register Classes

classes = (
    AAT_OT_add_slider,
    AAT_OT_remove_slider,
    AAT_OT_anim_transform_on,
    AAT_OT_anim_transform_off,
    AAT_OT_help,
    AAT_OT_manual,
    AAT_OT_sliders_settings,
    AAT_OT_global_settings,
    AAT_OT_anim_transform_settings,
    AAT_OT_get_ref_frame,
    AAT_OT_ease_to_ease,
    AAT_OT_ease,
    AAT_OT_blend_ease,
    AAT_OT_blend_neighbor,
    AAT_OT_blend_frame,
    AAT_OT_blend_offset,
    AAT_OT_push_pull,
    AAT_OT_scale_average,
    AAT_OT_scale_left,
    AAT_OT_scale_right,
    AAT_OT_smooth,
    AAT_OT_noise,
    AAT_OT_time_offset,
    AAT_OT_tween,
    AAT_OT_clone,
    AAT_OT_clone_remove,
    AAT_OT_create_anim_trans_mask,
    AAT_OT_delete_anim_trans_mask
)






