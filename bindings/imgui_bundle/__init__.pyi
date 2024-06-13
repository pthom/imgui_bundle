from . import imgui as imgui

from . import hello_imgui as hello_imgui
from . import implot as implot
from . import imgui_color_text_edit as imgui_color_text_edit
from . import imgui_node_editor as imgui_node_editor
from . import imgui_knobs as imgui_knobs
from . import im_file_dialog as im_file_dialog
from . import imspinner as imspinner
from . import imgui_md as imgui_md
from . import immvision as immvision
from . import imguizmo as imguizmo
from . import imgui_tex_inspect as imgui_tex_inspect
from . import imgui_command_palette as imgui_command_palette
from . import immapp as immapp
from . import imgui_toggle as imgui_toggle
from . import portable_file_dialogs as portable_file_dialogs

# Note: to enable font awesome 6:
#     runner_params.callbacks.default_icon_font = hello_imgui.DefaultIconFont.font_awesome6
from .immapp import icons_fontawesome_4 as icons_fontawesome_4
from .immapp import icons_fontawesome_4 as icons_fontawesome  # noqa # (icons_fontawesome is V4)
from .immapp import icons_fontawesome_6 as icons_fontawesome_6

from . import im_cool_bar as im_cool_bar
from . import nanovg as nanovg

from .imgui import ImVec2 as ImVec2, ImVec4 as ImVec4, ImColor as ImColor
from .imgui_pydantic import ImVec2_Pydantic as ImVec2_Pydantic, ImVec4_Pydantic as ImVec4_Pydantic, ImColor_Pydantic as ImColor_Pydantic
from .im_col32 import IM_COL32 as IM_COL32

def compilation_time() -> str:
    """Return date and time when imgui_bundle was compiled"""
    pass
