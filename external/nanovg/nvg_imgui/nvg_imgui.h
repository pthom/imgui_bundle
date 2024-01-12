#pragma once

#include "imgui.h"
#include <functional>
#include <memory>
#include "nanovg.h"

struct NVGcontext;

namespace NvgImgui
{
    using NvgDrawingFunction = std::function<void(float width, float height)>;

    // Duplicate of NVGcreateFlags in nanovg_gl.h
    enum NvgCreateFlags {
        // Flag indicating if geometry based anti-aliasing is used (may not be needed when using MSAA).
        NVG_ANTIALIAS 		= 1<<0,
        // Flag indicating if strokes should be drawn using stencil buffer. The rendering will be a little
        // slower, but path overlaps (i.e. self-intersecting or sharp turns) will be drawn just once.
        NVG_STENCIL_STROKES	= 1<<1,
        // Flag indicating that additional debug checks are done.
        NVG_DEBUG 			= 1<<2,
    };

    // Creates a NanoVG context, using the current rendering backend (OpenGL, Metal, ...)
    // Currently, the only supported backend is OpenGL (see NVGcreateFlags_GL)
    NVGcontext* CreateNvgContext(int flags = 0);

    // Deletes a NanoVG context
    void DeleteNvgContext(NVGcontext* vg);

    // Abstract class to represent a framebuffer that can be used by NanoVG + ImGui
    struct NvgFramebuffer
    {
        int Width, Height;
        int NvgImageFlags;
        ImTextureID TextureId;

        NvgFramebuffer(int width, int height, int nvgImageFlags) // See NVGimageFlags
            : Width(width), Height(height), NvgImageFlags(nvgImageFlags)
        {}
        virtual void Bind() = 0;
        virtual void Unbind() = 0;

        virtual ~NvgFramebuffer() = default;
    };

    using NvgFramebufferPtr = std::shared_ptr<NvgFramebuffer>;

    // Factory function: will create a NvgFramebuffer according to the current rendering backend
    NvgFramebufferPtr CreateNvgFramebuffer(NVGcontext* vg, int width, int height, int nvImageFlags);


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
        NvgFramebufferPtr texture,
        NvgDrawingFunction drawFunc,
        ImVec4 clearColor = ImVec4(0.f, 0.f, 0.f, 1.f)
        );

}

