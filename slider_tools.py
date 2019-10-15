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


import bpy

import random as rd

from . import utils, key_utils, cur_utils


# Sliders global variables

fcurve = None
global_fcurve = None
selected_keys = None
original_values = None
left_neighbor = None
right_neighbor = None
min_value = None
max_value = None


def set_handle(key, side, delta):

    handle = getattr(key, 'handle_%s' % side, None)
    handle_type = getattr(key, 'handle_%s_type' % side, None)

    if handle_type == 'FREE' or handle_type == 'ALIGNED':
        handle.y = key.co.y - delta


def set_handles(key, lh_delta, rh_delta):
    set_handle(key, 'left', lh_delta)
    set_handle(key, 'right', rh_delta)


def ease_to_ease(factor, slope):
    '''
    Transition selected keys from the neighboring ones in an "S" shape manner (ease-in and ease-out simultaneously)
    '''

    clamped_factor = utils.clamp(-factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y
        x = k.co.x - left_neighbor['x']
        try:
            key_ratio = 1 / (local_x / x)
        except:
            key_ratio = 0

        clamped_move = utils.clamp(clamped_factor, minimum=key_ratio - 1, maximum=key_ratio)

        ease_y = cur_utils.s_curve(key_ratio, slope=slope, xshift=clamped_move)

        k.co.y = left_neighbor['y'] + local_y * ease_y

        set_handles(k, lh_delta, rh_delta)


def ease(factor, slope):
    '''
    Transition selected keys from the neighboring ones in a "C" shape manner (ease-in or ease-out)
    '''

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
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y
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

        set_handles(k, lh_delta, rh_delta)


def blend_neighbor(factor):
    '''
    Blend selected keys to the value of the neighboring left and right keys
    '''

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        if factor < 0:
            delta = left_neighbor['y'] - original_values[index]['y']
        else:
            delta = right_neighbor['y'] - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


def blend_frame(factor, left_y_ref, right_y_ref):
    '''
    Blend selected keys to the value of the chosen left and right frames
    '''

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        if factor < 0:
            delta = left_y_ref - original_values[index]['y']
        else:
            delta = right_y_ref - original_values[index]['y']

        clamped_factor = utils.clamp(abs(factor), 0, max_value)

        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


def blend_ease(factor, slope):
    '''
    Blend selected keys to an ease-in or ease-out curve using the neighboring keys
    '''

    local_y = right_neighbor['y'] - left_neighbor['y']
    local_x = right_neighbor['x'] - left_neighbor['x']

    for index in selected_keys:

        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y
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

        set_handles(k, lh_delta, rh_delta)


def blend_offset(factor):
    '''
    Blend selected keys to the value of the chosen left and right frames
    '''

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
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


def tween(factor):
    '''
    Set lineal relative value of the selected keys in relationship to the neighboring ones
    '''

    clamped_factor = utils.clamp(factor, min_value, max_value)

    local_y = right_neighbor['y'] - left_neighbor['y']
    delta = local_y / 2
    mid = left_neighbor['y'] + delta

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        k.co.y = mid + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


def push_pull(factor):
    '''
    Exagerates or decreases the value of the selected keys
    '''

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        average_y = key_utils.linear_y(left_neighbor, right_neighbor, k)
        if average_y is None:
            continue
        delta = original_values[index]['y'] - average_y

        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


def smooth(factor):
    '''
    Averages values of selected keys creating a smoother fcurve
    '''

    # factor = (self.factor/2) + 0.5

    clamped_factor = utils.clamp(factor, min_value, max_value)
    print('first: ', selected_keys[0])
    print('original: ', original_values[selected_keys[0]]['sy'])

    for index in selected_keys:


        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        if 'sy' not in original_values[index]:
            continue

        smooth_y = original_values[index]['sy']
        # print('smooth_y: ', smooth_y)

        if smooth_y == 'book end':
            print('bookend')
            delta = 0
        else:
            delta = original_values[index]['y'] - smooth_y

        k.co.y = original_values[index]['y'] - delta * clamped_factor * 0.5

        set_handles(k, lh_delta, rh_delta)


def time_offset(factor, fcurves):
    '''
    Shift the value of selected keys to the ones of the left or right in the same fcurve
    '''

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
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        k.co.y = clone.evaluate(k.co.x - 20 * clamped_factor)

        set_handles(k, lh_delta, rh_delta)

    fcurves.remove(clone)


def noise(factor, fcurves, fcurve_index, phase):
    '''
    Set random values to the selected keys
    '''

    # factor = (self.factor/2) + 0.5
    # animaide = bpy.context.scene.animaide

    # clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone_name = 'animaide'
    clone = cur_utils.duplicate_from_data(fcurves,
                                          global_fcurve,
                                          clone_name)

    # cur_utils.add_noise(clone, strength=1, scale=0.2, phase=rd.uniform(0, 1))
    cur_utils.add_noise(clone, strength=1, scale=0.2, phase=phase + fcurve_index)

    clamped_factor = utils.clamp(factor, min_value, max_value)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        delta = clone.evaluate(k.co.x) - original_values[index]['y']
        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)

    fcurves.remove(clone)


