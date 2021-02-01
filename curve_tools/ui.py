from . import support
from .. import utils
from bpy.types import Panel, Menu, UIList, WorkSpaceTool


def step_button(layout, tool, factor, icon='',
                text='', emboss=True, active=True,
                operator_context='EXEC_DEFAULT'):

    layout.active = active

    layout.operator_context = operator_context

    buttons = dict(operator='anim.aide_%s' % str(tool.selector).lower(),
                  text=text, emboss=emboss)
    if icon:
        buttons['icon'] = icon

    step = layout.operator(**buttons)

    step.factor = factor
    if getattr(step, 'slope', None):
        step.slope = tool.slope
    if getattr(step, 'phase', None):
        step.phase = tool.noise_phase

    step.op_context = operator_context


def blend_button(layout, fac, text='', icon='NONE'):
    op = layout.operator('anim.aide_blend_neighbor', text=text, icon=icon)
    op.op_context = 'EXEC_DEFAULT'
    op.factor = fac


def reference_frames(context, layout, expand):
    tool = context.scene.animaide.tool

    if tool.selector == 'BLEND_FRAME' or not expand:

        row = layout.row(align=True)
        row.label(text='Referece frames:')

        left_frame, right_frame = support.set_ref_marker(context)

        row = layout.row(align=True)
        row.scale_y = .7

        col = row.column(align=False)
        col.scale_x = .3
        col.label(text='L:')

        # left reference botton
        col = row.column(align=False)
        left_ref_frame = col.operator("anim.aide_get_ref_frame", text=str(left_frame), emboss=True)
        left_ref_frame.side = 'L'

        col = row.column(align=False)
        col.scale_x = .3
        col.label(text='R:')

        # right reference button
        col = row.column(align=False)
        right_ref_frame = col.operator("anim.aide_get_ref_frame", text=str(right_frame), emboss=True)
        right_ref_frame.side = 'R'

        # layout.prop(tool, 'use_markers', text='Use markers', toggle=False)


def steps(context, layout, tool, expand):

    # -------- Steps -----------

    # box = layout.box()
    row = layout.row(align=True)
    row.scale_y = .6
    row.active = True
    row.operator_context = 'EXEC_DEFAULT'

    # left overshoot extra buttons
    if tool.overshoot:
        for f in [-2, -1.5]:
            step_button(row, tool, factor=f, text=' ', icon='')

    # left end button
    step_button(row, tool, factor=-1, text='-1',
                icon='NONE', emboss=True, active=True)

    # left buttons
    for f in [-0.75, -0.5, -0.25]:
        step_button(row, tool, factor=f, text=' ', icon='')

    # Center Button
    step_button(row, tool, factor=0, text='0',
                icon='NONE', emboss=True, active=True)

    # right buttons
    for f in [0.25, 0.5, 0.75]:
        step_button(row, tool, factor=f, text=' ', icon='')

    # right end button
    step_button(row, tool, factor=1, text='1',
                icon='NONE', emboss=True, active=True)

    # right overshoot extra buttons
    if tool.overshoot:
        for f in [1.5, 2]:
            step_button(row, tool, factor=f, text=' ', icon='')

    # -------- selector -----------

    if not expand:
        selected = support.get_items(context, any_mode=True)
        # row = box.row(align=True)
        row = layout.row(align=True)
        if not selected:
            row.active = False
        row.prop(tool, 'selector', text='')


def tool_button(context, layout_type, tool_type=''):
    area = context.area.type
    tool = context.scene.animaide.tool

    if tool.overshoot is False:
        rango = 'factor'
    else:
        rango = 'factor_overshoot'

    if tool_type == '':
        same_type = True
        tool_type = str(tool.selector).lower()
    else:
        same_type = (str(tool.selector).lower() == tool_type)

    if tool.show_factor and same_type and area == tool.area:
        layout_type.prop(tool, rango, text='', slider=True)
    else:
        layout_type.operator('anim.aide_%s' % tool_type, emboss=True)


