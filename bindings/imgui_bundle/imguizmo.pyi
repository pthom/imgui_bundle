from typing import List, Optional, Tuple
from imgui_bundle.imgui import ImVec2, ImVec4
from imgui_bundle.imgui.internal import ImRect
import enum


ImGuiZoomSliderFlags = int
ImGuiZoomSliderFlags_None = ImZoomSlider.ImGuiZoomSliderFlags_.none


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:ImCurveEditStl.h>    ####################
# THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmoStl/ImCurveEditStl.h                                                           //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmo/ImCurveEdit.h included by ImGuizmoStl/ImCurveEditStl.h                        //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
# https://github.com/CedricGuillemet/ImGuizmo
# v 1.89 WIP
#
# The MIT License(MIT)
#
# Copyright(c) 2021 Cedric Guillemet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmoStl/ImCurveEditStl.h continued                                                 //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////




# <submodule ImCurveEdit>
class ImCurveEdit:  # Proxy class that introduces typings for the *submodule* ImCurveEdit
    pass  # (This corresponds to a C++ namespace. All method are static!)
    class CurveType(enum.Enum):
        curve_none = enum.auto()     # (= 0)
        curve_discrete = enum.auto() # (= 1)
        curve_linear = enum.auto()   # (= 2)
        curve_smooth = enum.auto()   # (= 3)
        curve_bezier = enum.auto()   # (= 4)

    class EditPoint:
        curve_index: int
        point_index: int
        def __lt__(self, other: EditPoint) -> bool:
            pass
        def __init__(self) -> None:
            """Autogenerated default constructor"""
            pass

    class Delegate:
        focused: bool = False
        def get_curve_count(self) -> int:                    # overridable (pure virtual)
            pass
        def is_visible(self, param_0: int) -> bool:          # overridable
            pass
        def get_curve_type(self, param_0: int) -> CurveType: # overridable
            pass
        def get_min(self) -> ImVec2:                         # overridable (pure virtual)
            pass
        def get_max(self) -> ImVec2:                         # overridable (pure virtual)
            pass
        def get_curve_color(                                 # overridable (pure virtual)
            self,
            curve_index: int
            ) -> int:
            pass
        def edit_point(                                      # overridable (pure virtual)
            self,
            curve_index: int,
            point_index: int,
            value: ImVec2
            ) -> int:
            pass
        def add_point(                                       # overridable (pure virtual)
            self,
            curve_index: int,
            value: ImVec2
            ) -> None:
            pass
        def get_background_color(self) -> int:               # overridable
            pass
        # handle undo/redo thru this functions
        def begin_edit(self, param_0: int) -> None:          # overridable
            pass
        def end_edit(self) -> None:                          # overridable
            pass
        def __init__(self) -> None:
            """Autogenerated default constructor"""
            pass


    class DelegateStl(ImCurveEdit.Delegate):

        def get_points_list( # overridable (pure virtual)
            self,
            curve_index: int
            ) -> List[ImVec2]:
            pass

        def __init__(self) -> None:
            """Autogenerated default constructor"""
            pass

    def edit_stl(
        delegate: DelegateStl,
        size: ImVec2,
        id: int,
        clipping_rect: Optional[ImRect] = None
        ) -> Tuple[int, List[EditPoint]]:
        pass


# </submodule ImCurveEdit>
####################    </generated_from:ImCurveEditStl.h>    ####################


####################    <generated_from:ImGradientStl.h>    ####################
# THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.






#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmoStl/ImGradientStl.h continued                                                  //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////



# <submodule ImGradient>
class ImGradient:  # Proxy class that introduces typings for the *submodule* ImGradient
    pass  # (This corresponds to a C++ namespace. All method are static!)
    class Delegate:
        def edit_point(                             # overridable (pure virtual)
            self,
            point_index: int,
            value: ImVec4
            ) -> int:
            pass
        def get_point(self, t: float) -> ImVec4:    # overridable (pure virtual)
            pass
        def add_point(self, value: ImVec4) -> None: # overridable (pure virtual)
            pass
        def __init__(self) -> None:
            """Autogenerated default constructor"""
            pass

    class DelegateStl(ImGradient.Delegate):

        def get_points_list(self) -> List[ImVec4]: # overridable (pure virtual)
            pass

        def __init__(self) -> None:
            """Autogenerated default constructor"""
            pass

    def edit_stl(delegate: DelegateStl, size: ImVec2) -> Tuple[bool, int]:
        pass

# </submodule ImGradient>
####################    </generated_from:ImGradientStl.h>    ####################


####################    <generated_from:ImZoomSliderStl.h>    ####################
# THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmo/ImZoomSlider.h included by ImGuizmoStl/ImZoomSliderStl.h                      //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////
# https://github.com/CedricGuillemet/ImGuizmo
# v 1.89 WIP
#
# The MIT License(MIT)
#
# Copyright(c) 2021 Cedric Guillemet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# namespace


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#                       ImGuizmoStl/ImZoomSliderStl.h continued                                                //
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////



# <submodule ImZoomSlider>
class ImZoomSlider:  # Proxy class that introduces typings for the *submodule* ImZoomSlider
    pass  # (This corresponds to a C++ namespace. All method are static!)
    class ImGuiZoomSliderFlags_(enum.Enum):
        none = enum.auto()             # (= 0)
        vertical = enum.auto()         # (= 1)
        no_anchors = enum.auto()       # (= 2)
        no_middle_carets = enum.auto() # (= 4)
        no_wheel = enum.auto()         # (= 8)


    def im_zoom_slider_stl(
        lower: float,
        higher: float,
        view_lower: float,
        view_higher: float,
        wheel_ratio: float = 0.01,
        flags: ImGuiZoomSliderFlags = ImGuiZoomSliderFlags_None
        ) -> Tuple[bool, float, float]:
        pass


# </submodule ImZoomSlider>
####################    </generated_from:ImZoomSliderStl.h>    ####################

# </litgen_stub> // Autogenerated code end!