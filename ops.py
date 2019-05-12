import bpy

from . import utils, key_utils, cur_utils, slider_tools
from bpy.props import StringProperty, EnumProperty, BoolProperty, \
    IntProperty, FloatProperty
from bpy.types import Operator


class AAT_OT_sliders_everything(Operator):
    '''
    Slider
    '''
    bl_idname = "animaide.sliders"
    bl_label = "sliders"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    # is_collection: BoolProperty()
    op_context: StringProperty(default='INVOKE_DEFAULT')

    fcurve = None
    global_fcurve = None
    selected_keys = None
    original_values = None
    left_neighbor = None
    right_neighbor = None
    min_value = None
    max_value = None

    @classmethod
    def poll(cls, context):
        objects = context.selected_objects
        return objects != []

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        bpy.context.area.tag_redraw()

    def ease(self):

        clamped_factor = utils.clamp(-self.factor, self.min_value, self.max_value)

        local_y = self.right_neighbor['y'] - self.left_neighbor['y']
        local_x = self.right_neighbor['x'] - self.left_neighbor['x']

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]
            x = k.co.x - self.left_neighbor['x']
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0

            clamped_move = utils.clamp(clamped_factor, minimum=key_ratio - 1, maximum=key_ratio)

            ease_y = cur_utils.s_curve(key_ratio, slope=self.slope, xshift=clamped_move)

            k.co.y = self.left_neighbor['y'] + local_y * ease_y

    def ease_in_out(self):

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        local_y = self.right_neighbor['y'] - self.left_neighbor['y']
        local_x = self.right_neighbor['x'] - self.left_neighbor['x']

        new_slope = 1 + ((self.slope * 2) * abs(clamped_factor))

        if self.factor < 0:
            height = 2
            width = 2
            yshift = 0
            xshift = 0
        else:
            height = 2
            width = 2
            xshift = -1
            yshift = -1

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]
            x = k.co.x - self.left_neighbor['x']
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0

            ease_y = cur_utils.s_curve(key_ratio,
                                       slope=new_slope,
                                       width=width,
                                       height=height,
                                       xshift=xshift,
                                       yshift=yshift)

            k.co.y = self.left_neighbor['y'] + local_y * ease_y.real

    def blend_neighbor(self):

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]

            if self.factor < 0:
                delta = self.left_neighbor['y'] - self.original_values[index]['y']
            else:
                delta = self.right_neighbor['y'] - self.original_values[index]['y']

            clamped_factor = utils.clamp(abs(self.factor), 0, self.max_value)

            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

    def blend_frame(self, left_y_ref, right_y_ref):

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]

            if self.factor < 0:
                delta = left_y_ref - self.original_values[index]['y']
            else:
                delta = right_y_ref - self.original_values[index]['y']

            clamped_factor = utils.clamp(abs(self.factor), 0, self.max_value)

            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

    def blend_ease(self):

        local_y = self.right_neighbor['y'] - self.left_neighbor['y']
        local_x = self.right_neighbor['x'] - self.left_neighbor['x']

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]
            x = k.co.x - self.left_neighbor['x']

            if self.factor < 0:
                clamped_factor = utils.clamp(1 + self.factor * 2, self.min_value, self.max_value)
                try:
                    key_ratio = 1 / (local_x / x)
                except:
                    key_ratio = 0
                ease_y = cur_utils.s_curve(key_ratio,
                                           slope=1 + (self.slope),  # self.slope * 2,
                                           width=2,
                                           height=2,
                                           xshift=0,
                                           yshift=0)
            else:
                clamped_factor = utils.clamp(1 - self.factor * 2, self.min_value, self.max_value)
                try:
                    key_ratio = 1 / (local_x / x)
                except:
                    key_ratio = 0
                ease_y = cur_utils.s_curve(key_ratio,
                                           slope=1 + (self.slope),  # self.slope * 2,
                                           width=2,
                                           height=2,
                                           xshift=-1,
                                           yshift=-1)

            clamped_move = utils.clamp(clamped_factor,
                                       minimum=key_ratio - 1,
                                       maximum=key_ratio)

            blend = cur_utils.s_curve(key_ratio,
                                      slope=1.3,
                                      # xshift=clamped_move)
                                      width=2,
                                      height=2,
                                      xshift=clamped_move - 1,
                                      yshift=-1)

            clamped_factor = utils.clamp(abs(self.factor), 0, self.max_value)

            delta = (self.left_neighbor['y'] + local_y * ease_y.real) - self.original_values[index]['y']

            # k.co.y = original_values[index]['y'] + delta * blend.real
            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

    def blend_offset(self):

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        first_key_index = self.selected_keys[0]
        last_key_index = self.selected_keys[-1]

        if first_key_index is None or last_key_index is None:
            return

        if clamped_factor > 0:
            delta = self.right_neighbor['y'] - self.original_values[last_key_index]['y']
        else:
            delta = self.original_values[first_key_index]['y'] - self.left_neighbor['y']

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

    def tween(self):

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        local_y = self.right_neighbor['y'] - self.left_neighbor['y']
        delta = local_y / 2
        mid = self.left_neighbor['y'] + delta

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            k.co.y = mid + delta * clamped_factor

    def push_pull(self):

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            average_y = key_utils.linear_y(self.left_neighbor, self.right_neighbor, k)
            if average_y == 0:
                continue
            delta = self.original_values[index]['y'] - average_y

            k.co.y = self.original_values[index]['y'] + delta * clamped_factor * 2

    def smooth(self):

        # factor = (self.factor/2) + 0.5

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        for index in self.selected_keys:

            k = self.fcurve.keyframe_points[index]

            if 'sy' not in self.original_values[index]:
                continue

            smooth_y = self.original_values[index]['sy']

            if smooth_y == 'book end':
                delta = 0
            else:
                delta = self.original_values[index]['y'] - smooth_y

            k.co.y = self.original_values[index]['y'] - delta * clamped_factor

    def time_offset(self, fcurves):

        # factor = (self.factor/2) + 0.5
        animaide = bpy.context.scene.animaide
        cycle_before = animaide.clone.cycle_before
        cycle_after = animaide.clone.cycle_after

        clone_name = '%s.%d.clone' % (self.fcurve.data_path, self.fcurve.array_index)
        clone = cur_utils.duplicate_from_data(fcurves,
                                              self.global_fcurve,
                                              clone_name,
                                              before=cycle_before,
                                              after=cycle_after)

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            k.co.y = clone.evaluate(k.co.x - 20 * clamped_factor)

        fcurves.remove(clone)

    def noise(self, fcurves, fcurve_index):

        # factor = (self.factor/2) + 0.5
        # animaide = bpy.context.scene.animaide

        clone_name = '%s.%d.clone' % (self.fcurve.data_path, self.fcurve.array_index)
        clone = cur_utils.duplicate_from_data(fcurves,
                                              self.global_fcurve,
                                              clone_name)

        cur_utils.add_noise(clone, strength=1, scale=0.5, phase=fcurve_index * self.left_neighbor['y'])

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            delta = clone.evaluate(k.co.x) - self.original_values[index]['y']
            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

        fcurves.remove(clone)

    def scale(self, scale_type):

        clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

        y = 0
        for index in self.selected_keys:
            y = y + self.original_values[index]['y']
        y_average = y / len(self.selected_keys)

        for index in self.selected_keys:
            k = self.fcurve.keyframe_points[index]
            if scale_type == 'L':
                delta = self.original_values[index]['y'] - self.left_neighbor['y']
            elif scale_type == 'R':
                delta = self.right_neighbor['y'] - self.original_values[index]['y']
            else:
                delta = self.original_values[index]['y'] - y_average

            k.co.y = self.original_values[index]['y'] + delta * clamped_factor

    def execute(self, context):

        animaide = context.scene.animaide

        # if self.is_collection:
        #     slider = animaide.slider_slots[self.slot_index]
        # else:
        #     slider = animaide.slider

        if self.slot_index == -1:
            slider = animaide.slider
        else:
            slider = animaide.slider_slots[self.slot_index]

        if self.op_context == 'EXEC_DEFAULT':
            key_utils.get_globals(left_frame=slider.left_ref_frame,
                                  right_frame=slider.right_ref_frame)
            # key_utils.get_ref_frame_globals(slider.left_ref_frame, slider.right_ref_frame)

        slider.factor = self.factor
        slider.factor_overshoot = self.factor

        self.min_value = slider.min_value
        self.max_value = slider.max_value

        objects = context.selected_objects

        for obj in objects:
            anim = obj.animation_data
            if anim is None:
                continue
            if anim.action.fcurves is None:
                continue
            fcurves = obj.animation_data.action.fcurves

            for fcurve_index, self.fcurve in fcurves.items():

                if self.fcurve.select is False:
                    continue

                if self.fcurve.lock is True:
                    continue

                if self.fcurve.hide is True:
                    continue

                if self.fcurve.group.name == cur_utils.group_name:
                    continue  # we don't want to select keys on reference fcurves

                # print('global values: ', key_utils.global_values)

                self.global_fcurve = key_utils.global_values[obj.name][fcurve_index]
                self.selected_keys = self.global_fcurve['selected_keys']

                if self.selected_keys[0] is None:
                    return {'FINISHED'}

                self.original_values = self.global_fcurve['original_values']
                self.left_neighbor = self.global_fcurve['left_neighbor']
                self.right_neighbor = self.global_fcurve['right_neighbor']

                # if not self.selected_keys:
                #     continue

                # if not self.selected_keys:
                #     index = key_utils.on_current_frame(self.fcurve)
                #     self.selected_keys = [index]
                #     if index is None:
                #         continue

                # self.left_neighbor, self.right_neighbor = key_utils.get_selected_neigbors(self.fcurve,
                #                                                                           self.selected_keys)

                if self.slider_type == 'EASE':
                    self.ease()

                if self.slider_type == 'EASE_IN_OUT':
                    self.ease_in_out()

                if self.slider_type == 'BLEND_NEIGHBOR':
                    self.blend_neighbor()

                if self.slider_type == 'BLEND_FRAME':
                    left_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['left_y']
                    right_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['right_y']
                    self.blend_frame(left_y_ref, right_y_ref)

                if self.slider_type == 'BLEND_EASE':
                    self.blend_ease()

                if self.slider_type == 'BLEND_OFFSET':
                    self.blend_offset()

                if self.slider_type == 'TWEEN':
                    self.tween()

                if self.slider_type == 'PUSH_PULL':
                    self.push_pull()

                if self.slider_type == 'SCALE_LEFT':
                    self.scale('L',)

                if self.slider_type == 'SCALE_RIGHT':
                    self.scale('R')

                if self.slider_type == 'SCALE_AVERAGE':
                    self.scale('')

                if self.slider_type == 'SMOOTH':
                    self.smooth()

                if self.slider_type == 'TIME_OFFSET':
                    self.time_offset(fcurves)

                if self.slider_type == 'NOISE':
                    self.noise(fcurves, fcurve_index)

                self.fcurve.update()

