import bpy

from . import key_utils, cur_utils


group_name = 'helper_curves'


def animation_transfrom(objects):
    cur_frame = bpy.context.scene.frame_current

    for obj in objects:
        action = obj.animation_data.action
        fcurve_name = None
        index = 0
        for fcurve in action.fcurves:
            if fcurve_name != fcurve.data_path:
                fcurve_name = fcurve.data_path
                index = 0
            else:
                index += 1

            obj_atrib = getattr(obj, fcurve_name)

            fcurve_value = fcurve.evaluate(cur_frame)
            obj_value = obj_atrib[index]
            delta = obj_value - fcurve_value
            print('-----')
            print('index:', index)
            print('fcurve name:', fcurve_name)
            print('fcurve value:', fcurve_value)
            print('object atribute:', obj_atrib)
            print('object value:', obj_value)
            print('delta:', delta)

            for key in fcurve.keyframe_points:
                key.co.y = key.co.y + delta

            fcurve.update()


def animation_transfrom_proportional(objects, falloff='SMOOTH', size=40):
    cur_frame = bpy.context.scene.frame_current

    for obj in objects:
        action = obj.animation_data.action
        fcurve_name = None
        index = 0
        for fcurve in action.fcurves:
            # cur_index, cur_key = keyutils.on_current_frame(fcurve)
            #
            # if cur_key is None:
            #     left_neighbor, right_neighbor = keyutils.get_frame_neighbors(fcurve, cur_frame)
            #     delta_left = abs(cur_frame - left_neighbor)
            #     delta_right = abs(cur_frame - right_neighbor)
            #     if delta_left < delta_right:
            #         cur_key = left_neighbor
            #     else:
            #         cur_key = right_neighbor

            if fcurve_name != fcurve.data_path:
                fcurve_name = fcurve.data_path
                index = 0
            else:
                index += 1

            obj_atrib = getattr(obj, fcurve_name)

            fcurve_value = fcurve.evaluate(cur_frame)
            obj_value = obj_atrib[index]
            delta = obj_value - fcurve_value
            print('-----')
            print('index:', index)
            print('fcurve name:', fcurve_name)
            print('fcurve value:', fcurve_value)
            print('object atribute:', obj_atrib)
            print('object value:', obj_value)
            print('delta:', delta)

            # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            if delta != 0:
                bpy.ops.transform.translate(value=(0, delta, 0),
                                            constraint_axis=(False, True, False),
                                            proportional='ENABLED',
                                            proportional_edit_falloff=falloff,
                                            proportional_size=size)

            # fcurve.update()


def add_samples(fcurve, reference_fcurve, frequency=1):
        """

        :param fcurve:
        :param reference_fcurve:
        :param frequency:
        :return:
        """
        key_list = fcurve.keyframe_points

        selected_keys = key_utils.get_selected(fcurve)
        first_key, last_key = key_utils.first_and_last_selected(fcurve, selected_keys)

        amount = int(abs(last_key.co.x - first_key.co.x) / frequency)
        frame = first_key.co.x

        for n in range(amount):
            target = reference_fcurve.evaluate(frame)
            key_list.insert(frame, target)
            frame += frequency

        target = reference_fcurve.evaluate(last_key.co.x)
        key_list.insert(last_key.co.x, target)


def get_selected(fcurves):
    """
    return selected fcurves in the current action with the exception of the reference fcurves
    :param fcurves:
    :return:
    """
    selected = []

    for fcurve in fcurves:
        if fcurve.group.name == group_name:
            continue        # we don't want to add to the list the helper curves we have created

        if fcurve.select:
            selected.append(fcurve)

    print('selected fcurves: ', selected)

    return selected


def find(fcurves, data_path, index=0):
    """

    :param fcurves:
    :param data_path:
    :param index:
    :return:
    """

    for fcurve in fcurves:

        if fcurve.data_path != data_path:
            continue

        if fcurve.index_array != index:
            continue

        return fcurve


def update(fcurves):
    """

    :param fcurves:
    :return:
    """
    for fcurve in fcurves:
        fcurve.update()


def remove_helpers(objects):
    """
    Remove the all the helper curves that have been aded to an object action
    :param objects: object than owns the action to be afected.
    """
    for obj in objects:
        action = obj.animation_data.action

        animsliders = bpy.context.scene.animsliders
        aclones = animsliders.clone_data.clones
        # arefe = animsliders.reference
        # arefe.fcurve.data_path = ''
        # arefe.fcurve.index = -1

        for fcurve in action.fcurves:     # delete the first of the clones left
            if fcurve.group.name == group_name:
                action.fcurves.remove(fcurve)
                aclones.remove(0)


