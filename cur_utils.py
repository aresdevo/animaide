import bpy

from . import key_utils, utils


group_name = 'animaide'

user_preview_range = {}
user_scene_range = {}


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

        # animaide = bpy.context.scene.animaide
        # aclones = animaide.clone_data.clones
        # arefe = animaide.reference
        # arefe.fcurve.data_path = ''
        # arefe.fcurve.index = -1

        for fcurve in action.fcurves:     # delete the first of the clones left
            if fcurve.group.name == group_name:
                action.fcurves.remove(fcurve)
                # aclones.remove(0)


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


def add_noise(fcurve, strength=0.4, scale=1, phase=0):
    """

    :param fcurve:
    :return:
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

    clone_name = '%s.%d.clone' % (fcurve.data_path, fcurve.array_index)

    dup = action.fcurves.new(data_path=clone_name, index=index, action_group=group_name)
    dup.keyframe_points.add(len(selected_keys))
    dup.color_mode = 'CUSTOM'
    dup.color = (0, 0, 0)

    dup.lock = lock
    dup.select = False

    action.groups[group_name].lock = lock
    action.groups[group_name].color_set = 'THEME10'

    i = 0

    for index, key in selected_keys:
        dup.keyframe_points[i].co = key.co

        i += 1

    add_cycle(dup, before=before, after=after)

    dup.update()

    return dup


def duplicate_from_data(fcurves, global_fcurve, new_data_path, before='NONE', after='NONE', lock=False):
    """

    :param fcurve:
    :param new_data_path:
    :param selected_keys:
    :param lock:
    :return:
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
    animaide = bpy.context.scene.animaide
    adapted_factor = ((factor + 1) / 2)     # take the -1 to 1 range and converts it to a 0 to 1 range

    add_clone(objects, selected_keys=clone_selected_keys)

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


def anim_transform_handlers(dummy):

    context = bpy.context

    context.scene.tool_settings.use_keyframe_insert_auto = False

    selected_objects = context.selected_objects

    for obj in selected_objects:

        # obj = context.object
        obj_anim = obj.animation_data

        if obj_anim is None:
            return

        if obj_anim.action.fcurves is None:
            return

        fcurves = obj_anim.action.fcurves

        for fcurve in fcurves:

            # if fcurve.lock:
            #     continue
            #
            # if fcurve.group.name == group_name:
            #     continue  # we don't want to select keys on reference fcurves

            animation_transform(obj, fcurve)

    return


def anim_trans_mask_handlers(dummy):

    action = bpy.data.actions['animaide']

    if action is None:
        return
    if action.fcurves.items() != []:
        mask = action.fcurves[0]

    modify_anim_trans_mask(mask, mask.keyframe_points)

    return


def animation_transform(obj, fcurve):
    """

    :param objects:
    :param interpolation:
    :param go_to:
    :return:
    """

    mask = None

    if fcurve.lock is True:
        return

    if fcurve.group.name == group_name:
        return  # we don't want to select keys on reference fcurves

    if 'animaide' in bpy.data.actions:

        action = bpy.data.actions['animaide']

        if action.fcurves.items() != []:
            mask = action.fcurves[0]

    delta_y = get_anim_transform_delta(obj, fcurve)

    for k in fcurve.keyframe_points:

        if mask is None:
            factor = 1
        else:
            factor = mask.evaluate(k.co.x)

        k.co.y = k.co.y + (delta_y * factor)

    fcurve.update()

    return


def get_anim_transform_delta(obj, fcurve):
    cur_frame = bpy.context.scene.frame_current

    source = fcurve.evaluate(cur_frame)

    prop = obj.path_resolve(fcurve.data_path)

    target = prop[fcurve.array_index]

    return target - source


def remove_anim_trans_mask():
    scene = bpy.context.scene
    animaide = scene.animaide

    if animaide.anim_transform.use_mask is False:
        return

    if 'animaide' not in bpy.data.actions.keys():
        return

    fcurves = bpy.data.actions['animaide'].fcurves

    fcurves.remove(fcurves[0])

    animaide.anim_transform.use_mask = False

    reset_timeline_ranges()


def set_animaide_action():

    if 'animaide' not in bpy.data.actions:
        action = bpy.data.actions.new('animaide')
    else:
        action = bpy.data.actions['animaide']

    return action


