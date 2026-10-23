#pragma once
#ifdef IMGUI_BUNDLE_WITH_NANOVG

#if defined(HELLOIMGUI_HAS_OPENGL)
#define HAS_NVG_OPENGL
#endif
#if defined(HELLOIMGUI_HAS_METAL) && !defined(HELLOIMGUI_HAS_OPENGL)
#define HAS_NVG_METAL
#endif


#include "imgui.h"
#include <array>
#include <functional>
#include <memory>
#include <optional>
#include "nanovg.h"

struct NVGcontext;

// The 2x3 transforms for Python: a std::array<float, 6> in place of nanovg's float* (which would bind as one number).
// These overloads keep the C names; the functions that take float* are not bound.
inline std::array<float, 6> nvgCurrentTransform(NVGcontext* ctx) { std::array<float, 6> xform; nvgCurrentTransform(ctx, xform.data()); return xform; }
inline std::array<float, 6> nvgTransformIdentity() { std::array<float, 6> dst; nvgTransformIdentity(dst.data()); return dst; }
inline std::array<float, 6> nvgTransformTranslate(float tx, float ty) { std::array<float, 6> dst; nvgTransformTranslate(dst.data(), tx, ty); return dst; }
inline std::array<float, 6> nvgTransformScale(float sx, float sy) { std::array<float, 6> dst; nvgTransformScale(dst.data(), sx, sy); return dst; }
inline std::array<float, 6> nvgTransformRotate(float a) { std::array<float, 6> dst; nvgTransformRotate(dst.data(), a); return dst; }
inline std::array<float, 6> nvgTransformSkewX(float a) { std::array<float, 6> dst; nvgTransformSkewX(dst.data(), a); return dst; }
inline std::array<float, 6> nvgTransformSkewY(float a) { std::array<float, 6> dst; nvgTransformSkewY(dst.data(), a); return dst; }
// dst = dst * src
inline std::array<float, 6> nvgTransformMultiply(std::array<float, 6> dst, const std::array<float, 6>& src) { nvgTransformMultiply(dst.data(), src.data()); return dst; }
// dst = src * dst
inline std::array<float, 6> nvgTransformPremultiply(std::array<float, 6> dst, const std::array<float, 6>& src) { nvgTransformPremultiply(dst.data(), src.data()); return dst; }
// The inverse of src, or nullopt when src is singular
inline std::optional<std::array<float, 6>> nvgTransformInverse(const std::array<float, 6>& src) { std::array<float, 6> dst; if (!nvgTransformInverse(dst.data(), src.data())) return std::nullopt; return dst; }
// The point (srcx, srcy) transformed by xform
inline ImVec2 nvgTransformPoint(const std::array<float, 6>& xform, float srcx, float srcy) { ImVec2 r; nvgTransformPoint(&r.x, &r.y, xform.data(), srcx, srcy); return r; }

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
