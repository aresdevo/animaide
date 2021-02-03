import bpy

from . import support
# from .utils import curve, key
from bpy.props import StringProperty, EnumProperty, IntProperty, FloatProperty, BoolProperty
from bpy.types import Operator


class ANIMAIDE_OT_modal_test(Operator):
    """Slider Operators Preset"""
    bl_idname = "anim.aide_modal_test"
    bl_label = "Test"

    @classmethod
    def poll(cls, context):
        return True

    def modal(self, context, event):
        # print('EVENT TYPE: ', event.type)
        # print('EVENT VALUE: ', event.value)

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.leftmouse = True
            elif event.value == 'RELEASE':
                self.leftmouse = False
            print('LEFTMOUSE')

        if event.type == 'MOUSEMOVE':
            print('LEFTMOUSE: ', self.leftmouse)
            print('MOUSEMOVE')

            if self.leftmouse:
                print('leftmouse')

            if event.shift and self.leftmouse:
                print('shift')

            elif event.alt and self.leftmouse:
                print('alt')

            elif event.ctrl and self.leftmouse:
                print('ctrl')

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.leftmouse = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIMAIDE_OT_add_magnet_mask(Operator):
    """Adds of modifies Anim Offset mask and activates it"""

    bl_idname = "anim.aide_add_magnet_mask"
    bl_label = "Add Mask"
    # bl_options = {'UNDO_GROUPED'}

    @classmethod
    def poll(cls, context):
        return support.poll(context)

    def marign_blend_info(self, context, side):
        # status bar info when the blends are being modified
        margin = None
        blend = None

        if side is 'Left':
            blend = context.scene.frame_preview_start
            margin = context.scene.frame_start
        elif side is 'Right':
            blend = context.scene.frame_preview_end
            margin = context.scene.frame_end

        margin_info = f"{side} Margin: {margin}     "
        blend_info = f"{side} Blend: {blend}     "

        if margin == blend:
            return margin_info
        elif side is 'Left':
            return margin_info + blend_info
        elif side is 'Right':
            return blend_info + margin_info

    def finish_mask(self, context):
        context.window.cursor_set("DEFAULT")
        context.window.workspace.status_text_set(None)
        context.scene.animaide.anim_offset.mask_in_use = True
        context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

    def constraint(self, limit, side, frame, gap=0):
        # Use to limit the mask margins and blends
        condition = None
        n = 0
        if side == 'L':
            n = 1
            condition = frame > limit + gap
        if side == 'R':
            n = -1
            condition = frame < limit - gap

        if condition:
            return frame
        else:
            return limit + (gap * n)

    def info(self, context, event):
        anim_offset = context.scene.animaide.anim_offset
        if anim_offset.mask_in_use:
            left_mouse_info = 'Move margins'
            ctrl_info = '+ CTRL: Move blends       '
            alt_info = '+ ALT: Move range       '
        else:
            left_mouse_info = 'Create mask'
            ctrl_info = ''
            alt_info = ''

        if event.shift:
            context.window.workspace.status_text_set(
                f"MOUSE-LB: {left_mouse_info}       "
                f"{ctrl_info}"
                f"{alt_info}"
                f"MOUSE-RB: Exit masking mode"
            )
            if event.ctrl:
                context.window.workspace.status_text_set(
                    f"MOUSE-LB: Move blends       "
                    f"ALT: Move range       "
                    f"MOUSE-RB: Exit masking mode"
                )
            if event.alt:
                context.window.workspace.status_text_set(
                    f"MOUSE-LB: Move range       "
                    f"CTRL: Move blends       "
                    f"MOUSE-RB: Exit masking mode"
                )

        elif event.ctrl:
            context.window.workspace.status_text_set(
                f"MOUSE-LB: Move blends       "
                f"+ SHIFT: Persistent masking       "
                f"MOUSE-RB: Exit masking mode"
            )
        elif event.alt:
            context.window.workspace.status_text_set(
                f"MOUSE-LB: Move range       "
                f"+ SHIFT: Persistent masking       "
                f"MOUSE-RB: Exit masking mode"
            )
        else:
            context.window.workspace.status_text_set(
                f"MOUSE-LB: {left_mouse_info}       "
                f"+ SHIFT: Persistent masking       "
                f"{ctrl_info}"
                f"{alt_info}"
                f"MOUSE-RB: Exit masking mode"
            )

    def modal(self, context, event):
        scene = context.scene
        anim_offset = scene.animaide.anim_offset

        x = event.mouse_region_x
        y = event.mouse_region_y
        co = bpy.context.region.view2d.region_to_view(x, y)
        frame = int(co[0])

        context.window.cursor_set("SCROLL_X")

        # info for the status bar
        self.info(context, event)

        if self.created and not event.shift and not event.alt and not event.ctrl:
            # if there are not modifier keys leaves msking
            self.finish_mask(context)
            return {'FINISHED'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                # ------------- setup ---------------
                self.leftmouse = True
                self.init_mouse_x = event.mouse_x
                self.leftmouse_frame = frame
                self.delta_start = scene.frame_start - scene.frame_preview_start
                self.delta_end = scene.frame_preview_end - scene.frame_end
                self.end_distance = abs(self.leftmouse_frame - scene.frame_end)
                self.start_distance = abs(self.leftmouse_frame - scene.frame_start)
                self.init_preview_start = scene.frame_preview_start
                self.init_start = scene.frame_start
                self.init_end = scene.frame_end
                self.init_preview_end = scene.frame_preview_end
                # anim_offset.mask_in_use = True

            elif event.value == 'RELEASE':
                # ----------- center cursor ----------
                start = scene.frame_start
                end = scene.frame_end
                scene.frame_current = (end + start)/2

                self.leftmouse = False
                self.created = True
                anim_offset.mask_in_use = True

        elif event.type == 'MOUSEMOVE':

            anim_offset = scene.animaide.anim_offset

            if not anim_offset.mask_in_use:
                # ------------ fill timeline -----------
                scene.use_preview_range = True
                scene.frame_start = -100
                scene.frame_end = -100
                scene.frame_preview_start = -100
                scene.frame_preview_end = -100

            if self.leftmouse:
                if anim_offset.mask_in_use and scene.frame_start != scene.frame_end:
                    if event.ctrl:
                        # ----------- blends ------------
                        if self.end_distance < self.start_distance:
                            scene.frame_preview_end = self.constraint(scene.frame_end, 'L', frame)
                            context.window.workspace.status_text_set(
                                f"Right Blend: {scene.frame_preview_end}"
                            )
                        else:
                            scene.frame_preview_start = self.constraint(scene.frame_start, 'R', frame)
                            context.window.workspace.status_text_set(
                                f"Left Blend: {scene.frame_preview_start}     "
                            )

                        support.set_blend_values(context)

                    elif event.alt:
                        # -------------- Move range -------------
                        left_info = self.marign_blend_info(context, 'Left')
                        right_info = self.marign_blend_info(context, 'Right')
                        context.window.workspace.status_text_set(left_info + right_info)

                        distance = frame - self.leftmouse_frame
                        scene.frame_preview_start = self.init_preview_start + distance
                        scene.frame_start = self.init_start + distance
                        scene.frame_end = self.init_end + distance
                        scene.frame_preview_end = self.init_preview_end + distance
                        support.set_blend_values(context)

                    else:
                        # -------------- Move margins -------------
                        end_distance = abs(self.leftmouse_frame - scene.frame_end)
                        start_distance = abs(self.leftmouse_frame - scene.frame_start)

                        if end_distance < start_distance:
                            scene.frame_end = self.constraint(scene.frame_start, 'L', frame, gap=1)
                            scene.frame_preview_end = scene.frame_end + self.delta_end
                            info = self.marign_blend_info(context, 'Right')
                            context.window.workspace.status_text_set(info)
                        else:
                            scene.frame_start = self.constraint(scene.frame_end, 'R', frame, gap=1)
                            scene.frame_preview_start = scene.frame_start - self.delta_start
                            info = self.marign_blend_info(context, 'Left')
                            context.window.workspace.status_text_set(info)

                        support.set_blend_values(context)

                else:
                    # --------------- Add mask ----------------
                    context.window.workspace.status_text_set(
                        f"Left Margin: {scene.frame_start}     "
                        f"Right Margin: {scene.frame_end}     "
                    )
                    direction = None
                    if event.mouse_x > self.init_mouse_x:
                        direction = 'R'
                    elif event.mouse_x < self.init_mouse_x:
                        direction = 'L'

                    if direction == 'R':
                        scene.frame_end = frame
                        scene.frame_preview_end = frame

                        scene.frame_start = self.leftmouse_frame
                        scene.frame_preview_start = self.leftmouse_frame

                    elif direction == 'L':
                        scene.frame_start = frame
                        scene.frame_preview_start = frame

                        scene.frame_end = self.leftmouse_frame
                        scene.frame_preview_end = self.leftmouse_frame

                    support.set_blend_values(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.finish_mask(context)
            return {'CANCELLED'}

        elif event.type in {'MIDDLEMOUSE', 'RET'}:
            self.finish_mask(context)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene
        scene.tool_settings.use_keyframe_insert_auto = False

        self.leftmouse = False
        self.created = False

        anim_offset = scene.animaide.anim_offset

        if not anim_offset.mask_in_use:
            support.store_user_timeline_ranges(context)

        if support.magnet_handlers not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(support.magnet_handlers)

        support.add_blends()
        # scene.use_preview_range = True

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ANIMAIDE_OT_deactivate_magnet(Operator):
    """Deactivates Anim Offset"""

    bl_idname = "anim.aide_deactivate_magnet"
    bl_label = "Deactivate"

    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return support.poll(context)

    def execute(self, context):

        if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(support.magnet_handlers)

        support.remove_mask(context)

        context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # bpy.data.window_managers['WinMan'].windows.update()
        # bpy.data.window_managers['WinMan'].update_tag()

        return {'FINISHED'}


class ANIMAIDE_OT_without_magnet_mask(Operator):
    """Activates Anim Offset without maks"""

    bl_idname = "anim.aide_without_magnet_mask"
    bl_label = "Without Mask"

    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return support.poll(context)

    def execute(self, context):

        if support.magnet_handlers not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(support.magnet_handlers)

        support.remove_mask(context)

        context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # bpy.data.window_managers['WinMan'].windows.update()
        # bpy.data.window_managers['WinMan'].update_tag()

        return {'FINISHED'}


class ANIMAIDE_OT_delete_magnet_mask(Operator):
    """Deletes Anim Offset mask and deactivates it"""

    bl_idname = "anim.aide_delete_magnet_mask"
    bl_label = "Delete Mask"

    # bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return support.poll(context)

    def execute(self, context):

        # if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        #     bpy.app.handlers.depsgraph_update_post.remove(support.magnet_handlers)

        support.remove_mask(context)

        context.area.tag_redraw()
        # bpy.ops.wm.redraw_timer()
        # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # bpy.data.window_managers['WinMan'].windows.update()
        # bpy.data.window_managers['WinMan'].update_tag()

        return {'FINISHED'}


class ANIMAIDE_OT_anim_offset_settings(Operator):
    """Shows global options for Anim Offset"""

    bl_idname = "anim.aide_anim_offset_settings"
    bl_label = "Anim Offset Settings"
    # bl_options = {'REGISTER'}

    slot_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return support.poll(context)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=200)

    def draw(self, context):
        anim_offset = context.scene.animaide.anim_offset

        layout = self.layout

        layout.label(text='Settings')
        layout.separator()
        # layout.prop(anim_offset, 'end_on_release', text='masking ends on mouse release')
        layout.prop(anim_offset, 'fast_mask', text='Fast offset calculation')
        if context.area.type != 'VIEW_3D':
            layout.prop(anim_offset, 'insert_outside_keys', text='Auto Key outside margins')
            layout.separator()
            # layout.label(text='Mask blend interpolation')
            # row = layout.row(align=True)
            # row.prop(anim_offset, 'easing', text='', icon_only=False)
            # row.prop(anim_offset, 'interp', text='', expand=True)
            # layout.prop(anim.aide_anim_offset, 'use_markers', text='Use Markers')


classes = (
    ANIMAIDE_OT_modal_test,
    ANIMAIDE_OT_add_magnet_mask,
    ANIMAIDE_OT_without_magnet_mask,
    ANIMAIDE_OT_deactivate_magnet,
    ANIMAIDE_OT_delete_magnet_mask,
    ANIMAIDE_OT_anim_offset_settings,
)
