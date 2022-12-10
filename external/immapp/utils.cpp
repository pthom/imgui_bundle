#include "immapp/immapp.h"
#include "imgui-node-editor/imgui_node_editor_internal.h"

#include <chrono>


// Provide a texture loader for the demo of imgui_tex_inspect
#include "imgui_tex_inspect/imgui_tex_inspect_demo.h"
namespace ImGuiTexInspect
{
    Texture LoadTexture(const char * path)
    {
        auto textureId = HelloImGui::ImTextureIdFromAsset(path);
        Texture r;
        r.size = ImVec2(512.f, 512.f); // This function is only by used the demo, which uses a 51x512 image
        r.texture = textureId;
        return r;
    }
}


namespace ImmApp
{

    class ClockSeconds_
    {
        // Typical C++ shamanic incantations to get a time in seconds
    private:
        using Clock = std::chrono::high_resolution_clock;
        using second = std::chrono::duration<double, std::ratio<1>>;
        std::chrono::time_point<Clock> mStart;

    public:
        ClockSeconds_() : mStart(Clock::now()) {}

        double elapsed() const
        {
            return std::chrono::duration_cast<second>
                (Clock::now() - mStart).count();
        }
    };

    double ClockSeconds()
    {
        static ClockSeconds_ watch;
        return watch.elapsed();
    }


    ax::NodeEditor::EditorContext* CurrentNodeEditorContext_Impl();
    ax::NodeEditor::EditorContext* CurrentNodeEditorContext()
    {
        return CurrentNodeEditorContext_Impl();
    }

    void SuspendNodeEditorCanvas()
    {
        auto context  = ax::NodeEditor::GetCurrentEditor();
        auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
        context_cast->Suspend();
    }

    void ResumeNodeEditorCanvas()
    {
        auto context  = ax::NodeEditor::GetCurrentEditor();
        auto context_cast = (ax::NodeEditor::Detail::EditorContext *)context;
        context_cast->Resume();
    }

} // namespace ImmApp