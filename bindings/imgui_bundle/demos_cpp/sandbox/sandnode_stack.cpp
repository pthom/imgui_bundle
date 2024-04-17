#include "imgui.h"
#include "immapp/runner.h"
#include "hello_imgui/hello_imgui.h"

#include <string>
#include <vector>

struct ItemInfo
{
    std::string Name;
    std::string Description;
    bool IsSelected = false;
};

std::vector<ItemInfo> AllInfo{
    {
        {"Italian Salad", "A delicious salad with tomatoes, mozzarella, basil, and olive oil."},
        {"Greek Salad", "A delicious salad with tomatoes, feta, olives, and olive oil."},
        {"Caesar Salad", "A delicious salad with lettuce, croutons, parmesan, and Caesar dressing."},
        {"Nicoise Salad", "A delicious salad with tuna, green beans, olives, and olive oil."},
        {"Waldorf Salad", "A delicious salad with apples, walnuts, celery, and mayonnaise."},
    }
};

void gui()
{
    ImGui::BeginVertical("Infos");
    for(auto & info: AllInfo)
    {
        ImGui::PushID(&info);
        ImGui::BeginHorizontal("Info");        // All widgets layout horizontally here
        ImGui::Text("%s", info.Name.c_str());  // Display the name at the left
        ImGui::Spring();                       // A flexible space that grows
        ImGui::Checkbox("", &info.IsSelected); // As a consequence, all checkbox are right-aligned
        ImGui::EndHorizontal();
        ImGui::PopID();
    }
    ImGui::EndVertical();
}


int main()
{
    ImmApp::Run(gui, "Salads");
    return 0;
}