#        message = "Factor: %f03" % animaide.sliders.factor
#        self.report({'INFO'}, "Factor:" + message)

        return {'FINISHED'}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':  # Apply

            slider_from_zero = (event.mouse_x - self.init_mouse_x) / 200
            self.factor = slider_from_zero

            if self.slot_index == -1:
                self.item.factor = slider_from_zero
                self.item.factor_overshoot = slider_from_zero
            else:
                self.slots[self.slot_index].factor = slider_from_zero
                self.slots[self.slot_index].factor_overshoot = slider_from_zero

            self.execute(context)

        elif event.type == 'LEFTMOUSE':  # Confirm
            key_utils.get_globals()
            if self.slot_index == -1:
                self.animaide.slider.modal_switch = False
                self.animaide.slider.factor = 0.0
                self.animaide.slider.factor_overshoot = 0.0
            else:
                self.slots[self.slot_index].modal_switch = False
                self.slots[self.slot_index].factor = 0.0
                self.slots[self.slot_index].factor_overshoot = 0.0
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            key_utils.reset_original()
            if self.slot_index == -1:
                self.animaide.slider.modal_switch = False
                self.animaide.slider.factor = 0.0
                self.animaide.slider.factor_overshoot = 0.0
            else:
                self.slots[self.slot_index].modal_switch = False
                self.slots[self.slot_index].factor = 0.0
                self.slots[self.slot_index].factor_overshoot = 0.0
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        if self.slot_index == -1:
            slider = self.animaide.slider
        else:
            slider = self.slots[self.slot_index]

        slider.modal_switch = True
        slider.factor = 0.0
        slider.factor_overshoot = 0.0
        self.slope = slider.slope

        self.factor = 0.0
        self.init_mouse_x = event.mouse_x

        key_utils.get_globals(left_frame=slider.left_ref_frame,
                              right_frame=slider.right_ref_frame)

        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def slider_looper(self, context):
    animaide = context.scene.animaide

    if self.slot_index == -1:
        slider = animaide.slider
    else:
        slider = animaide.slider_slots[self.slot_index]

    if self.op_context == 'EXEC_DEFAULT':
        key_utils.get_globals(left_frame=slider.left_ref_frame,
                              right_frame=slider.right_ref_frame)

    # slider.factor = self.factor
    # slider.factor_overshoot = self.factor

    slider_tools.min_value = slider.min_value
    slider_tools.max_value = slider.max_value

    objects = context.selected_objects

    for obj in objects:
        anim = obj.animation_data

        if obj.type == 'ARMATURE' and obj.mode == 'POSE':
            channel_groups = [bone.name for bone in bpy.context.selected_pose_bones]
            # print('channel groups: ', channel_groups)
        else:
            channel_groups = anim.action.groups

        if anim is None:
            continue
        if anim.action.fcurves is None:
            continue
        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, slider_tools.fcurve in fcurves.items():
            # print('---')
            # print('channel groups: ', channel_groups)
            # print('fcurve group: ', slider_tools.fcurve.group.name)
            # print('not in group: ', slider_tools.fcurve.group.name not in channel_groups)
            # print('---')

            if slider_tools.fcurve.select is False:
                continue

            if slider_tools.fcurve.lock is True:
                continue

            if slider_tools.fcurve.hide is True:
                continue

            if slider_tools.fcurve.group.name not in channel_groups:
                continue

            if slider_tools.fcurve.group.name == cur_utils.group_name:
                continue  # we don't want to select keys on reference fcurves

            slider_tools.global_fcurve = key_utils.global_values[obj.name][fcurve_index]
            slider_tools.selected_keys = slider_tools.global_fcurve['selected_keys']

            if slider_tools.selected_keys[0] is None:
                return {'FINISHED'}

            slider_tools.original_values = slider_tools.global_fcurve['original_values']
            slider_tools.left_neighbor = slider_tools.global_fcurve['left_neighbor']
            slider_tools.right_neighbor = slider_tools.global_fcurve['right_neighbor']

            if self.slider_type == 'EASE':
                slider_tools.ease(self.factor, self.slope)

            if self.slider_type == 'EASE_IN_OUT':
                slider_tools.ease_in_out(self.factor, self.slope)

            if self.slider_type == 'BLEND_NEIGHBOR':
                slider_tools.blend_neighbor(self.factor)

            if self.slider_type == 'BLEND_FRAME':
                left_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['left_y']
                right_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['right_y']
                slider_tools.blend_frame(self.factor, left_y_ref, right_y_ref)

            if self.slider_type == 'BLEND_EASE':
                slider_tools.blend_ease(self.factor, self.slope)

            if self.slider_type == 'BLEND_OFFSET':
                slider_tools.blend_offset(self.factor)

            if self.slider_type == 'TWEEN':
                slider_tools.tween(self.factor)

            if self.slider_type == 'PUSH_PULL':
                slider_tools.push_pull(self.factor)

            if self.slider_type == 'SCALE_LEFT':
                slider_tools.scale(self.factor, 'L')

            if self.slider_type == 'SCALE_RIGHT':
                slider_tools.scale(self.factor, 'R')

            if self.slider_type == 'SCALE_AVERAGE':
                slider_tools.scale(self.factor, '')

            if self.slider_type == 'SMOOTH':
                slider_tools.smooth(self.factor)

            if self.slider_type == 'TIME_OFFSET':
                slider_tools.time_offset(self.factor, fcurves)

            if self.slider_type == 'NOISE':
                slider_tools.noise(self.factor, fcurves, fcurve_index)

            slider_tools.fcurve.update()

    #        message = "Factor: %f03" % animaide.sliders.factor
    #        self.report({'INFO'}, "Factor:" + message)

    return {'FINISHED'}


