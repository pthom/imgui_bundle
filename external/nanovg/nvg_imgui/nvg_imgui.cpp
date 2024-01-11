#include "nvg_imgui.h"

#include "nanovg.h"
#include "imgui.h"

#ifdef HELLOIMGUI_HAS_OPENGL
#include "hello_imgui_include_opengl.h"
#define NANOVG_GL3 1
#include "nanovg_gl.h"
#include "nanovg_gl_utils.h"
#endif

namespace NvgImgui
{
#ifdef HELLOIMGUI_HAS_OPENGL
    struct NvgFramebufferGl: public NvgFramebuffer
    {
        NVGLUframebuffer* fb = nullptr;
        GLint defaultViewport[4];  // To store the default viewport dimensions

        NvgFramebufferGl(NVGcontext* vg, int width, int height, int nvgImageFlags)
            : NvgFramebuffer(width, height, nvgImageFlags)
        {
            fb = nvgluCreateFramebuffer(vg, width, height, nvgImageFlags);
            IM_ASSERT(fb && "Failed to create NVGLU framebuffer");
            TextureId = (ImTextureID)(intptr_t)fb->texture;
        }

        ~NvgFramebufferGl() override
        {
            if (fb) {
                nvgluDeleteFramebuffer(fb);
                fb = nullptr;
            }
        }

        void Bind() override
        {
            nvgluBindFramebuffer(fb);
            glGetIntegerv(GL_VIEWPORT, defaultViewport);
            glViewport(0, 0, Width, Height);
        }

        void Unbind() override
        {
            nvgluBindFramebuffer(nullptr);
            glViewport(defaultViewport[0], defaultViewport[1], defaultViewport[2], defaultViewport[3]);
        }
    };

    NvgFramebufferPtr CreateNvgFramebuffer(NVGcontext* vg, int width, int height, int nvImageFlags)
    {
        return std::make_shared<NvgFramebufferGl>(vg, width, height, nvImageFlags);
    }

    static void FillClearColor(ImVec4 clearColor)
    {
        glClearColor(clearColor.x, clearColor.y, clearColor.z, clearColor.w);
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    }
#else
    static void FillClearColor(ImVec4 clearColor)
    {
        IM_ASSERT(false && "FillClearColor: Not implemented for this rendering backend!");
    }

    NvgFramebufferPtr CreateNvgFramebuffer(NVGcontext* vg, int width, int height, int nvImageFlags)
    {
        IM_ASSERT(false && "CreateNvgFramebuffer: Not implemented for this rendering backend!");
        return nullptr;
    }
#endif // HELLOIMGUI_HAS_OPENGL


    void RenderNvgToBackground(NVGcontext* vg, NvgDrawingFunction nvgDrawingFunction, ImVec4 clearColor)
    {
        if (clearColor.w > 0.f)
            FillClearColor(clearColor);

        auto displaySize = ImGui::GetIO().DisplaySize;
        float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;

        nvgBeginFrame(vg, displaySize.x, displaySize.y, pixelRatio);
        nvgDrawingFunction(displaySize.x, displaySize.y);
        nvgEndFrame(vg);
    }

    void RenderNvgToFrameBuffer(NVGcontext* vg, NvgFramebufferPtr texture, NvgDrawingFunction drawFunc, ImVec4 clearColor)
    {
        texture->Bind();
        if (clearColor.w > 0.f)
            FillClearColor(clearColor);

        // Note:
        //    - internally, we use NVGLUframebuffer, provided by NanoVG
        //    - NVGLUframebuffer does not handle pixelRatio
        //    => using pixelRatio=DisplayFramebufferScale would lead to non anti-aliased rendering
        //    => you may want to create texture of bigger size and scale down the drawing, in order to
        //       improve the quality of the rendering

        // float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;
        float pixelRatio = 1.f;
        nvgBeginFrame(vg, texture->Width, texture->Height, pixelRatio);

        // Flip the y-axis
        nvgSave(vg); // Save the current state
        nvgTranslate(vg, 0, texture->Height); // Move the origin to the bottom-left
        nvgScale(vg, 1, -1); // Flip the y-axis

        // Perform drawing operations
        drawFunc(texture->Width, texture->Height);

        nvgRestore(vg); // Restore the original state
        nvgEndFrame(vg);
        nvgReset(vg); // Reset any temporary state changes that may have been made

        texture->Unbind();
    }


}