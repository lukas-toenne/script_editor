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


status_items = bpy.types.ScriptCompiler.bl_rna.properties['status'].enum_items
message_type_items = bpy.types.ScriptCompilerMessage.bl_rna.properties['type'].enum_items


class  ScriptCompileOperator(bpy.types.Operator):
    """Compile script"""
    bl_idname = "script_editor.compile"
    bl_label = "Compile"

    compiler: PointerProperty(type=bpy.types.ScriptCompiler)

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'TEXT_EDITOR':
            if context.space_data.text:
                return True
        return False

    def execute(self, context):
        text = context.space_data.text
        text.script_compiler.compile_script(source_id=text, source=text.as_string())
        return {'FINISHED'}


class ScriptCompilerMessageList(bpy.types.UIList):
    bl_idname = "script_editor.message_list"

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
        row.label(text="{} Errors".format(compiler.num_errors), icon=message_type_items['ERROR'].icon)
        row.label(text="{} Warnings".format(compiler.num_warnings), icon=message_type_items['WARNING'].icon)

        layout.template_list("script_editor.message_list", "", compiler, "messages", compiler, "active_message")




def register():
    bpy.types.Text.script_compiler = PointerProperty(type=bpy.types.ScriptCompiler)
    bpy.types.ScriptCompiler.active_message = IntProperty(default=0)

    bpy.utils.register_class(ScriptCompileOperator)
    bpy.utils.register_class(ScriptCompilerMessageList)
    bpy.utils.register_class(ScriptCompilePanel)


def unregister():
    del bpy.types.Text.script_compiler
    del bpy.types.ScriptCompiler.active_message

    bpy.utils.unregister_class(ScriptCompileOperator)
    bpy.utils.unregister_class(ScriptCompilerMessageList)
    bpy.utils.unregister_class(ScriptCompilePanel)
