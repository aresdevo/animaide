import bpy
from .. import utils

# from . import key

group_name = 'animaide'
user_preview_range = {}
user_scene_range = {}


def add_curve3d(context, name, key_amount=0):
    curve_data = bpy.data.curves.new(name, 'CURVE')
    spline = curve_data.splines.new('BEZIER')
    if key_amount > 0:
        spline.bezier_points.add(key_amount)
    obj = bpy.data.objects.new(name, curve_data)
    context.collection.objects.link(obj)
    return obj


def create_path(context, fcurves):
    curve_obj = add_curve3d(context, "animaide_path")
    curve_obj.data.dimensions = '3D'
    curve_obj.data.bevel_depth = 0.1

    x = {}
    y = {}
    z = {}
    frames = []
    for fcurve in fcurves:
        if fcurve.data_path == 'location':
            for k in fcurve.keyframe_points:
                f = k.co.x
                if f not in frames:
                    frames.append(f)
                if fcurve.array_index == 0:
                    x['curve'] = fcurve
                    x[f] = k.co.y
                elif fcurve.array_index == 1:
                    y['curve'] = fcurve
                    y[f] = k.co.y
                elif fcurve.array_index == 2:
                    z['curve'] = fcurve
                    z[f] = k.co.y
    frames.sort()
    print(f'frames: {frames}')
    print(f'x: {x}')
    print(f'y: {y}')
    print(f'z: {z}')
    points = curve_obj.data.splines[0].bezier_points
    points.add(len(frames))
    print(f'amount of frames: {len(frames)}')
    n = 0
    for f in frames:
        if x.get(f) is None:
            points[n].co.x = x['curve'].evaluate(f)
        else:
            points[n].co.x = x.get(f)

        if y.get(f) is None:
            points[n].co.y = y['curve'].evaluate(f)
        else:
            points[n].co.y = y.get(f)

        if x.get(f) is None:
            points[n].co.z = z['curve'].evaluate(f)
        else:
            points[n].co.z = z.get(f)

        points[n].handle_left_type = 'AUTO'
        points[n].handle_right_type = 'AUTO'

        print(f'frame: {f}')
        print(f'point coordinate: {points[n].co}')
        print(f'n: {n}')

        n += 1


def get_selected(fcurves):
    """return selected fcurves in the current action with the exception of the reference fcurves"""

    selected = []

    for fcurve in fcurves:
        if getattr(fcurve.group, 'name', None) == group_name:
            continue        # we don't want to add to the list the helper curves we have created

        if fcurve.select:
            selected.append(fcurve)

    return selected


def remove_helpers(objects):
    """Remove the all the helper curves that have been added to an object action"""

    for obj in objects:
        action = obj.animation_data.action

        for fcurve in action.fcurves:     # delete the first of the clones left
            if getattr(fcurve.group, 'name', None) == group_name:
                action.fcurves.remove(fcurve)


def get_slope(fcurve):
    """Gets the slope of a curve at a specific range"""
    selected_keys = utils.key.get_selected(fcurve)
    first_key, last_key = utils.key.first_and_last_selected(fcurve, selected_keys)
    slope = (first_key.co.y**2 - last_key.co.y**2) / (first_key.co.x**2 - last_key.co.x**2)
    return slope


def add_cycle(fcurve, before='MIRROR', after='MIRROR'):
    """Adds cycle modifier to an fcurve"""
    cycle = fcurve.modifiers.new('CYCLES')

    cycle.mode_before = before
    cycle.mode_after = after


def duplicate(fcurve, selected_keys=True, before='NONE', after='NONE', lock=False):
    """Duploicates an fcurve"""

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
    """Duplicates a curve using the global values"""

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


def add_clone(objects, cycle_before='NONE', cycle_after="NONE", selected_keys=False):
    """Create an fcurve clone"""

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
    """Removes an fcurve clone"""

    for obj in objects:
        action = obj.animation_data.action

        animaide = bpy.context.scene.animaide
        aclones = animaide.clone_data.clones
        clones_n = len(aclones)
        blender_n = len(action.fcurves) - clones_n

        for n in range(clones_n):
            maybe_clone = action.fcurves[blender_n]     # delete the first of the clones left
            if 'clone' in maybe_clone.data_path:
                clone = maybe_clone
                action.fcurves.remove(clone)
                aclones.remove(0)


def move_clone(objects):
    """Moves clone fcurve in time"""

    for obj in objects:
        action = obj.animation_data.action

        animaide = bpy.context.scene.animaide
        aclone_data = animaide.clone_data
        aclones = aclone_data.clones
        move_factor = aclone_data.move_factor
        for aclone in aclones:
            clone = action.fcurves[aclone.fcurve.index]
            fcurve = action.fcurves[aclone.original_fcurve.index]
            selected_keys = utils.key.get_selected(fcurve)
            key1, key2 = utils.key.first_and_last_selected(fcurve, selected_keys)
            amount = abs(key2.co.x - key1.co.x)
            for key in clone.keyframe_points:
                key.co.x = key.co.x + (amount * move_factor)

            clone.update()

            utils.key.attach_selection_to_fcurve(fcurve, clone, is_gradual=False)

            fcurve.update()
