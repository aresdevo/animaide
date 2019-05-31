import bpy


from . import cur_utils


user_preview_range = {}
user_scene_range = {}


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

    if action.fcurves.items() == []:
        return

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

    if fcurve.group.name == cur_utils.group_name:
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


def poll(context):
    obj = context.object
    anim = obj.animation_data
    # space = context.area.spaces.active.type
    area = context.area.type
    # return obj is not None and area == 'GRAPH_EDITOR' and anim is not None
    return obj is not None and anim is not None

