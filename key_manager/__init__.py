import bpy
from . import props, ops, ui
classes = props.classes + ops.classes + ui.panel_classes # + ui.header_classes

# if bpy.context.scene.animaide.key_tweak.panel_pref == 'PANEL':
#     classes = \
#         props.classes + \
#         ops.classes + \
#         ui.panel_classes
# else:
#     classes = \
#         props.classes + \
#         ops.classes + \
#         ui.header_classes

