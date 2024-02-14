#pragma once
#ifdef IMGUI_BUNDLE_WITH_NANOVG

#if defined(HELLOIMGUI_HAS_OPENGL)
#define HAS_NVG_OPENGL
#endif
#if defined(HELLOIMGUI_HAS_METAL) && !defined(HELLOIMGUI_HAS_OPENGL)
#define HAS_NVG_METAL
#endif


#include "imgui.h"
#include <functional>
#include <memory>
#include "nanovg.h"

struct NVGcontext;

namespace NvgImgui
{

    ///////////////////////////////////////////////////////////////////////////
    //
    //           NanoVG context creation/deletion
    //
    ///////////////////////////////////////////////////////////////////////////

    // Combination of NVGcreateFlags in nanovg_gl.h + nanovg_mtl.h
    enum NvgCreateFlags {
        // Flag indicating if geometry based antialiasing is used (may not be needed when using MSAA).
        NVG_ANTIALIAS 		= 1<<0,
        // Flag indicating if strokes should be drawn using stencil buffer. The rendering will be a little
        // slower, but path overlaps (i.e. self-intersecting or sharp turns) will be drawn just once.
        NVG_STENCIL_STROKES	= 1<<1,
        // Flag indicating that additional debug checks are done.
        NVG_DEBUG 			= 1<<2,

        // Flag indicating if double buffering scheme is used (Metal only!)
        NVG_DOUBLE_BUFFER = 1 << 12,
        // Flag indicating if triple buffering scheme is used (Metal only!)
        NVG_TRIPLE_BUFFER = 1 << 13,
    };

#ifdef HAS_NVG_OPENGL
    // Creates a NanoVG context for OpenGL
    // This is just a wrapper that will call either nvgCreateGL3 or nvgCreateGLES3
    NVGcontext* CreateNvgContext_GL(int flags = 0);

    // Deletes a NanoVG context (created with CreateNvgContext_GL)
    void DeleteNvgContext_GL(NVGcontext* vg);
#endif
#ifdef HAS_NVG_METAL
    // For metal, and if you are not using HelloImGui, you need to include
    // nanovg_mtl.h and use nvgCreateMTL and nvgDeleteMTL
#endif

    // If using HelloImGui, you can use this function to create a NanoVG context
    // (it will select the correct function depending on the rendering backend)
    NVGcontext* CreateNvgContext_HelloImGui(int flags = 0);
    void DeleteNvgContext_HelloImGui(NVGcontext* vg);


    ///////////////////////////////////////////////////////////////////////////
    //
    //           NanoVG framebuffer
    //
    ///////////////////////////////////////////////////////////////////////////

    // NvgFramebuffer: a framebuffer that can be used by NanoVG + ImGui
    // Internally stored inside the renderer backend (e.g. OpenGL)
    // Note: this class can be instantiated only after a valid renderer backend (OpenGL) has been created
    class NvgFramebuffer
    {
    public:
        NVGcontext *vg = nullptr;
        int Width = 0, Height = 0;
        int NvgImageFlags = 0;
        ImTextureID TextureId = {};

        // Warning: this constructor can be called only after a valid renderer backend (OpenGL) has been created
        // (will call Init())
        NvgFramebuffer(
            NVGcontext *vg,
            int width, int height,
            int nvgImageFlags
            ); // See NVGimageFlags

        // Warning: this destructor should be called when a valid render backend (e.g. OpenGL) is still active
        // and when the NVGcontext vg is still valid
        ~NvgFramebuffer();

        // Make the framebuffer the current render target
        void Bind();

        // Restore the previous render target
        void Unbind();

    private:
        // PImpl that contains the actual implementation of the framebuffer, depending on the rendering backend
        struct PImpl;
        PImpl* pImpl = nullptr;
    };


    ///////////////////////////////////////////////////////////////////////////
    //
    //                 NanoVG rendering utilities
    //   (render NanoVG to either ImGui background or to a framebuffer)
    //
    ///////////////////////////////////////////////////////////////////////////

    // NvgDrawingFunction: a function that can be used to draw to a NanoVG context
    // it receives the NanoVG context, and the width and height of the rendering
    using NvgDrawingFunction = std::function<void(NVGcontext* vg, float width, float height)>;

    // Render the given drawing function to the background of the application
    // (i.e. the main viewport)
    // If clearColor.w > 0.f, the background will be cleared with this color
    void RenderNvgToBackground(
        NVGcontext* vg,
        NvgDrawingFunction nvgDrawingFunction,
        ImVec4 clearColor = ImVec4(0.f, 0.f, 0.f, 1.f)
        );

    // Render the given drawing function to the given framebuffer
    // If clearColor.w > 0.f, the background will be cleared with this color
    void RenderNvgToFrameBuffer(
        NVGcontext* vg,
        NvgFramebuffer& texture,
        NvgDrawingFunction drawFunc,
        ImVec4 clearColor = ImVec4(0.f, 0.f, 0.f, 1.f)
        );

}

#endif // #ifdef IMGUI_BUNDLE_WITH_NANOVG
