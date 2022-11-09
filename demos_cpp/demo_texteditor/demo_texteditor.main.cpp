#include <imgui.h>
#include "imgui_bundle/imgui_bundle.h"
#include "ImGuiColorTextEdit/TextEditor.h"

int main(int , char *[])
{
    std::string code = R"(
from __future__ import annotations
import copy
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional

from srcmlcpp.cpp_types.scope.cpp_scope import CppScope, CppScopePart, CppScopeType
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.blocks.cpp_unit import CppUnit


__all__ = ["CppElement", "CppElementsVisitorFunction", "CppElementsVisitorEvent"]


class CppElement(SrcmlWrapper):
    """
    Base class of all the cpp types"""

    # the parent of this element (will be None for the root, which is a CppUnit)
    # at construction time, this field is absent (hasattr return False)!
    # It will be filled later by CppBlock.fill_parents() (with a tree traversal)
    parent: Optional[CppElement]

    # members that are always copied as shallow members (this is intentionally a static list)
    CppElement__deep_copy_force_shallow_ = ["parent"]

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element.options, element.srcml_xml, element.filename)
        # self.parent is intentionally not filled!

    def __deepcopy__(self, memo=None):
        """CppElement.__deepcopy__: force shallow copy of the parent
        This improves the performance a lot.
        Reason: when we deepcopy, we only intend to modify children.
        """

        # __deepcopy___ "manual":
        #   See https://stackoverflow.com/questions/1500718/how-to-override-the-copy-deepcopy-operations-for-a-python-object
        #   (Antony Hatchkins's answer here)

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in CppElement.CppElement__deep_copy_force_shallow_:
                setattr(result, k, copy.deepcopy(v, memo))
            else:
                setattr(result, k, v)
        return result

    def str_code(self) -> str:
        """Returns a C++ textual representation of the contained code element.
        By default, it returns an exact copy of the original code.

        Derived classes override this implementation and str_code will return a string that differs
         a little from the original code, because it is based on information stored in these derived classes.
        """
        return self.str_code_verbatim()

)";

    TextEditor editor;
    editor.SetText(code);
    editor.SetPalette(TextEditor::GetLightPalette());
    editor.SetLanguageDefinition(TextEditor::LanguageDefinition::Python());

    auto gui = [&](){
        editor.Render("Editor");
    };

    ImGuiBundle::Run(HelloImGui::SimpleRunnerParams{.guiFunction=gui, .windowTitle="Text Editor", .windowSize={800, 500}});

    return 0;
}
