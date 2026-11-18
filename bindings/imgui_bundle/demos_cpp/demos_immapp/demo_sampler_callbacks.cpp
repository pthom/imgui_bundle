// Sharp or smooth pixels: show a small image, a heatmap or pixel art, with sharp pixels instead of blurred ones.
// For a texture made by Dear ImGui, the renderer decides the sampling: DrawCallback_SetSamplerNearest asks it for sharp
// pixels. A texture made with OpenGL has its own filter, which the renderer ignores, unless
// DrawCallback_SetSamplerFromTex gives it back.
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include "imgui_rich_md/rich_md.h"
#include "imgui.h"
#include "imgui_internal.h"  // ImGui::RegisterUserTexture
#include "demo_utils/api_demos.h"
#ifdef HELLOIMGUI_HAS_OPENGL
#include "hello_imgui/hello_imgui_include_opengl.h"
#endif

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <map>
#include <vector>


namespace
{
// The heatmap's width and height, in pixels
constexpr int HEATMAP_PIXELS = 10;
// Each image's width and height on screen, in em (1 em = the height of a character)
constexpr float IMAGE_SIZE_EM = 10.f;


// --------------------------------------------------------------------------------------------------------------------
// Part 1: a texture made by Dear ImGui, from pixels. Its renderer decides the sampling.
// --------------------------------------------------------------------------------------------------------------------
// A small heatmap, as RGBA pixels: a smooth function of x and y, colored from dark blue to yellow (viridis)
std::vector<unsigned char> MakeHeatmap()
{
    const float anchors[5][3] = {{68, 1, 84}, {59, 82, 139}, {33, 145, 140}, {94, 201, 98}, {253, 231, 37}};
    std::vector<unsigned char> pixels;
    for (int row = 0; row < HEATMAP_PIXELS; ++row)
        for (int col = 0; col < HEATMAP_PIXELS; ++col)
        {
            float x = (float)col / (HEATMAP_PIXELS - 1), y = (float)row / (HEATMAP_PIXELS - 1);
            float value = 0.5f + 0.5f * std::sin(5.f * x + 1.f) * std::cos(4.f * y);  // in [0, 1]
            float position = value * 4.f;  // between two of the 5 anchors
            int i = std::min((int)position, 3);
            float t = position - (float)i;
            for (int c = 0; c < 3; ++c)
                pixels.push_back((unsigned char)(anchors[i][c] + t * (anchors[i + 1][c] - anchors[i][c])));
            pixels.push_back(255);
        }
    return pixels;
}

// The renderer backend (OpenGL, Metal, Vulkan, WebGL...) uploads it at the end of the frame that creates it
ImTextureData gHeatmapTexture;

ImTextureRef HeatmapTexture()
{
    // "Destroyed": not created yet, or destroyed with the renderer of a previous run
    if (gHeatmapTexture.Status == ImTextureStatus_Destroyed)
    {
        gHeatmapTexture.Create(ImTextureFormat_RGBA32, HEATMAP_PIXELS, HEATMAP_PIXELS);
        std::vector<unsigned char> pixels = MakeHeatmap();
        std::memcpy(gHeatmapTexture.GetPixels(), pixels.data(), pixels.size());
        ImGui::RegisterUserTexture(&gHeatmapTexture);
    }
    return gHeatmapTexture.GetTexRef();
}


#ifdef HELLOIMGUI_HAS_OPENGL
// --------------------------------------------------------------------------------------------------------------------
// Part 2: textures made with OpenGL, each with its own filter (glTexParameteri). The renderer ignores it,
// unless DrawCallback_SetSamplerFromTex asks it to use it.
// --------------------------------------------------------------------------------------------------------------------
// A pixel-art heart: '#' its outline, 'x' its red, 'o' its highlight, '.' transparent
const char* HEART[] = {
    "...........",
    "..##...##..",
    ".#xx#.#xx#.",
    "#xoxx#xxxx#",
    "#xoxxxxxxx#",
    "#xxxxxxxxx#",
    ".#xxxxxxx#.",
    "..#xxxxx#..",
    "...#xxx#...",
    "....#x#....",
    ".....#.....",
};
constexpr int HEART_SIZE = 11;

std::vector<unsigned char> MakeHeart()
{
    std::vector<unsigned char> pixels;
    for (const char* row : HEART)
        for (int col = 0; col < HEART_SIZE; ++col)
            switch (row[col])
            {
                case '#': pixels.insert(pixels.end(), {110, 20, 40, 255}); break;
                case 'x': pixels.insert(pixels.end(), {225, 45, 70, 255}); break;
                case 'o': pixels.insert(pixels.end(), {255, 180, 190, 255}); break;
                default: pixels.insert(pixels.end(), {0, 0, 0, 0}); break;
            }
    return pixels;
}

std::map<GLint, GLuint> gOpenGlHeartIds;  // the OpenGL texture of the heart, by its filter

// The heart as a texture made with OpenGL, with its own filter: GL_NEAREST or GL_LINEAR
ImTextureRef OpenGlHeart(GLint glFilter)
{
    if (gOpenGlHeartIds.count(glFilter) == 0)
    {
        std::vector<unsigned char> heart = MakeHeart();
        GLuint textureId;
        glGenTextures(1, &textureId);
        glBindTexture(GL_TEXTURE_2D, textureId);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, glFilter);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, glFilter);
        // Clamp: by default, a linear filter at an edge blends in the opposite edge
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, HEART_SIZE, HEART_SIZE, 0, GL_RGBA, GL_UNSIGNED_BYTE, heart.data());
        gOpenGlHeartIds[glFilter] = textureId;
    }
    return ImTextureRef((ImTextureID)(intptr_t)gOpenGlHeartIds[glFilter]);
}
#endif // #ifdef HELLOIMGUI_HAS_OPENGL


