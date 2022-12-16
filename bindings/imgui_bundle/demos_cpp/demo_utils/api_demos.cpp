#include "api_demos.h"
#include "code_str_utils.h"
#include "imgui_md/imgui_md_wrapper.h"


void RenderMdUnindented(const std::string& md_str, bool flag_strip_empty_lines)
{
    auto s = UnindentCode(md_str, flag_strip_empty_lines, true);
    ImGuiMd::Render(s);
}
