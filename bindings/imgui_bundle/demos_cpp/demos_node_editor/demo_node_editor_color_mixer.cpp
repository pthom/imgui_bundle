// Node editor: a color mixer
//
// Colors flow through a small graph: pick two colors, mix them, and see the result in the swatches. Each link is drawn
// in the color it carries. A first graph with imgui-node-editor (https://github.com/thedmd/imgui-node-editor): the
// nodes, pins and links that the app owns, and how the user edits them.
#ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui-node-editor/imgui_node_editor.h"
#include "imgui_node_editor_immapp/node_editor_default_context.h"  // UpdateNodeEditorColorsFromImguiColors
#include "imgui_rich_md/rich_md.h"
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "imgui_internal.h"  // ImLerp

#include <algorithm>
#include <memory>
#include <string>
#include <vector>

namespace ed = ax::NodeEditor;

namespace
{

const float NODE_WIDTH_EM = 9.0f;  // the width of a node's content
const float SWATCH_SIZE_EM = 5.0f;  // the side of a swatch's square
const float PIN_RADIUS_EM = 0.4f;  // the radius of a pin's circle
const float LINK_THICKNESS = 3.0f;  // the thickness of the links (they follow the zoom)
const ImVec4 UNLINKED(0.3f, 0.3f, 0.3f, 1.0f);  // the color an input receives when no link reaches it

// The gestures, in markdown ("  \n" ends a line)
const char* HELP =
    "**Link** two pins: drag from one to the other  ·  "
    "**Delete** a node or a link: select it, then <kbd>Delete</kbd>  \n"
    "**Add a node**: right-click the background  ·  **Pan**: right-drag  ·  **Zoom**: the wheel  ·  "
    "**See the whole graph**: <kbd>F</kbd>";

// The kinds of node. Every kind has one output, except the swatch, which shows its input.
enum class Kind { Color, Mix, Invert, Grayscale, Swatch };

struct KindInfo
{
    const char* name;
    std::vector<const char*> inputs;  // the names of its input pins
    const char* doc;  // what it does, shown under its title (markdown, with math between $ signs)
};

const std::vector<KindInfo> KINDS = {  // in the order of Kind
    {"Color", {}, "Pick a color"},
    {"Mix", {"a", "b"}, R"($(1-t)\,a + t\,b$)"},
    {"Invert", {"in"}, R"($1 - c$, per channel)"},
    {"Grayscale", {"in"}, R"($0.3\,r + 0.59\,g + 0.11\,b$)"},
    {"Swatch", {"in"}, "Show the color"},
};

const KindInfo& Info(Kind kind) { return KINDS[(size_t)kind]; }


// =====================================================================================================================
// 1. The graph: nodes, pins and links
// =====================================================================================================================
// The editor draws the graph and lets the user edit it, but it does not store it: the app owns its nodes, pins and
// links, and submits them at each frame. Each of them has an id (ed::NodeId, ed::PinId, ed::LinkId), which must stay
// the same from one frame to the next: here, a counter gives new ones.
uintptr_t NewId()
{
    static uintptr_t lastId = 0;
    return ++lastId;
}

struct Node;

struct Pin
{
    std::string name;
    ed::PinKind kind;  // an input (on the left of its node) or an output (on the right)
    Node* node;
    ed::PinId id = ed::PinId(NewId());
};

struct Node
{
    Kind kind;
    ed::NodeId id = ed::NodeId(NewId());
    std::vector<std::unique_ptr<Pin>> inputs;  // the pins are owned by pointers: the links point to them
    std::unique_ptr<Pin> output;  // null for a swatch
    ImVec4 color = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);  // what a Color node gives
    float mix = 0.5f;  // t: a Mix node's share of b

    Node(Kind kind_, ImVec4 color_) : kind(kind_), color(color_)
    {
        for (const char* name : Info(kind).inputs)
            inputs.push_back(std::make_unique<Pin>(Pin{name, ed::PinKind::Input, this}));
        if (kind != Kind::Swatch)
            output = std::make_unique<Pin>(Pin{"out", ed::PinKind::Output, this});
    }
};

struct Link
{
    Pin* start;  // an output
    Pin* end;  // an input
    ed::LinkId id = ed::LinkId(NewId());
};

struct Graph
{
    std::vector<std::unique_ptr<Node>> nodes;  // owned by pointers: the pins point to their node
    std::vector<Link> links;

    Node* AddNode(Kind kind, ImVec2 positionEm, ImVec4 color = ImVec4(1.0f, 1.0f, 1.0f, 1.0f))
    {
        nodes.push_back(std::make_unique<Node>(kind, color));
        Node* node = nodes.back().get();
        // The editor keeps the positions: we only give the first one. They are in the editor's coordinates (pixels
        // at zoom 1), which is why we convert from em.
        ed::SetNodePosition(node->id, positionEm * HelloImGui::EmSize());
        return node;
    }

