import bpy


def gradual(key_y, target_y, delta=1.0, factor=0.15):
    """Gradualy transition the value of key_y to target_y"""
    print('source: ', key_y)
    print('target: ', target_y)
    print('factor: ', factor)
    step = abs(key_y - target_y) * (delta * factor)
    print('gap: ', key_y - target_y)
    print('step: ', step)

    if target_y > key_y:
        return key_y + step

    else:
        return key_y - step


def clamp(value, minimum, maximum, to_none=False):
    """Take a value and if it goes beyond the minimum and maximum it would replace it with those."""

    if value < minimum:
        if to_none is True:
            return None
        else:
            return minimum

    if value > maximum:
        if to_none is True:
            return None
        else:
            return maximum

    return value


def floor(value, minimum, to_none=False):
    """Take the value and if it goes lower than the minimum it would replace it with it"""
    if value < minimum:
        if to_none is True:
            return None
        else:
            return minimum

    return value


def ceiling(value, maximum, to_none=False):
    """Take the value and if it goes over the maximum it would replace it with it"""
    if value > maximum:
        if to_none is True:
            return None
        else:
            return maximum

    return value


def toggle(to_toggle, value_a, value_b):
    """Change 'to_toggle' to one of the tow values it doesn't have at the moment"""
    if to_toggle == value_a:
        return value_b
    elif to_toggle == value_b:
        return value_a


def add_marker(name, side, frame=0, overwrite=True):
    """add reference frames marker"""

    animaide = bpy.context.scene.animaide
    use_markers = animaide.tool.use_markers

    if not use_markers:
        return

    name = f'{side}{name}'

    markers = bpy.context.scene.timeline_markers
    if overwrite:
        remove_marker(side)
    marker = markers.new(name=name, frame=frame)
    marker['side'] = side
    return marker


def modify_marker(marker, name='SAME', frame='SAME'):
    if name != 'SAME':
        marker.name = name

    if frame != 'SAME':
        marker.frame = frame


def remove_marker(side):
    """Removes reference frame markers"""

    markers = bpy.context.scene.timeline_markers

    for marker in markers:
        if marker.get('side') == side:
            markers.remove(marker)
    return


def switch_aim(aim, factor):
    if factor < 0.5:
        aim = aim * -1
    return aim