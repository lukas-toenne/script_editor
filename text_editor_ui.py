# MIT License
#
# Copyright (c) 2021 Lukas Toenne
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper


status_items = bpy.types.ScriptCompiler.bl_rna.properties['status'].enum_items
message_type_items = bpy.types.ScriptCompilerMessage.bl_rna.properties['type'].enum_items


class  ScriptCompileOperator(bpy.types.Operator):
    """Compile script"""
    bl_idname = "script_editor.compile"
    bl_label = "Compile"

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'TEXT_EDITOR':
            if context.space_data.text:
                return True
        return False

    def execute(self, context):
        text = context.space_data.text
        text.script_compiler.compile_script(source_id=text, source=text.as_string(), tab_size=context.space_data.tab_width)
        return {'FINISHED'}


class  ScriptDotExportOperator(bpy.types.Operator, ExportHelper):
    """Export a dot file for visualizing the script procedure"""
    bl_idname = "script_editor.dot_export"
    bl_label = "Dot Export"

    # ExportHelper mixin class uses this
    filename_ext = ".dot"

    filter_glob: StringProperty(
        default="*.dot",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'TEXT_EDITOR':
            text = context.space_data.text
            if text and text.script_compiler.has_script(text):
                return True
        return False

    def execute(self, context):
        text = context.space_data.text
        text.script_compiler.dot_export(source_id=text, output_filepath=self.filepath)
        return {'FINISHED'}


class  ScriptDotImageOperator(bpy.types.Operator):
    """Show Graphviz generated image for the script procedure"""
    bl_idname = "script_editor.dot_image"
    bl_label = "Dot Image"

    img_format = "jpg"
    window_width = 800
    window_height = 600

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'TEXT_EDITOR':
            text = context.space_data.text
            if text and text.script_compiler.has_script(text):
                return True
        return False

    def execute(self, context):
        import os
        import subprocess

        filepath = os.path.join(bpy.app.tempdir, "script.dot")
        # print("Temporary dot file exported to {}".format(filepath))

        text = context.space_data.text
        text.script_compiler.dot_export(source_id=text, output_filepath=filepath)

        img_filepath = bpy.path.ensure_ext(filepath, "." + self.img_format)
        subprocess.run(["dot", "-T{}".format(self.img_format), "-o{}".format(img_filepath), filepath])
        # print("Temporary image file exported to {}".format(img_filepath))

        img = bpy.data.images.load(img_filepath, check_existing=True)

        bpy.ops.wm.window_new()
        window = bpy.context.window_manager.windows[-1]
        # XXX width and height are readonly, don't know a way to resize the window from within Blender
        # window.width = self.window_width
        # window.height = self.window_height
        area = window.screen.areas[0]
        area.type = "IMAGE_EDITOR"
        space = next(space for space in area.spaces if space.type == 'IMAGE_EDITOR')
        space.image = img

        return {'FINISHED'}


class ScriptCompilerMessageList(bpy.types.UIList):
    bl_idname = "SCRIPT_EDITOR_UL_message_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        compiler = data
        message = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="{},{}: {}".format(message.start_line, message.start_column, message.text), icon=message_type_items[message.type].icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon=message_type_items[message.type].icon)


class ScriptEditorPanel:
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'TEXT_EDITOR' and space.text is not None


class ScriptCompilePanel(bpy.types.Panel, ScriptEditorPanel):
    """Script Compiler"""
    bl_label = "Compile Script"
    bl_idname = "SCRIPT_EDITOR_PT_compile"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"

    def draw(self, context):
        text = context.space_data.text
        compiler = text.script_compiler
        layout = self.layout

        row = layout.row()
        row.operator("script_editor.compile")
        row2 = row.row()
        row2.alignment = 'RIGHT'
        row2.label(text=compiler.status, icon=status_items[compiler.status].icon)

        row = layout.row()
        row.operator("script_editor.dot_image")
        row.operator("script_editor.dot_export")

        row = layout.row()
        row.label(text="{} Errors".format(compiler.num_errors), icon=message_type_items['ERROR'].icon)
        row.label(text="{} Warnings".format(compiler.num_warnings), icon=message_type_items['WARNING'].icon)

        layout.template_list("SCRIPT_EDITOR_UL_message_list", "", compiler, "messages", compiler, "active_message")


def on_active_message_updated(self, context):
    text = context.space_data.text
    message = self.messages[self.active_message]
    if message is not None:
        # Subtract 1 because source location starts at 1, Blender text selection starts at 0.
        text.select_set(
            line_start=message.start_line - 1,
            char_start=message.start_column - 1,
            line_end=message.end_line - 1,
            char_end=message.end_column - 1
        )


def register():
    bpy.types.Text.script_compiler = PointerProperty(type=bpy.types.ScriptCompiler)
    bpy.types.ScriptCompiler.active_message = IntProperty(default=0, update=on_active_message_updated)

    bpy.utils.register_class(ScriptCompileOperator)
    bpy.utils.register_class(ScriptDotExportOperator)
    bpy.utils.register_class(ScriptDotImageOperator)
    bpy.utils.register_class(ScriptCompilerMessageList)
    bpy.utils.register_class(ScriptCompilePanel)


def unregister():
    del bpy.types.Text.script_compiler
    del bpy.types.ScriptCompiler.active_message

    bpy.utils.unregister_class(ScriptCompileOperator)
    bpy.utils.unregister_class(ScriptDotExportOperator)
    bpy.utils.unregister_class(ScriptDotImageOperator)
    bpy.utils.unregister_class(ScriptCompilerMessageList)
    bpy.utils.unregister_class(ScriptCompilePanel)