def slider_modal(self, context, event):
    if event.type == 'MOUSEMOVE':  # Apply

        slider_from_zero = (event.mouse_x - self.init_mouse_x) / 200
        self.factor = slider_from_zero

        if self.slot_index == -1:
            self.item.factor = slider_from_zero
            self.item.factor_overshoot = slider_from_zero
        else:
            self.slots[self.slot_index].factor = slider_from_zero
            self.slots[self.slot_index].factor_overshoot = slider_from_zero

        self.execute(context)

    elif event.type == 'LEFTMOUSE':  # Confirm
        if context.area.type == 'GRAPH_EDITOR':
            context.area.tag_redraw()
        key_utils.get_globals()
        if self.slot_index == -1:
            self.animaide.slider.modal_switch = False
            self.animaide.slider.factor = 0.0
            self.animaide.slider.factor_overshoot = 0.0
        else:
            self.slots[self.slot_index].modal_switch = False
            self.slots[self.slot_index].factor = 0.0
            self.slots[self.slot_index].factor_overshoot = 0.0
        return {'FINISHED'}

    if event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
        if context.area.type == 'GRAPH_EDITOR':
            context.area.tag_redraw()
        key_utils.reset_original()
        if self.slot_index == -1:
            self.animaide.slider.modal_switch = False
            self.animaide.slider.factor = 0.0
            self.animaide.slider.factor_overshoot = 0.0
        else:
            self.slots[self.slot_index].modal_switch = False
            self.slots[self.slot_index].factor = 0.0
            self.slots[self.slot_index].factor_overshoot = 0.0
        return {'CANCELLED'}

    return {'RUNNING_MODAL'}


