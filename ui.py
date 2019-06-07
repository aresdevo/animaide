import bpy
from . import props, key_utils, magnet
from bpy.types import Panel, Menu


def step_button(row, slot, factor, icon='',
                text='', emboss=True, active=True,
                operator_context='EXEC_DEFAULT'):

    col = row.column(align=True)
    col.active = active

    col.operator_context = operator_context

    # if icon == '':
    #     step = col.operator('animaide.sliders', text=text, emboss=emboss)
    # else:
    #     step = col.operator('animaide.sliders', text=text, icon=icon, emboss=emboss)

    if icon == '':
        step = col.operator('animaide.%s' % str(slot.selector).lower(), text=text, emboss=emboss)
    else:
        step = col.operator('animaide.%s' % str(slot.selector).lower(), text=text, icon=icon, emboss=emboss)

    step.factor = factor
    step.slope = slot.slope
    # step.slider_type = slot.selector
    step.slot_index = slot.index
    # step.is_collection = is_collection
    step.op_context = operator_context


def slider_box(layout, slot, index=-1):

    if slot.overshoot is False:
        slider_length = 'factor'

    else:
        slider_length = 'factor_overshoot'

    # -------- Options ---------

    box = layout.box()
    row = box.row(align=True)

    col = row.column(align=False)
    # col.prop_menu_enum(slot, 'selector', text=props.names[slot.selector], icon=props.icons[slot.selector])
    col.prop(slot, 'selector', text='')

    col = row.column(align=False)
    setting = col.operator('animaide.sliders_settings', text='', icon='SETTINGS', emboss=False)
    setting.slot_index = slot.index

    # -------- Slider -----------

    row = box.row(align=True)
    row.scale_y = .6
    row.active = True
    row.operator_context = 'EXEC_DEFAULT'

    if slot.modal_switch == False:

        if slot.overshoot == True:
            for f in [-2, -1.5]:
                step_button(row, slot, factor=f, text=' ', icon='')

        step_button(row, slot, factor=-1, text='',
                    icon='CHECKBOX_DEHLT', emboss=False, active=True)

        for f in [-0.75, -0.5, -0.25]:
            step_button(row, slot, factor=f, text=' ', icon='')

        step_button(row, slot, factor=0, text='', icon='ANTIALIASED',
                    emboss=False, operator_context='INVOKE_DEFAULT',
                    active=True)

        for f in [0.25, 0.5, 0.75]:
            step_button(row, slot, factor=f, text=' ', icon='')

        step_button(row, slot, factor=1, text='',
                    icon='CHECKBOX_DEHLT', emboss=False, active=True)

        if slot.overshoot == True:
            for f in [1.5, 2]:
                step_button(row, slot, factor=f, text=' ', icon='')

    else:
        row.prop(slot, slider_length, text='', slider=True)

    row.operator_context = 'INVOKE_DEFAULT'

    # -------- Frames -----------

    row = box.row(align=False)
    row.scale_y = 0.6
    row.active = True

    if slot.selector == 'BLEND_FRAME':
        # if key_utils.left_neighbor_global == {}:
        #     left_text = '#'
        # else:
        #     left_text = str(slot.left_neighbor)
        #
        # if key_utils.right_neighbor_global == {}:
        #     right_text = '#'
        # else:
        #     right_text = str(slot.right_neighbor)

        left_text = str(slot.left_ref_frame)
        right_text = str(slot.right_ref_frame)

        col = row.column(align=True)
        left_ref_frame = col.operator("animaide.get_ref_frame",
                                      text=left_text, emboss=True)
        left_ref_frame.slot_index = index
        left_ref_frame.side = 'L'
        # left_ref_frame.is_collection = is_collection

        if slot.modal_switch == False:
            col = row.column(align=True)
            col.scale_x = 0.85
            col.alignment = 'CENTER'
            # col.label(text='%0.2f' % factor)
            col.label(text='')
        else:
            col = row.column(align=True)
            col.scale_x = 0.85
            col.alignment = 'CENTER'
            col.label(text='')

        col = row.column(align=True)
        right_ref_frame = col.operator("animaide.get_ref_frame",
                                       text=right_text, emboss=True)
        right_ref_frame.slot_index = index
        right_ref_frame.side = 'R'
        # right_ref_frame.is_collection = is_collection

    # elif slot.modal_switch == False:
    #     row.active = False
    #     row.alignment = 'CENTER'
    #     row.scale_x = 0.85
    #     row.enabled = False
    #     row.label(text='%0.2f' % factor)
    # else:
    #     row.scale_x = 0.85
    #     row.alignment = 'CENTER'
    #     row.label(text='')


