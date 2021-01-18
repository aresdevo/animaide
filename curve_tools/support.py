import bpy

# from utils.key import global_values, on_current_frame, get_selected_neigbors, \
#     get_frame_neighbors

from .. import utils


global_values = {}


def scale_tools(self, scale_type):
    """Increase or decrease the value of selected keys acording to the "scale_type"
    L = use left neighboring key as anchor
    R = use right neighboring key as anchor
    Anything else =  use the average point as the anchor"""

    clamped_factor = utils.clamp(self.factor, self.min_value, self.max_value)

    y = 0
    for index in self.selected_keys:
        y = y + self.original_values[index]['y']
    y_average = y / len(self.selected_keys)

    for index in self.selected_keys:
        k = self.fcurve.keyframe_points[index]
        lh_delta = k.co.y - k.handle_left.y
        rh_delta = k.co.y - k.handle_right.y

        if scale_type == 'L':
            delta = self.original_values[index]['y'] - self.left_neighbor['y']
        elif scale_type == 'R':
            delta = self.original_values[index]['y'] - self.right_neighbor['y']
        else:
            delta = self.original_values[index]['y'] - y_average

        k.co.y = self.original_values[index]['y'] + delta * clamped_factor

        utils.key.set_handles(k, lh_delta, rh_delta)


def set_min_max_values(self, context):
    self.animaide = context.scene.animaide
    tool = self.animaide.tool

    if self.op_context == 'EXEC_DEFAULT':
        get_tools_globals(left_frame=tool.left_ref_frame,
                          right_frame=tool.right_ref_frame)

    self.min_value = tool.min_value
    self.max_value = tool.max_value


def valid_obj(context, obj):
    if not valid_anim(obj):
        return False

    visible = obj.visible_get()

    if not visible:
        return False

    if context.area.type != 'VIEW_3D':
        if not context.space_data.dopesheet.show_hidden and not visible:
            return False

    return True


def to_execute(self, context, function, *args):

    set_min_max_values(self, context)

    objects = get_items(context)

    self.noise_steps = 0

    for obj in objects:

        if not valid_obj(context, obj):
            continue

        self.fcurves = obj.animation_data.action.fcurves

        for fcurve_index, self.fcurve in self.fcurves.items():
            if not poll_fcurve(context, obj, self.fcurve):
                continue

            self.noise_steps += 1

            self.global_fcurve = global_values[obj.name][fcurve_index]
            self.selected_keys = self.global_fcurve['selected_keys']

            if not self.selected_keys:
                continue

            self.original_values = self.global_fcurve['original_values']
            self.left_neighbor = self.global_fcurve['left_neighbor']
            self.right_neighbor = self.global_fcurve['right_neighbor']

            function(*args)

            self.fcurve.update()

    return {'FINISHED'}


def update_keyframe_points(context):
    # The select operator(s) are bugged, and can fail to update selected keys, so

    area = context.area.type
    if area != 'GRAPH_EDITOR':
        context.area.type = 'GRAPH_EDITOR'

    snap = context.space_data.auto_snap
    context.space_data.auto_snap = 'NONE'

    bpy.ops.transform.transform()

    context.space_data.auto_snap = snap
    if area != 'GRAPH_EDITOR':
        context.area.type = area


def poll(context):
    """Poll used on all the slider operators"""

    selected = get_items(context, any_mode=True)

    area = context.area.type
    return bool((area == 'GRAPH_EDITOR' or
                area == 'DOPESHEET_EDITOR' or
                area == 'VIEW_3D') and
                selected)


def poll_fcurve(context, obj, fcurve):
    if not valid_fcurve(fcurve):
        return

    if obj.type == 'ARMATURE':

        if getattr(fcurve.group, 'name', None) == 'Object Transforms':
            # When animating an object, by default its fcurves grouped with this name.
            return
        elif not fcurve.group:
            transforms = (
                'location', 'rotation_euler', 'scale',
                'rotation_quaternion', 'rotation_axis_angle',
                '[\"',  # custom property
            )
            if fcurve.data_path.startswith(transforms):
                # fcurve belongs to the  object, so skip it
                return

        # if fcurve.group.name not in bones_names:
            # return

        split_data_path = fcurve.data_path.split(sep='"')
        bone_name = split_data_path[1]
        bone = obj.data.bones.get(bone_name)

        if bone is None or bone.hide:
            return

        if context.area.type == 'VIEW_3D':
            if not bone.select:
                return
        else:
            only_selected = context.space_data.dopesheet.show_only_selected
            if only_selected and not bone.select:
                return

        # if bone_name is None:
            # return

    if getattr(fcurve.group, 'name', None) == utils.curve.group_name:
        return  # we don't want to select keys on reference fcurves

    return True


def get_items(context, any_mode=False):
    """returns objects"""
    if any_mode:
        if context.mode == 'OBJECT':
            selected = context.selected_objects
        elif context.mode == 'POSE':
            selected = context.selected_pose_bones
        else:
            selected = None
    else:
        selected = context.selected_objects

    if context.area.type == 'VIEW_3D':
        return selected
    elif context.space_data.dopesheet.show_only_selected:
        return selected
    else:
        return bpy.data.objects