def slider_invoke(self, context, event):

    # self.animaide.slider.selector = self.slider_type

    if self.slot_index == -1:
        slider = self.animaide.slider
        overshoot = slider.overshoot
        slider.selector = self.slider_type
        slider.overshoot = overshoot
    else:
        slider = self.slots[self.slot_index]

    slider.modal_switch = True
    slider.factor = 0.0
    slider.factor_overshoot = 0.0
    self.slope = slider.slope

    self.factor = 0.0
    self.init_mouse_x = event.mouse_x

    key_utils.get_globals(left_frame=slider.left_ref_frame,
                          right_frame=slider.right_ref_frame)

    self.execute(context)
    context.window_manager.modal_handler_add(self)

    return {'RUNNING_MODAL'}


def slider_poll(context):
    objects = context.selected_objects
    # space = context.area.spaces.active.type
    area = context.area.type
    return objects != [] and area == 'GRAPH_EDITOR'


class AAT_OT_sliders(Operator):
    bl_idname = "animaide.sliders"
    bl_label = "Sliders"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')

    @classmethod
    def poll(cls, context):
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_ease(Operator):
    ''' EASE

Transition selected keys - or current key - from the neighboring
ones with a "S" shape manner (ease-in and ease-out simultaneously).
It doesn't take into consideration the current key values.

shortcut:   1
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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_ease_in_out(Operator):
    ''' EASE-IN-OUT

