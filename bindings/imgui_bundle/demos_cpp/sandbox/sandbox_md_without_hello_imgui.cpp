// Demonstrates how to use imgui_md (Markdown) WITHOUT HelloImGui::Run().
//
// This is the C++ counterpart of demos_python/sandbox/sandbox_md_without_hello_imgui.py.
// It hosts imgui_md inside a vanilla Dear-ImGui glfw + opengl3 main loop, with
// no HelloImGui runner.
//
// Built only when HelloImGui was compiled with both HELLOIMGUI_USE_GLFW3 and
// HELLOIMGUI_HAS_OPENGL3 (which is the default desktop configuration).
// Other configurations get a stub main() that explains the requirements.

#if defined(HELLOIMGUI_USE_GLFW3) && defined(HELLOIMGUI_HAS_OPENGL3)

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "imgui_md_wrapper/imgui_md_wrapper.h"

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include <cstdio>

static const char* kMarkdown = R"(
# imgui_md without HelloImGui (C++)

> **Running without HelloImGui::Run()** — pure GLFW + OpenGL3 backend.
> `ImGuiMd::InitializeMarkdown()` takes care of the GLAD setup automatically;
> no `HelloImGui::*` ceremony required.

## Markdown features

* Wrapped paragraphs
* **Bold**, *emphasis*, ~~strikethrough~~
* Inline code: `int answer() { return 42; }`
* Tables, links, headings, ...

## Image asset

![World](images/world.png)

## LaTeX math

Inline like $E = mc^2$, and display:

$$\int_{-\infty}^{\infty} e^{-x^2}\, dx = \sqrt{\pi}$$

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
)";

static void glfw_error_callback(int error, const char* description)
{
    std::fprintf(stderr, "GLFW error %d: %s\n", error, description);
}

int main(int, char**)
{
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit())
        return 1;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
#endif

    GLFWwindow* window = glfwCreateWindow(
        1280, 720, "imgui_md without HelloImGui (C++)", nullptr, nullptr);
    if (!window)
    {
        glfwTerminate();
        return 1;
    }
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui::StyleColorsLight();

    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 150");

    // ImGuiMd::InitializeMarkdown internally calls HelloImGui::InitGlLoader()
    // (which calls gladLoadGL() outside HelloImGui::Run()), so by the time we
    // try to upload image / LaTeX-math textures, GLAD is ready.
    ImGuiMd::MarkdownOptions md_options;
    md_options.withLatex = true;
    ImGuiMd::InitializeMarkdown(md_options);
    ImGuiMd::GetFontLoaderFunction()();

    while (!glfwWindowShouldClose(window))
    {
        glfwPollEvents();

        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        const ImGuiViewport* vp = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(vp->WorkPos);
        ImGui::SetNextWindowSize(vp->WorkSize);
        ImGui::Begin("##md", nullptr,
            ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize
            | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoCollapse
            | ImGuiWindowFlags_NoBringToFrontOnFocus);
        ImGuiMd::RenderUnindented(kMarkdown);
        ImGui::End();

        ImGui::Render();
        int w, h;
        glfwGetFramebufferSize(window, &w, &h);
        glViewport(0, 0, w, h);
        glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
    }

    // ImGuiMd::DeInitializeMarkdown internally calls HelloImGui::FreeImageCache()
    // so the GPU textures are dropped before we destroy the GL context.
    ImGuiMd::DeInitializeMarkdown();

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}

#else  // !HELLOIMGUI_USE_GLFW3 || !HELLOIMGUI_HAS_OPENGL3

#include <cstdio>

int main(int, char**)
{
    std::fprintf(stderr,
        "sandbox_md_without_hello_imgui: this demo requires HelloImGui to be\n"
        "compiled with both HELLOIMGUI_USE_GLFW3 and HELLOIMGUI_HAS_OPENGL3.\n"
        "Rebuild with -DHELLOIMGUI_USE_GLFW3=ON -DHELLOIMGUI_HAS_OPENGL3=ON.\n");
    return 0;
}

#endif