void ImageWithCaption(ImTextureRef texRef, const char* caption)
{
    ImGui::BeginGroup();
    ImGui::Image(texRef, HelloImGui::EmToVec2(IMAGE_SIZE_EM, IMAGE_SIZE_EM));
    ImGui::TextUnformatted(caption);
    ImGui::EndGroup();
}
} // namespace


void gui_demo_sampler_callbacks()
{
    ImDrawList* drawList = ImGui::GetWindowDrawList();
    // The renderer backend gives its standard callbacks here: NULL when it does not support one
    ImGuiPlatformIO& platformIo = ImGui::GetPlatformIO();

    RichMd::Render(R"(
        # Sharp or smooth pixels
        Shown large, a small image blurs: Dear ImGui draws images with *linear* sampling.
        For a heatmap or pixel art, each pixel should stay a sharp square: *nearest* sampling.

        ## A texture made by Dear ImGui: the renderer decides
        `DrawCallback_SetSamplerNearest` asks the renderer for nearest sampling, for the images that follow.
        )");
    if (platformIo.DrawCallback_SetSamplerNearest != nullptr)
    {
        drawList->AddCallback(platformIo.DrawCallback_SetSamplerNearest);  // the images that follow: nearest sampling
        ImageWithCaption(HeatmapTexture(), "SetSamplerNearest\nsharp");
        drawList->AddCallback(platformIo.DrawCallback_SetSamplerLinear);  // back to the default, for what follows
        ImGui::SameLine();
    }
    ImageWithCaption(HeatmapTexture(), "The default\nsmooth");

    ImGui::Dummy(HelloImGui::EmToVec2(0.f, 1.f));
    RichMd::Render(R"(
        ## A texture made with OpenGL: it decides
        Each texture has its own filter, but the renderer imposes its sampling (since Dear ImGui 1.92.8).
        `DrawCallback_SetSamplerFromTex` gives each texture its own filter back.
        )");
#ifdef HELLOIMGUI_HAS_OPENGL
    if (platformIo.DrawCallback_SetSamplerFromTex == nullptr)
        ImGui::TextUnformatted("This renderer cannot use a texture's own filter (OpenGL only).");
    else
    {
        drawList->AddCallback(platformIo.DrawCallback_SetSamplerFromTex);  // the images that follow: their own filter
        ImageWithCaption(OpenGlHeart(GL_NEAREST), "GL_NEAREST\nFromTex: sharp");
        ImGui::SameLine();
        ImageWithCaption(OpenGlHeart(GL_LINEAR), "GL_LINEAR\nFromTex: smooth");
        // Back to the renderer's sampling. After SetSamplerFromTex, SetSamplerLinear would write GL_LINEAR
        // into the textures that follow, which would lose their own filter.
        drawList->AddCallback(platformIo.DrawCallback_ResetRenderState);
        ImGui::SameLine();
        ImageWithCaption(OpenGlHeart(GL_NEAREST), "GL_NEAREST\nthe default: blurred");
    }
#else
    ImGui::TextUnformatted("This part needs the OpenGL renderer.");
#endif
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    // This call is specific to the ImGui Bundle Explorer. In a standard application, you could write:
    //         HelloImGui::SetAssetsFolder("my_assets"); // (By default, HelloImGui will search inside "assets")
    ChdirBesideAssetsFolder();

    HelloImGui::SimpleRunnerParams runnerParams{
        .guiFunction = gui_demo_sampler_callbacks, .windowTitle = "Sharp or smooth pixels", .windowSize = {540, 740}};
    ImmApp::AddOnsParams addons{.withMarkdown = true};
    ImmApp::Run(runnerParams, addons);
    return 0;
}
#endif
