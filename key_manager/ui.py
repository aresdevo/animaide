from . import support
from .. import utils
from bpy.types import Panel, Menu, UIList, WorkSpaceTool


class ANIMAIDE_PT_key_manager:
    bl_label = "Key Manager"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        animaide = context.scene.animaide
        tool = animaide.tool

        layout.operator('anim.aide_add_bookmark', text='', emboss=True, icon='ADD')


class ANIMAIDE_PT_frame_bookmarks_ge(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_frame_bookmarks_de(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_PT_frame_bookmarks_3d(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_3d'
    bl_space_type = 'VIEW_3D'


classes = (
    ANIMAIDE_PT_frame_bookmarks_ge,
    ANIMAIDE_PT_frame_bookmarks_de,
    ANIMAIDE_PT_frame_bookmarks_3d,
)
