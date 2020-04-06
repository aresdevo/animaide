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

from . import key_utils, utils


group_name = 'animaide'

user_preview_range = {}
user_scene_range = {}


# def add_samples(fcurve, reference_fcurve, frequency=1):
        # """
        # Add keys to an fcurve with the given frequency
        # """
        # key_list = fcurve.keyframe_points

        # selected_keys = key_utils.get_selected(fcurve)
        # first_key, last_key = key_utils.first_and_last_selected(fcurve, selected_keys)

        # amount = int(abs(last_key.co.x - first_key.co.x) / frequency)
        # frame = first_key.co.x

        # for n in range(amount):
            # target = reference_fcurve.evaluate(frame)
            # key_list.insert(frame, target)
            # frame += frequency

        # target = reference_fcurve.evaluate(last_key.co.x)
        # key_list.insert(last_key.co.x, target)


def get_selected(fcurves):
    '''
    return selected fcurves in the current action with the exception of the reference fcurves
    '''
    selected = []

    for fcurve in fcurves:
        if getattr(fcurve.group, 'name', None) == group_name:
            continue        # we don't want to add to the list the helper curves we have created

        if fcurve.select:
            selected.append(fcurve)

    print('selected fcurves: ', selected)

    return selected


def remove_helpers(objects):
    """
    Remove the all the helper curves that have been aded to an object action
    :param objects: object than owns the action to be afected.
    """
    for obj in objects:
        action = obj.animation_data.action

        # animaide = bpy.context.scene.animaide
        # aclones = animaide.clone_data.clones
        # arefe = animaide.reference
        # arefe.fcurve.data_path = ''
        # arefe.fcurve.index = -1

        for fcurve in action.fcurves:     # delete the first of the clones left
            if getattr(fcurve.group, 'name', None) == group_name:
                action.fcurves.remove(fcurve)
                # aclones.remove(0)


# def get_slope(fcurve):
    # """

    # """
    # selected_keys = key_utils.get_selected(fcurve)
    # first_key, last_key = key_utils.first_and_last_selected(fcurve, selected_keys)
    # slope = (first_key.co.y**2 - last_key.co.y**2) / (first_key.co.x**2 - last_key.co.x**2)
    # return slope


def add_cycle(fcurve, before='MIRROR', after='MIRROR'):
    """
    Add cycle modifier to an fcurve
    """
    cycle = fcurve.modifiers.new('CYCLES')

    cycle.mode_before = before
    cycle.mode_after = after


def add_noise(fcurve, strength=0.4, scale=1, phase=0):
    """
    add noise modifier to an fcurve
    """
    noise = fcurve.modifiers.new('NOISE')

    noise.strength = strength
    noise.scale = scale
    noise.phase = phase
    # fcurve.convert_to_samples(0, 100)
    # fcurve.convert_to_keyframes(0, 100)
    # fcurve.modifiers.remove(noise)


def duplicate(fcurve, selected_keys=True, before='NONE', after='NONE', lock=False):
    """
    Duploicates an fcurve
    """
    action = fcurve.id_data
    index = len(action.fcurves)

    if selected_keys:
        selected_keys = get_selected(fcurve)
    else:
        selected_keys = fcurve.keyframe_points.items()

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)

    dup = action.fcurves.new(data_path=clone_name, index=index, action_group=group_name)
    dup.keyframe_points.add(len(selected_keys))
    dup.color_mode = 'CUSTOM'
    dup.color = (0, 0, 0)

    dup.lock = lock
    dup.select = False

    action.groups[group_name].lock = lock
    action.groups[group_name].color_set = 'THEME10'

    for i, (index, key) in enumerate(selected_keys):
        dup.keyframe_points[i].co = key.co

    add_cycle(dup, before=before, after=after)

    dup.update()

    return dup


def duplicate_from_data(fcurves, global_fcurve, new_data_path, before='NONE', after='NONE', lock=False):
    """
    Duplicates a curve using the global values
    """

    index = len(fcurves)
    every_key = global_fcurve['every_key']
    original_values = global_fcurve['original_values']

    dup = fcurves.new(data_path=new_data_path, index=index, action_group=group_name)
    dup.keyframe_points.add(len(every_key))
    dup.color_mode = 'CUSTOM'
    dup.color = (0, 0, 0)

    dup.lock = lock
    dup.select = False

    action = fcurves.id_data
    action.groups[group_name].lock = lock
    action.groups[group_name].color_set = 'THEME10'

    i = 0

    for index in every_key:
        original_key = original_values[index]
        dup.keyframe_points[i].co.x = original_key['x']
        dup.keyframe_points[i].co.y = original_key['y']

        i += 1

    add_cycle(dup, before=before, after=after)

    dup.update()

    return dup


def s_curve(x, slope=1.0, width=1.0, height=1.0, xshift=0.0, yshift=0.0):
    '''
    Formula for "s" curve
    '''
    return height * ((x - xshift) ** slope / ((x - xshift) ** slope + (width - (x - xshift)) ** slope)) + yshift


def ramp_curve(x, slope=2.0, height=1.0, yshift=0.0, width=1.0, xshift=0.0, invert=False):
    '''
    Formula for ease-in or ease-out curve
    '''
    if invert:
        slope = 1 / slope

    return height * (((1 / width) * (x - xshift)) ** slope) + yshift
    # return height * ((((x-xshift)/width)**slope)+yshift)


