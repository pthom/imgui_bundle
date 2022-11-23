#include "functions_composition_graph/functions_composition_graph.h"
#include "imgui_bundle/imgui_bundle.h"
#include "imgui-node-editor/imgui_node_editor.h"


using namespace VisualProg;


struct IntWithGui: public AnyDataWithGui
{
    int _value = 0;

    IntWithGui(int value): _value(value){}

    virtual void GuiData(std::string_view function_name) override
    {
        ImGui::Text("%s", function_name.data());
        ImGui::Text("Int Value %i", _value);
    }

    std::shared_ptr<AnyDataWithGui> GuiSetInput() override
    {
        ImGui::SetNextItemWidth(100.f);
        int v = _value;
        bool changed = ImGui::SliderInt("value", &v, 0, 1000);
        if (changed)
            return std::make_shared<IntWithGui>(v);
        else
            return nullptr;
    }
};

struct AddWithGui: public FunctionWithGui
{
    int _whatToAdd = 1;

    AnyDataWithGuiPtr f(const AnyDataWithGuiPtr& x) override
    {
        auto asInt = dynamic_cast<IntWithGui*>(x.get());
        assert(asInt);
        auto r = std::make_shared<IntWithGui>(asInt->_value + _whatToAdd);
        return r;
    }

    std::string Name() override { return "Add"; }

    virtual bool GuiParams() override
    {
        ImGui::SetNextItemWidth(75.f);
        bool changed = ImGui::SliderInt("What to add", &_whatToAdd, 0, 10);
        return changed;
    }

};

/*
 */

int main(int, char**)
{
    std::vector<FunctionWithGuiPtr> functions = {
        std::make_shared<AddWithGui>(),
        std::make_shared<AddWithGui>(),
        std::make_shared<AddWithGui>(),
    };

    FunctionsCompositionGraph functions_graph(functions);
    functions_graph.SetInput( std::make_shared<IntWithGui>(1) );

    auto gui = [&]() {
        functions_graph.Draw();
    };

    ImGuiBundle::AddOnsParams addOnsParams;

    ax::NodeEditor::Config config;
    config.SettingsFile = "add.json";
    //addOnsParams.withNodeEditorConfig =
    addOnsParams.withNodeEditorConfig = config;

    HelloImGui::SimpleRunnerParams params;
    params.guiFunction = gui;
    params.windowSize = {1200, 600};

    ImGuiBundle::Run(params, addOnsParams);

    return 0;
}