class AAT_PT_sliders(Panel):
    bl_idname = 'AA_PT_slider'
    bl_label = "Sliders"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_space_type = 'GRAPH_EDITOR'

    def draw(self, context):
        animaide = context.scene.animaide
        slots = animaide.slider_slots
        slider = animaide.slider

        if key_utils.global_values == {}:
            key_utils.get_sliders_globals()

        layout = self.layout

        # row = layout.row(align=True)
        # row.label(text='Main Slider')

        slider_box(layout, slider)

        row = layout.row(align=True)
        row.operator("animaide.add_slider", text='', icon='ADD')
        row.operator("animaide.remove_slider", text='', icon='REMOVE')
        # row.label(text='Extra Sliders')

        if len(slots) == 0:
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'CENTER'
            row.label(text='Extra sliders', translate=False)

        index = 0
        for slot in slots:

            slider_box(layout, slot, index)

            index += 1

        # row = layout.row(align=True)
        # row.template_list("AA_UL_sliders", "", animaide, "slider_slots", animaide, "slider_i")


class AAT_PT_anim_transform(Panel):
    bl_idname = 'AAT_PT_anim_transform'
    bl_label = "Anim Transform"
    bl_space_type = 'GRAPH_EDITOR'
    # bl_space_type = props.space_type_pref()
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):
        animaide = context.scene.animaide

        layout = self.layout

        row = layout.row(align=True)

        # if animaide.anim_transform.active is False:
        if magnet.anim_transform_handlers not in bpy.app.handlers.depsgraph_update_pre:
            row.operator("animaide.anim_transform_on", text='Activate', icon='PLUGIN')
        else:
            row.operator("animaide.anim_transform_off", text="Dectivate", icon='CANCEL')

            row = layout.row(align=True)

            # if animaide.anim_transform.use_mask is False:
            if magnet.anim_trans_mask_handlers not in bpy.app.handlers.depsgraph_update_pre:
                row.operator("animaide.create_anim_trans_mask", text="Add Mask", icon='SELECT_SUBTRACT')
                row.operator('animaide.anim_transform_settings', text='', icon='SETTINGS', emboss=True)
            else:
                row.operator("animaide.delete_anim_trans_mask", text="Remove Mask", icon='TRASH')
                row.operator('animaide.anim_transform_settings', text='', icon='SETTINGS', emboss=True)

                # col = layout.column_flow(columns=2, align=False)
                # col.label(text='Margins')
                # row = col.row(align=True)
                row = layout.row(align=True)
                row.prop(animaide.anim_transform, 'mask_margin_l', text='Margin', slider=False)
                row.prop(animaide.anim_transform, 'mask_margin_r', text='Margin', slider=False)

                # col = layout.column_flow(columns=2, align=False)
                # col.label(text='Blends')
                # row = col.row(align=True)
                row = layout.row(align=True)
                row.prop(animaide.anim_transform, 'mask_blend_l', text='Blend', slider=False)
                row.prop(animaide.anim_transform, 'mask_blend_r', text='Blend', slider=False)


class AAT_MT_pie_menu_a(Menu):
    bl_idname = "AAT_MT_pie_menu_a"
    bl_label = "Sliders A"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        col = pie.column()
        col.operator("animaide.ease")

        col = pie.column(align=True)
        col.operator("animaide.tween")

        col = pie.column(align=True)
        col.operator("animaide.blend_ease")

        col = pie.column(align=True)
        col.operator("animaide.ease_in_out")

        col = pie.column(align=True)
        col.operator("animaide.blend_neighbor")

        col = pie.column(align=True)
        col.operator("animaide.scale_average")

        col = pie.column(align=True)
        col.operator("animaide.push_pull")

        col = pie.column(align=True)
        col.operator("animaide.blend_frame")


class AAT_MT_pie_menu_b(Menu):
    bl_idname = "AAT_MT_pie_menu_b"
    bl_label = "Sliders B"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        col = pie.column()
        col.operator("animaide.scale_left")

        col = pie.column(align=True)
        col.operator("animaide.scale_right")

        col = pie.column(align=True)
        col.operator("animaide.noise")

        col = pie.column(align=True)
        col.operator("animaide.smooth")

        col = pie.column(align=True)

        col = pie.column(align=True)
        col.operator("animaide.blend_offset")

        col = pie.column(align=True)
        col.operator("animaide.time_offset")

        col = pie.column(align=True)


classes = (
    AAT_PT_sliders,
    AAT_PT_anim_transform,
    AAT_MT_pie_menu_a,
    AAT_MT_pie_menu_b
)