    void Connect(Pin* output, Pin* input)
    {
        std::erase_if(links, [input](const Link& link) { return link.end == input; });  // an input receives one link at most
        links.push_back(Link{output, input});
    }

    void RemoveNode(Node* node)
    {
        std::erase_if(links, [node](const Link& link) { return link.start->node == node || link.end->node == node; });
        std::erase_if(nodes, [node](const std::unique_ptr<Node>& n) { return n.get() == node; });
    }

    Pin* FindPin(ed::PinId pinId)
    {
        for (auto& node : nodes)
        {
            for (auto& pin : node->inputs)
                if (pin->id == pinId)
                    return pin.get();
            if (node->output && node->output->id == pinId)
                return node->output.get();
        }
        return nullptr;
    }

    // True if `node` is `other`, or feeds it through links
    bool Feeds(const Node* node, const Node* other) const
    {
        if (node == other)
            return true;
        for (const Link& link : links)
            if (link.end->node == other && Feeds(node, link.start->node))
                return true;
        return false;
    }
};

Graph InitialGraph()
{
    Graph graph;
    Node* red = graph.AddNode(Kind::Color, ImVec2(0, 0), ImVec4(0.95f, 0.2f, 0.2f, 1.0f));
    Node* blue = graph.AddNode(Kind::Color, ImVec2(0, 9), ImVec4(0.2f, 0.35f, 0.95f, 1.0f));
    Node* mix = graph.AddNode(Kind::Mix, ImVec2(13, 4));
    Node* swatch = graph.AddNode(Kind::Swatch, ImVec2(26, 0));
    Node* invert = graph.AddNode(Kind::Invert, ImVec2(26, 12));
    Node* swatch2 = graph.AddNode(Kind::Swatch, ImVec2(39, 10));
    graph.Connect(red->output.get(), mix->inputs[0].get());
    graph.Connect(blue->output.get(), mix->inputs[1].get());
    graph.Connect(mix->output.get(), swatch->inputs[0].get());
    graph.Connect(mix->output.get(), invert->inputs[0].get());
    graph.Connect(invert->output.get(), swatch2->inputs[0].get());
    return graph;
}


// =====================================================================================================================
// 2. What the nodes compute
// =====================================================================================================================
// Colors are cheap: the whole graph is computed again at each frame, from each node back to its sources.
ImVec4 NodeColor(const Graph& graph, const Node& node);

ImVec4 InputColor(const Graph& graph, const Pin* pin)
{
    for (const Link& link : graph.links)
        if (link.end == pin)
            return NodeColor(graph, *link.start->node);
    return UNLINKED;
}

// The color that a node gives (for a swatch: the color it shows)
ImVec4 NodeColor(const Graph& graph, const Node& node)
{
    std::vector<ImVec4> inputs;
    for (const auto& pin : node.inputs)
        inputs.push_back(InputColor(graph, pin.get()));
    switch (node.kind)
    {
        case Kind::Color:
            return node.color;
        case Kind::Mix:
            return ImLerp(inputs[0], inputs[1], node.mix);
        case Kind::Invert:
        {
            const ImVec4& c = inputs[0];
            return ImVec4(1.0f - c.x, 1.0f - c.y, 1.0f - c.z, c.w);
        }
        case Kind::Grayscale:
        {
            const ImVec4& c = inputs[0];
            float luminance = 0.299f * c.x + 0.587f * c.y + 0.114f * c.z;
            return ImVec4(luminance, luminance, luminance, c.w);
        }
        case Kind::Swatch:
            return inputs[0];
    }
    return UNLINKED;
}


// =====================================================================================================================
// 3. Drawing the graph
// =====================================================================================================================
// Between ed::Begin() and ed::End(), a node is drawn with ordinary widgets, between ed::BeginNode() and ed::EndNode().
// The widgets drawn between ed::BeginPin() and ed::EndPin() become the pin: the user drags a link from them.
void DrawPin(const Pin& pin, ImVec4 color)
{
    ed::BeginPin(pin.id, pin.kind);
    ed::PinPivotAlignment(ImVec2(0.5f, 0.5f));  // the links reach the center of the circle...
    ed::PinPivotSize(ImVec2(0, 0));  // ...and not the edge of the pin's rectangle
    float radius = HelloImGui::EmSize(PIN_RADIUS_EM);
    ImVec2 topLeft = ImGui::GetCursorScreenPos();
    ImGui::Dummy(ImVec2(2 * radius, 2 * radius));  // the space of the pin; the draw list paints it
    ImVec2 center = topLeft + ImVec2(radius, radius);
    ImDrawList* drawList = ImGui::GetWindowDrawList();
    drawList->AddCircleFilled(center, radius, ImGui::GetColorU32(color));
    drawList->AddCircle(center, radius, ImGui::GetColorU32(ImGuiCol_Text), 0, 1.5f);
    ed::EndPin();
}

