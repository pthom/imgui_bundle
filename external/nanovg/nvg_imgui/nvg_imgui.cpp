#include "nvg_imgui.h"

#include "nanovg.h"
#include "imgui.h"

#ifdef HELLOIMGUI_HAS_OPENGL
    #include "hello_imgui_include_opengl.h"

    #ifdef HELLOIMGUI_USE_GLES3
    #define NANOVG_GLES3
    #define NANOVG_GLES3_IMPLEMENTATION
    #else
    #define NANOVG_GL3 1
    #define NANOVG_GL3_IMPLEMENTATION
    #endif

    #include "nanovg_gl.h"
    #include "nanovg_gl_utils.h"
#endif

#ifdef HELLOIMGUI_HAS_OPENGL
namespace NvgImgui
{
    struct NvgFramebuffer::PImpl
    {
        NVGLUframebuffer *fb = nullptr;
        GLint defaultViewport[4];  // To store the default viewport dimensions
        NvgFramebuffer *_parent = nullptr;

        PImpl(NvgFramebuffer *parent) : _parent(parent)
        {
            AcquireResource();
        }

        ~PImpl()
        {
            ReleaseResource();
        }

        void AcquireResource()
        {
            if (_parent->vg == nullptr)
                return;
            fb = nvgluCreateFramebuffer(_parent->vg, _parent->Width, _parent->Height, _parent->NvgImageFlags);
            IM_ASSERT(fb && "Failed to create NVGLU framebuffer");
            _parent->TextureId = (ImTextureID) (intptr_t) fb->texture;
        }

        void ReleaseResource()
        {
            if (fb)
            {
                nvgluDeleteFramebuffer(fb);
                fb = nullptr;
            }
        }

        void Bind()
        {
            nvgluBindFramebuffer(fb);
            glGetIntegerv(GL_VIEWPORT, defaultViewport);
            glViewport(0, 0, _parent->Width, _parent->Height);
        }

        void Unbind()
        {
            nvgluBindFramebuffer(nullptr);
            glViewport(defaultViewport[0], defaultViewport[1], defaultViewport[2], defaultViewport[3]);
        }
    };

    static void FillClearColor(ImVec4 clearColor)
    {
        glClearColor(clearColor.x, clearColor.y, clearColor.z, clearColor.w);
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    }

    #ifdef HELLOIMGUI_USE_GLES3
    NVGcontext* CreateNvgContext(int flags) { return nvgCreateGLES3(flags); }
    void DeleteNvgContext(NVGcontext* vg) { nvgDeleteGLES3(vg); }
    #else
    NVGcontext *CreateNvgContext_GL(int flags) { return nvgCreateGL3(flags); }
    void DeleteNvgContext_GL(NVGcontext *vg) { nvgDeleteGL3(vg); }
    #endif

} // namespace NvgImgui
#endif // #ifdef HELLOIMGUI_HAS_OPENGL


#ifndef HELLOIMGUI_HAS_OPENGL
namespace NvgImgui
{
    static void FillClearColor(ImVec4 clearColor)
    {
        IM_ASSERT(false && "FillClearColor: Not implemented for this rendering backend!");
    }

    NvgFramebufferPtr CreateNvgFramebuffer(NVGcontext* vg, int width, int height, int nvImageFlags)
    {
        IM_ASSERT(false && "CreateNvgFramebuffer: Not implemented for this rendering backend!");
        return nullptr;
    }

    NVGcontext CreateNvgContext(int flags)
    {
        IM_ASSERT(false && "CreateNvgContext: Not implemented for this rendering backend!");
        return nullptr;
    }

    void DeleteNvgContext(NVGcontext* vg)
    {
        IM_ASSERT(false && "DeleteNvgContext: Not implemented for this rendering backend!");
    }
} // namespace NvgImgui
#endif // #ifndef HELLOIMGUI_HAS_OPENGL


namespace NvgImgui
{
    NvgFramebuffer::NvgFramebuffer(NVGcontext* vg, int width, int height, int nvgImageFlags) // See NVGimageFlags
        : vg(vg), Width(width), Height(height), NvgImageFlags(nvgImageFlags)
    {
        pImpl = new PImpl(this);
    }

    NvgFramebuffer::~NvgFramebuffer() { delete pImpl; }

    void NvgFramebuffer::Bind() { pImpl->Bind(); }
    void NvgFramebuffer::Unbind() { pImpl->Unbind(); }


    void RenderNvgToBackground(NVGcontext* vg, NvgDrawingFunction nvgDrawingFunction, ImVec4 clearColor)
    {
        if (clearColor.w > 0.f)
            FillClearColor(clearColor);

        auto displaySize = ImGui::GetIO().DisplaySize;
        float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;

        nvgBeginFrame(vg, displaySize.x, displaySize.y, pixelRatio);
        nvgDrawingFunction(vg, displaySize.x, displaySize.y);
        nvgEndFrame(vg);
    }

    void RenderNvgToFrameBuffer(NVGcontext* vg, NvgFramebuffer& texture, NvgDrawingFunction drawFunc, ImVec4 clearColor)
    {
        texture.Bind();
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
        nvgBeginFrame(vg, texture.Width, texture.Height, pixelRatio);

        // Flip the y-axis
        nvgSave(vg); // Save the current state
        nvgTranslate(vg, 0, texture.Height); // Move the origin to the bottom-left
        nvgScale(vg, 1, -1); // Flip the y-axis

        // Perform drawing operations
        drawFunc(vg, texture.Width, texture.Height);

        nvgRestore(vg); // Restore the original state
        nvgEndFrame(vg);
        nvgReset(vg); // Reset any temporary state changes that may have been made

        texture.Unbind();
    }

}