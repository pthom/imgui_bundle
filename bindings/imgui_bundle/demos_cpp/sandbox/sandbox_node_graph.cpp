// Test bed for imgui-node-editor.
//
// Features:
//   - Several seeded nodes, each with one input pin + one output pin
//   - Drag from a pin to another pin to create a link
//   - Right-click on the background        -> "Add node" context menu
//   - Right-click on a node / pin / link   -> "Delete" context menu
//   - Hit Delete (or use the popup) to remove selected nodes / links
//   - Status text at the top shows interaction state

#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui.h"
#include "imgui-node-editor/imgui_node_editor.h"

#include <string>
#include <unordered_set>
#include <vector>

namespace ed = ax::NodeEditor;

enum class PinKind { Input, Output };

struct Pin
{
    int       id;
    int       node_id;
    std::string name;
    PinKind   kind;
};

struct Node
{
    int       id;
    std::string name;
    std::vector<Pin> inputs;
    std::vector<Pin> outputs;
    bool      is_group  = false;       // true -> use ed::Group() instead of pins
    bool      collapsed = false;       // groups only: hide member nodes
    ImVec2    group_initial_size{260, 160};
};

struct Link
{
    int id;
    int src_pin_id;
    int dst_pin_id;
};

struct Graph
{
    std::vector<Node> nodes;
    std::vector<Link> links;
    int               next_id = 1;

    int new_id() { return next_id++; }

    Node& add_node(const char* name, int n_in, int n_out)
    {
        Node n;
        n.id   = new_id();
        n.name = name;
        for (int i = 0; i < n_in; ++i)
            n.inputs.push_back({new_id(), n.id, "In " + std::to_string(i + 1), PinKind::Input});
        for (int i = 0; i < n_out; ++i)
            n.outputs.push_back({new_id(), n.id, "Out " + std::to_string(i + 1), PinKind::Output});
        nodes.push_back(std::move(n));
        return nodes.back();
    }

    Node& add_group(const char* name, ImVec2 initial_size = ImVec2(280, 180))
    {
        Node n;
        n.id   = new_id();
        n.name = name;
        n.is_group = true;
        n.group_initial_size = initial_size;
        nodes.push_back(std::move(n));
        return nodes.back();
    }

    const Pin* find_pin(int pin_id) const
    {
        for (const auto& n : nodes)
        {
            for (const auto& p : n.inputs)  if (p.id == pin_id) return &p;
            for (const auto& p : n.outputs) if (p.id == pin_id) return &p;
        }
        return nullptr;
    }

    bool has_link_with_pin(int pin_id) const
    {
        for (const auto& l : links)
            if (l.src_pin_id == pin_id || l.dst_pin_id == pin_id) return true;
        return false;
    }

    void erase_node(int node_id)
    {
        // also remove any link touching one of this node's pins
        std::vector<int> pin_ids;
        for (const auto& n : nodes)
            if (n.id == node_id)
            {
                for (const auto& p : n.inputs)  pin_ids.push_back(p.id);
                for (const auto& p : n.outputs) pin_ids.push_back(p.id);
            }
        links.erase(std::remove_if(links.begin(), links.end(),
            [&](const Link& l) {
                for (int pid : pin_ids)
                    if (l.src_pin_id == pid || l.dst_pin_id == pid) return true;
                return false;
            }), links.end());

        nodes.erase(std::remove_if(nodes.begin(), nodes.end(),
            [&](const Node& n) { return n.id == node_id; }), nodes.end());
    }

    void erase_link(int link_id)
    {
        links.erase(std::remove_if(links.begin(), links.end(),
            [&](const Link& l) { return l.id == link_id; }), links.end());
    }
};

static Graph g_graph;

static void seed_graph()
{
    if (!g_graph.nodes.empty()) return;
    g_graph.add_node("Source A", 0, 1);
    g_graph.add_node("Source B", 0, 1);
    g_graph.add_node("Mix",      2, 1);
    g_graph.add_node("Filter",   1, 1);
    g_graph.add_node("Output",   1, 0);
    g_graph.add_group("Audio chain", ImVec2(380, 220));
}

