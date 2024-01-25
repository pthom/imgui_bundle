#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui.h"

#include <string>
#include <memory>
#include <vector>


namespace ed = ax::NodeEditor;

namespace
{
    uintptr_t _next_id = 0;
    uintptr_t get_next_id() { return ++_next_id; }
}


struct Lover
{
    std::string name;
    ed::NodeId nodeId;
    ed::PinId pinLoves;
    ed::PinId pinHates;
    ed::PinId pinIn;

    explicit Lover(std::string _name) : name(std::move(_name))
    {
        nodeId = ed::NodeId(get_next_id());
        pinLoves = ed::PinId(get_next_id());
        pinHates = ed::PinId(get_next_id());
        pinIn = ed::PinId(get_next_id());
    }

    void Draw() const
    {
        ed::BeginNode(nodeId);
        ed::BeginPin(pinIn, ed::PinKind::Input);
        ImGui::Text("%s", name.c_str());
        ed::EndPin();
        ed::BeginPin(pinLoves, ed::PinKind::Output);
        ImGui::Text("Loves");
        ed::EndPin();
        ed::BeginPin(pinHates, ed::PinKind::Output);
        ImGui::Text("Hates");
        ed::EndPin();
        ed::EndNode();
    }
};


struct Tie
{
    std::shared_ptr<Lover> lover;
    std::shared_ptr<Lover> loved;
    std::string kind;
    ed::LinkId id;

    Tie(std::shared_ptr<Lover> _lover, const char* _kind, std::shared_ptr<Lover> _loved)
    {
        auto& self = *this;
        self.id = ed::LinkId(get_next_id());
        self.lover = std::move(_lover);
        self.loved = std::move(_loved);
        self.kind = _kind;
    }

    void Draw() const
    {
        auto& self = *this;
        ImVec4 red(1.0, 0.3, 0.2, 1.0);
        ImVec4 green(0.3, 0.9, 0.0, 1.0);
        if (kind == "loves")
            ed::Link(self.id, self.lover->pinLoves, self.loved->pinIn, green);
        else
            ed::Link(self.id, self.lover->pinHates, self.loved->pinIn, red);
    }
};


void demo_romeo_and_juliet()
{
    static std::vector<std::shared_ptr<Lover>> lovers;
    static std::vector<Tie> links;

    if (lovers.empty())
    {
        auto Romeo = std::make_shared<Lover>("Romeo");
        auto Juliet = std::make_shared<Lover>("Juliet");
        auto CountParis = std::make_shared<Lover>("Count Paris");
        lovers = { Romeo, Juliet, CountParis };

        links = {
            {Romeo, "loves", Juliet},
            {Juliet, "loves", Romeo},

            {CountParis, "loves", Juliet},

            {CountParis, "hates", Romeo},
            {Romeo, "hates", CountParis}
        };
    }

    // ed::GetConfig().SettingsFile = "romeo_and_juliet.json"; // GetConfig() is const!
    ed::Begin("Romeo and Juliet");
    for (auto &lover: lovers)
        lover->Draw();
    for (auto &link: links)
        link.Draw();
    ed::End();
}

#else // #ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "imgui.h"
void demo_romeo_and_juliet() { ImGui::Text("This demo requires ImGui Node Editor\n"); }
#endif