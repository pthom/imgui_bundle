#ifdef IMGUI_BUNDLE_WITH_NANOVG
#include "nvg_imgui.h"

#include "nanovg.h"
#include "imgui.h"

#ifdef HAS_NVG_OPENGL
    #include "hello_imgui/hello_imgui_include_opengl.h"

    #ifdef HELLOIMGUI_USE_GLES3
    // #define NANOVG_GLES3
    #define NANOVG_GLES3_IMPLEMENTATION
    #else
    #define NANOVG_GL3 1
    #define NANOVG_GL3_IMPLEMENTATION
    #endif

    #include "nanovg_gl.h"
    #include "nanovg_gl_utils.h"
#endif

#ifdef HAS_NVG_METAL
    #include "nvg_mtl_hello_imgui.h"
    #include "nanovg_mtl.h"
#endif


#ifdef HAS_NVG_OPENGL
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

    static void FillClearColor(NVGcontext *vg, ImVec4 clearColor)
    {
        (void)vg;
        glClearColor(clearColor.x, clearColor.y, clearColor.z, clearColor.w);
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    }

    static void UseFullViewport(NVGcontext *vg)
    {
        (void)vg;
        ImVec2 displaySize = ImGui::GetIO().DisplaySize;
        ImVec2 scale = ImGui::GetIO().DisplayFramebufferScale;
        glViewport(0, 0, (int)(displaySize.x * scale.x), (int)(displaySize.y * scale.y));
    }

    #ifdef HELLOIMGUI_USE_GLES3
    NVGcontext* CreateNvgContext_GL(int flags) { return nvgCreateGLES3(flags); }
    void DeleteNvgContext_GL(NVGcontext* vg) { nvgDeleteGLES3(vg); }
    #else
    NVGcontext *CreateNvgContext_GL(int flags) { return nvgCreateGL3(flags); }
    void DeleteNvgContext_GL(NVGcontext *vg) { nvgDeleteGL3(vg); }
    #endif

} // namespace NvgImgui
#endif // #ifdef HAS_NVG_OPENGL


#ifdef HAS_NVG_METAL
namespace NvgImgui
{
    struct NvgFramebuffer::PImpl
    {
        MNVGframebuffer *fb = nullptr;
        // GLint defaultViewport[4];  // To store the default viewport dimensions
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
            fb = mnvgCreateFramebuffer(_parent->vg, _parent->Width, _parent->Height, _parent->NvgImageFlags);
            IM_ASSERT(fb && "Failed to create NVGLU framebuffer");
            _parent->TextureId = mnvgImageHandle(_parent->vg, fb->image);
        }

        void ReleaseResource()
        {
            if (fb)
            {
                mnvgDeleteFramebuffer(fb);
                fb = nullptr;
            }
        }

        void Bind()
        {
            mnvgBindFramebuffer(fb);
        }

        void Unbind()
        {
            mnvgBindFramebuffer(nullptr);
        }
    };

    static void FillClearColor(NVGcontext* vg, ImVec4 clearColor)
    {
        mnvgClearWithColor(vg, nvgRGBAf(clearColor.x, clearColor.y, clearColor.z, clearColor.w));
    }

    static void UseFullViewport(NVGcontext *vg)
    {
    }

} // namespace NvgImgui
#endif // #ifndef HAS_NVG_METAL


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
#ifdef HAS_NVG_METAL
        printf("RenderNvgToBackground works poorly with Metal backend, use RenderNvgToFrameBuffer instead\n");
        return;
#endif
        UseFullViewport(vg);

        if (clearColor.w > 0.f)
            FillClearColor(vg, clearColor);

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
            FillClearColor(vg, clearColor);

        // Note:
        //    - internally, we use NVGLUframebuffer, provided by NanoVG
        //    - NVGLUframebuffer does not handle pixelRatio
        //    => using pixelRatio=DisplayFramebufferScale would lead to non anti-aliased rendering
        //    => you may want to create texture of bigger size and scale down the drawing, in order to
        //       improve the quality of the rendering

        // float pixelRatio = ImGui::GetIO().DisplayFramebufferScale.x;
        float pixelRatio = 1.f;
        nvgBeginFrame(vg, texture.Width, texture.Height, pixelRatio);

#ifdef HAS_NVG_OPENGL
        // Flip the y-axis
        nvgSave(vg); // Save the current state
        nvgTranslate(vg, 0, texture.Height); // Move the origin to the bottom-left
        nvgScale(vg, 1, -1); // Flip the y-axis
#endif

        // Perform drawing operations
        drawFunc(vg, texture.Width, texture.Height);

        nvgRestore(vg); // Restore the original state
        nvgEndFrame(vg);
        nvgReset(vg); // Reset any temporary state changes that may have been made

        texture.Unbind();
    }


    // Context creation for HelloImGui
    NVGcontext* CreateNvgContext_HelloImGui(int flags)
    {
#ifdef HAS_NVG_OPENGL
        return CreateNvgContext_GL(flags);
#endif
#ifdef HAS_NVG_METAL
        return NvgHelloImGui::CreateNvgContext_Mtl_HelloImGui(flags);
#endif
        return nullptr;
    }

    void DeleteNvgContext_HelloImGui(NVGcontext* vg)
    {
#ifdef HAS_NVG_OPENGL
        DeleteNvgContext_GL(vg);
#endif
#ifdef HAS_NVG_METAL
        NvgHelloImGui::DeleteNvgContext_Mtl_HelloImGui(vg);
#endif
    }

}

#endif // #ifdef IMGUI_BUNDLE_WITH_NANOVG