def noise_random(factor, fcurves, range=1):
    '''
    Set random values to the selected keys
    '''

    # factor = (self.factor/2) + 0.5
    # animaide = bpy.context.scene.animaide

    # clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    # clone = cur_utils.duplicate_from_data(fcurves,
    #                                       global_fcurve,
    #                                       clone_name)

    # cur_utils.add_noise(clone, strength=1, scale=0.5, phase=fcurve_index * left_neighbor['y'])

    clamped_factor = utils.clamp(factor, min_value, max_value)

    noise = []
    half_range = range / 2
    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        random_y = rd.uniform(k.co.y - half_range, k.co.y + half_range)
        noise.append(random_y)

    for n, index in enumerate(selected_keys):
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        delta = noise[n] - original_values[index]['y']
        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)

    # fcurves.remove(clone)


def scale(factor, scale_type):
    '''
    Increase or decrease the value of selected keys acording to the "scale_type"
    L = use left neighboring key as anchor
    R = use right neighboring key as anchor
    Anything else =  use the average point as the anchor
    '''

    clamped_factor = utils.clamp(factor, min_value, max_value)

    y = 0
    for index in selected_keys:
        y = y + original_values[index]['y']
    y_average = y / len(selected_keys)

    for index in selected_keys:
        k = fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        if scale_type == 'L':
            delta = original_values[index]['y'] - left_neighbor['y']
        elif scale_type == 'R':
            delta = original_values[index]['y'] - right_neighbor['y']
        else:
            delta = original_values[index]['y'] - y_average

        k.co.y = original_values[index]['y'] + delta * clamped_factor

        set_handles(k, lh_delta, rh_delta)


# ###### Sliders Tools


def add_marker(name_a='marker', name_b='0', side='L', frame=0, overwrite_name=True):
    '''
    add reference frames marker
    '''
    if side in ['L', 'R']:
        name = '%s%s%s' % (side, name_a, name_b)
    else:
        name = '%s%s' % (name_a, name_b)

    markers = bpy.context.scene.timeline_markers
    # if markers.keys != []:
    if overwrite_name:
        if name in markers.keys():
            markers.remove(markers[name])
    marker = markers.new(name=name, frame=frame)
    # marker.select = False
    return marker


def modify_marker(marker, name='SAME', frame='SAME'):
    if name != 'SAME':
        marker.name = name

    if frame != 'SAME':
        marker.frame = frame


def remove_marker(name_a='marker', name_b='0', side='L'):
    if side in ['L', 'R']:
        name = '%s%s%s' % (side, name_a, name_b)
    else:
        name = '%s%s' % (name_a, name_b)

    markers = bpy.context.scene.timeline_markers

    if name in markers.keys():
        markers.remove(markers[name])

    return


# ###### Functions for Operators


