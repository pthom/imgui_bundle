#if defined(IMGUI_BUNDLE_WITH_IMGUI_NODE_EDITOR)
#include "hello_imgui/hello_imgui.h"
#include "immapp/immapp.h"
#include "imgui.h"
#include "misc/cpp/imgui_stdlib.h"
#include "imgui-node-editor/imgui_node_editor.h"
#include <string>

namespace ed = ax::NodeEditor;




void Gui()
{
    static std::string text =
        "Hello, World!\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n"
        "Line 7\nLine 8\nLine 9\nLine 10\nLine 11\nLine 12";
    static ImVec4 clearColor = ImVec4(0, 0, 0, 0);
    const char* items[] = { "AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH", "IIII", "JJJJ", "KKKK", "LLLLLLL", "MMMM", "OOOOOOO" };
    static int item_selected_idx = 0; // Here we store our selection data as an index.


    static HelloImGui::InputTextData input_text_data_multiline, input_text_data_singleline;
    static bool initialized = false;
    if (!initialized)
    {
        initialized = true;

        input_text_data_multiline.Text = R"(
Demain, dès l'aube, à l'heure où blanchit la campagne,
Je partirai. Vois-tu, je sais que tu m'attends.
J'irai par la forêt, j'irai par la montagne.
Je ne puis demeurer loin de toi plus longtemps.

Je marcherai les yeux fixés sur mes pensées,
Sans rien voir au dehors, sans entendre aucun bruit,
Seul, inconnu, le dos courbé, les mains croisées,
Triste, et le jour pour moi sera comme la nuit.

Je ne regarderai ni l'or du soir qui tombe,
Ni les voiles au loin descendant vers Harfleur,
Et quand j'arriverai, je mettrai sur ta tombe
Un bouquet de houx vert et de bruyère en fleur.

Victor Hugo, extrait du recueil «Les Contemplations» (1856)
        )";
        input_text_data_multiline.Multiline = true;
        input_text_data_multiline.Resizable =true;
        input_text_data_multiline.SizeEm = ImVec2(15, 3);

        input_text_data_singleline.Text = "This is a simple test";
        input_text_data_singleline.Multiline = false;
        input_text_data_singleline.Resizable = true;
        input_text_data_singleline.SizeEm = ImVec2(20, 1);
    }

    ImGui::Text("Hello, world!");

    ed::Begin("My Node Editor");

    ed::BeginNode(ed::NodeId(1));
    ImGui::Text("Hello");

    // Inside a node, InputTextMultiline renders a read-only preview box and opens a
    // resizable popup editor on click (child windows do not work inside a node).
    ImVec2 editSize = HelloImGui::EmToVec2(10, 8);
    ImGui::InputTextMultiline("Text", &text, editSize);

    // Resizable text via Hello ImGui
    HelloImGui::InputTextResizable("Resizable Multi", &input_text_data_multiline);
    HelloImGui::InputTextResizable("Resizable Single", &input_text_data_singleline);

    // Pass in the preview value visible before opening the combo (it could technically be different contents or not pulled from items[])
    const char* combo_preview_value = items[item_selected_idx];
    ImGui::SetNextItemWidth(200);
    if (ImGui::BeginCombo("combo 1", combo_preview_value))
    {
        for (int n = 0; n < IM_COUNTOF(items); n++)
        {
            const bool is_selected = (item_selected_idx == n);
            if (ImGui::Selectable(items[n], is_selected))
                item_selected_idx = n;

            // Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
            if (is_selected)
                ImGui::SetItemDefaultFocus();
        }
        ImGui::EndCombo();
    }

    ImGui::ColorEdit4("Color", &clearColor.x);

    ed::EndNode();

    ed::End();
}

int main()
{
    ImmApp::AddOnsParams addonsParams;
    addonsParams.withNodeEditor = true;

    HelloImGui::RunnerParams runnerParams;
    // runnerParams.iniDisable = true;
    runnerParams.callbacks.ShowGui = Gui;

    ImmApp::Run(runnerParams, addonsParams);

    return 0;
}
#else
int main() { return 0; }
#endif