void DrawNode(Graph& graph, Node& node)
{
    float width = HelloImGui::EmSize(NODE_WIDTH_EM);
    ed::BeginNode(node.id);
    ImGui::PushID((int)node.id.Get());  // the widgets of two nodes of the same kind need different ids
    // The title, and on the next line the doc
    RichMd::Render(std::string("**") + Info(node.kind).name + "**  \n" + Info(node.kind).doc);
    ImGui::Dummy(ImVec2(width, 0));  // the node's width: its text wraps at it (see Editor())

    for (auto& pin : node.inputs)  // the inputs, on the left
    {
        DrawPin(*pin, InputColor(graph, pin.get()));
        ImGui::SameLine();
        ImGui::Text("%s", pin->name.c_str());
    }

    // The widgets of the node. A color picker opens its popup from inside the node, as it would anywhere else.
    if (node.kind == Kind::Color)
    {
        ImGui::SetNextItemWidth(width);
        ImGui::ColorEdit4("##color", &node.color.x, ImGuiColorEditFlags_NoAlpha);
    }
    else if (node.kind == Kind::Mix)
    {
        ImGui::SetNextItemWidth(width);
        ImGui::SliderFloat("##mix", &node.mix, 0.0f, 1.0f, "t = %.2f");
    }
    else if (node.kind == Kind::Swatch)
    {
        float swatchSize = HelloImGui::EmSize(SWATCH_SIZE_EM);
        ImGui::ColorButton("##swatch", NodeColor(graph, node), 0, ImVec2(swatchSize, swatchSize));
    }

    if (node.output)  // the output, on the right
    {
        ImGui::BeginHorizontal("output", ImVec2(width, 0));
        ImGui::Spring();
        ImGui::Text("%s", node.output->name.c_str());
        DrawPin(*node.output, NodeColor(graph, node));
        ImGui::EndHorizontal();
    }

    ImGui::PopID();
    ed::EndNode();
}

void DrawLinks(const Graph& graph)
{
    for (const Link& link : graph.links)
        ed::Link(link.id, link.start->id, link.end->id, NodeColor(graph, *link.start->node), LINK_THICKNESS);
}


// =====================================================================================================================
// 4. Letting the user edit the graph
// =====================================================================================================================
// The editor tells what the user wants (a new link, a deletion); the app decides, and changes its graph.

// Why a link from `output` to `input` is refused ("" if it is accepted)
std::string WhyNot(const Pin& output, const Pin& input, const Graph& graph)
{
    if (output.kind != ed::PinKind::Output || input.kind != ed::PinKind::Input)
        return "A link goes from an output (right) to an input (left)";
    if (graph.Feeds(input.node, output.node))
        return "This link would make a loop";
    return "";
}

void HandleNewLinks(Graph& graph)
{
    // ed::EndCreate() only when ed::BeginCreate() returned true
    if (ed::BeginCreate(ImVec4(1.0f, 1.0f, 1.0f, 1.0f), 2.0f))
    {
        ed::PinId startId, endId;
        // True while the user drags a link; the ids are filled with the pins at its two ends (0 when there is none
        // yet). The drag may start from an input or from an output.
        if (ed::QueryNewLink(&startId, &endId))
        {
            Pin* start = graph.FindPin(startId);
            Pin* end = graph.FindPin(endId);
            if (start != nullptr && end != nullptr)  // the mouse is over a second pin
            {
                bool startIsInput = (start->kind == ed::PinKind::Input);
                Pin* output = startIsInput ? end : start;
                Pin* input = startIsInput ? start : end;
                std::string reason = WhyNot(*output, *input, graph);
                if (!reason.empty())
                {
                    ed::RejectNewItem(ImVec4(1.0f, 0.3f, 0.3f, 1.0f), 2.0f);  // the link turns red
                    ImGui::SetTooltip("%s", reason.c_str());
                }
                else
                {
                    ImGui::SetTooltip("Release to link");
                    if (ed::AcceptNewItem())  // true when the user releases the mouse
                        graph.Connect(output, input);
                }
            }
        }
        ed::EndCreate();
    }
}

