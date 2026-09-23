// Markdown with stock Dear ImGui (GLFW + OpenGL3), no HelloImGui: fonts and images come from the
// embedded assets, textures go through Dear ImGui's ImTextureData (the default UploadRgba).
// IMGUI_RICHMD_SHOT=<file.ppm> in the environment: writes a screenshot after 30 frames and exits.
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "imgui_rich_md/rich_md.h"
#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#include <OpenGL/gl3.h>
#else
#include <GL/gl.h>
#endif
#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <cstdio>
#include <cstdlib>
#include <vector>

static const char* kMarkdown = R"(
# Markdown with stock Dear ImGui
No HelloImGui here: the fonts and the images below are **embedded** in the library, the textures are
`ImTextureData` created by the OpenGL3 backend.

## Text
*Emphasis*, **bold**, `code`, ~~strikethrough~~, a [link](https://github.com/pthom/imgui_bundle), and a
formula, rendered when the library is built with LaTeX (shown as source otherwise): $e^{i\pi} + 1 = 0$.

## Table
| Feature | State |
|---|---|
| Fonts | embedded |
| Images | embedded, ImTextureData |

## Image
![world](images/world.png)
An image that does not exist: ![nope](images/nope.png)

## Code
```cpp
RichMd::InitializeMarkdown();
RichMd::Render(markdown);
```
)";

static void WriteScreenshotPpm(GLFWwindow* window, const char* path)
{
    int w, h;
    glfwGetFramebufferSize(window, &w, &h);
    std::vector<unsigned char> rgb((size_t)w * h * 3);
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, rgb.data());
    FILE* f = fopen(path, "wb");
    fprintf(f, "P6\n%d %d\n255\n", w, h);
    for (int y = h - 1; y >= 0; --y)
        fwrite(rgb.data() + (size_t)y * w * 3, 1, (size_t)w * 3, f);
    fclose(f);
}

int main(int, char**)
{
    if (!glfwInit())
        return 1;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#ifdef __APPLE__
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
#endif
    GLFWwindow* window = glfwCreateWindow(900, 800, "imgui_rich_md minimal example", nullptr, nullptr);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 150");

    RichMd::MarkdownOptions options;
#ifdef IMGUI_RICHMD_WITH_LATEX
    options.withLatex = true;
#endif
    RichMd::InitializeMarkdown(options);

    const char* shot = std::getenv("IMGUI_RICHMD_SHOT");
    int frame = 0;
    while (!glfwWindowShouldClose(window))
    {
        glfwPollEvents();
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        const ImGuiViewport* vp = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(vp->WorkPos);
        ImGui::SetNextWindowSize(vp->WorkSize);
        ImGui::Begin("##md", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove);
        RichMd::Render(kMarkdown);
        ImGui::End();

        ImGui::Render();
        int w, h;
        glfwGetFramebufferSize(window, &w, &h);
        glViewport(0, 0, w, h);
        glClearColor(0.1f, 0.1f, 0.12f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        if (shot && ++frame == 30)
        {
            WriteScreenshotPpm(window, shot);
            glfwSetWindowShouldClose(window, GLFW_TRUE);
        }
        glfwSwapBuffers(window);
    }

    RichMd::DeInitializeMarkdown();  // frees the markdown textures while the backend is alive
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