static void draw_node(const Node& n)
{
    if (n.is_group)
    {
        // Group node: a resizable, labeled rectangle that other nodes can sit
        // inside. Drag the group to drag every node enclosed in it. Drag the
        // bottom-right corner to resize. The size argument here is only used
        // on the very first frame; user resizes are persisted by the editor.
        //
        // Anything we draw before ed::Group(size) lands in the group's title
        // strip. We use that to add a [-]/[+] minimize toggle.
        Node& nm = const_cast<Node&>(n);  // we want to mutate `collapsed`
        ed::BeginNode(ed::NodeId(n.id));
            if (ImGui::SmallButton(n.collapsed ? "+" : "-"))
                nm.collapsed = !nm.collapsed;
            ImGui::SameLine();
            ImGui::TextUnformatted(n.name.c_str());
            if (n.collapsed)
                ImGui::Text("(collapsed)");
            ed::Group(n.group_initial_size);
        ed::EndNode();
        return;
    }

    ed::BeginNode(ed::NodeId(n.id));
        ImGui::TextUnformatted(n.name.c_str());
        ImGui::Dummy(ImVec2(120, 2));

        // Two columns: inputs on the left, outputs on the right.
        ImGui::BeginGroup();
        for (const auto& p : n.inputs)
        {
            ed::BeginPin(ed::PinId(p.id), ed::PinKind::Input);
                ImGui::Text("-> %s", p.name.c_str());
            ed::EndPin();
        }
        ImGui::EndGroup();

        ImGui::SameLine(0, 40);

        ImGui::BeginGroup();
        for (const auto& p : n.outputs)
        {
            ed::BeginPin(ed::PinId(p.id), ed::PinKind::Output);
                ImGui::Text("%s ->", p.name.c_str());
            ed::EndPin();
        }
        ImGui::EndGroup();
    ed::EndNode();
}

// Compute the set of node ids that should be hidden this frame because their
// center sits inside a COLLAPSED group's rectangle. Uses only the public
// editor API (GetNodePosition / GetNodeSize), which return values measured on
// the previous frame -- good enough for membership tests.
static std::unordered_set<int> compute_hidden_node_ids()
{
    std::unordered_set<int> hidden;
    for (const auto& g : g_graph.nodes)
    {
        if (!g.is_group || !g.collapsed) continue;

        ImVec2 g_pos  = ed::GetNodePosition(ed::NodeId(g.id));
        ImVec2 g_size = ed::GetNodeSize(ed::NodeId(g.id));
        if (g_size.x <= 0 || g_size.y <= 0) continue;  // not laid out yet

        for (const auto& n : g_graph.nodes)
        {
            if (n.id == g.id) continue;
            ImVec2 p = ed::GetNodePosition(ed::NodeId(n.id));
            ImVec2 s = ed::GetNodeSize(ed::NodeId(n.id));
            if (s.x <= 0 || s.y <= 0) continue;
            ImVec2 center{p.x + s.x * 0.5f, p.y + s.y * 0.5f};
            if (center.x >= g_pos.x && center.x <= g_pos.x + g_size.x
             && center.y >= g_pos.y && center.y <= g_pos.y + g_size.y)
            {
                hidden.insert(n.id);
            }
        }
    }
    return hidden;
}

// Draw a big, fading title above each Group node — but only once the user has
// zoomed out enough that the in-node title becomes hard to read. The editor
// itself decides when this should appear: BeginGroupHint() returns false at
// normal zoom levels and only returns true when zoom < ~0.75x.
static void draw_group_hints()
{
    for (const auto& n : g_graph.nodes)
    {
        if (!n.is_group) continue;

        if (ed::BeginGroupHint(ed::NodeId(n.id)))
        {
            const ImVec2 group_min = ed::GetGroupMin();
            ImDrawList*  fg        = ed::GetHintForegroundDrawList();

            const ImVec2 text_size = ImGui::CalcTextSize(n.name.c_str());
            const ImVec2 text_pos(group_min.x, group_min.y - text_size.y - 4.0f);

            const ImU32 col = ImGui::GetColorU32(ImGuiCol_Text);
            fg->AddText(text_pos, col, n.name.c_str());
        }
        ed::EndGroupHint();
    }
}

static void handle_create()
{
    if (ed::BeginCreate())
    {
        ed::PinId a, b;
        if (ed::QueryNewLink(&a, &b))
        {
            // QueryNewLink returns true when the user is hovering a candidate
            // endpoint while dragging a link. We must call AcceptNewItem only
            // on mouse release to actually create the link.
            const Pin* pa = g_graph.find_pin((int)a.Get());
            const Pin* pb = g_graph.find_pin((int)b.Get());

            bool can_link = pa && pb
                         && pa->kind != pb->kind                // must be input <-> output
                         && pa->node_id != pb->node_id;         // no self-loop

            if (!can_link)
            {
                ed::RejectNewItem(ImVec4(1, 0.3f, 0.3f, 1), 2.0f);
            }
            else if (ed::AcceptNewItem(ImVec4(0.5f, 1, 0.5f, 1), 3.0f))
            {
                // canonical direction: src = output, dst = input
                int src = pa->kind == PinKind::Output ? pa->id : pb->id;
                int dst = pa->kind == PinKind::Input  ? pa->id : pb->id;
                g_graph.links.push_back({g_graph.new_id(), src, dst});
            }
        }
        ed::EndCreate();
    }
}

static void handle_delete()
{
    if (ed::BeginDelete())
    {
        ed::LinkId del_link;
        while (ed::QueryDeletedLink(&del_link))
            if (ed::AcceptDeletedItem())
                g_graph.erase_link((int)del_link.Get());

        ed::NodeId del_node;
        while (ed::QueryDeletedNode(&del_node))
            if (ed::AcceptDeletedItem())
                g_graph.erase_node((int)del_node.Get());
        ed::EndDelete();
    }
}