void HandleDeletions(Graph& graph)
{
    if (ed::BeginDelete())
    {
        // The Delete key, or ed::DeleteNode() below, sends the selected items here, one by one
        ed::LinkId linkId;
        while (ed::QueryDeletedLink(&linkId))
            if (ed::AcceptDeletedItem())
                std::erase_if(graph.links, [linkId](const Link& link) { return link.id == linkId; });
        ed::NodeId nodeId;
        while (ed::QueryDeletedNode(&nodeId))
        {
            if (ed::AcceptDeletedItem())
            {
                auto it = std::find_if(graph.nodes.begin(), graph.nodes.end(),
                                       [nodeId](const std::unique_ptr<Node>& node) { return node->id == nodeId; });
                if (it != graph.nodes.end())
                    graph.RemoveNode(it->get());
            }
        }
        ed::EndDelete();
    }
}

struct MenuState
{
    ImVec2 newNodePosition;  // where the background menu was opened
    ed::NodeId nodeId;  // the node whose menu is open
};

void HandleMenus(Graph& graph, MenuState& menu)
{
    if (ed::ShowBackgroundContextMenu())
    {
        ImGui::OpenPopup("Add a node");
        menu.newNodePosition = ed::GetMousePosOnCanvas();  // in the editor's coordinates, as the node positions
    }
    if (ImGui::BeginPopup("Add a node"))
    {
        for (size_t i = 0; i < KINDS.size(); i++)
            if (ImGui::MenuItem(KINDS[i].name))
                graph.AddNode((Kind)i, menu.newNodePosition / HelloImGui::EmSize());
        ImGui::EndPopup();
    }

    if (ed::ShowNodeContextMenu(&menu.nodeId))
        ImGui::OpenPopup("Node");
    if (ImGui::BeginPopup("Node"))
    {
        if (ImGui::MenuItem("Delete"))
            ed::DeleteNode(menu.nodeId);  // the node then goes through HandleDeletions()
        ImGui::EndPopup();
    }
}


// =====================================================================================================================
// 5. The app
// =====================================================================================================================
struct AppState
{
    ed::EditorContext* editor = nullptr;  // the demo's own editor (see Editor())
    std::unique_ptr<Graph> graph;  // created at the first frame: the node positions need the editor
    MenuState menu;
    int frame = 0;
};

AppState& State()
{
    static AppState state;
    return state;
}

// The demo's own editor, with its own config, whatever the app that shows it: an app such as the bundle's explorer
// shows several node editor demos, which need different configs.
ed::EditorContext* Editor()
{
    AppState& state = State();
    if (!state.editor)
    {
        ed::Config config;
        config.SettingsFile = nullptr;  // the demo places its nodes at start: nothing to save
        // The text wraps at the width of the node, not of the window
        config.ForceWindowContentWidthToNodeWidth = true;
        state.editor = ed::CreateEditor(&config);
    }
    return state.editor;
}

}  // namespace

void gui_demo_node_editor_color_mixer()
{
    AppState& state = State();
    RichMd::Render(HELP);
    ed::EditorContext* previousEditor = ed::GetCurrentEditor();
    ed::SetCurrentEditor(Editor());
    // Its colors follow the theme, light or dark (immapp does it for its own editor only)
    UpdateNodeEditorColorsFromImguiColors();
    ed::Begin("Color mixer");
    if (!state.graph)
        state.graph = std::make_unique<Graph>(InitialGraph());
    for (auto& node : state.graph->nodes)
        DrawNode(*state.graph, *node);
    DrawLinks(*state.graph);
    HandleNewLinks(*state.graph);
    HandleDeletions(*state.graph);
    HandleMenus(*state.graph, state.menu);
    ed::End();

    // Fit the graph in the view, once the editor knows the size of the nodes: at the third frame (at the second, the
    // fit has no effect). The navigation functions work after ed::End().
    if (state.frame == 2)
        ed::NavigateToContent(0.0f);
    state.frame++;
    ed::SetCurrentEditor(previousEditor);
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    HelloImGui::RunnerParams params;
    params.callbacks.ShowGui = gui_demo_node_editor_color_mixer;
    params.appWindowParams.windowTitle = "Node editor: a color mixer";
    params.appWindowParams.windowGeometry.size = {1100, 600};
    params.callbacks.BeforeExit = [] { ed::DestroyEditor(Editor()); };
    ImmApp::AddOnsParams addOns;  // the demo creates its own node editor
    addOns.withLatex = true;  // implies withMarkdown
    ImmApp::Run(params, addOns);
    return 0;
}
#endif

#else // #ifdef IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR
#include "imgui.h"
void gui_demo_node_editor_color_mixer() { ImGui::Text("This demo requires imgui-node-editor"); }
#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
#include <cstdio>
int main(int, char**) { printf("This demo requires imgui-node-editor\n"); return 0; }
#endif
#endif
