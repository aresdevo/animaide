import bpy
from . import props, key_utils
from bpy.types import Panel


def step_button(row, slot, factor, icon='',
                text='', emboss=True, active=True,
                operator_context='EXEC_DEFAULT', is_collection=True):
    # if key_utils.original_keys_info == {}:
    #     key_utils.get_selected_global(selected=False)
    # if slot.selector == 'BLEND_FRAME':
    #     left_ref_frame = self.slots[self.slot_index].left_ref_frame
    #     right_ref_frame = self.slots[self.slot_index].right_ref_frame
    #     key_utils.get_ref_frame_globals(slot.index)
    # key_utils.get_selected_global(original=False)

    col = row.column(align=True)
    col.active = active

    col.operator_context = operator_context

    if icon == '':
        step = col.operator('animaide.sliders', text=text, emboss=emboss)
    else:
        step = col.operator('animaide.sliders', text=text, icon=icon, emboss=emboss)

    # if slot.overshoot:
    #     min_value = -2.0
    #     max_value = 2.0
    # else:
    #     min_value = -1.0
    #     max_value = 1.0

    # step.min_value = min_value
    # step.max_value = max_value
    step.factor = factor
    step.slope = slot.slope
    step.slider_type = slot.selector
    step.slot_index = slot.index
    step.is_collection = is_collection
    step.op_context = operator_context


def slider_box(layout, slot, index=0, is_collection=True):
    if slot.overshoot == False:
        slider_length = 'factor'
        # factor = slot.factor

    else:
        slider_length = 'factor_overshoot'
        # factor = slot.factor_overshoot

    # -------- Options ---------

    if slot.index == -1:
        slider_num = '1'
    else:
        slider_num = '%s' % (slot.index + 2)

    # animaide = bpy.context.scene.animaide

    box = layout.box()
    row = box.row(align=True)

    col = row.column(align=True)
    col.alignment = 'LEFT'
    col.active = False
    col.scale_x = 0.8
    col.label(text=slider_num)

    col = row.column(align=False)
    col.prop_menu_enum(slot, 'selector', text=props.names[slot.selector])

    col = row.column(align=False)
    setting = col.operator('animaide.settings', text='', icon='SETTINGS', emboss=False)
    setting.slot_index = slot.index
    setting.is_collection = is_collection

    # -------- Slider -----------

    row = box.row(align=True)
    row.scale_y = .6
    row.active = True
    row.operator_context = 'EXEC_DEFAULT'

    if slot.modal_switch == False:

        if slot.overshoot == True:
            for f in [-2, -1.5]:
                step_button(row, slot, factor=f, text=' ', icon='', is_collection=is_collection)

        step_button(row, slot, factor=-1, text='',
                    icon='CHECKBOX_DEHLT', emboss=False, active=True, is_collection=is_collection)

        for f in [-0.75, -0.5, -0.25]:
            step_button(row, slot, factor=f, text=' ', icon='', is_collection=is_collection)

        step_button(row, slot, factor=0, text='', icon='ANTIALIASED',
                    emboss=False, operator_context='INVOKE_DEFAULT',
                    active=True, is_collection=is_collection)

        for f in [0.25, 0.5, 0.75]:
            step_button(row, slot, factor=f, text=' ', icon='', is_collection=is_collection)

        step_button(row, slot, factor=1, text='',
                    icon='CHECKBOX_DEHLT', emboss=False, active=True, is_collection=is_collection)

        if slot.overshoot == True:
            for f in [1.5, 2]:
                step_button(row, slot, factor=f, text=' ', icon='', is_collection=is_collection)

    else:
        if slot.modal_switch == True:
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
        left_ref_frame.is_collection = is_collection

        if slot.modal_switch == False:
            col = row.column(align=True)
            col.scale_x = 0.85
            col.alignment = 'CENTER'
            # col.label(text='%0.2f' % factor)
            col.label(text='')
        else:
            col = row.column(align=True)
            col.label(text='')

        col = row.column(align=True)
        right_ref_frame = col.operator("animaide.get_ref_frame",
                                       text=right_text, emboss=True)
        right_ref_frame.slot_index = index
        right_ref_frame.side = 'R'
        right_ref_frame.is_collection = is_collection

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
    bl_label = "Slider"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_space_type = 'GRAPH_EDITOR'

    def draw(self, context):
        animaide = context.scene.animaide
        slots = animaide.slider_slots
        item = animaide.slider

        if key_utils.global_values == {}:
            key_utils.get_globals()

        layout = self.layout
        row = layout.row(align=True)
        row.operator("animaide.add_slider", text='', icon='ADD')
        row.operator("animaide.remove_slider", text='', icon='REMOVE')

        slider_box(layout, item, is_collection=False)

        if len(slots) == 0:
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'CENTER'
            row.label(text='You can add more sliders', translate=False)

        index = 0
        for slot in slots:

            slider_box(layout, slot, index)

            index += 1

        # row = layout.row(align=True)
        # row.template_list("AA_UL_sliders", "", animaide, "slider_slots", animaide, "slider_i")


class AAT_PT_clone(Panel):
    bl_idname = 'AA_PT_clone'
    bl_label = "Clone"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):
        clone = context.scene.animaide.clone

        layout = self.layout
        row = layout.row(align=True)

        row.operator("animaide.fcurve_clone", text="Add", icon='NODE_COMPOSITING')
        row.operator("animaide.remove_clone", text="Remove", icon='CANCEL')

        row = layout.row()
        # row.alignment = 'RIGHT'
        row.label(text='Cycle Before')
        row.prop(clone, 'cycle_before', text='')
        row = layout.row()
        # row.alignment = 'RIGHT'
        row.label(text='Cycle After')
        row.prop(clone, 'cycle_after', text='')






