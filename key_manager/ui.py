from . import support
from .. import utils
import bpy
from bpy.types import Panel, Menu, UIList, WorkSpaceTool


def key_type_row(layout, name, key_type, icon):
    row = layout.row(align=True)
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='HIDE_OFF')
    op.type = key_type
    op.selection = True
    op = row.operator('anim.aide_select_key_type', text='', emboss=True, icon='HIDE_ON')
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


def handles_type_row(context, layout, act_on, name, icon='NONE', handle_type='NONE'):
    subcol = layout.column(align=True)
    if not utils.general.poll(context):
        subcol.active = False
    key_tweak = context.scene.animaide.key_tweak
    # subcol.prop(key_tweak, act_on, text='', icon='LAYER_USED', icon_only=True, emboss=False)
    op = subcol.operator('anim.aide_set_handles_type', text=' ', emboss=True, icon=icon)
    op.handle_type = handle_type
    op.act_on = 'SELECTION'
    op.strict = True
    subcol.prop(key_tweak, act_on, text='', icon='CHECKMARK', icon_only=True, emboss=False)



class ANIMAIDE_PT_key_manager:
    bl_label = "Key Manager"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout


class ANIMAIDE_PT_key_manager_ge(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_key_manager_de(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_PT_key_manager_3d(Panel, ANIMAIDE_PT_key_manager):
    bl_idname = 'ANIMAIDE_PT_key_manager_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_PT_move_keys:
    bl_label = "Move-Insert"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):

        layout = self.layout

        if not utils.general.poll(context):
            layout.active = False

        key_tweak = context.scene.animaide.key_tweak

        row = layout.row(align=True)

        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRACKING_BACKWARDS_SINGLE')
        op.direction = 'LEFT'
        op.amount = key_tweak.frames

        row.separator()

        op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRACKING_FORWARDS_SINGLE')
        op.direction = 'RIGHT'
        op.amount = key_tweak.frames

        row.separator()

        sub = row.split(factor=0.9, align=True)

        sub.prop(key_tweak, 'frames', text='', slider=False)
        sub.prop(key_tweak, 'amount', text='', icon='DOWNARROW_HLT', icon_only=True, emboss=False)

        row.separator()

        op = row.operator('anim.aide_insert_frames', text='', emboss=True, icon='IMPORT')
        op.amount = key_tweak.frames

        row.separator()

        op = row.operator('anim.aide_insert_frames', text='', emboss=True, icon='EXPORT')
        op.amount = -key_tweak.frames

        # row = layout.row(align=True)
        #
        # op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_UP')
        # op.direction = 'UP'
        # op.amount = key_tweak.value_change
        # row.prop(key_tweak, 'value_change', text='', slider=False)
        # op = row.operator('anim.aide_move_key', text='', emboss=True, icon='TRIA_DOWN')
        # op.direction = 'DOWN'
        # op.amount = key_tweak.value_change


class ANIMAIDE_PT_move_keys_ge(Panel, ANIMAIDE_PT_move_keys):
    bl_idname = 'ANIMAIDE_PT_move_keys_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_move_keys_de(Panel, ANIMAIDE_PT_move_keys):
    bl_idname = 'ANIMAIDE_PT_move_keys_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_de'


class ANIMAIDE_PT_move_keys_3d(Panel, ANIMAIDE_PT_move_keys):
    bl_idname = 'ANIMAIDE_PT_move_keys_3d'
    bl_space_type = 'VIEW_3D'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_3d'


class ANIMAIDE_PT_key_type:
    bl_label = "Type"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout

        key_type_row(layout, 'Keyframe', 'KEYFRAME', 'KEYTYPE_KEYFRAME_VEC')
        key_type_row(layout, 'Breakdown', 'BREAKDOWN', 'KEYTYPE_BREAKDOWN_VEC')
        key_type_row(layout, 'Jitter', 'JITTER', 'KEYTYPE_JITTER_VEC')
        key_type_row(layout, 'Extreme', 'EXTREME', 'KEYTYPE_EXTREME_VEC')


class ANIMAIDE_PT_key_type_ge(Panel, ANIMAIDE_PT_key_type):
    bl_idname = 'ANIMAIDE_PT_key_type_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_key_type_de(Panel, ANIMAIDE_PT_key_type):
    bl_idname = 'ANIMAIDE_PT_key_type_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_de'


class ANIMAIDE_PT_key_type_3d(Panel, ANIMAIDE_PT_key_type):
    bl_idname = 'ANIMAIDE_PT_key_type_3d'
    bl_space_type = 'VIEW_3D'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_3d'


class ANIMAIDE_PT_key_interp:
    bl_label = "Interpolation"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        support.external_op = context.active_operator

        layout = self.layout

        key_tweak = context.scene.animaide.key_tweak

        if not utils.general.poll(context):
            layout.active = False

        layout.prop(key_tweak, 'interp', text='')

        layout.separator()

        if key_tweak.interp == 'CONSTANT':

            op = layout.operator('anim.aide_set_handles_interp',
                                 text='Assign to every key',
                                 emboss=True, icon='CHECKMARK')
            op.interp = 'CONSTANT'
            # op.strength = 'NONE'
            # op.easing = 'NONE'
            op.act_on = 'ALL'
            op.strict = False

        elif key_tweak.interp == 'LINEAR':

            op = layout.operator('anim.aide_set_handles_interp',
                                 text='Assign to every key',
                                 emboss=True, icon='CHECKMARK')
            op.interp = 'LINEAR'
            # op.strength = 'NONE'
            # op.easing = 'NONE'
            op.act_on = 'ALL'
            op.strict = False

        elif key_tweak.interp == 'BEZIER':

            subrow = layout.row(align=True)

            if support.external_op and support.external_op != support.last_op:
                if support.external_op.name == 'Box Select':
                    left = True
                    point = True
                    right = True
                else:
                    left = False
                    point = True
                    right = False
            else:
                if key_tweak.left:
                    left = True
                else:
                    left = False

                if key_tweak.point:
                    point = True
                else:
                    point = False

                if key_tweak.right:
                    right = True
                else:
                    right = False

            handles_select_row(subrow, 'Left', left=True, depress=left)
            handles_select_row(subrow, '', icon='DECORATE_KEYFRAME', point=point, depress=point)
            handles_select_row(subrow, 'Right', right=True, depress=right)

            subrow = layout.row(align=True)

            handles_type_row(context, subrow, 'free_act_on', 'Free', icon='HANDLE_FREE', handle_type='FREE')
            handles_type_row(context, subrow, 'aligned_act_on', 'Aligned', icon='HANDLE_ALIGNED', handle_type='ALIGNED')
            handles_type_row(context, subrow, 'vector_act_on', 'Vector', icon='HANDLE_VECTOR', handle_type='VECTOR')
            handles_type_row(context, subrow, 'auto_act_on', 'Auto', icon='HANDLE_AUTO', handle_type='AUTO')
            handles_type_row(context, subrow, 'auto_clamped_act_on', 'Auto Clamped', icon='HANDLE_AUTOCLAMPED', handle_type='AUTO_CLAMPED')

        elif key_tweak.interp == 'EASE':

            col = layout.column(align=True)
            subrow = col.row(align=True)
            subrow.prop(key_tweak, 'strength', text='', icon_only=False)
            subrow.prop(key_tweak, 'easing', text='', expand=True)

            op = layout.operator('anim.aide_set_handles_interp',
                                 text='Assign to every key',
                                 emboss=True, icon='CHECKMARK')
            op.easing = key_tweak.easing
            op.strength = key_tweak.strength
            op.act_on = 'ALL'
            op.strict = False


class ANIMAIDE_PT_key_interp_ge(Panel, ANIMAIDE_PT_key_interp):
    bl_idname = 'ANIMAIDE_PT_key_interp_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_ge'


class ANIMAIDE_PT_key_interp_de(Panel, ANIMAIDE_PT_key_interp):
    bl_idname = 'ANIMAIDE_PT_key_interp_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_de'


class ANIMAIDE_PT_key_interp_3d(Panel, ANIMAIDE_PT_key_interp):
    bl_idname = 'ANIMAIDE_PT_key_interp_3d'
    bl_space_type = 'VIEW_3D'
    bl_parent_id = 'ANIMAIDE_PT_key_manager_3d'


classes = (
    ANIMAIDE_PT_key_manager_ge,
    ANIMAIDE_PT_key_manager_de,
    ANIMAIDE_PT_key_manager_3d,
    ANIMAIDE_PT_move_keys_ge,
    ANIMAIDE_PT_move_keys_de,
    ANIMAIDE_PT_move_keys_3d,
    ANIMAIDE_PT_key_interp_ge,
    ANIMAIDE_PT_key_interp_de,
    ANIMAIDE_PT_key_interp_3d,
    ANIMAIDE_PT_key_type_ge,
    ANIMAIDE_PT_key_type_de,
    ANIMAIDE_PT_key_type_3d,

)