def to_linear_curve(left_neighbor, right_neighbor, selected_keys, factor=1):
    '''
    Lineal transition between neighbors
    '''
    local_y = right_neighbor.y - left_neighbor.y
    local_x = right_neighbor.x - left_neighbor.x
    ratio = local_y / local_x
    for k in selected_keys:
        x = k.co.x - left_neighbor.co.x
        average_y = ratio * x + left_neighbor.y
        delta = average_y - k.co.y
        k.co.y = k.co.y + (delta * factor)


def from_clone_to_reference(objects, factor, clone_selected_keys=False):
    """
    Create a copy of the selected fcurve and put it on the "helper_curves" group
    :param objects: ... objects that own the actions to be used
    :param factor: rate of transition, value from -1 to 1
    :param clone_selected_keys: If True use only the selected keys
    """
    animaide = bpy.context.scene.animaide
    adapted_factor = ((factor + 1) / 2)     # take the -1 to 1 range and converts it to a 0 to 1 range

    add_clone(objects, selected_keys=clone_selected_keys)

    for obj in objects:
        action = obj.animation_data.action

        aclone_index = 0
        for fcurve in action.fcurves:

            if not fcurve.select or fcurve.hide:
                continue

            if 'clone' in fcurve.data_path:
                continue    # so it doesn't create a reference out of a clone

            if 'reference' in fcurve.data_path:
                continue    # so it doesn't create a reference out of a reference

            if animaide.reference.fcurve.index > -1:
                print('reference already exist')
                index = animaide.reference.fcurve.index
                reference = action.fcurves[index]   # get the reference already exist
            else:
                reference = refe.add_curve(fcurve, animaide.reference.interpol)     # creates a new reference

            aclone = animaide.clone_data.clones[aclone_index]   # finds the new created animaide clone
            aclone_index += 1

            clone = action.fcurves[aclone.fcurve.index]     # uses the animaide clone index to find the new clone

            selected_keys = key_utils.get_selected(fcurve)

            if not selected_keys:
                index = key_utils.on_current_frame(fcurve)
                key = fcurve.keyframe_points[index]
                selected_keys = [index]     # gets the current key if no key is selected
                if key is None:
                    return

            for n, index in enumerate(selected_keys):
                key = fcurve.keyframe_points[index]
                if clone_selected_keys is True:
                    i = n
                else:
                    i = index
                clone_key = clone.keyframe_points[i]
                # key.co.y = reference.evaluate(key.co.x)
                key_utils.attach_to_fcurve(key, clone_key, reference, adapted_factor, is_gradual=True)
                # target_y = reference.evaluate(key.co.x)
                # diference = target_y - key.co.y
                # key.co.y = key.co.y + diference * ((factor + 1)/2)

            fcurve.update()
            refe.remove(action, reference)
    # remove_clones(objects)


def add_clone(objects, cycle_before='NONE', cycle_after="NONE", selected_keys=False):
    """
    Create an fcurve clone
    """

    for obj in objects:
        fcurves = obj.animation_data.action.fcurves

        for fcurve in fcurves:
            if getattr(fcurve.group, 'name', None) == group_name:
                continue  # we don't want to add to the list the helper curves we have created

            if fcurve.hide or not fcurve.select:
                continue

            duplicate(fcurve, selected_keys=selected_keys, before=cycle_before, after=cycle_after)

            fcurve.update()


def remove_clone(objects):
    """
    Removes an fcurve clone
    """
    for obj in objects:
        action = obj.animation_data.action

        animaide = bpy.context.scene.animaide
        aclones = animaide.clone_data.clones
        clones_n = len(aclones)
        blender_n = len(action.fcurves) - clones_n

        for n in range(clones_n):
            print('regular curves: ', blender_n)
            maybe_clone = action.fcurves[blender_n]     # delete the first of the clones left
            if 'clone' in maybe_clone.data_path:
                clone = maybe_clone
                action.fcurves.remove(clone)
                aclones.remove(0)
        # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


def move_clone(objects):
    """
    moves clone fcurve in time
    """

    for obj in objects:
        action = obj.animation_data.action

        animaide = bpy.context.scene.animaide
        aclone_data = animaide.clone_data
        aclones = aclone_data.clones
        move_factor = aclone_data.move_factor
        for aclone in aclones:
            clone = action.fcurves[aclone.fcurve.index]
            fcurve = action.fcurves[aclone.original_fcurve.index]
            selected_keys = key_utils.get_selected(fcurve)
            key1, key2 = key_utils.first_and_last_selected(fcurve, selected_keys)
            amount = abs(key2.co.x - key1.co.x)
            # index = 0
            for key in clone.keyframe_points:
                # frame = fcurve.keyframe_points[index].co.x
                # key.co.x = frame + int(amount * move_factor)  # moves the clone in the direction or aim
                # key.co.x = frame + amount * move_factor
                key.co.x = key.co.x + (amount * move_factor)

                # index += 1
            clone.update()

            key_utils.attach_selection_to_fcurve(fcurve, clone, is_gradual=False)

            fcurve.update()
