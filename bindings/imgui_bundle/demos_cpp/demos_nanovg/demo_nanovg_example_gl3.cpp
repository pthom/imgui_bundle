#define IMGUI_DEFINE_MATH_OPERATORS
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"

#include "imgui.h"
#include "nanovg.h"

#include "nanovg_demo/nanovg_demo.h"

#include <memory>
#include <functional>

using NvgDrawingFunction = std::function<void(float width, float height)>;


void RenderNvgToDisplayBackground(NvgDrawingFunction nvgDrawingFunction)
{
    auto vg = ImmApp::NanoVGContext();
    auto displaySize = ImGui::GetIO().DisplaySize;
    float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;

    nvgBeginFrame(vg, displaySize.x, displaySize.y, pixelRatio);
    nvgDrawingFunction(displaySize.x, displaySize.y);
    nvgEndFrame(vg);
}


struct MyNvgDemo
{
    bool Blowup = false;
    DemoData nvgDemoData;
    NVGcontext* vg;

    MyNvgDemo(NVGcontext* _vg)
        : vg(_vg)
    {
        int status = loadDemoData(vg, &nvgDemoData);
        IM_ASSERT((status == 0) && "Could not load demo data!");
    }

    ~MyNvgDemo()
    {
        freeDemoData(vg, &nvgDemoData);
    }

    void Render(float width, float height, int mousex, int mousey, float t)
    {
        // Clear background
        {
            nvgBeginPath(vg);
            nvgRect(vg, 0, 0, width, height);
            nvgFillColor(vg, nvgRGBA(50, 50, 50, 255));
            nvgFill(vg);
        }

        renderDemo(vg, mousex, mousey, width, height, t, Blowup, &nvgDemoData);
    }

};


struct Texture
{
    int Width, Height;
    ImTextureID TextureId;

    Texture(int width, int height)
        : Width(width), Height(height)
    {}
    virtual void activateTexture() = 0;
    virtual void deactivateTexture() = 0;

    virtual ~Texture() = default;
};

#include "hello_imgui_include_opengl.h"
#define NANOVG_GL3 1
#include "nanovg_gl.h"
#include "nanovg_gl_utils.h"
struct TextureGl: public Texture
{
    NVGLUframebuffer* fb = nullptr;
    GLint defaultViewport[4];  // To store the default viewport dimensions

    TextureGl(NVGcontext* vg, int width, int height)
        : Texture(width, height)
    {
        //fb = nvgluCreateFramebuffer(vg, width, height, NVG_IMAGE_FLIPY | NVG_IMAGE_PREMULTIPLIED);
        fb = nvgluCreateFramebuffer(vg, width, height, 0);
        if (!fb) {
            throw std::runtime_error("Failed to create NVGLU framebuffer");
        }
        TextureId = (ImTextureID)(intptr_t)fb->texture;
    }

    ~TextureGl() override
    {
        if (fb) {
            nvgluDeleteFramebuffer(fb);
            fb = nullptr;
        }
    }

    void activateTexture() override
    {
        nvgluBindFramebuffer(fb);
        glGetIntegerv(GL_VIEWPORT, defaultViewport);
        glViewport(0, 0, Width, Height);
    }

    void deactivateTexture() override
    {
        nvgluBindFramebuffer(nullptr);
        glViewport(defaultViewport[0], defaultViewport[1], defaultViewport[2], defaultViewport[3]);
    }
};


// Factory function
std::unique_ptr<Texture> CreateTextureGl(int width, int height)
{
    auto texture = std::make_unique<TextureGl>(ImmApp::NanoVGContext(), width, height);
    return std::move(texture);
}


void RenderNvgToTexture(Texture& texture, NvgDrawingFunction drawFunc)
{
    auto vg = ImmApp::NanoVGContext();
    float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;

    texture.activateTexture();

    nvgBeginFrame(vg, texture.Width, texture.Height, pixelRatio);

    // Flip the y-axis
    nvgSave(vg); // Save the current state
    nvgTranslate(vg, 0, texture.Height); // Move the origin to the bottom-left
    nvgScale(vg, 1, -1); // Flip the y-axis

    // Perform drawing operations
    drawFunc(texture.Width, texture.Height);

    nvgRestore(vg); // Restore the original state
    nvgEndFrame(vg);
    nvgReset(vg); // Reset any temporary state changes that may have been made

    texture.deactivateTexture();
}




struct AppState
{
    std::unique_ptr<MyNvgDemo> myNvgDemo;

    std::unique_ptr<Texture> myTexture;

    bool useCustomBackground = true;
};



int main(int, char**)
{
    ChdirBesideAssetsFolder();

    AppState appState;

    HelloImGui::RunnerParams runnerParams;
    runnerParams.imGuiWindowParams.defaultImGuiWindowType = HelloImGui::DefaultImGuiWindowType::NoDefaultWindow;
    runnerParams.appWindowParams.windowGeometry.size = {1200, 900};
    ImmApp::AddOnsParams addons;
    addons.withNanoVG = true;

    runnerParams.callbacks.PostInit = [&]()
    {
        auto vg = ImmApp::NanoVGContext();
        appState.myNvgDemo = std::make_unique<MyNvgDemo>(vg);
        float scale = ImGui::GetIO().DisplayFramebufferScale.x;
        appState.myTexture = CreateTextureGl((int)(1000 * scale), (int)(600 * scale));
    };
    runnerParams.callbacks.BeforeExit = [&]()
    {
        appState.myNvgDemo.release();
        appState.myTexture.release();
    };


    runnerParams.callbacks.CustomBackground = [&]()
    {
//        if (!appState.useCustomBackground)
//            return;
        //auto displaySize = ImGui::GetIO().DisplaySize;
        //appState->Render(displaySize.x, displaySize.y);

        auto nvgDrawingFunction = [&](float width, float height)
        {
            double now = ImGui::GetTime();
            auto mousePos = ImGui::GetMousePos() - ImGui::GetMainViewport()->Pos;
            printf("%f %f\n", mousePos.x, mousePos.y);
            appState.myNvgDemo->Render(width, height, (int)mousePos.x, (int)mousePos.y, (float)now);
        };
        RenderNvgToDisplayBackground(nvgDrawingFunction);
    };

    runnerParams.callbacks.ShowGui = [&]()
    {
        ImGui::Begin("My Window!");
        ImGui::Checkbox("Use custom background", &appState.useCustomBackground);

        if (!appState.useCustomBackground)
        {
            RenderNvgToTexture(*appState.myTexture, [&](float width, float height)
            {
                double now = ImGui::GetTime();
                auto mousePos = ImGui::GetMousePos();
                appState.myNvgDemo->Render(width, height, (int)mousePos.x, (int)mousePos.y, (float)now);
            });
            ImGui::Image(appState.myTexture->TextureId, ImVec2(1000, 600));
        }


        ImGui::End();
    };

    runnerParams.imGuiWindowParams.enableViewports = true;
    ImmApp::Run(runnerParams, addons);
    return 0;
}