class ANIMAIDE_PT_curve_tools:
    bl_label = "Curve Tools"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        animaide = context.scene.animaide
        tool = animaide.tool
        clone = animaide.clone

        if context.area.type == 'VIEW_3D':
            expand = tool.expand_3d
            expand_text = 'expand_3d'
        else:
            expand = tool.expand
            expand_text = 'expand'

        if expand:
            icon = 'RIGHTARROW'
            title = 'Compact'
        else:
            title = 'Expanded'
            icon = 'DOWNARROW_HLT'

        layout = self.layout

        flow = layout.column_flow(columns=2)
        sub = flow.row(align=True)
        sub.alignment = 'LEFT'
        sub.prop(tool, expand_text, text='', icon=icon, emboss=False)
        sub.label(text=title)
        sub = flow.row(align=True)
        sub.alignment = 'RIGHT'
        sub.operator('anim.aide_tools_settings', text='', icon='PREFERENCES', emboss=False)

        box = layout.box()
        col = box.column(align=True)

        selected = support.get_items(context, any_mode=True)

        if expand:
            subrow = col.row(align=True)

            if not selected:
                subrow.active = False

            tool_button(context, subrow)
            subrow.prop_menu_enum(tool, 'selector', text='', icon='FCURVE')
        else:
            tool_button(context, col, 'ease_to_ease')
            tool_button(context, col, 'ease')
            tool_button(context, col, 'blend_ease')
            tool_button(context, col, 'blend_neighbor')
            tool_button(context, col, 'blend_frame')
            tool_button(context, col, 'blend_offset')
            tool_button(context, col, 'tween')
            tool_button(context, col, 'push_pull')
            tool_button(context, col, 'scale_left')
            tool_button(context, col, 'scale_average')
            tool_button(context, col, 'scale_right')
            tool_button(context, col, 'smooth')
            tool_button(context, col, 'wave_noise')
            tool_button(context, col, 'time_offset')

        steps(context, box, tool, expand)

        layout.use_property_split = True
        layout.use_property_decorate = False

        if tool.selector == 'TIME_OFFSET':

            subrow = layout.row(align=True)
            subrow.prop(clone, 'cycle_before', text='Cycle Before')

            subrow = layout.row(align=True)
            subrow.prop(clone, 'cycle_after', text='Cycle After')

        reference_frames(context, layout, expand)


class ANIMAIDE_PT_curve_tools_ge(Panel, ANIMAIDE_PT_curve_tools):
    bl_idname = 'ANIMAIDE_PT_curve_tools_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_curve_tools_de(Panel, ANIMAIDE_PT_curve_tools):
    bl_idname = 'ANIMAIDE_PT_curve_tools_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_PT_curve_tools_3d(Panel, ANIMAIDE_PT_curve_tools):
    bl_idname = 'ANIMAIDE_PT_curve_tools_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_UL_frame_bookmarks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        bookmark = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row.prop(bookmark, "name", text="", emboss=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            row.alignment = 'CENTER'
            row.label(text="", icon_value=icon)


class ANIMAIDE_PT_frame_bookmarks:
    bl_label = "Frame Bookmarks"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        animaide = context.scene.animaide
        tool = animaide.tool

        row = layout.row(align=False)
        row.template_list("ANIMAIDE_UL_frame_bookmarks", "", tool, "frame_bookmarks", tool, "bookmark_index")
        col = row.column(align=True)
        col.operator('anim.aide_add_bookmark', text='', emboss=True, icon='ADD')
        col.operator('anim.aide_delete_bookmark', text='', emboss=True, icon='REMOVE')
        col.separator()
        op = col.operator('anim.aide_push_bookmark', text='', emboss=True, icon='EVENT_L')
        op.side = 'L'
        op = col.operator('anim.aide_push_bookmark', text='', emboss=True, icon='EVENT_R')
        op.side = 'R'


class ANIMAIDE_PT_frame_bookmarks_ge(Panel, ANIMAIDE_PT_frame_bookmarks):
    bl_idname = 'ANIMAIDE_PT_frame_bookmarks_ge'
    bl_space_type = 'GRAPH_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_curve_tools_ge'


class ANIMAIDE_PT_frame_bookmarks_de(Panel, ANIMAIDE_PT_frame_bookmarks):
    bl_idname = 'ANIMAIDE_PT_frame_bookmarks_de'
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_parent_id = 'ANIMAIDE_PT_curve_tools_de'


class ANIMAIDE_PT_frame_bookmarks_3d(Panel, ANIMAIDE_PT_frame_bookmarks):
    bl_idname = 'ANIMAIDE_PT_frame_bookmarks_3d'
    bl_space_type = 'VIEW_3D'
    bl_parent_id = 'ANIMAIDE_PT_curve_tools_3d'


classes = (
    ANIMAIDE_PT_curve_tools_ge,
    ANIMAIDE_PT_curve_tools_de,
    ANIMAIDE_PT_curve_tools_3d,
    ANIMAIDE_UL_frame_bookmarks,
    ANIMAIDE_PT_frame_bookmarks_ge,
    ANIMAIDE_PT_frame_bookmarks_de,
    ANIMAIDE_PT_frame_bookmarks_3d,
)
