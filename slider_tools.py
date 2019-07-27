import bpy

import random as rd

from . import utils, key_utils, cur_utils

fcurve = None
global_fcurve = None
selected_keys = None
original_values = None
left_neighbor = None
right_neighbor = None
min_value = None
max_value = None


def ease_to_ease(factor, slope):
    # global selected_keys, fcurve, left_neighbor, right_neighbor

    clamped_factor = utils.clamp(-factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']
        try:
            key_ratio = 1 / (local_x / x)
        except:
            key_ratio = 0

        clamped_move = utils.clamp(clamped_factor, minimum=key_ratio - 1, maximum=key_ratio)

        ease_y = cur_utils.s_curve(key_ratio, slope=slope, xshift=clamped_move)

        k.co.y = left_neighbor['y'] + local_y * ease_y


def ease(factor, slope):
    # global selected_keys, fcurve, left_neighbor, right_neighbor

    clamped_factor = utils.clamp(factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    new_slope = 1 + ((slope * 2) * abs(clamped_factor))

    if factor < 0:
        height = 2
        width = 2
        yshift = 0
        xshift = 0
    else:
        height = 2
        width = 2
        xshift = -1
        yshift = -1

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']
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

        k.co.y = left_neighbor['y'] + local_y * ease_y.real


def blend_neighbor(factor):
    # global selected_keys, fcurve, left_neighbor, right_neighbor, original_values
    # global max_value

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if factor < 0:
            delta = left_neighbor['y'] - original_values[index]['y']
        else:
            delta = right_neighbor['y'] - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_frame(factor, left_y_ref, right_y_ref):
    # global selected_keys, fcurve, original_values, max_value

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if factor < 0:
            delta = left_y_ref - original_values[index]['y']
        else:
            delta = right_y_ref - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_ease(factor, slope):
    # global selected_keys, fcurve, left_neighbor, right_neighbor, min_value, max_value
    # global original_values

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        x = k.co.x - left_neighbor['x']

        if factor < 0:
            clamped_factor = utils.clamp(1 + factor * 2, min_value, max_value)
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0
            ease_y = cur_utils.s_curve(key_ratio,
                                       slope=1 + (slope),  # self.slope * 2,
                                       width=2,
                                       height=2,
                                       xshift=0,
                                       yshift=0)
        else:
            clamped_factor = utils.clamp(1 - factor * 2, min_value, max_value)
            try:
                key_ratio = 1 / (local_x / x)
            except:
                key_ratio = 0
            ease_y = cur_utils.s_curve(key_ratio,
                                       slope=1 + (slope),  # self.slope * 2,
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

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        delta = (left_neighbor['y'] + local_y * ease_y.real) - original_values[index]['y']

        # k.co.y = original_values[index]['y'] + delta * blend.real
        k.co.y = original_values[index]['y'] + delta * clamped_factor


def blend_offset(factor):
    # global selected_keys, min_value, max_value, right_neighbor, left_neighbor
    # global original_values, fcurve

    clamped_factor = utils.clamp(factor, min_value, max_value)

    first_key_index = selected_keys[0]
    last_key_index = selected_keys[-1]

    if first_key_index is None or last_key_index is None:
        return

    if clamped_factor > 0:
        delta = right_neighbor['y'] - original_values[last_key_index]['y']
    else:
        delta = original_values[first_key_index]['y'] - left_neighbor['y']

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = original_values[index]['y'] + delta * clamped_factor


def tween(factor):
    # global selected_keys, min_value, max_value, right_neighbor, left_neighbor
    # global fcurve

    clamped_factor = utils.clamp(factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    delta = local_y / 2
    mid = left_neighbor['y'] + delta

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = mid + delta * clamped_factor


def push_pull(factor):
    # global selected_keys, min_value, max_value, right_neighbor, left_neighbor
    # global fcurve, original_values

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        average_y = key_utils.linear_y(left_neighbor, right_neighbor, k)
        if average_y is None:
            continue
        delta = original_values[index]['y'] - average_y

        k.co.y = original_values[index]['y'] + delta * clamped_factor * 2


def smooth(factor):
    # global selected_keys, min_value, max_value, fcurve, original_values

    # factor = (self.factor/2) + 0.5

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:

        k = fcurve.keyframe_points[index]

        if 'sy' not in original_values[index]:
            continue

        smooth_y = original_values[index]['sy']

        if smooth_y == 'book end':
            delta = 0
        else:
            delta = original_values[index]['y'] - smooth_y

        k.co.y = original_values[index]['y'] - delta * clamped_factor


def time_offset(factor, fcurves):
    # global selected_keys, min_value, max_value, fcurve

    # factor = (self.factor/2) + 0.5
    animaide = bpy.context.scene.animaide
    cycle_before = animaide.clone.cycle_before
    cycle_after = animaide.clone.cycle_after

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone = cur_utils.duplicate_from_data(fcurves,
                                          global_fcurve,
                                          clone_name,
                                          before=cycle_before,
                                          after=cycle_after)

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        k.co.y = clone.evaluate(k.co.x - 20 * clamped_factor)

    fcurves.remove(clone)


def noise(factor, fcurves, fcurve_index):
    # global selected_keys, min_value, max_value, fcurve, original_values

    # factor = (self.factor/2) + 0.5
    # animaide = bpy.context.scene.animaide

    # clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone_name = 'animaide'
    clone = cur_utils.duplicate_from_data(fcurves,
                                          global_fcurve,
                                          clone_name)

    cur_utils.add_noise(clone, strength=1, scale=0.2, phase=rd.uniform(0, 1))

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        delta = clone.evaluate(k.co.x) - original_values[index]['y']
        k.co.y = original_values[index]['y'] + delta * clamped_factor

    fcurves.remove(clone)


def noise_random(factor, fcurves, range=1):
    # global selected_keys, min_value, max_value, fcurve, original_values

    # factor = (self.factor/2) + 0.5
    # animaide = bpy.context.scene.animaide

    # clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    # clone = cur_utils.duplicate_from_data(fcurves,
    #                                       global_fcurve,
    #                                       clone_name)

    # cur_utils.add_noise(clone, strength=1, scale=0.5, phase=fcurve_index * left_neighbor['y'])

    clamped_factor = utils.clamp(factor, min_value, max_value)

    noise = []
    half_range = range/2
    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        random_y = rd.uniform(k.co.y - half_range, k.co.y + half_range)
        noise.append(random_y)

    n = 0
    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        delta = noise[n] - original_values[index]['y']
        k.co.y = original_values[index]['y'] + delta * clamped_factor
        n += 1

    # fcurves.remove(clone)


def scale(factor, scale_type):
    # global selected_keys, min_value, max_value, original_values, fcurve
    # global original_values, left_neighbor, right_neighbor

    clamped_factor = utils.clamp(factor, min_value, max_value)

    y = 0
    for index in selected_keys:
        y = y + original_values[index]['y']
    y_average = y / len(selected_keys)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        if scale_type == 'L':
            delta = original_values[index]['y'] - left_neighbor['y']
        elif scale_type == 'R':
            delta = right_neighbor['y'] - original_values[index]['y']
        else:
            delta = original_values[index]['y'] - y_average

        k.co.y = original_values[index]['y'] + delta * clamped_factor


####### For Operators


def looper(self, context):
    global min_value, max_value, global_fcurve, selected_keys
    global original_values, left_neighbor, right_neighbor, fcurve

    animaide = context.scene.animaide

    if self.slot_index == -1:
        slider = animaide.slider
    else:
        slider = animaide.slider_slots[self.slot_index]

    if self.op_context == 'EXEC_DEFAULT':
        key_utils.get_sliders_globals(left_frame=slider.left_ref_frame,
                                      right_frame=slider.right_ref_frame)

    # slider.factor = self.factor
    # slider.factor_overshoot = self.factor

    min_value = slider.min_value
    max_value = slider.max_value

    if bpy.context.space_data.dopesheet.show_only_selected is True:
        objects = context.selected_objects
    else:
        objects = bpy.data.objects

    selected_pose_bones = bpy.context.selected_pose_bones
    usable_bones_names = []

    for obj in objects:
        # anim = obj.animation_data

        if not key_utils.valid_anim(obj):
            continue

        visible = obj.visible_get()

        if bpy.context.space_data.dopesheet.show_hidden is not True:

            if not visible:
                continue

        # if anim is None:
        #     continue
        #
        # if anim.action is None:
        #     continue
        #
        # if anim.action.fcurves is None:
        #     continue

        if obj.type == 'ARMATURE':
            # if obj.mode == 'POSE':
            if bpy.context.space_data.dopesheet.show_only_selected is True:
                if selected_pose_bones is None:
                    usable_bones_names = []
                else:
                    # usable_bones = selected_pose_bones
                    usable_bones_names = [bone.name for bone in obj.pose.bones if bone in selected_pose_bones
                                          and bone.bone.hide is False]
            else:
                # channel_groups = ['Object Transforms']
                # channel_groups = anim.action.groups
                # usable_bones = obj.pose.bones
                usable_bones_names = [bone.name for bone in obj.pose.bones if bone.bone.hide is False]

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():

            # # if fcurve.select is False:
            # #     continue
            #
            # if fcurve.lock is True:
            #     continue
            #
            # if fcurve.hide is True:
            #     continue

            if not key_utils.valid_fcurve(fcurve):
                continue

            if obj.type == 'ARMATURE':
                if fcurve.group.name != 'Object Transforms':
                    split_data_path = fcurve.data_path.split(sep='"')
                    bone_name = split_data_path[1]

                    if bone_name not in usable_bones_names:
                        if fcurve.group.name != 'Object Transforms':
                            continue

            if fcurve.group.name == cur_utils.group_name:
                continue  # we don't want to select keys on reference fcurves

            global_fcurve = key_utils.global_values[obj.name][fcurve_index]
            selected_keys = global_fcurve['selected_keys']

            if selected_keys == []:
                continue

            original_values = global_fcurve['original_values']
            left_neighbor = global_fcurve['left_neighbor']
            right_neighbor = global_fcurve['right_neighbor']

            if self.slider_type == 'EASE_TO_EASE':
                ease_to_ease(self.factor, self.slope)

            if self.slider_type == 'EASE':
                ease(self.factor, self.slope)

            if self.slider_type == 'BLEND_NEIGHBOR':
                blend_neighbor(self.factor)

            if self.slider_type == 'BLEND_FRAME':
                left_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['left_y']
                right_y_ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']['right_y']
                blend_frame(self.factor, left_y_ref, right_y_ref)

            if self.slider_type == 'BLEND_EASE':
                blend_ease(self.factor, self.slope)

            if self.slider_type == 'BLEND_OFFSET':
                blend_offset(self.factor)

            if self.slider_type == 'TWEEN':
                tween(self.factor)

            if self.slider_type == 'PUSH_PULL':
                push_pull(self.factor)

            if self.slider_type == 'SCALE_LEFT':
                scale(self.factor, 'L')

            if self.slider_type == 'SCALE_RIGHT':
                scale(self.factor, 'R')

            if self.slider_type == 'SCALE_AVERAGE':
                scale(self.factor, '')

            if self.slider_type == 'SMOOTH':
                smooth(self.factor)

            if self.slider_type == 'TIME_OFFSET':
                time_offset(self.factor, fcurves)

            if self.slider_type == 'NOISE':
                noise(self.factor, fcurves, fcurve_index)

            fcurve.update()

    #        message = "Factor: %f03" % animaide.sliders.factor
    #        self.report({'INFO'}, "Factor:" + message)

    return {'FINISHED'}


def modal(self, context, event):
    if event.type == 'MOUSEMOVE':  # Apply

        slider_from_zero = (event.mouse_x - self.init_mouse_x) / 100
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
        key_utils.get_sliders_globals()
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


def invoke(self, context, event):

    # self.animaide.slider.selector = self.slider_type

    if self.op_context == 'EXEC_DEFAULT':
        return self.execute(context)

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

    key_utils.get_sliders_globals(left_frame=slider.left_ref_frame,
                                  right_frame=slider.right_ref_frame)

    self.execute(context)
    context.window_manager.modal_handler_add(self)

    return {'RUNNING_MODAL'}


def poll(context):
    objects = context.selected_objects
    animaide = context.scene.animaide
    anim_transform_active = animaide.anim_transform.active
    # space = context.area.spaces.active.type
    area = context.area.type
    # return objects != [] and area == 'GRAPH_EDITOR'
    return anim_transform_active is False and area == 'GRAPH_EDITOR' and objects is not None

