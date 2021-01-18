
import bpy
from . import support
# from .utils import key
from bpy.types import Panel, Menu


class ANIMAIDE_PT:
    bl_label = "Anim Offset"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        layout = self.layout

        row = layout.row(align=True)

        in_use = context.scene.animaide.anim_offset.in_use
        if in_use:
            name = 'Modify Mask'
        else:
            name = 'Add Mask'
        row.operator("anim.aide_add_magnet_mask", text=name)
        row.operator("anim.aide_delete_magnet_mask", text='', icon='TRASH')
        row.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)


class ANIMAIDE_PT_anim_offset_ge(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_anim_offset_de(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_de'
    bl_space_type = 'DOPESHEET_EDITOR'


classes = (
    ANIMAIDE_PT_anim_offset_ge,
    ANIMAIDE_PT_anim_offset_de,
)