Transition selected keys - or current key - from the neighboring
ones with a "C" shape manner (ease-in or ease-out). It doesn't
take into consideration the current key values.

shortcut:   2
pie_menu-1:  (alt-1)'''

    bl_idname = "animaide.ease_in_out"
    bl_label = "Ease In Out"

    slope: FloatProperty(default=2.0)
    factor: FloatProperty(default=0.0)
    # slider_type: StringProperty()
    slot_index: IntProperty(default=-1)
    op_context: StringProperty(default='INVOKE_DEFAULT')
    slider_type = 'EASE_IN_OUT'

    @classmethod
    def poll(cls, context):
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_blend_neighbor(Operator):
    ''' BLEND NEIGHBOR

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_blend_frame(Operator):
    ''' BLEND FRAME

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_blend_ease(Operator):
    ''' BLEND EASE

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_blend_offset(Operator):
    ''' BLEND OFFSET

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_tween(Operator):
    ''' TWEEN

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_push_pull(Operator):
    ''' PUSH-PULL

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_smooth(Operator):
    ''' SMOOTH

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_time_offset(Operator):
    ''' TIME OFFSET

Shift the value of selected keys - or current key -
to the ones of the left or right in the seme fcurve

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_noise(Operator):
    ''' NOISE

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_scale_left(Operator):
    ''' SCALE LEFT

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_scale_right(Operator):
    ''' SCALE RIGHT

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


class AAT_OT_scale_average(Operator):
    ''' SCALE AVERAGE

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
        return slider_poll(context)

    def __init__(self):
        self.animaide = bpy.context.scene.animaide
        self.slots = self.animaide.slider_slots
        self.item = self.animaide.slider
        self.init_mouse_x = None

    def __del__(self):
        pass

    def execute(self, context):

        return slider_looper(self, context)

    def modal(self, context, event):

        return slider_modal(self, context, event)

    def invoke(self, context, event):

        return slider_invoke(self, context, event)


################  TOOLS  ###############


class AAT_OT_add_slider(Operator):
    ''' ADD EXTRA SLIDER

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
    ''' REMOVE SLIDERS

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
        utils.remove_marker(index+2)

        return {'FINISHED'}


class AAT_OT_get_ref_frame(Operator):
    ''' SET REFERENCE FRAME

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

        utils.add_marker(slider_num, self.side, current_frame)

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


class AAT_OT_settings(Operator):
    ''' SLIDER SETTING

Options related to the current tool on the slider'''

    bl_idname = "animaide.settings"
    bl_label = "Sliders Settings"

    slot_index: IntProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

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
        col.prop(slider, 'overshoot', text='Overshoot', toggle=True)


class AAT_OT_clone(Operator):
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










