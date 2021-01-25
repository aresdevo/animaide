from bpy.types import Panel, Menu
from .curve_tools.ui import blend_button


class ANIMAIDE_PT_help:
    bl_label = "Help"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout

        row = layout.row(align=True)

        row.operator('anim.aide_manual', text='', icon='HELP', emboss=False)
        row.operator('anim.aide_demo', text='', icon='FILE_MOVIE', emboss=False)


class ANIMAIDE_MT_pie_tools_a(Menu):
    bl_idname = "ANIMAIDE_MT_pie_tools_a"
    bl_label = "Tools A"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("anim.aide_ease_to_ease")
        pie.operator("anim.aide_tween")
        pie.operator("anim.aide_blend_ease")
        pie.operator("anim.aide_ease")
        pie.operator("anim.aide_blend_neighbor")
        pie.operator("anim.aide_scale_average")
        pie.operator("anim.aide_push_pull")
        pie.operator("anim.aide_blend_frame")


class ANIMAIDE_MT_pie_tools_b(Menu):
    bl_idname = "ANIMAIDE_MT_pie_tools_b"
    bl_label = "Tools B"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("anim.aide_scale_left")
        pie.operator("anim.aide_scale_right")
        pie.operator("anim.aide_wave_noise")
        pie.operator("anim.aide_smooth")
        pie.operator("anim.aide_blend_offset")
        pie.operator("anim.aide_time_offset")


class ANIMAIDE_MT_pie_anim_offset(Menu):
    bl_idname = "ANIMAIDE_MT_pie_anim_offset"
    bl_label = "AnimOffset"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator('anim.aide_without_magnet_mask', text='AnimOffset Without Mask')
        pie.operator('anim.aide_add_magnet_mask', text='Add AnimOffset Mask')
        pie.operator('anim.aide_delete_magnet_mask', text='Delete AnimOffset Mask')
        pie.operator('anim.aide_deactivate_magnet', text='Deactivate AnimOffset')


class ANIMAIDE_MT_operators(Menu):
    bl_idname = 'ANIMAIDE_MT_menu_operators'
    bl_label = "AnimAide"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.operator('wm.call_menu_pie', text="Pie Menu A").name = 'ANIMAIDE_MT_pie_tools_a'
        layout.operator('wm.call_menu_pie', text="Pie Menu B").name = 'ANIMAIDE_MT_pie_tools_b'
        layout.operator('wm.call_menu_pie', text="Pie AnimOffset").name = 'ANIMAIDE_MT_pie_anim_offset'
        layout.separator()

        layout.operator('anim.aide_ease_to_ease')
        layout.operator('anim.aide_ease')
        layout.operator('anim.aide_blend_ease')

        layout.operator('anim.aide_blend_neighbor')
        layout.operator('anim.aide_blend_frame')
        layout.operator('anim.aide_blend_offset')

        layout.operator('anim.aide_tween')
        layout.operator('anim.aide_push_pull')

        layout.operator('anim.aide_scale_left')
        layout.operator('anim.aide_scale_average')
        layout.operator('anim.aide_scale_right')

        layout.operator('anim.aide_smooth')
        layout.operator('anim.aide_wave_noise')

        layout.operator('anim.aide_time_offset')

        layout.separator()

        blend_button(layout, -0.10, text="Tweak Left")
        blend_button(layout, 0.10, text="Tweak Right")
        blend_button(layout, -1, text="Match Left")
        blend_button(layout, 1, text="Match Right")

        layout.separator()

        layout.operator('anim.aide_without_magnet_mask', text='AnimOffset Without Mask')
        layout.operator('anim.aide_add_magnet_mask', text='Add AnimOffset Mask')
        layout.operator('anim.aide_delete_magnet_mask', text='Delete AnimOffset Mask')
        layout.operator('anim.aide_deactivate_magnet', text='Deactivate AnimOffset')


classes = (
    ANIMAIDE_MT_pie_tools_a,
    ANIMAIDE_MT_pie_tools_b,
    ANIMAIDE_MT_pie_anim_offset,
    ANIMAIDE_MT_operators,
)