def reset_original():
    """Set selected keys to the values in the global variables"""

    context = bpy.context

    objects = get_items(context)

    for obj in objects:

        if not valid_anim(obj):
            continue

        visible = obj.visible_get()

        if context.area.type != 'VIEW_3D':
            if not context.space_data.dopesheet.show_hidden and not visible:
                continue

        fcurves = obj.animation_data.action.fcurves

        for fcurve_index, fcurve in fcurves.items():
            if not poll_fcurve(context, obj, fcurve):
                continue

            global_fcurve = global_values[obj.name][fcurve_index]

            selected_keys = global_fcurve['selected_keys']
            original_values = global_fcurve['original_values']

            if not selected_keys:
                index = utils.key.on_current_frame(fcurve)
                if index is None:
                    continue
                selected_keys = [index]

            for index in selected_keys:
                if index is None:
                    continue
                k = fcurve.keyframe_points[index]
                k.co.y = original_values[index]['y']
                k.handle_left.y = original_values[index]['handles']['l']
                k.handle_right.y = original_values[index]['handles']['r']

            fcurve.update()

    return


def get_tools_globals(selected=True, original=True, left_frame=None, right_frame=None):
    """Gets all the global values needed to work with the curve_tools"""

    context = bpy.context
    animaide = context.scene.animaide

    objects = get_items(context)

    for obj in objects:

        if not valid_anim(obj):
            continue

        # Level 1 variables
        # if object.type == 'ARMATURE':
        #     bones = context.selected_pose_bones

        fcurves = obj.animation_data.action.fcurves
        curves = {}

        for fcurve_index, fcurve in fcurves.items():

            if not valid_fcurve(fcurve):
                continue

            # level 2 variables
            curve_items = {}
            keyframes = []
            values = {}
            every_key = []
            left_neighbor = None
            right_neighbor = None

            keys = fcurve.keyframe_points

            for key_index, key in keys.items():

                # stores coordinate of every key
                handles = {'l': key.handle_left.y, 'r': key.handle_right.y}
                co = {'x': key.co.x, 'y': key.co.y}
                values[key_index] = co
                values[key_index]['handles'] = handles

                # stores every key
                every_key.append(key_index)

                if animaide.tool.keys_under_cursor:
                    index = utils.key.on_current_frame(fcurve)
                    if index is not None:
                        keyframes = [index]
                        # left_neighbor, right_neighbor = utils.key.get_frame_neighbors(fcurve, frame=None, clamped=False)
                elif key.select_control_point:
                    # stores only selected keys
                    keyframes.append(key_index)

                    # find smooth values (average) of the original keys

                    # key = fcurve.keyframe_points[key_index]

                    if key_index - 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        prevkey_value = key.co.y
                    else:
                        prevkey_value = fcurve.keyframe_points[key_index - 1].co.y

                    if key_index + 1 not in keyframes:
                        values[key_index]['sy'] = 'book end'
                        nextkey_value = key.co.y
                    else:
                        nextkey_value = fcurve.keyframe_points[key_index + 1].co.y

                    # smooth = (prevkey_value + key.co.y + nextkey_value) / 3
                    smooth = (prevkey_value + nextkey_value) / 2
                    values[key_index]['sy'] = smooth

            if keyframes:
                left_neighbor, right_neighbor = utils.key.get_selected_neigbors(fcurve, keyframes)

            if selected:
                # Store selected keys
                curve_items['selected_keys'] = keyframes

            if left_neighbor is None:
                curve_items['left_neighbor'] = None
            else:
                # stores coordinates of left neighboring key
                co = {'x': left_neighbor.co.x, 'y': left_neighbor.co.y}
                curve_items['left_neighbor'] = co

            if right_neighbor is None:
                curve_items['right_neighbor'] = None
            else:
                # stores coordinates of right neighboring key
                co = {'x': right_neighbor.co.x, 'y': right_neighbor.co.y}
                curve_items['right_neighbor'] = co

            if original:
                # stores original values of every key
                curve_items['original_values'] = values
                curve_items['every_key'] = every_key

            if left_frame is not None or right_frame is not None:
                frames = {'left_y': fcurve.evaluate(left_frame),
                          'right_y': fcurve.evaluate(right_frame)}

                curve_items['ref_frames'] = frames

            curves[fcurve_index] = curve_items

        global_values[obj.name] = curves

    return


def get_ref_frame_globals(left_ref_frame, right_ref_frame):
    """Get global values for the reference frames"""

    objects = bpy.context.selected_objects

    for obj in objects:
        anim = obj.animation_data
        if anim is None:
            continue
        if anim.action.fcurves is None:
            continue
        fcurves = obj.animation_data.action.fcurves

        curves = {}
        ref_frames = {}

        for fcurve_index, fcurve in fcurves.items():
            frames = {}

            if fcurve.select is False:
                continue

            if fcurve.lock is True:
                continue

            if fcurve.hide is True:
                continue

            frames['left_y'] = fcurve.evaluate(left_ref_frame)
            frames['right_y'] = fcurve.evaluate(right_ref_frame)

            curves[fcurve_index]['ref_frames'] = frames

        if curves != {}:
            global_values[obj.name] = curves


def valid_anim(obj):
    """checks if the obj has an active action"""

    anim = obj.animation_data
    action = getattr(anim, 'action', None)
    fcurves = getattr(action, 'fcurves', None)

    return bool(fcurves)


def valid_fcurve(fcurve):
    """Validates an fcurve to see if it can be used with animaide"""

    animaide = bpy.context.scene.animaide
    if animaide.tool.unselected_fcurves is False:
        if fcurve.select is False:
            return False

    if fcurve.lock or fcurve.hide:
        return False
    elif getattr(fcurve.group, 'name', None) == utils.curve.group_name:
        return False  # we don't want to select keys on reference fcurves
    else:
        return True


def set_ref_marker(context):
    tool = context.scene.animaide.tool
    if tool.use_markers:
        markers = context.scene.timeline_markers
        left = 0
        right = 0
        for marker in markers:
            if marker.get('side') == 'L':
                left = marker.frame
            elif marker.get('side') == 'R':
                right = marker.frame
    else:
        left = tool.left_ref_frame
        right = tool.right_ref_frame

    return left, right