static void handle_context_menus()
{
    ed::Suspend();

    ed::NodeId  ctx_node;
    ed::LinkId  ctx_link;
    ed::PinId   ctx_pin;

    if (ed::ShowNodeContextMenu(&ctx_node))     ImGui::OpenPopup("node_ctx");
    else if (ed::ShowPinContextMenu(&ctx_pin))  ImGui::OpenPopup("pin_ctx");
    else if (ed::ShowLinkContextMenu(&ctx_link))ImGui::OpenPopup("link_ctx");
    else if (ed::ShowBackgroundContextMenu())   ImGui::OpenPopup("bg_ctx");

    static int last_node = 0, last_link = 0, last_pin = 0;
    if (ctx_node) last_node = (int)ctx_node.Get();
    if (ctx_link) last_link = (int)ctx_link.Get();
    if (ctx_pin)  last_pin  = (int)ctx_pin.Get();

    if (ImGui::BeginPopup("node_ctx"))
    {
        ImGui::Text("Node #%d", last_node);
        ImGui::Separator();
        if (ImGui::MenuItem("Delete node"))
            g_graph.erase_node(last_node);
        ImGui::EndPopup();
    }
    if (ImGui::BeginPopup("pin_ctx"))
    {
        ImGui::Text("Pin #%d", last_pin);
        ImGui::EndPopup();
    }
    if (ImGui::BeginPopup("link_ctx"))
    {
        ImGui::Text("Link #%d", last_link);
        ImGui::Separator();
        // ed::Flow() triggers a one-shot animated "flow" along the link
        // (one call kicks off a time-bounded animation, no per-frame loop).
        if (ImGui::MenuItem("Flow forward"))
            ed::Flow(ed::LinkId(last_link), ed::FlowDirection::Forward);
        if (ImGui::MenuItem("Flow backward"))
            ed::Flow(ed::LinkId(last_link), ed::FlowDirection::Backward);
        ImGui::Separator();
        if (ImGui::MenuItem("Delete link"))
            g_graph.erase_link(last_link);
        ImGui::EndPopup();
    }
    if (ImGui::BeginPopup("bg_ctx"))
    {
        ImGui::Text("Add node");
        ImGui::Separator();
        struct Recipe { const char* name; int n_in; int n_out; };
        static const Recipe recipes[] = {
            {"Source",  0, 1},
            {"Filter",  1, 1},
            {"Mix",     2, 1},
            {"Split",   1, 2},
            {"Output",  1, 0},
        };
        for (const auto& r : recipes)
            if (ImGui::MenuItem(r.name))
                g_graph.add_node(r.name, r.n_in, r.n_out);
        ImGui::Separator();
        if (ImGui::MenuItem("Group"))
            g_graph.add_group("New group");
        ImGui::EndPopup();
    }

    ed::Resume();
}

void Gui()
{
    seed_graph();

    ImGui::Text("Nodes: %zu  Links: %zu  | "
                "Drag from a pin to another to link. "
                "Right-click for menus. "
                "Press F to zoom-to-fit, Delete to remove selection.",
                g_graph.nodes.size(), g_graph.links.size());

    ed::Begin("Graph", ImVec2(0, 0));

    // Compute who is inside a collapsed group (uses last frame's geometry).
    const auto hidden = compute_hidden_node_ids();

    for (const auto& n : g_graph.nodes)
    {
        if (hidden.count(n.id)) continue;   // skip members of collapsed groups
        draw_node(n);
    }

    for (const auto& l : g_graph.links)
    {
        // Hide a link as soon as either endpoint sits in a hidden node.
        const Pin* a = g_graph.find_pin(l.src_pin_id);
        const Pin* b = g_graph.find_pin(l.dst_pin_id);
        if (a && hidden.count(a->node_id)) continue;
        if (b && hidden.count(b->node_id)) continue;
        ed::Link(ed::LinkId(l.id), ed::PinId(l.src_pin_id), ed::PinId(l.dst_pin_id));
    }

    draw_group_hints();
    handle_create();
    handle_delete();
    handle_context_menus();

    ed::End();

    // ImGuiTheme::ApplyTheme(ImGuiTheme::ImGuiTheme_WhiteIsWhite);
}

int main()
{
    ImmApp::AddOnsParams addonsParams;
    addonsParams.withNodeEditor = true;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.appWindowParams.windowTitle = "Node Graph Sandbox";
    runnerParams.appWindowParams.windowGeometry.size = {1200, 800};
    runnerParams.imGuiWindowParams.showMenuBar = true;
    runnerParams.callbacks.ShowGui = Gui;

    ImmApp::Run(runnerParams, addonsParams);
    return 0;
}
#else
int main() { return 0; }
#endif
