# MIT License
#
# Copyright (c) 2022 Lukas Toenne
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

bl_info = {
    "name": "Script Editor",
    "author": "Lukas Toenne",
    "version": (0, 1),
    "blender": (3, 2, 0),
    "location": "Text Editor",
    "description": "Text editor extensions to integrate with the script compiler",
    "warning": "",
    "doc_url": "",
    "category": "Scripting",
}

import bpy
from . import preferences, text_editor_ui

if "bpy" in locals():
    import importlib
    importlib.reload(preferences)
    importlib.reload(text_editor_ui)

def register():
    preferences.register()
    text_editor_ui.register()

def unregister():
    preferences.unregister()
    text_editor_ui.unregister()

if __name__ == "__main__":
    register()