def get_slope(fcurve):
    """

    :param fcurve:
    :return:
    """
    selected_keys = key_utils.get_selected(fcurve)
    first_key, last_key = key_utils.first_and_last_selected(fcurve, selected_keys)
    slope = (first_key.co.y**2 - last_key.co.y**2) / (first_key.co.x**2 - last_key.co.x**2)
    return slope


def add_cycle(fcurve, before='MIRROR', after='MIRROR'):
    """

    :param fcurve:
    :param before:
    :param after:
    :return:
    """
    cycle = fcurve.modifiers.new('CYCLES')

    cycle.mode_before = before
    cycle.mode_after = after


def add_noise(fcurve):
    """

    :param fcurve:
    :return:
    """
    noise = fcurve.modifiers.new('NOISE')

    noise.strength = 5
    noise.scale = 3
    # fcurve.convert_to_samples(0, 100)
    # fcurve.convert_to_keyframes(0, 100)
    # fcurve.modifiers.remove(noise)


def duplicate(fcurve, new_data_path, selected_keys=True, lock=False):
    """

    :param fcurve:
    :param new_data_path:
    :param selected_keys:
    :param lock:
    :return:
    """
    action = fcurve.id_data
    index = len(action.fcurves)

    if selected_keys:
        selected_keys = get_selected(fcurve)
    else:
        selected_keys = fcurve.keyframe_points.items()

    dup = action.fcurves.new(data_path=new_data_path, index=index, action_group=group_name)
    dup.keyframe_points.add(len(selected_keys))
    dup.color_mode = 'CUSTOM'
    dup.color = (0, 0, 0)

    dup.lock = lock
    action.groups[group_name].lock = lock
    action.groups[group_name].color_set = 'THEME10'

    i = 0

    for index, key in selected_keys:
        dup.keyframe_points[i].co = key.co

        i += 1

    dup.update()

    return dup


def s_curve(x, slope=1.0, width=1.0, height=1.0, xshift=0.0, yshift=0.0):
    return height*((x-xshift)**slope/((x-xshift)**slope+(width-(x-xshift))**slope))+yshift


def ramp_curve(x, slope=2.0, height=1.0, yshift=0.0, width=1.0, xshift=0.0, invert=False):
    if invert:
        slope = 1 / slope

    return height * (((1 / width) * (x - xshift)) ** slope) + yshift
    # return height * ((((x-xshift)/width)**slope)+yshift)


def to_linear_curve(selected_keys, factor=1):
    for k in selected_keys:
        average_y = key_utils.linear_y(k)
        delta = average_y - k.co.y
        k.co.y = k.co.y + (delta * factor)


def to_linear_curve_b(left_neighbor, right_neighbor, selected_keys, factor=1):
    local_y = right_neighbor.y - left_neighbor.y
    local_x = right_neighbor.x - left_neighbor.x
    ratio = local_y / local_x
    for k in selected_keys:
        x = k.co.x - left_neighbor.co.x
        average_y = ratio * x + left_neighbor.y
        delta = average_y - k.co.y
        k.co.y = k.co.y + (delta * factor)


def blend(obj, fcurve, slope, factor, source, target, inout='OUT'):
    if inout is not 'IN' or inout is not 'OUT':
        return

    selected_keys = key_utils.selected_keys_global[obj.name][fcurve.array_index]
    original_keys = key_utils.original_keys_info[obj.name][fcurve.array_index]

    if not selected_keys:
        index = key_utils.on_current_frame(fcurve)
        key = fcurve.keyframe_points[index]
        selected_keys = [index]  # gets the current key if no key is selected
        if key is None:
            return

    left_neighbor, right_neighbor = key_utils.get_selected_neigbors(fcurve, selected_keys)
    local_y = right_neighbor.co.y - left_neighbor.co.y
    local_x = right_neighbor.co.x - left_neighbor.co.x

    slope = 1 + ((slope * 2) * abs(factor))

    if inout == 'OUT':
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
        average_y = key_utils.linear_y(left_neighbor, right_neighbor, k)
        delta = original_keys[index]['y'] - average_y
        x = k.co.x - left_neighbor.co.x
        key_ratio = 1 / (local_x / x)

        ease_y = s_curve(key_ratio,
                         slope=slope,
                         width=width,
                         height=height,
                         xshift=xshift,
                         yshift=yshift)

        if factor < 0:
            # delta = right_neighbor.co.y - original_keys[index]['y']
            delta = local_y * ease_y.real - original_keys[index]['y']
        else:
            # delta = original_keys[index]['y'] - left_neighbor.co.y
            delta = original_keys[index]['y'] - local_y * ease_y.real

        # ease_y_b = curveutils.s_curve(clamped_factor, slope=slope, width=2, height=2, xshift=-1, yshift=-1)

        # k.co.y = original_keys[index]['y'] + delta * clamped_factor

        k.co.y = left_neighbor.co.y + local_y * ease_y.real