def add_animaide_fcurve(action_group, color=(1, 1, 1)):
    action = bpy.data.actions['animaide']

    fcurve = action.fcurves.new(data_path='animaide', index=0, action_group=action_group)
    fcurve.color_mode = 'CUSTOM'
    fcurve.color = color

    return fcurve


def set_timeline_ranges(blend_l, margin_l, margin_r, blend_r):
    scene = bpy.context.scene
    scene.use_preview_range = True

    scene.frame_preview_start = blend_l
    scene.frame_start = margin_l
    scene.frame_end = margin_r
    scene.frame_preview_end = blend_r


def reset_timeline_ranges():
    scene = bpy.context.scene

    scene.frame_preview_start = user_preview_range['start']
    scene.frame_preview_end = user_preview_range['end']
    scene.use_preview_range = user_preview_range['use']
    scene.frame_start = user_scene_range['start']
    scene.frame_end = user_scene_range['end']


def store_user_timeline_ranges():
    scene = bpy.context.scene

    user_preview_range['start'] = scene.frame_preview_start
    user_preview_range['end'] = scene.frame_preview_end
    user_preview_range['use'] = scene.use_preview_range
    user_scene_range['start'] = scene.frame_start
    user_scene_range['end'] = scene.frame_end


def add_anim_trans_mask():
    """

    :param fcurve:
    :param interpolation:
    :return:
    """
    store_user_timeline_ranges()

    animaide = bpy.context.scene.animaide

    action = set_animaide_action()

    if action.fcurves.items() == []:
        mask = add_animaide_fcurve(action_group='Magnet')
        keys = mask.keyframe_points
        keys.add(4)
    else:
        action = bpy.data.actions['animaide']
        mask = action.fcurves[0]
        keys = mask.keyframe_points

    modify_anim_trans_mask(mask, keys)

    animaide.anim_transform.use_mask = True

    mask.update()

    return mask


def modify_anim_trans_mask(mask, keys):

    animaide = bpy.context.scene.animaide

    mask_margin_l = animaide.anim_transform.mask_margin_l
    mask_blend_l = animaide.anim_transform.mask_blend_l
    mask_margin_r = animaide.anim_transform.mask_margin_r
    mask_blend_r = animaide.anim_transform.mask_blend_r
    interp = animaide.anim_transform.interp
    easing = animaide.anim_transform.easing

    always_l = mask_margin_l
    always_r = mask_margin_r

    if mask_margin_l > mask_margin_r:
        always_l = mask_margin_r
        always_r = mask_margin_l

    if mask_blend_l > 0:
        mask_blend_l = 0

    if mask_blend_r < 0:
        mask_blend_r = 0

    keys[0].co.x = always_l + mask_blend_l
    keys[0].co.y = 0
    keys[1].co.x = always_l
    keys[1].co.y = 1
    keys[2].co.x = always_r
    keys[2].co.y = 1
    keys[3].co.x = always_r + mask_blend_r
    keys[3].co.y = 0

    set_timeline_ranges(blend_l=keys[0].co.x,
                        margin_l=keys[1].co.x,
                        margin_r=keys[2].co.x,
                        blend_r=keys[3].co.x)

    easing_b = easing

    if easing == 'EASE_IN':
        easing_b = 'EASE_OUT'

    if easing == 'EASE_OUT':
        easing_b = 'EASE_IN'

    keys[0].interpolation = interp
    keys[0].easing = easing
    keys[1].interpolation = 'LINEAR'
    keys[1].easing = 'EASE_IN_OUT'
    keys[2].interpolation = interp
    keys[2].easing = easing_b

    mask.lock = True
    mask.select = True




def add_clone(objects, cycle_before='NONE', cycle_after="NONE", selected_keys=False):
    """

    :param objects:
    :param cycle_before:
    :param cycle_after:
    :param selected_keys:
    :return:
    """

    for obj in objects:
        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if fcurve.group.name == group_name:
                continue  # we don't want to add to the list the helper curves we have created

            if fcurve.hide is True:
                continue

            if fcurve.select is False:
                continue

            duplicate(fcurve, selected_keys=selected_keys, before=cycle_before, after=cycle_after)

            fcurve.update()


def remove_clone(objects):
    """

    :param objects:
    :return:
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

    :param objects:
    :return:
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