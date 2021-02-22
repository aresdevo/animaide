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


class ANIMAIDE_PT_info:
    bl_label = "Info"
    bl_region_type = 'UI'
    bl_category = 'AnimAide'

    def draw(self, context):

        layout = self.layout

        layout.label(text='-Anim offset buttons')
        layout.label(text='now located in the Timeline')
        layout.label(text='and Graph Editor headers.')
        layout.label(text='-Some preferences are now')
        layout.label(text='located in the addon tab')
        layout.label(text='in Blender Preferences.')
        layout.label(text='Because of that Blender')
        layout.label(text='will remember them after')
        layout.label(text='you quit.')
        layout.label(text='-This info panel can be')
        layout.label(text='removed in the addon')
        layout.label(text='preferences')


class ANIMAIDE_PT_info_3d(Panel, ANIMAIDE_PT_info):
    bl_idname = 'ANIMAIDE_PT_info_3d'
    bl_space_type = 'VIEW_3D'


class ANIMAIDE_PT_info_ge(Panel, ANIMAIDE_PT_info):
    bl_idname = 'ANIMAIDE_PT_info_ge'
    bl_space_type = 'GRAPH_EDITOR'


class ANIMAIDE_PT_info_de(Panel, ANIMAIDE_PT_info):
    bl_idname = 'ANIMAIDE_PT_info_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class ANIMAIDE_MT_operators(Menu):
    bl_idname = 'ANIMAIDE_MT_menu_operators'
    bl_label = "AnimAide"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.area.type != 'DOPESHEET_EDITOR':
            if context.area.type == 'GRAPH_EDITOR':
                layout.menu('ANIMAIDE_MT_pie_menus')

            if context.area.type == 'VIEW_3D':
                layout.menu('ANIMAIDE_MT_curve_tools', text='On Frame Curve Tools')
            else:
                layout.menu('ANIMAIDE_MT_curve_tools')
                layout.menu('ANIMAIDE_MT_tweak')

            layout.separator()

        if context.area.type != 'VIEW_3D':
            layout.operator('wm.call_menu_pie', text="Pie AnimOffset").name = 'ANIMAIDE_MT_pie_anim_offset'
        layout.menu('ANIMAIDE_MT_anim_offset')
        if context.area.type != 'VIEW_3D':
            layout.menu('ANIMAIDE_MT_anim_offset_mask')


def draw_menu(self, context):
    layout = self.layout
    layout.menu('ANIMAIDE_MT_menu_operators')


menu_classes = (
    ANIMAIDE_MT_operators,
)

info_classes = (
    ANIMAIDE_PT_info_3d,
    ANIMAIDE_PT_info_ge,
    ANIMAIDE_PT_info_de,
)
