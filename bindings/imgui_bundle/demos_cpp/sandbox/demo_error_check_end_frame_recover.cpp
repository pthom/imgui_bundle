// This demo show how we can call ImGui::ErrorCheckEndFrameRecover()
// to recover from errors originating when ImGui::End() is not called (for example when an exception is raised)

#include "hello_imgui.h"
#include "imgui.h"
#include "imgui_internal.h"

void SubWindowGui()
{
    ImGui::SetNextWindowSize(ImVec2(600.f, 200.f));
    ImGui::Begin("Sub window");
    ImGui::Text("The button below will raise an exception which lead to imgui.end() not being called");

    if (ImGui::Button("Raise exception")) { // This button raises an exception that bypasses `ImGui::End()`
        throw std::runtime_error("Argh");
    }
    ImGui::End();
}

void Gui()
{
    try
    {
        ImGui::Text("Hello");
        SubWindowGui();
    }
    catch (const std::runtime_error& e)
    {
        std::cout << "Ouch, caught an exception: " << e.what() << std::endl;
    }
}

// By default, ImGui::ErrorCheckEndFrameRecover() uses a C-Style callback with va_args, such as below
void MyEndFrameErrorCallback_CStyle(void* user_data, const char* fmt, ...)
{
    printf("MyEndFrameErrorCallback_CStyle ==> ");

    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);

    printf("\n");
};

// ImGui Bundle provides a fork of ImGui where another version of ImGui::ErrorCheckEndFrameRecover()
// can use a simpler C++ style callback, such a below
// (only available if IMGUI_BUNDLE_PYTHON_API is defined)
void MyEndFrameErrorCallback(const std::string& message)
{
    printf("MyEndFrameErrorCallback ==> %s\n", message.c_str());
};



int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui;

    // you can use either the C style or the C++ style callback
    runnerParams.callbacks.BeforeImGuiRender = [](){ ImGui::ErrorCheckEndFrameRecover(MyEndFrameErrorCallback_CStyle); };
    // runnerParams.callbacks.BeforeImGuiRender = [](){ ImGui::ErrorCheckEndFrameRecover(MyEndFrameErrorCallback); };

    HelloImGui::Run(runnerParams);
    return 0;
}
