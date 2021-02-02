from . import support
from .. import utils
import bpy
from bpy.types import Panel, Menu, UIList, WorkSpaceTool


def key_type_row(layout, name, key_type, icon):
    row = layout.row(align=True)
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='CHECKMARK')
    op.type = key_type
    op.selection = True
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='X')
    op.type = key_type
    op.selection = False
    op = row.operator('anim.aide_set_key_type', text=name, emboss=True, icon=icon)
    op.type = key_type
    op = row.operator('anim.aide_delete_key_type', text='', emboss=True, icon='TRASH')
    op.type = key_type


def handles_select_row(layout, name, icon='NONE', left=False, right=False, point=False, depress=False):
    op = layout.operator('anim.aide_select_key_parts', text=name, emboss=True, icon=icon, depress=depress)
    op.left = left
    op.right = right
    op.point = point


def handles_type_row(layout, icon='NONE', handle_type='NONE'):
    op = layout.operator('anim.aide_set_handles_type', text='', emboss=True, icon=icon)
    op.act_on = 'SELECTION'
    op.handle_type = handle_type


class ANIMAIDE_PT_key_manager:
    bl_label = "Key Manager"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        key_tweak = context.scene.animaide.key_tweak

        layout = self.layout
        row = layout.row(align=True)

        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_LEFT')
        op.direction = 'LEFT'
        op.amount = key_tweak.frame_change
        row.prop(key_tweak, 'frame_change', text='', slider=False)
        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_RIGHT')
        op.direction = 'RIGHT'
        op.amount = key_tweak.frame_change
        row.separator()
        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_UP')
        op.direction = 'UP'
        op.amount = key_tweak.value_change
        row.prop(key_tweak, 'value_change', text='', slider=False)
        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_DOWN')
        op.direction = 'DOWN'
        op.amount = key_tweak.value_change

        layout = self.layout

        layout.label(text='Key type:')

        key_type_row(layout, 'Keyframe', 'KEYFRAME', 'KEYTYPE_KEYFRAME_VEC')
        key_type_row(layout, 'Breakdown', 'BREAKDOWN', 'KEYTYPE_BREAKDOWN_VEC')
        key_type_row(layout, 'Jitter', 'JITTER', 'KEYTYPE_JITTER_VEC')
        key_type_row(layout, 'Extreme', 'EXTREME', 'KEYTYPE_EXTREME_VEC')

        layout.label(text='Key Interpolation:')
        layout.prop(key_tweak, 'interp', text='')

        if key_tweak.interp == 'BEZIER':

            subrow = layout.row(align=True)

            handles_type_row(subrow, icon='HANDLE_FREE', handle_type='FREE')
            subrow.prop_menu_enum(key_tweak, 'free_act_on', text='', icon='DOWNARROW_HLT')

            handles_type_row(subrow, icon='HANDLE_ALIGNED', handle_type='ALIGNED')
            subrow.prop_menu_enum(key_tweak, 'aligned_act_on', text='', icon='DOWNARROW_HLT')

            handles_type_row(subrow, icon='HANDLE_VECTOR', handle_type='VECTOR')
            subrow.prop_menu_enum(key_tweak, 'vector_act_on', text='', icon='DOWNARROW_HLT')

            handles_type_row(subrow, icon='HANDLE_AUTO', handle_type='AUTO')
            subrow.prop_menu_enum(key_tweak, 'auto_act_on', text='', icon='DOWNARROW_HLT')

            handles_type_row(subrow, icon='HANDLE_AUTOCLAMPED', handle_type='AUTO_CLAMPED')
            subrow.prop_menu_enum(key_tweak, 'auto_clamped_act_on', text='', icon='DOWNARROW_HLT')

            # layout.label(text='Handles selection:')

            subrow = layout.row(align=True)

            if key_tweak.left:
                depress = True
            else:
                depress = False
            handles_select_row(subrow, 'Left', left=True, depress=depress)

            if key_tweak.point:
                handles_select_row(subrow, '', icon='DECORATE_KEYFRAME', point=True, depress=True)
            else:
                handles_select_row(subrow, '', icon='DECORATE_KEYFRAME', point=False, depress=False)

            if key_tweak.right:
                depress = True
            else:
                depress = False
            handles_select_row(subrow, 'Right', right=True, depress=depress)

        elif key_tweak.interp == 'EASE':

            col = layout.column(align=True)
            subrow = col.row(align=True)
            subrow.prop(key_tweak, 'strength', text='', icon_only=False)
            subrow.prop(key_tweak, 'easing', text='', expand=True)

            # col.prop(key_tweak, 'easing', text='')
            # subrow = col.row(align=True)
            # subrow.prop(key_tweak, 'strength', text='', icon_only=True, expand=True)
            # layout.prop_tabs_enum(key_tweak, 'easing')


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
