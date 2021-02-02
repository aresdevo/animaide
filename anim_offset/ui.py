
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

        if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
            row.operator("anim.aide_deactivate_magnet", text='Deactivate', depress=True)
        else:
            row.operator("anim.aide_without_magnet_mask", text='Without Mask')

        row.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)

        if context.area.type != 'VIEW_3D':
            mask_in_use = context.scene.animaide.anim_offset.mask_in_use
            if mask_in_use:
                mask_name = 'Modify Mask'
                depress = True
            else:
                mask_name = 'With Mask'
                depress = False

            row = layout.row(align=True)
            row.operator("anim.aide_add_magnet_mask", text=mask_name, depress=depress)
            row.operator("anim.aide_delete_magnet_mask", text='', icon='TRASH')


class ANIMAIDE_PT_anim_offset_3d(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_PT_anim_offset_ge(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_anim_offset_de(Panel, ANIMAIDE_PT):
    bl_idname = 'ANIMAIDE_PT_anim_offset_de'
    bl_space_type = 'DOPESHEET_EDITOR'


classes = (
    ANIMAIDE_PT_anim_offset_3d,
    ANIMAIDE_PT_anim_offset_ge,
    ANIMAIDE_PT_anim_offset_de,
)