def looper(self, context):
    '''
    Common actions used in the "execute" of the different slider operators
    '''

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

    if context.space_data.dopesheet.show_only_selected is True:
        objects = context.selected_objects
    else:
        objects = context.scene.objects

    # selected_pose_bones = bpy.context.selected_pose_bones
    # usable_bones_names = []

    for obj in objects:
        # anim = obj.animation_data

        if not key_utils.valid_anim(obj):
            continue

        visible = obj.visible_get()

        if not context.space_data.dopesheet.show_hidden and not visible:
            continue

        # if obj.type == 'ARMATURE':
        #     usable_bones_names = utils.get_usable_bone(obj, selected_pose_bones)

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():

            if not key_utils.valid_fcurve(fcurve):
                continue

            if obj.type == 'ARMATURE':
                # bone_name = utils.get_bone_name(fcurve, usable_bones_names)
                # bone_name = utils.get_bone_name(obj, fcurve)
                #

                if getattr(fcurve.group, 'name', None) == 'Object Transforms':
                    # When animating an object, by default its fcurves grouped with this name.
                    continue
                elif not fcurve.group:
                    transforms = (
                        'location', 'rotation_euler', 'scale',
                        'rotation_quaternion', 'rotation_axis_angle',
                        '[\"',  # custom property
                    )
                    if fcurve.data_path.startswith(transforms):
                        # fcurve belongs to the  object, so skip it
                        continue

                split_data_path = fcurve.data_path.split(sep='"')
                bone_name = split_data_path[1]
                bone = obj.data.bones.get(bone_name)

                only_selected = context.space_data.dopesheet.show_only_selected

                if bone is None or bone.hide or (only_selected and not bone.select):
                    continue

                # if bone_name is None:
                #     continue

            if getattr(fcurve.group, 'name', None) == cur_utils.group_name:
                continue  # we don't want to select keys on reference fcurves

            global_fcurve = key_utils.global_values[obj.name][fcurve_index]
            selected_keys = global_fcurve['selected_keys']

            if not selected_keys:
                continue

            original_values = global_fcurve['original_values']
            left_neighbor = global_fcurve['left_neighbor']
            right_neighbor = global_fcurve['right_neighbor']

            if self.slider_type == 'EASE_TO_EASE':
                ease_to_ease(self.factor, self.slope)

            elif self.slider_type == 'EASE':
                ease(self.factor, self.slope)

            elif self.slider_type == 'BLEND_NEIGHBOR':
                blend_neighbor(self.factor)

            elif self.slider_type == 'BLEND_FRAME':
                ref = key_utils.global_values[obj.name][fcurve_index]['ref_frames']
                left_y_ref = ref['left_y']
                right_y_ref = ref['right_y']
                blend_frame(self.factor, left_y_ref, right_y_ref)

            elif self.slider_type == 'BLEND_EASE':
                blend_ease(self.factor, self.slope)

            elif self.slider_type == 'BLEND_OFFSET':
                blend_offset(self.factor)

            elif self.slider_type == 'TWEEN':
                tween(self.factor)

            elif self.slider_type == 'PUSH_PULL':
                push_pull(self.factor)

            elif self.slider_type == 'SCALE_LEFT':
                scale(self.factor, 'L')

            elif self.slider_type == 'SCALE_RIGHT':
                scale(self.factor, 'R')

            elif self.slider_type == 'SCALE_AVERAGE':
                scale(self.factor, '')

            elif self.slider_type == 'SMOOTH':
                smooth(self.factor)

            elif self.slider_type == 'TIME_OFFSET':
                time_offset(self.factor, fcurves)

            elif self.slider_type == 'NOISE':
                # noise_random(self.factor, fcurves, fcurve_index)
                noise(self.factor, fcurves, fcurve_index, animaide.slider.noise_phase)

            fcurve.update()

    #        message = "Factor: %f03" % animaide.sliders.factor
    #        self.report({'INFO'}, "Factor:" + message)

    return {'FINISHED'}


def modal(self, context, event):
    '''
    Common actions used in the "modal" of the different slider operators
    '''

    if self.slot_index == -1:
        prop = self.animaide.slider
    else:
        prop = self.slots[self.slot_index]

    if event.type == 'MOUSEMOVE':  # Apply

        slider_from_zero = (event.mouse_x - self.init_mouse_x) / 100
        self.factor = slider_from_zero

        prop.factor = slider_from_zero
        prop.factor_overshoot = slider_from_zero

        self.execute(context)

    elif event.type == 'LEFTMOUSE':  # Confirm
        if context.area.type == 'GRAPH_EDITOR':
            context.area.tag_redraw()
        key_utils.get_sliders_globals()

        prop.modal_switch = False
        prop.factor = 0.0
        prop.factor_overshoot = 0.0

        return {'FINISHED'}

    elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
        if context.area.type == 'GRAPH_EDITOR':
            context.area.tag_redraw()
        key_utils.reset_original()

        prop.modal_switch = False
        prop.factor = 0.0
        prop.factor_overshoot = 0.0

        return {'CANCELLED'}

    return {'RUNNING_MODAL'}


def invoke(self, context, event):
    '''
    Common actions used in the "invoke" of the different slider operators
    '''

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
    self.phase = slider.noise_phase

    self.factor = 0.0
    self.init_mouse_x = event.mouse_x

    key_utils.get_sliders_globals(left_frame=slider.left_ref_frame,
                                  right_frame=slider.right_ref_frame)

    self.execute(context)
    context.window_manager.modal_handler_add(self)

    return {'RUNNING_MODAL'}


def poll(context):
    '''
    Poll used on all the slider operators
    '''

    objects = context.selected_objects
    animaide = context.scene.animaide
    anim_transform_active = animaide.anim_transform.active
    # space = context.area.spaces.active.type
    area = context.area.type
    # return objects != [] and area == 'GRAPH_EDITOR'
    return bool(not anim_transform_active and area == 'GRAPH_EDITOR' and objects)