def from_clone_to_reference(objects, factor, clone_selected_keys=False):
    """
    Create a copy of the selected fcurve and put it on the "helper_curves" group
    :param objects: ... objects that own the actions to be used
    :param factor: rate of transition, value from -1 to 1
    :param clone_selected_keys: If True use only the selected keys
    """
    animsliders = bpy.context.scene.animsliders
    adapted_factor = ((factor + 1) / 2)     # take the -1 to 1 range and converts it to a 0 to 1 range

    create_clone(objects, selected_keys=clone_selected_keys)

    for obj in objects:
        action = obj.animation_data.action

        aclone_index = 0
        for fcurve in action.fcurves:

            if fcurve.select is False:
                continue

            if fcurve.hide:
                continue

            if 'clone' in fcurve.data_path:
                continue    # so it doesn't create a reference out of a clone

            if 'reference' in fcurve.data_path:
                continue    # so it doesn't create a reference out of a reference

            if animsliders.reference.fcurve.index > -1:
                print('reference already exist')
                index = animsliders.reference.fcurve.index
                reference = action.fcurves[index]   # get the reference already exist
            else:
                reference = refe.add_curve(fcurve, animsliders.reference.interpol)     # creates a new reference

            aclone = animsliders.clone_data.clones[aclone_index]   # finds the new created animsliders clone
            aclone_index += 1

            clone = action.fcurves[aclone.fcurve.index]     # uses the animsliders clone index to find the new clone

            selected_keys = key_utils.get_selected(fcurve)

            if not selected_keys:
                index = key_utils.on_current_frame(fcurve)
                key = fcurve.keyframe_points[index]
                selected_keys = [index]     # gets the current key if no key is selected
                if key is None:
                    return

            n = 0
            for index in selected_keys:
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
                n += 1

            fcurve.update()
            refe.remove(action, reference)
    # remove_clones(objects)


def create_clone(objects,
                 cycle_before='NONE',
                 cycle_after="NONE",
                 selected_keys=False):
    """

    :param objects:
    :param cycle_before:
    :param cycle_after:
    :param selected_keys:
    :return:
    """

    for obj in objects:
        fcurves = obj.animation_data.action.fcurves

        animsliders = bpy.context.scene.animsliders
        aclones = animsliders.clone_data.clones
        clones = []
        print('amount of curves: ', len(fcurves))

        for fcurve_index, fcurve in fcurves.items():
            if fcurve.group.name == group_name:
                continue  # we don't want to add to the list the helper curves we have created

            clone = None

            for aclone in aclones:
                if aclone.original_fcurve.index == fcurve_index:
                    clone = fcurves[aclone.fcurve.index]
                    cycle = clone.modifiers[0]
                    cycle.mode_before = cycle_before
                    cycle.mode_after = cycle_after

            if fcurve.hide is True:
                continue

            if fcurve.select is False:
                continue

            if clone is None:
                clone = add_clone_curve(fcurve,
                                        cycle_before,
                                        cycle_after,
                                        selected_keys=selected_keys)
                clones.append(clone)
                print('clone:', clone.data_path)

            fcurve.update()

        return clones


def add_clone_curve(fcurve, before='NONE', after='NONE', selected_keys=False):
    """

    :param fcurve:
    :param before:
    :param after:
    :param selected_keys:
    :return:
    """
    animsliders = bpy.context.scene.animsliders

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)
    clone = cur_utils.duplicate(fcurve, clone_name, selected_keys=selected_keys)
    aclone = animsliders.clone_data.clones.add()
    aclone.fcurve.data_path = clone.data_path
    aclone.fcurve.index = clone.array_index
    aclone.original_fcurve.data_path = fcurve.data_path
    aclone.original_fcurve.index = fcurve.array_index

    cur_utils.add_cycle(clone, before=before, after=after)

    clone.lock = True
    clone.select = False
    clone.update()
    return clone


def remove_clone(objects):
    """

    :param objects:
    :return:
    """
    for obj in objects:
        action = obj.animation_data.action

        animsliders = bpy.context.scene.animsliders
        aclones = animsliders.clone_data.clones
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

    :param objects:
    :return:
    """

    for obj in objects:
        action = obj.animation_data.action

        animsliders = bpy.context.scene.animsliders
        aclone_data = animsliders.clone_data
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