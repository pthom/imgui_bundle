// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui.h                                                                          //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#if defined(__ANDROID__) && defined(HELLOIMGUI_USE_SDL2)
// We need to include SDL, so that it can instantiate its main function under Android
#include "SDL.h"
#endif


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/dpi_aware.h included by hello_imgui.h                                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include "imgui.h"

namespace HelloImGui
{
// @@md#DpiAwareParams

//
// Hello ImGui will try its best to automatically handle DPI scaling for you.
//
// Parameters to change the scaling behavior:
// ------------------------------------------
// - `dpiWindowSizeFactor`:
//        factor by which window size should be multiplied
//
// - `fontRenderingScale`:
//     factor by which fonts glyphs should be scaled at rendering time
//     (typically 1 on windows, and 0.5 on macOS retina screens)
//
//    By default, Hello ImGui will compute them automatically,
//    when dpiWindowSizeFactor and fontRenderingScale are set to 0.
//
// Parameters to improve font rendering quality:
// ---------------------------------------------
// - `fontOversampleH` and `fontOversampleV` : Font oversampling parameters
//     Rasterize at higher quality for sub-pixel positioning. Probably unused if freeType is used.
//     If not zero, these values will be used to set the oversampling factor when loading fonts.
//
//
// How to set those values manually:
// ---------------------------------
// If it fails (i.e. your window and/or fonts are too big or too small),
// you may set them manually:
//    (1) Either by setting them programmatically in your application
//        (set their values in `runnerParams.dpiAwareParams`)
//    (2) Either by setting them in a `hello_imgui.ini` file. See hello_imgui/hello_imgui_example.ini for more info
// Note: if several methods are used, the order of priority is (1) > (2)
//
// For more information, see the documentation on DPI handling, here: https://pthom.github.io/hello_imgui/book/doc_api.html#handling-screens-with-high-dpi
//
struct DpiAwareParams
{
    // `dpiWindowSizeFactor`
    //     factor by which window size should be multiplied to get a similar
    //     physical size on different OSes (as if they were all displayed on a 96 PPI screen).
    //     This affects the size of native app windows,
    //     but *not* imgui Windows, and *not* the size of widgets and text.
    //  In a standard environment (i.e. outside of Hello ImGui), an application with a size of 960x480 pixels,
    //  may have a physical size (in mm or inches) that varies depending on the screen DPI, and the OS.
    //
    //  Inside Hello ImGui, the window size is always treated as targeting a 96 PPI screen, so that its size will
    //  look similar whatever the OS and the screen DPI.
    //  In our example, our 960x480 pixels window will try to correspond to a 10x5 inches window
    //
    //  Hello ImGui does its best to compute it on all OSes.
    //  However, if it fails you may set its value manually.
    //  If it is set to 0, Hello ImGui will compute it automatically,
    //  and the resulting value will be stored in `dpiWindowSizeFactor`.
    float dpiWindowSizeFactor = 0.0f;

    // `fontRenderingScale`
    //     factor (that is either 1 or < 1.) by which fonts glyphs should be scaled at rendering time.
    //  On macOS retina screens, it will be 0.5, since macOS APIs hide the real resolution of the screen.
    //  Changing this value will *not* change the visible font size on the screen, however it will
    //  affect the size of the loaded glyphs.
    //  For example, if fontRenderingScale=0.5 (which is the default on a macOS retina screen),
    //  a font size of 16 will be loaded as if it was 32, and will be rendered at half size.
    //   This leads to a better rendering quality on some platforms.
    // (This parameter will be used to set ImGui::GetIO().FontGlobalScale at startup)
    float fontRenderingScale = 0.0f;

    // `onlyUseFontDpiResponsive`
    // If true, guarantees that only HelloImGui::LoadDpiResponsiveFont will be used to load fonts.
    // (also for the default font)
    bool onlyUseFontDpiResponsive = false;

    // `fontOversampleH` and `fontOversampleV` : Font oversampling parameters
    // Rasterize at higher quality for sub-pixel positioning. Probably unused if freeType is used.
    // If not zero, these values will be used to set the oversampling factor when loading fonts.
    // (i.e. they will be set in ImFontConfig::OversampleH and ImFontConfig::OversampleV)
    // OversampleH: The difference between 2 and 3 for OversampleH is minimal.
    //              You can reduce this to 1 for large glyphs save memory.
    // OversampleV: This is not really useful as we don't use sub-pixel positions on the Y axis.
    // Read https://github.com/nothings/stb/blob/master/tests/oversample/README.md for details.
    int             fontOversampleH = 0;  // Default is 2 in ImFontConfig
    int             fontOversampleV = 0;  // Default is 1 in ImFontConfig


    // `dpiFontLoadingFactor`
    //     factor by which font size should be multiplied at loading time to get a similar
    //     visible size on different OSes.
    //  The size will be equivalent to a size given for a 96 PPI screen
    float DpiFontLoadingFactor() const {
        float r = dpiWindowSizeFactor / fontRenderingScale;
        return r;
    };
};

// ----------------------------------------------------------------------------

// @@md

/**
@@md#DocEmToVec2

Special care must be taken in order to correctly handle screen with high DPI
 (for example, almost all recent laptops screens).

Using ImVec2 with fixed values is *almost always a bad idea* if you intend your
application to be used on high DPI screens!
Otherwise, widgets might be misplaced or too small on different screens and/or OS.

Instead you should use scale your widgets and windows relatively to the font size,
as is done with the [em CSS Unit](https://lyty.dev/css/css-unit.html).

@@md
**/

// @@md#EmToVec2
//  __HelloImGui::EmToVec2()__ returns an ImVec2 that you can use to size
//  or place your widgets in a DPI independent way.
//  Values are in multiples of the font size (i.e. as in the em CSS unit).
ImVec2 EmToVec2(float x, float y);
ImVec2 EmToVec2(ImVec2 v);

// __HelloImGui::EmSize()__ returns the visible font size on the screen.
float EmSize();
// __HelloImGui::EmSize(nbLines)__ returns a size corresponding to nbLines text lines
float EmSize(float nbLines);

// __HelloImGui::PixelToEm()__ converts a Vec2 in pixels coord to a Vec2 in em units
ImVec2 PixelsToEm(ImVec2 pixels);

// __HelloImGui::PixelSizeToEm()__ converts a size in pixels coord to a size in em units
float  PixelSizeToEm(float pixelSize);

// @@md

// Returns the current DpiAwareParams, which are used
// for font loading and window size scaling
DpiAwareParams* GetDpiAwareParams();

} // namespace HelloImGui


// ----------------------------------------------------------------------------

//
// Legacy API, you should use RunnerParams.dpAwareParams instead
//
namespace HelloImGui
{
// Multiply font sizes by this factor when loading fonts manually with ImGui::GetIO().Fonts->AddFont...
// (HelloImGui::LoadFontTTF does this by default)
float DpiFontLoadingFactor();

// DpiWindowSizeFactor() is the factor by which window size should be multiplied to get a similar visible size on different OSes.
// It returns ApplicationScreenPixelPerInch / 96  under windows and linux. Under macOS, it will return 1.
float DpiWindowSizeFactor();

// returns the default value that should be stored inside `ImGui::GetIO().FontGlobalScale`
float ImGuiDefaultFontGlobalScale();
} // namespace HelloImGui


// ----------------------------------------------------------------------------
//           Handling screens with high DPI
// ----------------------------------------------------------------------------
/*
@@md#HandlingScreenHighDPI

_Note: This part is relevant only for more advanced usages. If you use `HelloImGui::LoadFont()`,
 and always use `HelloImGui::EmToVec2()` to place widgets, you do not need to worry about DPI handling_

## OS specificities

There are several important things to know about high-DPI handling within Hello ImGui and Dear ImGui:

1. (virtual) screen coordinates vs (physical) pixels
2. DisplayFramebufferScale: Frame buffer size vs window size
3. FontGlobalScale: display-time font scaling factor
4. How to load fonts with the correct size
5. How to get similar window sizes on different OSes/DPI


## Screen coordinates

Screen coordinates are the coordinates you use to place and size windows on the screen.

**Screen coordinates do not always correspond to physical pixels**

- On macOS/iOS retina screens, a screen coordinate corresponds typically
  to 2x2 physical pixels (but this may vary if you change the display scaling)
- On most Linux distributions, whenever there is a high DPI screen
  you can set the display scale. For example if you set the scale to 300%,
  then a screen coordinate will correspond to 3x3 physical pixels
- On Windows, there are two possible situations:
    - If the application is DPI aware, a screen coordinate corresponds to 1x1 physical pixel,
      and you can use the full extent of your screen resolution.
    - If the application is not DPI aware, a screen coordinate may correspond to 2x2 physical pixels
      (if the display scaling is set to 200% for example). However, the rendering of your application
      will be blurry and will not use the full extent of your screen resolution.
    - Notes:
        - Applications created with HelloImGui are DPI aware by default (when using glfw and sdl backends).
        - SDL applications are normally not DPI aware. However, HelloImGui makes them DPI aware.


## DisplayFramebufferScale
`DisplayFramebufferScale` is the ratio between the frame buffer size and the window size.

The frame buffer size is the size of the internal buffer used by the rendering backend.
It might be bigger than the actual window size.
`ImVec2 ImGui::GetIO().DisplayFramebufferScale` is a factor by which the frame buffer size is bigger than the window size.
It is set by the platform backend after it was initialized, and typically reflects the scaling ratio between
physical pixels and screen coordinates.

Under windows, it will always be (1,1). Under macOS / linux, it will reflect the current display scaling.
It will typically be (2,2) on a macOS retina screen.

Notes:
- You cannot change DisplayFramebufferScale manually, it will be reset at each new frame, by asking the platform backend.


## FontGlobalScale

`ImGui::GetIO().FontGlobalScale` is a factor by which fonts glyphs should be scaled at rendering time.
It is typically 1 on windows, and 0.5 on macOS retina screens.


## How to load fonts with the correct size

### Using HelloImGui (recommended)

[`HelloImGui::LoadFont()` and `HelloImGui::LoadFontDpiResponsive`](https://pthom.github.io/hello_imgui/book/doc_api.html#load-fonts) will load fonts
 with the correct size, taking into account the DPI scaling.

### Using Dear ImGui
`ImGui::GetIO().Fonts->AddFontFromFileTTF()` loads a font with a given size, in *physical pixels*.

If for example, DisplayFramebufferScale is (2,2), and you load a font with a size of 16, it will by default be rendered
 with size of 16 *virtual screen coordinate pixels* (i.e. 32 physical pixels). This will lead to blurry text.
To solve this, you should load your font with a size of 16 *virtual screen coordinate pixels* (i.e. 32 physical pixels),
and set `ImGui::GetIO().FontGlobalScale` to 0.5.

Helpers if using `ImGui::GetIO().Fonts->AddFontFromFileTTF()`:
- `HelloImGui::ImGuiDefaultFontGlobalScale()` returns the default value that should be stored inside `ImGui::GetIO().FontGlobalScale`.
- `HelloImGui::DpiFontLoadingFactor()` returns a factor by which you shall multiply your font sizes when loading them.


## Reproducible physical window sizes (in mm or inches)

### Using HelloImGui
Simply specify a window size that corresponds to theoretical 96 PPI screen (inside `RunnerParams.appWindowParams.windowGeometry.size`)

### Using your own code to create the backend window
If you prefer to create the window by yourself, its physical size in millimeters may vary widely,
depending on the OS and the current screen DPI setting.
Typically under Windows, your window may appear to be very small if your screen is high DPI.

To get a similar window size on different OSes/DPI, you should multiply the window size by `HelloImGui::DpiWindowSizeFactor()`.

Note: DpiWindowSizeFactor() is equal to `CurrentScreenPixelPerInch / 96` under windows and linux, and always 1 under macOS.

## Fine tune DPI Handling

See [`HelloImGui::DpiAwareParams`](https://pthom.github.io/hello_imgui/book/doc_params.html#dpi-aware-params)
for more information on how to fine tune DPI handling when using Hello ImGui.
@@md
*/

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_assets.h included by hello_imgui.h                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <string>

namespace HelloImGui
{
/**
@@md#AssetsStructure

Assets located beside the application CMakeLists are embedded automatically.

For example, you can have the following project structure:
```
my_app/
├── CMakeLists.txt        # Your app's CMakeLists
├── assets/               # Its assets: for mobile devices and emscripten
│         └── fonts/            # they are embedded automatically by hello_imgui_add_app.cmake
│             └── my_font.ttf
├── my_app.main.cpp       # Its source code
```

Then you can load the asset "fonts/my_font.ttf", on all platforms.

@@md
*/


// @@md#LoadAssetFileData

struct AssetFileData
{
    void * data = nullptr;
    size_t dataSize = 0;
};

// LoadAssetFileData(const char *assetPath)`
// Will load an entire asset file into memory. This works on all platforms,
// including android.
// You *have* to call FreeAssetFileData to free the memory, except if you use
// ImGui::GetIO().Fonts->AddFontFromMemoryTTF, which will take ownership of the
// data and free it for you.
AssetFileData LoadAssetFileData(const char *assetPath);

// FreeAssetFileData(AssetFileData *)
// Will free the memory.
// Note: "ImGui::GetIO().Fonts->AddFontFromMemoryTTF" takes ownership of the data
// and will free the memory for you.
void FreeAssetFileData(AssetFileData * assetFileData);
// @@md


// @@md#assetFileFullPath

//`std::string AssetFileFullPath(const std::string& assetRelativeFilename)`
// will return the path to assets.
//
// This works under all platforms *except Android*
// For compatibility with Android and other platforms, prefer to use `LoadAssetFileData`
// whenever possible.
//    * Under iOS it will give a path in the app bundle (/private/XXX/....)
//    * Under emscripten, it will be stored in the virtual filesystem at "/"
//    * Under Android, assetFileFullPath is *not* implemented, and will throw an error:
//      assets can be compressed under android, and you can't use standard file operations!
//      Use LoadAssetFileData instead
std::string AssetFileFullPath(const std::string& assetRelativeFilename,
                              bool assertIfNotFound = true);

// Returns true if this asset file exists
bool AssetExists(const std::string& assetRelativeFilename);

// Sets the assets folder location
// (when using this, automatic assets installation on mobile platforms may not work)
void SetAssetsFolder(const std::string& folder);

// @@md



// Legacy API, kept for compatibility
void SetAssetsFolder(const char* folder);
inline std::string assetFileFullPath(const std::string& assetRelativeFilename, bool assertIfNotFound = true)
    { return AssetFileFullPath(assetRelativeFilename, assertIfNotFound); }
void overrideAssetsFolder(const char* folder); // synonym of SetAssetsFolder

extern std::string gAssetsSubfolderFolderName;  // "assets" by default

} // namespace HelloImGui

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_error.h included by hello_imgui.h                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <stdexcept>
#include <iostream>


#define HIMG_ERROR(msg) \
    { \
        std::cerr << "HelloImGui ERROR: " << msg << "\t\t at " << __FILE__ << ":" << __LINE__ << "\n"; \
        IM_ASSERT(false); \
    }

#ifdef __EMSCRIPTEN__
// Log utilities for emscripten, where the best debug tool is printf


#define HIMG_LOG(...) \
{\
    std::cout << "HIMG_LOG: " << __VA_ARGS__ << "\t\t at " << __FILE__ << ":" << __LINE__ << "\n"; \
}

#define HIMG_LOG_VALUE(...) \
{\
    std::cout << "HIMG_LOG_VALUE: " << #__VA_ARGS__ << "=" << (__VA_ARGS__) << "\t\t at " << __FILE__ << ":" << __LINE__ << "\n"; \
}

#define HIMG_LOG_POINTER(value) \
{\
    std::cout << "HIMG_LOG_POINTEr: " << #value << "=" << (size_t)(void *)value << "\t\t at " << __FILE__ << ":" << __LINE__ << "\n"; \
}

#else
#define HIMG_LOG(...) {}
#define HIMG_LOG_VALUE(...) {}
#define HIMG_LOG_POINTER(value) {}
#endif

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_logger.h included by hello_imgui.h                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/**
@@md#HelloImGui::Log

HelloImGui provides a simple Log utility that is able to collect message and display them with a specific widget.

* __HelloImGui::Log(LogLevel level, char const* const format, ... )__ will log a message (printf like format)
* __HelloImGui::LogClear()__ will clear the Log list
* __HelloImGui::LogGui()__ will display the Log widget

@@md
*/
namespace HelloImGui
{
    enum class LogLevel
    {
        Debug,
        Info,
        Warning,
        Error
    };

    void Log(LogLevel level, char const* const format, ...);
    void LogClear();
    void LogGui(ImVec2 size=ImVec2(0.f, 0.f));
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/image_from_asset.h included by hello_imgui.h                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace HelloImGui
{
// @@md#HelloImGui::ImageFromAsset

//
//Images are loaded when first displayed, and then cached
// (they will be freed just before the application exits).
//
//For example, given this files structure:
//```
//├── CMakeLists.txt
//├── assets/
//│         └── my_image.jpg
//└── my_app.main.cpp
//```
//
//then, you can display "my_image.jpg", using:
//
//    ```cpp
//    HelloImGui::ImageFromAsset("my_image.jpg");
//    ```


// `HelloImGui::ImageFromAsset(const char *assetPath, size, ...)`:
// will display a static image from the assets.
void ImageFromAsset(const char *assetPath, const ImVec2& size = ImVec2(0, 0),
                    const ImVec2& uv0 = ImVec2(0, 0), const ImVec2& uv1 = ImVec2(1,1),
                    const ImVec4& tint_col = ImVec4(1,1,1,1),
                    const ImVec4& border_col = ImVec4(0,0,0,0));

// `bool HelloImGui::ImageButtonFromAsset(const char *assetPath, size, ...)`:
// will display a button using an image from the assets.
bool ImageButtonFromAsset(const char *assetPath, const ImVec2& size = ImVec2(0, 0),
                          const ImVec2& uv0 = ImVec2(0, 0),  const ImVec2& uv1 = ImVec2(1,1),
                          int frame_padding = -1,
                          const ImVec4& bg_col = ImVec4(0,0,0,0),
                          const ImVec4& tint_col = ImVec4(1,1,1,1));

// `ImTextureID HelloImGui::ImTextureIdFromAsset(assetPath)`:
// will return a texture ID for an image loaded from the assets.
ImTextureID ImTextureIdFromAsset(const char *assetPath);

// `ImVec2 HelloImGui::ImageSizeFromAsset(assetPath)`:
// will return the size of an image loaded from the assets.
ImVec2 ImageSizeFromAsset(const char *assetPath);


// `HelloImGui::ImageAndSize HelloImGui::ImageAndSizeFromAsset(assetPath)`:
// will return the texture ID and the size of an image loaded from the assets.
struct ImageAndSize
{
    ImTextureID textureId = ImTextureID(0);
    ImVec2 size = ImVec2(0.f, 0.f);
};
ImageAndSize ImageAndSizeFromAsset(const char *assetPath);


// `ImVec2 HelloImGui::ImageProportionalSize(askedSize, imageSize)`:
//  will return the displayed size of an image.
//     - if askedSize.x or askedSize.y is 0, then the corresponding dimension
//       will be computed from the image size, keeping the aspect ratio.
//     - if askedSize.x>0 and askedSize.y> 0, then the image will be scaled to fit
//       exactly the askedSize, thus potentially changing the aspect ratio.
//  Note: this function is used internally by ImageFromAsset and ImageButtonFromAsset,
//        so you don't need to call it directly.
ImVec2 ImageProportionalSize(const ImVec2& askedSize, const ImVec2& imageSize);

// @@md

namespace internal
{
    void Free_ImageFromAssetMap();
}
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/imgui_theme.h included by hello_imgui.h                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// Theme tweak utilities for ImGui.
// Reuse and adaptation of imgui_theme.h and imgui_theme.cpp file is granted for other projects,
// provided the origin of those files is stated in the copied version
// Some themes were adapted by themes posted by ImGui users at https://github.com/ocornut/imgui/issues/707
//

namespace ImGuiTheme
{
    enum ImGuiTheme_
    {
        ImGuiTheme_ImGuiColorsClassic = 0,
        ImGuiTheme_ImGuiColorsDark,
        ImGuiTheme_ImGuiColorsLight,
        ImGuiTheme_MaterialFlat,
        ImGuiTheme_PhotoshopStyle,
        ImGuiTheme_GrayVariations,
        ImGuiTheme_GrayVariations_Darker,
        ImGuiTheme_MicrosoftStyle,
        ImGuiTheme_Cherry,
        ImGuiTheme_Darcula,
        ImGuiTheme_DarculaDarker,
        ImGuiTheme_LightRounded,
        ImGuiTheme_SoDark_AccentBlue,
        ImGuiTheme_SoDark_AccentYellow,
        ImGuiTheme_SoDark_AccentRed,
        ImGuiTheme_BlackIsBlack,
        ImGuiTheme_WhiteIsWhite,
        ImGuiTheme_Count
    };
    const char* ImGuiTheme_Name(ImGuiTheme_ theme);
    ImGuiTheme_ ImGuiTheme_FromName(const char* themeName);
    ImGuiStyle ThemeToStyle(ImGuiTheme_ theme);
    void ApplyTheme(ImGuiTheme_ theme);


    struct ImGuiThemeTweaks
    {
        // Common rounding for widgets. If < 0, this is ignored.
        float Rounding = -1.f;
        // If rounding is applied, scrollbar rounding needs to be adjusted to be visually pleasing in conjunction with other widgets roundings. Only applied if Rounding > 0.f)
        float RoundingScrollbarRatio = 4.f;
        // Change the alpha that will be applied to windows, popups, etc. If < 0, this is ignored.
        float AlphaMultiplier = -1.f;

        //
        // HSV Color tweaks
        //
        // Change the hue of all widgets (gray widgets will remain gray, since their saturation is zero). If < 0, this is ignored.
        float Hue = -1.f;
        // Multiply the saturation of all widgets (gray widgets will remain gray, since their saturation is zero). If < 0, this is ignored.
        float SaturationMultiplier = -1.f;
        // Multiply the value (luminance) of all front widgets. If < 0, this is ignored.
        float ValueMultiplierFront = -1.f;
        // Multiply the value (luminance) of all backgrounds. If < 0, this is ignored.
        float ValueMultiplierBg = -1.f;
        // Multiply the value (luminance) of text. If < 0, this is ignored.
        float ValueMultiplierText = -1.f;
        // Multiply the value (luminance) of FrameBg. If < 0, this is ignored.
        // (Background of checkbox, radio button, plot, slider, text input)
        float ValueMultiplierFrameBg = -1.f;

        ImGuiThemeTweaks() {}
    };

    struct ImGuiTweakedTheme
    {
        ImGuiTheme_ Theme = ImGuiTheme_DarculaDarker;
        ImGuiThemeTweaks Tweaks = ImGuiThemeTweaks();

        ImGuiTweakedTheme(ImGuiTheme_ theme = ImGuiTheme_DarculaDarker, const ImGuiThemeTweaks& tweaks = ImGuiThemeTweaks())
            : Theme(theme), Tweaks(tweaks) {}
    };

    ImGuiStyle TweakedThemeThemeToStyle(const ImGuiTweakedTheme& tweaked_theme);
    void ApplyTweakedTheme(const ImGuiTweakedTheme& tweaked_theme);

    // PushTweakedTheme() / PopTweakedTheme()
    // Push and pop a tweaked theme
    //
    // Note: If you want the theme to apply globally to a window, you need to apply it
    //       *before* calling ImGui::Begin
    //
    //     For example, within Hello ImGui, given a dockable window, you should set this option:
    //        myDockableWindow.callBeginEnd = false;
    //     And then:
    //     - call ImGuiTheme::PushTweakedTheme
    //     - call ImGui::Begin
    //     - display your content
    //     - call ImGui::End
    //     - call ImGuiTheme::PopTweakedTheme
    //
    // See demo inside src/hello_imgui_demos/hello_imgui_demodocking/hello_imgui_demodocking.main.cpp:
    //     look at `GuiWindowAlternativeTheme()`
    void PushTweakedTheme(const ImGuiTweakedTheme& tweaked_theme);
    void PopTweakedTheme();

    // Show the theme selection listbox, the theme tweak widgets, as well as ImGui::ShowStyleEditor. Returns true if modified (Warning, when using ShowStyleEditor, no info about modification is transmitted)
    bool ShowThemeTweakGui(ImGuiTweakedTheme *tweaked_theme);

    // Some tweakable themes
    ImGuiStyle SoDark(float hue);
    ImGuiStyle ShadesOfGray(float rounding=0.f, float value_multiplier_front=1.f, float value_multiplier_bg=1.f);
    ImGuiStyle Darcula(
        float rounding=1.f,
        float hue=-1.f,
        float saturation_multiplier=1.f,
        float value_multiplier_front=1.f,
        float value_multiplier_bg=1.f,
        float alpha_bg_transparency=1.f
    );


} // namespace ImGuiTheme
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_theme.h included by hello_imgui.h                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace HelloImGui
{
    void ShowThemeTweakGuiWindow(bool* p_open = nullptr);
}
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_font.h included by hello_imgui.h                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <vector>
#include <array>

namespace HelloImGui
{
    using ImWcharPair = std::array<ImWchar, 2>;

    // Utility to translate DearImGui common Unicode ranges to ImWcharPair (Python)
    //   (get_glyph_ranges_chinese_simplified_common, get_glyph_ranges_japanese, ...)
    std::vector<ImWcharPair> translate_common_glyph_ranges(const std::vector<ImWchar> & glyphRanges);

    // Utility to translate DearImGui common Unicode ranges to ImWcharPair (C++)
    //   (GetGlyphRangesChineseSimplifiedCommon, GetGlyphRangesJapanese, ...)
    std::vector<ImWcharPair> TranslateCommonGlyphRanges(const ImWchar* glyphRanges);

    // @@md#Fonts

    // When loading fonts, use
    //          HelloImGui::LoadFont(..)
    //      or
    //      	HelloImGui::LoadDpiResponsiveFont()
    //
    // Use these functions instead of ImGui::GetIO().Fonts->AddFontFromFileTTF(),
    // because they will automatically adjust the font size to account for HighDPI,
    // and will help you to get consistent font size across different OSes.

    //
    // Font loading parameters: several options are available (color, merging, range, ...)
    struct FontLoadingParams
    {
        // if true, the font size will be adjusted automatically to account for HighDPI
        bool adjustSizeToDpi = true;

        // if true, the font will be loaded with the full glyph range
        bool useFullGlyphRange = false;
        // if set, fontConfig.GlyphRanges, and
        //   fontConfig.OversampleH / fontConfig.OversampleV will be set to 1
        //   when useFullGlyphRange is true (this is useful to save memory)
        bool reduceMemoryUsageIfFullGlyphRange = true;

        // if true, the font will be merged to the last font
        bool mergeToLastFont = false;

        // if true, the font will be loaded using colors
        // (requires freetype, enabled by IMGUI_ENABLE_FREETYPE)
        bool loadColor = false;

        // if true, the font will be loaded using HelloImGui asset system.
        // Otherwise, it will be loaded from the filesystem
        bool insideAssets = true;

        // the ranges of glyphs to load, as a list of pairs of ImWchar
        //    - if empty, the default glyph range will be used
        //    - you can specify several ranges
        //    - intervals bounds are inclusive
        // Note: in order to use common ranges defined by ImGui (GetGlyphRangesJapanese, GetGlyphRangesChinese, ...)
        //       use TranslateCommonGlyphRanges (or translate_common_glyph_ranges in Python)
        std::vector<ImWcharPair> glyphRanges = {};

        // ImGui native font config to use
        ImFontConfig fontConfig = ImFontConfig();

        // if true, the font will be loaded and then FontAwesome icons will be merged to it
        // (deprecated, use mergeToLastFont instead, and load in two steps)
        // This will use an old version of FontAwesome (FontAwesome 4)
        bool mergeFontAwesome = false;
        ImFontConfig fontConfigFontAwesome = ImFontConfig();
    };

    // A font that will be automatically resized to account for changes in DPI
    // Use LoadAdaptiveFont instead of LoadFont to get this behavior.
    // Fonts loaded with LoadAdaptiveFont will be reloaded during execution
    // if ImGui::GetIO().FontGlobalScale is changed.
    struct FontDpiResponsive
    {
        ImFont* font = nullptr;
        std::string fontFilename;
        float fontSize = 0.f;
        FontLoadingParams fontLoadingParams;
    };


    // Loads a font with the specified parameters
    // (this font will not adapt to DPI changes after startup)
    ImFont* LoadFont(
        const std::string & fontFilename, float fontSize,
        const FontLoadingParams & params = {});

    // Loads a font with the specified parameters
    // This font will adapt to DPI changes after startup.
    // Only fonts loaded with LoadAdaptiveFont will adapt to DPI changes:
    // avoid mixing LoadFont/LoadFontDpiResponsive)
    FontDpiResponsive* LoadFontDpiResponsive(
        const std::string & fontFilename, float fontSize,
        const FontLoadingParams & params = {});

    // @@md

    //
    // Deprecated API below, kept for compatibility (uses LoadFont internally)
    //
    ImFont* LoadFontTTF(
        const std::string & fontFilename,
        float fontSize,
        bool useFullGlyphRange = false,
        ImFontConfig config = ImFontConfig()
        );
    ImFont* LoadFontTTF_WithFontAwesomeIcons(
        const std::string & fontFilename,
        float fontSize,
        bool useFullGlyphRange = false,
        ImFontConfig configFont = ImFontConfig(),
        ImFontConfig configIcons = ImFontConfig()
        );
    ImFont* MergeFontAwesomeToLastFont(float fontSize, ImFontConfig config = ImFontConfig());


    // indicates that fonts were loaded using HelloImGui::LoadFont. In that case, fonts may have been resized to
    // account for HighDPI (on macOS and emscripten)
    bool DidCallHelloImGuiLoadFontTTF();
}
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/runner_params.h included by hello_imgui.h                                  //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/app_window_params.h included by hello_imgui/runner_params.h                //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/screen_bounds.h included by hello_imgui/app_window_params.h                //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <stddef.h>


#define ForDim2(dim) for (size_t dim = 0; dim < 2; dim += 1)


namespace HelloImGui
{
    using ScreenPosition = std::array<int, 2>;
    using ScreenSize = std::array<int, 2>;

    // Note: note related to DPI and high resolution screens:
    // ScreenPosition and ScreenSize are in "Screen Coordinates":
    // Screen coordinates *might* differ from real pixel on high dpi screens; but this depends on the OS.
    // - For example, on apple a retina screenpixel size 3456x2052 might be seen as 1728x1026 in screen coordinates
    // - Under windows, ScreenCoordinates correspond to pixels, even on high density screens
    constexpr ScreenPosition DefaultScreenPosition = {0, 0};
    constexpr ScreenSize DefaultWindowSize = {800, 600};

    struct ScreenBounds
    {
        ScreenPosition position = DefaultScreenPosition;
        ScreenSize size = DefaultWindowSize;

        ScreenPosition TopLeftCorner() const{ return position; }
        ScreenPosition BottomRightCorner() const{ return { position[0] + size[0], position[1] + size[1] }; }
        ScreenPosition Center() const{ return { position[0] + size[0] / 2, position[1] + size[1] / 2 }; }

        bool Contains(ScreenPosition pixel) const;
        ScreenPosition WinPositionCentered(ScreenSize windowSize) const;
        int DistanceFromPixel(ScreenPosition point) const;
        ScreenBounds EnsureWindowFitsThisMonitor(ScreenBounds windowBoundsOriginal) const;
        bool operator==(const ScreenBounds& other) const;
    };



} // namespace BackendApi

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/app_window_params.h continued                                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#ifdef __APPLE__
#include <TargetConditionals.h>
#endif

namespace HelloImGui
{
enum class FullScreenMode
{
    NoFullScreen,
    FullScreen,                    // Full screen with specified resolution
    FullScreenDesktopResolution,   // Full screen with current desktop mode & resolution
    FullMonitorWorkArea            // Fake full screen, maximized window on the selected monitor
};


enum class WindowSizeState
{
    Standard,
    Minimized,
    Maximized
};


enum class WindowPositionMode
{
    OsDefault,
    MonitorCenter,
    FromCoords,
};


enum class WindowSizeMeasureMode
{
    // ScreenCoords: measure window size in screen coords.
    //     Note: screen coordinates *might* differ from real pixel on high dpi screens; but this depends on the OS.
    //         - For example, on apple a retina screenpixel size 3456x2052 might be seen as 1728x1026 in screen
    //           coordinates
    //         - Under windows, and if the application is DPI aware, ScreenCoordinates correspond to real pixels,
    //           even on high density screens
    ScreenCoords,

    // RelativeTo96Ppi enables to give screen size that are independant from the screen density.
    // For example, a window size expressed as 800x600 will correspond to a size
    //    800x600 (in screen coords) if the monitor dpi is 96
    //    1600x120 (in screen coords) if the monitor dpi is 192
    RelativeTo96Ppi
};



// @@md#WindowGeometry
//
// WindowGeometry is a struct that defines the window geometry.
struct WindowGeometry
{
    // --------------- Window Size ------------------

    // Size of the application window
    // used if fullScreenMode==NoFullScreen and sizeAuto==false. Default=(800, 600)
    // The size will be handled as if it was specified for a 96PPI screen
    // (i.e. a given size will correspond to the same physical size on different screens, whatever their DPI)
    ScreenSize size = DefaultWindowSize;

    // If sizeAuto=true, adapt the app window size to the presented widgets.
    // After the first frame was displayed, HelloImGui will measure its size, and the
    // application window will be resized.
    // As a consequence, the application window may change between the 1st and 2nd frame.
    // If true, adapt the app window size to the presented widgets. This is done at startup
    bool sizeAuto = false;

    // `windowSizeState`: _WindowSizeState, default=Standard_
    //  You can choose between several window size states:
    //      Standard,
    //      Minimized,
    //      Maximized
    WindowSizeState windowSizeState = WindowSizeState::Standard;

    // `windowSizeMeasureMode`: _WindowSizeMeasureMode_, default=RelativeTo96Ppi
    // Define how the window size is specified:
    //      * RelativeTo96Ppi enables to give a screen size whose physical result
    //      (in millimeters) is independent of the screen density.
    //         For example, a window size expressed as 800x600 will correspond to a size
    //            - 800x600 (in screen coords) if the monitor dpi is 96
    //            - 1600x120 (in screen coords) if the monitor dpi is 192
    //          (this works with Glfw. With SDL, it only works under windows)
    //      * ScreenCoords: measure window size in screen coords
    //        (Note: screen coordinates might differ from real pixels on high dpi screen)
    WindowSizeMeasureMode windowSizeMeasureMode = WindowSizeMeasureMode::RelativeTo96Ppi;


    // --------------- Position ------------------

    // `positionMode`: you can choose between several window position modes:
    //      OsDefault,
    //      MonitorCenter,
    //      FromCoords,
    WindowPositionMode positionMode = WindowPositionMode::OsDefault;

    // `position`: used if windowPositionMode==FromCoords, default=(40, 40)
    ScreenPosition position = DefaultScreenPosition;

    // `monitorIdx`: index of the monitor to use, default=0
    //  used if positionMode==MonitorCenter or if fullScreenMode!=NoFullScreen
    int monitorIdx = 0;


    // --------------- Full screen ------------------

    // `fullScreenMode`: you can choose between several full screen modes:
    //      NoFullScreen,
    //      FullScreen,                  // Full screen with specified resolution
    //      FullScreenDesktopResolution, // Full screen with current desktop mode & resolution
    //      FullMonitorWorkArea          // Fake full screen (maximized window) on the selected monitor
    FullScreenMode fullScreenMode = FullScreenMode::NoFullScreen;


    // --------------- Auto Resize ------------------

    // `resizeAppWindowAtNextFrame`: _bool_, default=false;
    //  If you set this to flag to true at any point during the execution, the application
    //  window will then try to resize based on its content on the next displayed frame,
    //  and this flag will subsequently be set to false.
    //  Example:
    //   ```cpp
    //   // Will resize the app window at next displayed frame
    //   HelloImGui::GetRunnerParams()->appWindowParams.windowGeometry.resizeAppWindowAtNextFrame = true;
    //   ```
    //  Note: this flag is intended to be used during execution, not at startup
    //  (use sizeAuto at startup).
    bool resizeAppWindowAtNextFrame = false;
};
// @@md


// If there is a notch on the iPhone, you should not display inside these insets
struct EdgeInsets
{
    double top = 0.;     // Typically around 47
    double left = 0.;    // Typically 0
    double bottom = 0.;  // Typically around 34
    double right = 0.;   // Typically 0
};


// @@md#AppWindowParams
//
// AppWindowParams is a struct that defines the application window display params.
//See https://raw.githubusercontent.com/pthom/hello_imgui/master/src/hello_imgui/doc_src/hello_imgui_diagram.jpg
// for details.
struct AppWindowParams
{
    // --------------- Standard params ------------------

    // `windowTitle`: _string, default=""_. Title of the application window
    std::string windowTitle;

    // `windowGeometry`: _WindowGeometry_
    //  Enables to precisely set the window geometry (position, monitor, size,
    //  full screen, fake full screen, etc.)
    //   _Note: on a mobile device, the application will always be full screen._
    WindowGeometry windowGeometry;

    // `restorePreviousGeometry`: _bool, default=false_.
    // If true, then save & restore windowGeometry from last run (the geometry
    // will be written in imgui_app_window.ini)
    bool restorePreviousGeometry = false;

    // `resizable`: _bool, default = false_. Should the window be resizable.
    // This is taken into account at creation.
    bool resizable = true;
    // `hidden`: _bool, default = false_. Should the window be hidden.
    // This is taken into account dynamically (you can show/hide the window with this).
    // Full screen windows cannot be hidden.
    bool hidden = false;


    // --------------- Borderless window params ------------------

    // `borderless`: _bool, default = false_. Should the window have borders.
    // This is taken into account at creation.
    bool   borderless = false;
    // `borderlessMovable`: if the window is borderless, should it be movable.
    //   If so, a drag zone is displayed at the top of the window when the mouse is over it.
    bool   borderlessMovable = true;
    // `borderlessResizable`: if the window is borderless, should it be resizable.
    //  If so, a drag zone is displayed at the bottom-right of the window
    //  when the mouse is over it.
    bool   borderlessResizable = true;
    // `borderlessClosable`: if the window is borderless, should it have a close button.
    //  If so, a close button is displayed at the top-right of the window
    //  when the mouse is over it.
    bool   borderlessClosable = true;
    // `borderlessHighlightColor`:
    //   Color of the highlight displayed on resize/move zones.
    //   If borderlessHighlightColor.w==0, then the highlightColor will be automatically
    //   set to ImGui::GetColorU32(ImGuiCol_TitleBgActive, 0.6f)
    ImVec4 borderlessHighlightColor = ImVec4(0.2f, 0.4f, 1.f, 0.3f);


    // --------------- iOS Notch ------------------

    // `edgeInsets`: _EdgeInsets_. iOS only, out values filled by HelloImGui.
    // If there is a notch on the iPhone, you should not display inside these insets.
    // HelloImGui handles this automatically, if handleEdgeInsets is true and
    // if runnerParams.imGuiWindowParams.defaultImGuiWindowType is not NoDefaultWindow.
    // (warning, these values are updated only after a few frames,
    //  they are typically 0 for the first 4 frames)
    EdgeInsets edgeInsets;
    // `handleEdgeInsets`: _bool, default = true_. iOS only.
    // If true, HelloImGui will handle the edgeInsets on iOS.
    bool       handleEdgeInsets = true;

    // ----------------- repaint the window during resize -----------------
    // Very advanced and reserved for advanced C++ users.
    // If you set this to true, the window will be repainted during resize.
    // Do read https://github.com/pthom/hello_imgui/issues/112 for info about the possible gotchas
    // (This API is not stable, as the name suggests, and this is not supported)
    bool repaintDuringResize_GotchaReentrantRepaint = false;
};
// @@md

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/imgui_window_params.h included by hello_imgui/runner_params.h              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <functional>


namespace HelloImGui
{
// @@md#DefaultImGuiWindowType

// `DefaultImGuiWindowType` is an enum class that defines whether a full screen background
// window is provided or not
enum class DefaultImGuiWindowType
{
    // `ProvideFullScreenWindow`: a full window is provided in the background
    ProvideFullScreenWindow,
    // `ProvideFullScreenDockSpace`: a full screen dockspace is provided in the background
    ProvideFullScreenDockSpace,
    // `NoDefaultWindow`: No default window is provided
    // (except for ImGui's default "debug" window)
    NoDefaultWindow
};
// @@md


// @@md#ImGuiWindowParams

// `ImGuiWindowParams` is a struct that defines the ImGui inner windows params
// These settings affect the imgui inner windows inside the application window.
// In order to change the application window settings, change the `AppWindowsParams`
struct ImGuiWindowParams
{
    // ------------ Main Options  -------------------------------------------------------

    // defaultImGuiWindowType: (enum DefaultImGuiWindowType)
    // Choose between:
    //    - ProvideFullScreenWindow (default)
    //      a full window is provided in the background
    //      You can still add windows on top of it, since the Z-order
    //      of this background window is always behind
    //    - ProvideFullScreenDockSpace:
    //      a full screen dockspace is provided in the background
    //      (use this if you intend to use docking)
    //    - NoDefaultWindow:
    //      no default window is provided
    DefaultImGuiWindowType defaultImGuiWindowType =
        DefaultImGuiWindowType::ProvideFullScreenWindow;

    // enableViewports: Enable multiple viewports (i.e. multiple native windows)
    // If true, you can drag windows outside the main window,
    // in order to put their content into new native windows.
    bool enableViewports = false;

    // Make windows only movable from the title bar
    bool configWindowsMoveFromTitleBarOnly = true;


    // ------------ Menus & Status bar --------------------------------------------------

    // Set the title of the App menu. If empty, the menu name will use
    // the "windowTitle" from AppWindowParams//
    std::string menuAppTitle = "";

    // Show Menu bar on top of imgui main window.
    // In order to fully customize the menu, set showMenuBar to true, and set showMenu_App
    // and showMenu_View params to false. Then, implement the callback
    // `RunnerParams.callbacks.ShowMenus`
    // which can optionally call `HelloImGui::ShowViewMenu` and `HelloImGui::ShowAppMenu`.
    bool showMenuBar = false;

    //  If menu bar is shown, include or not the default app menu
    bool showMenu_App = true;

    // Include or not a "Quit" item in the default app menu.
    // Set this to false if you intend to provide your own quit callback
    // with possible user confirmation
    // (and implement it inside RunnerCallbacks.ShowAppMenuItems)
    bool showMenu_App_Quit = true;

    // If menu bar is shown, include or not the default _View_ menu, that enables
    // to change the layout and set the docked windows and status bar visibility)
    bool showMenu_View = true;

    // Show theme selection in view menu
    bool showMenu_View_Themes = true;
    // `rememberTheme`: _bool, default=true_. Remember selected theme
    bool rememberTheme = true;

    // Flag that enable to show a Status bar at the bottom. You can customize
    // the status bar via RunnerCallbacks.ShowStatus()
    bool showStatusBar = false;

    // If set, display the FPS in the status bar.
    bool showStatus_Fps = true;
    // If set, showStatusBar and showStatus_Fps are stored in the application settings.
    bool rememberStatusBarSettings = true;


    // ------------ Change the dockspace or background window size -----------------------

    // If defaultImGuiWindowType = ProvideFullScreenWindow or ProvideFullScreenDockSpace,
    // you can set the position and size of the background window:
    //    - fullScreenWindow_MarginTopLeft is the window position
    //    - fullScreenWindow_MarginBottomRight is the margin between
    //      the "application window" bottom right corner
    //      and the "imgui background window" bottom right corner
    // Important note:
    //     In order to be Dpi aware, those sizes are in *em units*, not in pixels,
    //     i.e. in multiples of the font size! (See HelloImGui::EmToVec2)
    ImVec2 fullScreenWindow_MarginTopLeft     = ImVec2(0.f, 0.f);
    ImVec2 fullScreenWindow_MarginBottomRight = ImVec2(0.f, 0.f);


    // ------------ Theme ---------------------------------------------------------------

    // tweakedTheme: (enum ImGuiTheme::ImGuiTweakedTheme)
    // Changes the ImGui theme. Several themes are available, you can query the list
    // by calling HelloImGui::AvailableThemes()
    ImGuiTheme::ImGuiTweakedTheme tweakedTheme;

    // backgroundColor:
    // This is the "clearColor", i.e. the app window background color, is visible *only if*
    //    runnerParams.imGuiWindowParams.defaultImGuiWindowType = NoDefaultWindow
    // Alternatively, you can set your own RunnerCallbacks.CustomBackground to have full
    // control over what is drawn behind the Gui.
    ImVec4 backgroundColor = ImVec4(0.f, 0.f, 0.f, 0.f);

};
// @@md

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/runner_callbacks.h included by hello_imgui/runner_params.h                 //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/imgui_default_settings.h included by hello_imgui/runner_callbacks.h        //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace HelloImGui
{

    namespace ImGuiDefaultSettings
    {
        // LoadDefaultFont_WithFontAwesome will load from assets/fonts and reverts to the imgui embedded font if not found.
        void LoadDefaultFont_WithFontAwesomeIcons();

        void SetupDefaultImGuiConfig();
        void SetupDefaultImGuiStyle();
    }  // namespace ImGuiDefaultSettings

}  // namespace HelloImGui

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/runner_callbacks.h continued                                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <map>


namespace HelloImGui
{
// --------------------------------------------------------------------------------------------------------------------

// @@md#VoidFunction_AnyEventCallback

// VoidFunctionPointer can hold any void(void) function.
using VoidFunction = std::function<void(void)>;
inline VoidFunction EmptyVoidFunction() { return {}; }


// SequenceFunctions: returns a function that will call f1 and f2 in sequence
VoidFunction SequenceFunctions(const VoidFunction& f1, const VoidFunction& f2);


// AnyEventCallback can hold any bool(void *) function.
using AnyEventCallback = std::function<bool(void * backendEvent)>;
inline AnyEventCallback EmptyEventCallback() {return {}; }

// @@md


// --------------------------------------------------------------------------------------------------------------------

// @@md#MobileCallbacks

// MobileCallbacks is a struct that contains callbacks that are called by the application
// when running under "Android, iOS and WinRT".
// These events are specific to mobile and embedded devices that have different
// requirements from your usual desktop application.
// These events must be handled quickly, since often the OS needs an immediate response
// and will terminate your process shortly after sending the event
// if you do not handle them appropriately.
// On mobile devices, it is not possible to "Quit" an application,
// it can only be put on Pause.
struct MobileCallbacks
{
    //`OnDestroy`: The application is being terminated by the OS.
    VoidFunction OnDestroy = EmptyVoidFunction();

    //`OnLowMemory`: _VoidFunction, default=empty_.
    // When the application is low on memory, free memory if possible.
    VoidFunction OnLowMemory = EmptyVoidFunction();

    //`OnPause`: The application is about to enter the background.
    VoidFunction OnPause = EmptyVoidFunction();

    //`OnResume`: The application came to foreground and is now interactive.
    // Note: 'OnPause' and 'OnResume' are called twice consecutively under iOS
    // (before and after entering background or foreground).
    VoidFunction OnResume = EmptyVoidFunction();
};
// @@md


// --------------------------------------------------------------------------------------------------------------------

// @@md#EdgeToolbar

// EdgeToolbarType: location of an Edge Toolbar
enum class EdgeToolbarType
{
    Top,
    Bottom,
    Left,
    Right
};

struct EdgeToolbarOptions
{
    // height or width the top toolbar, in em units
    // (i.e. multiples of the default font size, to be Dpi aware)
    float sizeEm = 2.5f;

    // Padding inside the window, in em units
    ImVec2 WindowPaddingEm = ImVec2(0.3f, 0.3f);

    // Window background color, only used if WindowBg.w > 0
    ImVec4 WindowBg = ImVec4(0.f, 0.f, 0.f, 0.f);
};


// EdgeToolbar :a toolbar that can be placed on the edges of the App window
// It will be placed in a non-dockable window
struct EdgeToolbar
{
    VoidFunction ShowToolbar = EmptyVoidFunction();
    EdgeToolbarOptions options;
};

std::vector<EdgeToolbarType> AllEdgeToolbarTypes();
std::string EdgeToolbarTypeName(EdgeToolbarType e);
// @@md


// --------------------------------------------------------------------------------------------------------------------

// @@md#DefaultIconFont

// HelloImGui can optionally merge an icon font (FontAwesome 4 or 6) to the default font
// Breaking change in v1.5.0:
// - the default icon font is now FontAwesome 6, which includes many more icons.
// - you need to include manually icons_font_awesome_4.h or icons_font_awesome_6.h:
//     #include "hello_imgui/icons_font_awesome_6.h" or #include "hello_imgui/icons_font_awesome_4.h"
enum class DefaultIconFont
{
    NoIcons,
    FontAwesome4,
    FontAwesome6
};
// @@md


// --------------------------------------------------------------------------------------------------------------------

// @@md#RunnerCallbacks
// RunnerCallbacks is a struct that contains the callbacks
// that are called by the application
//
struct RunnerCallbacks
{
    // --------------- GUI Callbacks -------------------

    // `ShowGui`: Fill it with a function that will add your widgets.
    // (ShowGui will be called at each frame, before rendering the Dockable windows, if any)
    VoidFunction ShowGui = EmptyVoidFunction();

    // `ShowMenus`: Fill it with a function that will add ImGui menus by calling:
    //       ImGui::BeginMenu(...) / ImGui::MenuItem(...) / ImGui::EndMenu()
    //   Notes:
    //   * you do not need to call ImGui::BeginMenuBar and ImGui::EndMenuBar
    //   * Some default menus can be provided:
    //     see ImGuiWindowParams options:
    //         _showMenuBar, showMenu_App_QuitAbout, showMenu_View_
    VoidFunction ShowMenus = EmptyVoidFunction();

    // `ShowAppMenuItems`: A function that will render items that will be placed
    // in the App menu. They will be placed before the "Quit" MenuItem,
    // which is added automatically by HelloImGui.
    //  This will be displayed only if ImGuiWindowParams.showMenu_App is true
    VoidFunction ShowAppMenuItems = EmptyVoidFunction();

    // `ShowStatus`: A function that will add items to the status bar.
    //  Use small items (ImGui::Text for example), since the height of the status is 30.
    //  Also, remember to call ImGui::SameLine() between items.
    VoidFunction ShowStatus = EmptyVoidFunction();

    // `EdgesToolbars`:
    // A dict that contains toolbars that can be placed on the edges of the App window
    std::map<EdgeToolbarType, EdgeToolbar> edgesToolbars;

    // `AddEdgeToolbar`: Add a toolbar that can be placed on the edges of the App window
    void AddEdgeToolbar(EdgeToolbarType edgeToolbarType,
                        VoidFunction guiFunction,
                        const EdgeToolbarOptions& options = EdgeToolbarOptions());


    // --------------- Startup sequence callbacks -------------------

    // `PostInit_AddPlatformBackendCallbacks`:
    //  You can here add a function that will be called once after OpenGL and ImGui are inited,
    //  but before the platform backend callbacks are initialized.
    //  If you, want to add your own glfw callbacks, you should use this function to do so
    //  (and then ImGui will call your callbacks followed by its own callbacks)
    VoidFunction PostInit_AddPlatformBackendCallbacks = EmptyVoidFunction();


    // `PostInit`: You can here add a function that will be called once after everything
    //  is inited (ImGui, Platform and Renderer Backend)
    VoidFunction PostInit = EmptyVoidFunction();

    // `EnqueuePostInit`: Add a function that will be called once after OpenGL
    //  and ImGui are inited, but before the backend callback are initialized.
    //  (this will modify the `PostInit` callback by appending the new callback (using `SequenceFunctions`)
    void EnqueuePostInit(const VoidFunction& callback);

    // `LoadAdditionalFonts`: default=_LoadDefaultFont_WithFontAwesome*.
    //  A function that is called in order to load fonts.
    // `LoadAdditionalFonts` will be called once, then *set to nullptr*.
    // If you want to load additional fonts, during the app execution, you can
    // set LoadAdditionalFonts to a function that will load the additional fonts.
    VoidFunction LoadAdditionalFonts = (VoidFunction)ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons;
    // If LoadAdditionalFonts==LoadDefaultFont_WithFontAwesomeIcons, this parameter control
    // which icon font will be loaded by default.
    DefaultIconFont defaultIconFont = DefaultIconFont::FontAwesome4;

    // `SetupImGuiConfig`: default=_ImGuiDefaultSettings::SetupDefaultImGuiConfig*.
    //  If needed, change ImGui config via SetupImGuiConfig
    //  (enable docking, gamepad, etc)
    VoidFunction SetupImGuiConfig = (VoidFunction)ImGuiDefaultSettings::SetupDefaultImGuiConfig;

    // `SetupImGuiStyle`: default=_ImGuiDefaultSettings::SetupDefaultImGuiConfig*.
    //  If needed, set your own style by providing your own SetupImGuiStyle callback
    VoidFunction SetupImGuiStyle = (VoidFunction)ImGuiDefaultSettings::SetupDefaultImGuiStyle;

    // `RegisterTests`: A function that is called once ImGuiTestEngine is ready
    // to be filled with tests and automations definitions.
    VoidFunction RegisterTests = EmptyVoidFunction();
    // `registerTestsCalled`: will be set to true when RegisterTests was called
    // (you can set this to false if you want to RegisterTests to be called again
    //  during the app execution)
    bool         registerTestsCalled = false;


    // --------------- Exit sequence callbacks -------------------

    // `BeforeExit`: You can here add a function that will be called once before exiting
    //  (when OpenGL and ImGui are still inited)
    VoidFunction BeforeExit = EmptyVoidFunction();

    // `EnqueueBeforeExit`: Add a function that will be called once before exiting
    //  (when OpenGL and ImGui are still inited)
    // (this will modify the `BeforeExit` callback by appending the new callback (using `SequenceFunctions`)
    void EnqueueBeforeExit(const VoidFunction& callback);

    // `BeforeExit_PostCleanup`: You can here add a function that will be called once
    // before exiting (after OpenGL and ImGui have been stopped)
    VoidFunction BeforeExit_PostCleanup = EmptyVoidFunction();


    // --------------- Callbacks in the render loop -------------------

    // `PreNewFrame`: You can here add a function that will be called at each frame,
    //  and before the call to ImGui::NewFrame().
    //  It is a good place to add new dockable windows.
    VoidFunction PreNewFrame = EmptyVoidFunction();

    // `BeforeImGuiRender`: You can here add a function that will be called at each frame,
    //  after the user Gui code, and just before the call to
    //  ImGui::Render() (which will also call ImGui::EndFrame()).
    VoidFunction BeforeImGuiRender = EmptyVoidFunction();

    // `AfterSwap`: You can here add a function that will be called at each frame,
    //  after the Gui was rendered and swapped to the screen.
    VoidFunction AfterSwap = EmptyVoidFunction();

    // `CustomBackground`:
    //  By default, the background is cleared using ImGuiWindowParams.backgroundColor.
    //  If set, this function gives you full control over the background that is drawn
    //  behind the Gui. An example use case is if you have a 3D application
    //  like a mesh editor, or game, and just want the Gui to be drawn
    //  on top of that content.
    VoidFunction CustomBackground = EmptyVoidFunction();

    // `PostRenderDockableWindows`: Fill it with a function that will be called
    // after the dockable windows are rendered.
    VoidFunction PostRenderDockableWindows = EmptyVoidFunction();

    // `AnyBackendEventCallback`:
    //  Callbacks for events from a specific backend. _Only implemented for SDL.
    //  where the event will be of type 'SDL_Event *'_
    //  This callback should return true if the event was handled
    //  and shall not be processed further.
    //  Note: in the case of GLFW, you should use register them in `PostInit`
    AnyEventCallback AnyBackendEventCallback = EmptyEventCallback();


    // --------------- Mobile callbacks -------------------
#ifdef HELLOIMGUI_MOBILEDEVICE
    // `mobileCallbacks`: Callbacks that are called by the application
    //  when running under "Android, iOS and WinRT".
    // Notes:
    //  * 'mobileCallbacks' is present only if the target device
    //    is a mobile device (iOS, Android).
    //    Use `#ifdef HELLOIMGUI_MOBILEDEVICE` to detect this.
    //  * These events are currently handled only with SDL backend.
    MobileCallbacks mobileCallbacks;
#endif
};
// @@md


// AppendCallback: legacy synonym for SequenceFunctions
VoidFunction AppendCallback(const VoidFunction& previousCallback, const VoidFunction& newCallback);

}  // namespace HelloImGui

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/docking_params.h included by hello_imgui/runner_params.h                   //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <utility>
#include <optional>
#include <stdio.h>

namespace HelloImGui
{
/**
@@md#DockingIntro

HelloImGui makes it easy to use dockable windows
 (based on ImGui [docking branch](https://github.com/ocornut/imgui/tree/docking)).

You can define several layouts and switch between them:  each layout which will remember
 the user modifications and the list of opened windows

HelloImGui will then provide a "View" menu with options to show/hide the dockable windows,
 restore the default layout, switch between layouts, etc.

![demo docking](https://traineq.org/ImGuiBundle/HelloImGuiLayout.gif)

* Source for this example: https://github.com/pthom/hello_imgui/tree/master/src/hello_imgui_demos/hello_imgui_demodocking
* [Video explanation on YouTube](https://www.youtube.com/watch?v=XKxmz__F4ow) (5 minutes)


The different available layouts are provided inside RunnerParams via the two members below:
```cpp
struct RunnerParams
{
    ...
    // default layout of the application
    DockingParams dockingParams;

    // optional alternative layouts
    std::vector<DockingParams> alternativeDockingLayouts;

    ...
};
```

And `DockingParams` contains members that define a layout:

```cpp
struct DockingParams
{
    // displayed name of the layout
    std::string layoutName = "Default";

    // list of splits
    // (which define spaces where the windows will be placed)
    std::vector<DockingSplit> dockingSplits;

    // list of windows
    // (with their gui code, and specifying in which space they will be placed)
    std::vector<DockableWindow> dockableWindows;

    ...
};
```

Inside DockingParams, the member `dockingSplits` specifies the layout, and the member `dockableWindows`
 specifies the list of dockable windows, along with their default location, and their code (given by lambdas).

 @@md


@@md#DockingExample

Below is an example that shows how to instantiate a layout:

1. First, define the docking splits:

```cpp
std::vector<HelloImGui::DockingSplit> CreateDefaultDockingSplits()
{
    //   Here, we want to split "MainDockSpace" (which is provided automatically)
    //   into three zones, like this:
    //    ___________________________________________
    //    |        |                                |
    //    | Command|                                |
    //    | Space  |    MainDockSpace               |
    //    |        |                                |
    //    |        |                                |
    //    |        |                                |
    //    -------------------------------------------
    //    |     MiscSpace                           |
    //    -------------------------------------------
    //

    // add a space named "MiscSpace" whose height is 25% of the app height.
    // This will split the preexisting default dockspace "MainDockSpace" in two parts.
    HelloImGui::DockingSplit splitMainMisc;
    splitMainMisc.initialDock = "MainDockSpace";
    splitMainMisc.newDock = "MiscSpace";
    splitMainMisc.direction = ImGuiDir_Down;
    splitMainMisc.ratio = 0.25f;

    // Then, add a space to the left which occupies a column
    // whose width is 25% of the app width
    HelloImGui::DockingSplit splitMainCommand;
    splitMainCommand.initialDock = "MainDockSpace";
    splitMainCommand.newDock = "CommandSpace";
    splitMainCommand.direction = ImGuiDir_Left;
    splitMainCommand.ratio = 0.25f;

    std::vector<HelloImGui::DockingSplit> splits {splitMainMisc, splitMainCommand};
    return splits;
}
```

2. Then, define the dockable windows:

```cpp
std::vector<HelloImGui::DockableWindow> CreateDockableWindows(AppState& appState)
{
    // A Command panel named "Commands" will be placed in "CommandSpace".
    // Its Gui is provided calls "CommandGui"
    HelloImGui::DockableWindow commandsWindow;
    commandsWindow.label = "Commands";
    commandsWindow.dockSpaceName = "CommandSpace";
    commandsWindow.GuiFunction = [&] { CommandGui(appState); };

    // A Log window named "Logs" will be placed in "MiscSpace".
    // It uses the HelloImGui logger gui
    HelloImGui::DockableWindow logsWindow;
    logsWindow.label = "Logs";
    logsWindow.dockSpaceName = "MiscSpace";
    logsWindow.GuiFunction = [] { HelloImGui::LogGui(); };

    ...
}
```

3. Finally, fill the RunnerParams

```cpp
HelloImGui::RunnerParams runnerParams;
runnerParams.imGuiWindowParams.defaultImGuiWindowType =
    HelloImGui::DefaultImGuiWindowType::ProvideFullScreenDockSpace;

runnerParams.dockingParams.dockingSplits = CreateDefaultDockingSplits();
runnerParams.dockingParams.dockableWindows = CreateDockableWindows();


HelloImGui::Run(runnerParams);
```

@@md
*/

/*****************************************************************************/

// A DockSpaceName is a simple string that identifies a zone on the screen
// where windows can be docked.
using DockSpaceName = std::string;


// @@md#DockingSplit

// DockingSplit is a struct that defines the way the docking splits should
// be applied on the screen in order to create new Dock Spaces.
// DockingParams contains a
//     vector<DockingSplit>
// in order to partition the screen at your will.
struct DockingSplit
{
    // `initialDock`: _DockSpaceName (aka string)_
    //  id of the space that should be split.
    //  At the start, there is only one Dock Space named "MainDockSpace".
    //  You should start by partitioning this space, in order to create a new dock space.
    DockSpaceName initialDock;

    // `newDock`: _DockSpaceName (aka string)_.
    //  id of the new dock space that will be created.
    DockSpaceName newDock;

    // `direction`: *ImGuiDir_*
    //  (enum with ImGuiDir_Down, ImGuiDir_Down, ImGuiDir_Left, ImGuiDir_Right)*
    //  Direction where this dock space should be created.
    ImGuiDir direction;

    // `ratio`: _float, default=0.25f_.
    //  Ratio of the initialDock size that should be used by the new dock space.
    float ratio = 0.25f;

    // `nodeFlags`: *ImGuiDockNodeFlags_ (enum)*.
    //  Flags to apply to the new dock space
    //  (enable/disable resizing, splitting, tab bar, etc.)
    ImGuiDockNodeFlags nodeFlags = ImGuiDockNodeFlags_None;

    // Constructor
    DockingSplit(const DockSpaceName& initialDock_ = "", const DockSpaceName& newDock_ = "",
                 ImGuiDir direction_ = ImGuiDir_Down, float ratio_ = 0.25f,
                 ImGuiDockNodeFlags nodeFlags_ = ImGuiDockNodeFlags_None)
        : initialDock(initialDock_), newDock(newDock_), direction(direction_), ratio(ratio_), nodeFlags(nodeFlags_) {}
};
// @@md



// @@md#DockableWindow

// DockableWindow is a struct that represents a window that can be docked.
struct DockableWindow
{
    // --------------- Main params -------------------

    // `label`: _string_. Title of the window.
    std::string label;

    // `dockSpaceName`: _DockSpaceName (aka string)_.
    //  Id of the dock space where this window should initially be placed
    DockSpaceName dockSpaceName;

    // `GuiFunction`: _VoidFunction_.
    // Any function that will render this window's Gui
    VoidFunction GuiFunction = EmptyVoidFunction();


    // --------------- Options --------------------------

    // `isVisible`: _bool, default=true_.
    //  Flag that indicates whether this window is visible or not.
    bool isVisible = true;

    // `rememberIsVisible`: _bool, default=true_.
    //  Flag that indicates whether the window visibility should be saved in settings.
    bool rememberIsVisible = true;

    // `canBeClosed`: _bool, default=true_.
    //  Flag that indicates whether the user can close this window.
    bool canBeClosed = true;

    // `callBeginEnd`: _bool, default=true_.
    //  Flag that indicates whether ImGui::Begin and ImGui::End
    //  calls should be added automatically (with the given "label").
    //  Set to false if you want to call ImGui::Begin/End yourself
    bool callBeginEnd = true;

    // `includeInViewMenu`: _bool, default=true_.
    //  Flag that indicates whether this window should be mentioned in the view menu.
    bool includeInViewMenu = true;

    // `imGuiWindowFlags`: _ImGuiWindowFlags, default=0_.
    //  Window flags, see enum ImGuiWindowFlags_
    ImGuiWindowFlags imGuiWindowFlags = 0;


    // --------------- Focus window -----------------------------

    // `focusWindowAtNextFrame`: _bool, default = false_.
    //  If set to true this window will be focused at the next frame.
    bool focusWindowAtNextFrame = false;


    // --------------- Size & Position --------------------------
    //              (only if not docked)

    // `windowSize`: _ImVec2, default=(0.f, 0.f) (i.e let the app decide)_.
    //  Window size (unused if docked)
    ImVec2 windowSize = ImVec2(0.f, 0.f);

    // `windowSizeCondition`: _ImGuiCond, default=ImGuiCond_FirstUseEver_.
    //  When to apply the window size.
    ImGuiCond  windowSizeCondition = ImGuiCond_FirstUseEver;

    // `windowPos`: _ImVec2, default=(0.f, 0.f) (i.e let the app decide)_.
    //  Window position (unused if docked)
    ImVec2 windowPosition = ImVec2(0.f, 0.f);

    // `windowPosCondition`: _ImGuiCond, default=ImGuiCond_FirstUseEver_.
    //  When to apply the window position.
    ImGuiCond  windowPositionCondition = ImGuiCond_FirstUseEver;


    // --------------- Constructor ------------------------------
    // Constructor
    DockableWindow(
        const std::string & label_ = "",
        const DockSpaceName & dockSpaceName_ = "",
        const VoidFunction guiFunction_ = EmptyVoidFunction(),
        bool isVisible_ = true,
        bool canBeClosed_ = true)
        : label(label_), dockSpaceName(dockSpaceName_),
          GuiFunction(guiFunction_),
          isVisible(isVisible_),
          canBeClosed(canBeClosed_) {}

};
// @@md


enum class DockingLayoutCondition
{
    FirstUseEver,
    ApplicationStart,
    Never
};


// @@md#DockingParams

// DockingParams contains all the settings concerning the docking:
//     - list of splits
//     - list of dockable windows
struct DockingParams
{
    // --------------- Main params -----------------------------

    // `dockingSplits`: _vector[DockingSplit]_.
    //  Defines the way docking splits should be applied on the screen
    //  in order to create new Dock Spaces
    std::vector<DockingSplit>   dockingSplits;

    // `dockableWindows`: _vector[DockableWindow]_.
    //  List of the dockable windows, together with their Gui code
    std::vector<DockableWindow> dockableWindows;

    // `layoutName`: _string, default="default"_.
    //  Displayed name of the layout.
    //  Only used in advanced cases, when several layouts are available.
    std::string layoutName = "Default";


    // --------------- Options -----------------------------

    // `mainDockSpaceNodeFlags`: _ImGuiDockNodeFlags (enum),
    //      default=ImGuiDockNodeFlags_PassthruCentralNode_
    //  Flags to apply to the main dock space
    //  (enable/disable resizing, splitting, tab bar, etc.).
    //  Most flags are inherited by children dock spaces.
    //  You can also set flags for specific dock spaces via `DockingSplit.nodeFlags`
    ImGuiDockNodeFlags mainDockSpaceNodeFlags = ImGuiDockNodeFlags_PassthruCentralNode;


    // --------------- Layout handling -----------------------------

    // `layoutCondition`: _enum DockingLayoutCondition, default=FirstUseEver_.
    //  When to apply the docking layout. Choose between
    //      FirstUseEver (apply once, then keep user preference),
    //      ApplicationStart (always reapply at application start)
    //      Never
    DockingLayoutCondition layoutCondition = DockingLayoutCondition::FirstUseEver;

    // `layoutReset`: _bool, default=false_.
    //  Reset layout on next frame, i.e. drop the layout customizations which were
    //  applied manually by the user. layoutReset will be reset to false after this.
    bool layoutReset = false;


    // --------------- Helper Methods -----------------------------

    // `DockableWindow * dockableWindowOfName(const std::string & name)`:
    // returns a pointer to a dockable window
    DockableWindow * dockableWindowOfName(const std::string& name);

    // `bool focusDockableWindow(const std::string& name)`:
    // will focus a dockable window (and make its tab visible if needed)
    bool focusDockableWindow(const std::string& windowName);

    // `optional<ImGuiID> dockSpaceIdFromName(const std::string& dockSpaceName)`:
    // may return the ImGuiID corresponding to the dockspace with this name.
    // **Warning**: this will work reliably only if
    //     layoutCondition = DockingLayoutCondition::ApplicationStart.
    // In other cases, the ID may be cached by ImGui himself at the first run,
    // and HelloImGui will *not* know it on subsequent runs!
    std::optional<ImGuiID> dockSpaceIdFromName(const std::string& dockSpaceName);
};
// @@md

} // namespace HelloImGui


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/backend_pointers.h included by hello_imgui/runner_params.h                 //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace HelloImGui
{

// @@md#BackendPointers
//
// BackendPointers is a struct that contains optional pointers to the
// backend implementations (for SDL and GLFW).
//
// These pointers will be filled when the application starts, and you can use them
// to customize your application behavior using the selected backend.
//
// Note: If using the Metal, Vulkan or DirectX rendering backend, you can find
// some interesting pointers inside
//     `src/hello_imgui/internal/backend_impls/rendering_metal.h`
//     `src/hello_imgui/internal/backend_impls/rendering_vulkan.h`
//     `src/hello_imgui/internal/backend_impls/rendering_dx11.h`
//     `src/hello_imgui/internal/backend_impls/rendering_dx12.h`
struct BackendPointers
{
    //* `glfwWindow`: Pointer to the main GLFW window (of type `GLFWwindow*`).
    //  Only filled if the backend is GLFW.
    void* glfwWindow     = nullptr; /* GLFWwindow*    */

    //* `sdlWindow`: Pointer to the main SDL window (of type `SDL_Window*`).
    //  Only filled if the backend is SDL (or emscripten + sdl)
    void* sdlWindow      = nullptr; /* SDL_Window*    */

    //* `sdlGlContext`: Pointer to SDL's GlContext (of type `SDL_GLContext`).
    //  Only filled if the backend is SDL (or emscripten + sdl)
    void* sdlGlContext   = nullptr; /* SDL_GLContext  */
};
// @@md

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/remote_params.h included by hello_imgui/runner_params.h                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <cstdint>


namespace HelloImGui
{


// @@md#RemoteParams

// RemoteParams is a struct that contains the settings for displaying the application on a remote device.
// using https://github.com/sammyfreg/netImgui
// or using https://github.com/ggerganov/imgui-ws
// Those features are experimental and not supported with the standard version of HelloImGui,
struct RemoteParams
{
    bool enableRemoting = false;

    //
    // Params used only by imgui-ws
    //
    int wsPort = 5003;
    std::string wsHttpRootFolder = "";  // Optional folder were some additional files can be served
    bool wsProvideIndexHtml = true;     // If true, will automatically serve a simple index.html file that contains the canvas and the imgui-ws client code

    //
    // Params used only by netImgui
    //
    bool exitWhenServerDisconnected = false;
    double durationMaxDisconnected = 30.0;
    // The server host (if empty, will use "localhost")
    // The server is the app that simply displays the application on a remote device
    std::string serverHost = "localhost";
    // The server port (default is 8888)
    uint32_t serverPort = 8888;
    // If true, transmit the window size to the server
    bool transmitWindowSize = false;
};

// @@md


}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/renderer_backend_options.h included by hello_imgui/runner_params.h         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace HelloImGui
{
// --------------------------------------------------------------------------------------------------------------------

// @@md#OpenGlOptions

// OpenGlOptions contains advanced options used at the startup of OpenGL.
// These parameters are reserved for advanced users.
// By default, Hello ImGui will select reasonable default values, and these parameters are not used.
// Use at your own risk, as they make break the multi-platform compatibility of your application!
// All these parameters are platform dependent.
// For real multiplatform examples, see
//     hello_imgui/src/hello_imgui/internal/backend_impls/opengl_setup_helper/opengl_setup_glfw.cpp
// and
//     hello_imgui/src/hello_imgui/internal/backend_impls/opengl_setup_helper/opengl_setup_sdl.cpp
//
// How to set those values manually:
// ---------------------------------
// you may set them manually:
//    (1) Either by setting them programmatically in your application
//        (set their values in `runnerParams.rendererBackendOptions.openGlOptions`)
//    (2) Either by setting them in a `hello_imgui.ini` file in the current folder, or any of its parent folders.
//       (this is useful when you want to set them for a specific app or set of apps, without modifying the app code)
//       See hello_imgui/hello_imgui_example.ini for an example of such a file.
// Note: if several methods are used, the order of priority is (1) > (2)
//
struct OpenGlOptions
{
    // Could be for example:
    //    "150" on macOS
    //    "130" on Windows
    //    "300es" on GLES
    std::optional<std::string>  GlslVersion =  std::nullopt;

    // OpenGL 3.3 (these options won't work for GlEs)
    std::optional<int>          MajorVersion = std::nullopt;
    std::optional<int>          MinorVersion = std::nullopt;

    // OpenGL Core Profile (i.e. only includes the newer, maintained features of OpenGL)
    std::optional<bool>         UseCoreProfile = std::nullopt;
    // OpenGL Forward Compatibility (required on macOS)
    std::optional<bool>         UseForwardCompat = std::nullopt;

    // `AntiAliasingSamples`
    // If > 0, this value will be used to set the number of samples used for anti-aliasing.
    // This is used only when running with Glfw  + OpenGL (which is the default)
    // Notes:
    // - we query the maximum number of samples supported by the hardware, via glGetIntegerv(GL_MAX_SAMPLES)
    // - if you set this value to a non-zero value, it will be used instead of the default value of 8
    //   (except if it is greater than the maximum supported value, in which case a warning will be issued)
    // - if you set this value to 0, antialiasing will be disabled
    //
    // AntiAliasingSamples has a strong impact on the quality of the text rendering
    //     - 0: no antialiasing
    //     - 8: optimal
    //     - 16: optimal if using imgui-node-editor and you want to render very small text when unzooming
    std::optional<int> AntiAliasingSamples =  std::nullopt;
};
// @@md


// @@md#RendererBackendOptions

// `bool hasEdrSupport()`:
// Check whether extended dynamic range (EDR), i.e. the ability to reproduce
// intensities exceeding the standard dynamic range from 0.0-1.0, is supported.
//
// To leverage EDR support, you need to set `floatBuffer=true` in `RendererBackendOptions`.
// Only the macOS Metal backend currently supports this.
//
// This currently returns false on all backends except Metal, where it checks whether
// this is supported on the current displays.
bool hasEdrSupport();


// RendererBackendOptions is a struct that contains options for the renderer backend
// (Metal, Vulkan, DirectX, OpenGL)
struct RendererBackendOptions
{
    // `requestFloatBuffer`:
    // Set to true to request a floating-point framebuffer.
    // Only available on Metal, if your display supports it.
    // Before setting this to true, first check `hasEdrSupport()`
    bool requestFloatBuffer = false;

    // `openGlOptions`:
    // Advanced options for OpenGL. Use at your own risk.
    OpenGlOptions openGlOptions;
};


// Note:
// If using Metal, Vulkan or DirectX, you can find interesting pointers inside:
//     src/hello_imgui/internal/backend_impls/rendering_metal.h
//     src/hello_imgui/internal/backend_impls/rendering_vulkan.h
//     src/hello_imgui/internal/backend_impls/rendering_dx11.h
//     src/hello_imgui/internal/backend_impls/rendering_dx12.h

// @@md


// (Private structure, not part of the public API)
// OpenGlOptions after selecting the default platform-dependent values + after applying the user settings
struct OpenGlOptionsFilled_
{
    std::string  GlslVersion =  "150";
    int          MajorVersion = 3;
    int          MinorVersion = 3;
    bool         UseCoreProfile = true;
    bool         UseForwardCompat = true;
    int          AntiAliasingSamples = 8;
};

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/runner_params.h continued                                                  //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace HelloImGui
{

// --------------------------------------------------------------------------------------------------------------------

// @@md#PlatformBackendType

// You can select the platform backend type (SDL, GLFW) and the rendering backend type
// via RunnerParams.platformBackendType and RunnerParams.renderingBackendType.

// Platform backend type (SDL, GLFW)
// They are listed in the order of preference when FirstAvailable is selected.
enum class PlatformBackendType
{
    FirstAvailable,
    Glfw,
    Sdl,
    Null
};

// Rendering backend type (OpenGL3, Metal, Vulkan, DirectX11, DirectX12)
// They are listed in the order of preference when FirstAvailable is selected.
enum class RendererBackendType
{
    FirstAvailable,
    OpenGL3,
    Metal,
    Vulkan,
    DirectX11,
    DirectX12,
    Null
};

// @@md

// --------------------------------------------------------------------------------------------------------------------

// @@md#IniFolderType

// IniFolderType is an enum which describes where is the base path to store
// the ini file for the application settings.
//
// You can use IniFolderLocation(iniFolderType) to get the corresponding path.
//
// RunnerParams contains the following members, which are used to compute
// the ini file location:
//     iniFolderType           (IniFolderType::CurrentFolder by default)
//     iniFilename             (empty string by default)
//     iniFilename_useAppWindowTitle
//         (true by default: iniFilename is derived from
//          appWindowParams.windowTitle)
//
// iniFilename may contain a subfolder
// (which will be created inside the iniFolderType folder if needed)
//
enum class IniFolderType
{
    // CurrentFolder: the folder where the application is executed
    // (convenient for development, but not recommended for production)
    CurrentFolder,

    // AbsolutePath: an absolute path
    // (convenient, but not recommended if targeting multiple platforms)
    AbsolutePath,

    // AppUserConfigFolder:
    //      AppData under Windows (Example: C:\Users\[Username]\AppData\Roaming under windows)
    //      ~/.config under Linux
    //      "~/Library/Application Support" under macOS
    // (recommended for production, if settings do not need to be easily accessible by the user)
    AppUserConfigFolder,

    // AppExecutableFolder: the folder where the application executable is located
    // (this may be different from CurrentFolder if the application is launched from a shortcut)
    // (convenient for development, but not recommended for production)
    AppExecutableFolder,

    // HomeFolder: the user home folder
    // (recommended for production, if settings need to be easily accessible by the user)
    HomeFolder,

    // DocumentsFolder: the user documents folder
    DocumentsFolder,

    // TempFolder: the system temp folder
    TempFolder
};

// Returns the path corresponding to the given IniFolderType
std::string IniFolderLocation(IniFolderType iniFolderType);

// @@md

// --------------------------------------------------------------------------------------------------------------------

// @@md#FpsIdling

// FpsIdling is a struct that contains Fps Idling parameters
struct FpsIdling
{
    // `fpsIdle`: _float, default=9_.
    //  ImGui applications can consume a lot of CPU, since they update the screen
    //  very frequently. In order to reduce the CPU usage, the FPS is reduced when
    //  no user interaction is detected.
    //  This is ok most of the time but if you are displaying animated widgets
    //  (for example a live video), you may want to ask for a faster refresh:
    //  either increase fpsIdle, or set it to 0 for maximum refresh speed
    //  (you can change this value during the execution depending on your application
    //  refresh needs)
    float fpsIdle = 9.f;

    // `timeActiveAfterLastEvent`: _float, default=3.f_.
    //  Time in seconds after the last event before the application is considered idling.
    float timeActiveAfterLastEvent = 3.f;

    // `enableIdling`: _bool, default=true_.
    //  Disable idling by setting this to false.
    //  (this can be changed dynamically during execution)
    bool  enableIdling = true;

    // `isIdling`: bool (dynamically updated during execution)
    //  This bool will be updated during the application execution,
    //  and will be set to true when it is idling.
    bool  isIdling = false;

    // `rememberEnableIdling`: _bool, default=true_.
    //  If true, the last value of enableIdling is restored from the settings at startup.
    bool  rememberEnableIdling = false;
};
// @@md


// --------------------------------------------------------------------------------------------------------------------

// @@md#RunnerParams

// RunnerParams contains the settings and callbacks needed to run an application.
//
struct RunnerParams
{
    // --------------- Callbacks and Window params -------------------

    // `callbacks`: _see runner_callbacks.h_
    // callbacks.ShowGui() will render the gui, ShowMenus() will show the menus, etc.
    RunnerCallbacks callbacks;

    // `appWindowParams`: _see app_window_params.h_
    // application Window Params (position, size, title)
    AppWindowParams appWindowParams;

    // `imGuiWindowParams`: _see imgui_window_params.h_
    // imgui window params (use docking, showMenuBar, ProvideFullScreenWindow, etc.)
    ImGuiWindowParams imGuiWindowParams;


    // --------------- Docking -------------------

    // `dockingParams`: _see docking_params.h_
    // dockable windows content and layout
    DockingParams dockingParams;

    // `alternativeDockingLayouts`: _vector<DockingParams>, default=empty_
    // List of possible additional layout for the applications. Only used in advanced
    // cases when several layouts are available.
    std::vector<DockingParams> alternativeDockingLayouts;

    // `rememberSelectedAlternativeLayout`: _bool, default=true_
    // Shall the application remember the last selected layout. Only used in advanced
    // cases when several layouts are available.
    bool rememberSelectedAlternativeLayout = true;


    // --------------- Backends -------------------

    // `backendPointers`: _see backend_pointers.h_
    // A struct that contains optional pointers to the backend implementations.
    // These pointers will be filled when the application starts
    BackendPointers backendPointers;

    // `rendererBackendOptions`: _see renderer_backend_options.h_
    // Options for the renderer backend
    RendererBackendOptions rendererBackendOptions;

    // `platformBackendType`: _enum PlatformBackendType, default=PlatformBackendType::FirstAvailable_
    // Select the wanted platform backend type between `Sdl`, `Glfw`.
    // if `FirstAvailable`, Glfw will be preferred over Sdl when both are available.
    // Only useful when multiple backend are compiled and available.
    PlatformBackendType platformBackendType = PlatformBackendType::FirstAvailable;

    // `renderingBackendType`: _enum RenderingBackendType, default=RenderingBackendType::FirstAvailable_
    // Select the wanted rendering backend type between `OpenGL3`, `Metal`, `Vulkan`, `DirectX11`, `DirectX12`.
    // if `FirstAvailable`, it will be selected in the order of preference mentioned above.
    // Only useful when multiple rendering backend are compiled and available.
    RendererBackendType rendererBackendType = RendererBackendType::FirstAvailable;


    // --------------- Settings -------------------

    // `iniFolderType`: _IniFolderType, default = IniFolderType::CurrentFolder_
    // Sets the folder where imgui will save its params.
    // (possible values are:
    //     CurrentFolder, AppUserConfigFolder, DocumentsFolder,
    //     HomeFolder, TempFolder, AppExecutableFolder)
    // AppUserConfigFolder is
    //     [Home]/AppData/Roaming under Windows,
    //     ~/.config under Linux,
    //     ~/Library/Application Support under macOS
    IniFolderType iniFolderType = IniFolderType::CurrentFolder;
    // `iniFilename`: _string, default = ""_
    // Sets the ini filename under which imgui will save its params.
    // Its path is relative to the path given by iniFolderType, and can include
    // a subfolder (which will be created if needed).
    // If iniFilename empty, then it will be derived from
    // appWindowParams.windowTitle
    // (if both are empty, the ini filename will be imgui.ini).
    std::string iniFilename = "";  // relative to iniFolderType
    // `iniFilename_useAppWindowTitle`: _bool, default = true_.
    // Shall the iniFilename be derived from appWindowParams.windowTitle (if not empty)
    bool iniFilename_useAppWindowTitle = true;


    // --------------- Exit -------------------

    // * `appShallExit`: _bool, default=false_.
    // During execution, set this to true to exit the app.
    // _Note: 'appShallExit' has no effect on Mobile Devices (iOS, Android)
    // and under emscripten, since these apps shall not exit._
    bool appShallExit = false;

    // --------------- Idling -------------------

    // `fpsIdling`: _FpsIdling_. Idling parameters
    // (set fpsIdling.enableIdling to false to disable Idling)
    FpsIdling fpsIdling;

    // --------------- DPI Handling -----------
    // Hello ImGui will try its best to automatically handle DPI scaling for you.
    // If it fails, look at DpiAwareParams (and the corresponding Ini file settings)
    DpiAwareParams dpiAwareParams;

    // --------------- Misc -------------------

    // `useImGuiTestEngine`: _bool, default=false_.
    // Set this to true if you intend to use Dear ImGui Test & Automation Engine
    //     ( https://github.com/ocornut/imgui_test_engine )
    // HelloImGui must be compiled with the option -DHELLOIMGUI_WITH_TEST_ENGINE=ON
    // See demo in src/hello_imgui_demos/hello_imgui_demo_test_engine.
    // License:
    // imgui_test_engine is subject to a specific license:
    //     https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt)
    // (TL;DR: free for individuals, educational, open-source and small businesses uses.
    //  Paid for larger businesses.)
    bool useImGuiTestEngine = false;

    // `emscripten_fps`: _int, default = 0_.
    // Set the application refresh rate
    // (only used on emscripten: 0 stands for "let the app or the browser decide")
    int emscripten_fps = 0;

    #ifdef HELLOIMGUI_WITH_REMOTE_DISPLAY
    RemoteParams remoteParams; // Parameters for Remote display (experimental, unsupported)
    #endif
};
// @@md


// @@md#IniIniSettingsLocation

// IniSettingsLocation returns the path to the ini file for the application settings.
std::string IniSettingsLocation(const RunnerParams& runnerParams);

// HasIniSettings returns true if the ini file for the application settings exists.
bool HasIniSettings(const RunnerParams& runnerParams);

// DeleteIniSettings deletes the ini file for the application settings.
void DeleteIniSettings(const RunnerParams& runnerParams);

// @@md

// --------------------------------------------------------------------------------------------------------------------

// @@md#SimpleRunnerParams

// SimpleRunnerParams is a struct that contains simpler params adapted for simple use cases.
//For example, this is sufficient to run an application:
//    ```cpp
//    void MyGui() {
//        ImGui::Text("Hello, world");
//        if (ImGui::Button("Exit"))
//            HelloImGui::GetRunnerParams()->appShallExit = true;
//    }
//
//    int main(){
//        auto params = HelloImGui::SimpleRunnerParams {
//            .guiFunction = MyGui, .windowSizeAuto = true, .windowTitle = "Example"
//        };
//        HelloImGui::Run(params);
//    }
//    ```
struct SimpleRunnerParams
{
    // `guiFunction`: _VoidFunction_.
    //  Function that renders the Gui.
    VoidFunction guiFunction = EmptyVoidFunction();
    // `windowTitle`: _string, default=""_.
    //  Title of the application window
    std::string windowTitle = "";

    // `windowSizeAuto`: _bool, default=false_.
    //  If true, the size of the window will be computed from its widgets.
    bool windowSizeAuto = false;

    // `windowRestorePreviousGeometry`: _bool, default=true_.
    //  If true, restore the size and position of the window between runs.
    bool windowRestorePreviousGeometry = false;

    // `windowSize`: _ScreenSize, default={800, 600}_.
    //  Size of the window
    // The size will be handled as if it was specified for a 96PPI screen
    // (i.e. a given size will correspond to the same physical size on different screens, whatever their DPI)
    ScreenSize windowSize = DefaultWindowSize;

    // `fpsIdle`: _float, default=9_.
    //  FPS of the application when idle (set to 0 for full speed).
    float fpsIdle = 9.f;

    // `enableIdling`: _bool, default=true_.
    //  Disable idling at startup by setting this to false
    //  When running, use:
    //      HelloImGui::GetRunnerParams()->fpsIdling.enableIdling = false;
    bool  enableIdling = true;

    RunnerParams ToRunnerParams() const;
};
// @@md

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_widgets.h included by hello_imgui.h                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Some additional widgets and utilities for ImGui
#include <variant>

namespace HelloImGui
{
    using VoidFunction = std::function<void(void)>;

    void BeginGroupColumn(); // calls ImGui::BeginGroup()

    void EndGroupColumn();   // calls ImGui::EndGroup() + ImGui::SameLine()

    // @@md#WidgetWithResizeHandle

    // WidgetWithResizeHandle: adds a resize handle to a widget
    // Example usage with ImPlot:
    //        void gui()
    //        {
    //            static ImVec2 widget_size(200, 200);
    //            auto myWidgetFunction = []()
    //            {
    //                if (ImPlot::BeginPlot("My Plot", widget_size)) {
    //                    ImPlot::PlotLine("My Line", x.data(), y.data(), 1000);
    //                    ImPlot::EndPlot();
    //                }
    //            };
    //            widget_size = widget_with_resize_handle("plot", myWidgetFunction);
    //        }
    ImVec2 WidgetWithResizeHandle(
        const char* id,
        VoidFunction widgetGuiFunction,
        float handleSizeEm = 1.0f,
        std::optional<VoidFunction> onItemResized = std::nullopt,
        std::optional<VoidFunction> onItemHovered = std::nullopt
        );

    // @@md


    // --------------------------------------------------------------------------------------------

    // @@md#InputTextResizable

    // `InputTextResizable`: displays a resizable text input widget
    //
    // The `InputTextResizable` widget allows you to create a text input field that can be resized by the user.
    // It supports both single-line and multi-line text input.
    // Note: the size of the widget is expressed in em units.
    // **Usage example:**
    //    C++:
    //       ```cpp
    //       // Somewhere in the application state
    //       (static) InputTextData textInput("My text", true, ImVec2(10, 3));
    //       // In the GUI function
    //       bool changed = InputTextResizable("Label", &textInput);
    //       ```
    //    Python:
    //       ```python
    //       # Somewhere in the application state
    //       text_input = hello_imgui.InputTextData("My text", multiline=True, size_em=ImVec2(10, 3))
    //       # In the GUI function
    //       changed = hello_imgui.input_text_resizable("Label", text_input)
    //       ```
    struct InputTextData
    {
        // The text edited in the input field
        std::string Text;

        // An optional hint displayed when the input field is empty
        // (only works for single-line text input)
        std::string Hint;

        // If true, the input field is multi-line
        bool Multiline = false;

        // If true, the input field is resizable
        bool Resizable = true;

        // The size of the input field in em units
        ImVec2 SizeEm = ImVec2(0, 0);

        InputTextData(const std::string& text = "", bool multiline = false, ImVec2 size_em = ImVec2(0, 0)) : Text(text), Multiline(multiline), SizeEm(size_em) {}
    };
    bool InputTextResizable(const char* label, InputTextData* textInput);

    // Serialization for InputTextData
    // -------------------------------
    // to/from dict
    using DictTypeInputTextData = std::map<std::string, std::variant<std::string, bool, float>>;
    DictTypeInputTextData InputTextDataToDict(const InputTextData& data);
    InputTextData InputTextDataFromDict(const DictTypeInputTextData& dict);
    // to/from string
    std::string InputTextDataToString(const InputTextData& data);
    InputTextData InputTextDataFromString(const std::string& str);

    // @@md
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui.h continued                                                                //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#include <cstddef>

#ifdef HELLOIMGUI_USE_SDL2
    #ifdef _WIN32
        #ifndef HELLOIMGUI_WIN32_AUTO_WINMAIN
            // Under Windows, we redefine WinMain ourselves
            #include <SDL.h>
        #endif
    #endif
     // Let SDL redefine main under iOS
    #ifdef HELLOIMGUI_IOS
        #include <SDL.h>
    #endif
#endif

struct ImGuiTestEngine;


namespace HelloImGui
{

// =========================== HelloImGui::Run ==================================
/**
@@md#HelloImGui::Run

__HelloImGui::Run()__ will run an application with a single call.

Three signatures are provided:

* `HelloImGui::Run(RunnerParams &)`: full signature, the most customizable version.
  Runs an application whose params and Gui are provided by runnerParams.

* `HelloImGui::Run(const SimpleRunnerParams&)`:
  Runs an application, using simpler params.

* `HelloImGui::Run(guiFunction, windowTitle, windowSize, windowSizeAuto=false, restoreLastWindowGeometry=false, fpsIdle=10)`
  Runs an application, by providing the Gui function, the window title, etc.

Although the API is extremely simple, it is highly customizable, and you can set many options by filling
the elements in the `RunnerParams` struct, or in the simpler  `SimpleRunnerParams`.

__HelloImGui::GetRunnerParams()__  will return the runnerParams of the current application.

@@md
*/

// `HelloImGui::Run(RunnerParams &)`: full signature, the most customizable version.
// Runs an application whose params and Gui are provided by runnerParams.
void Run(RunnerParams &runnerParams);

// `HelloImGui::Run(const SimpleRunnerParams&)`:
// Runs an application, using simpler params.
void Run(const SimpleRunnerParams &simpleParams);

// Runs an application, by providing the Gui function, the window title, etc.
void Run(
    const VoidFunction &guiFunction,
    const std::string &windowTitle = "",
    bool windowSizeAuto = false,
    bool windowRestorePreviousGeometry = false,
    const ScreenSize &windowSize = DefaultWindowSize,
    float fpsIdle = 10.f
);

// `GetRunnerParams()`:  a convenience function that will return the runnerParams
// of the current application
RunnerParams* GetRunnerParams();

// `IsUsingHelloImGui()`: returns true if the application is using HelloImGui
bool IsUsingHelloImGui();


// ============================== Utility functions ===============================

// @@md#UtilityFunctions


// `FrameRate(durationForMean = 0.5)`: Returns the current FrameRate.
//  May differ from ImGui::GetIO().FrameRate, since one can choose the duration
//  for the calculation of the mean value of the fps
//  Returns the current FrameRate. May differ from ImGui::GetIO().FrameRate,
//  since one can choose the duration for the calculation of the mean value of the fps
//  (Will only lead to accurate values if you call it at each frame)
float FrameRate(float durationForMean = 0.5f);

// `ImGuiTestEngine* GetImGuiTestEngine()`: returns a pointer to the global instance
//  of ImGuiTestEngine that was initialized by HelloImGui
//  (iif ImGui Test Engine is active).
ImGuiTestEngine* GetImGuiTestEngine();

// `GetBackendDescription()`: returns a string with the backend info
// Could be for example:
//     "Glfw - OpenGL3"
//     "Glfw - Metal"
//     "Sdl - Vulkan"
std::string GetBackendDescription();

// `ChangeWindowSize(const ScreenSize &windowSize)`: sets the window size
// (useful if you want to change the window size during execution)
void ChangeWindowSize(const ScreenSize &windowSize);

// @@md


// ============================== Layout Utils =============================

// @@md#HelloImGui::Layouts

// In advanced cases when several layouts are available, you can switch between layouts.
// See demo inside
//     https://github.com/pthom/hello_imgui/tree/master/src/hello_imgui_demos/hello_imgui_demodocking/hello_imgui_demodocking.main.cpp

// `SwitchLayout(layoutName)`
//  Changes the application current layout. Only used in advanced cases
//  when several layouts are available, i.e. if you filled
//      runnerParams.alternativeDockingLayouts.
void           SwitchLayout(const std::string& layoutName);

// `CurrentLayoutName()`: returns the name of the current layout
std::string    CurrentLayoutName();
// @@md


// ============================== User prefs Utils =============================

// @@md#HelloImGui::UserPref

// You may store additional user settings in the application settings.
// This is provided as a convenience only, and it is not intended to store large
// quantities of text data. Use sparingly.

// `SaveUserPref(string userPrefName, string userPrefContent)`:
//  Shall be called in the callback runnerParams.callbacks.BeforeExit
void        SaveUserPref(const std::string& userPrefName, const std::string& userPrefContent);

// `string LoadUserPref(string& userPrefName)`
//  Shall be called in the callback runnerParams.callbacks.PostInit
std::string LoadUserPref(const std::string& userPrefName);
// @@md


// ============================== Menus defaults =============================

/**
@@md#MenuIntro

Hello ImGui provides a default menu and status bar, which you can customize by using the params:
        `RunnerParams.imGuiWindowParams.` `showMenuBar` / `showMenu_App` / `showMenu_View`

If you want to fully customize the menu:
* set `showMenuBar` to true, then set `showMenu_App` and `showMenu_View` params to false
* implement the callback `RunnerParams.callbacks.ShowMenus`:
  it can optionally call `ShowViewMenu` and `ShowAppMenu` (see below).

@@md
*/
// @@md#MenuFunctions

// `ShowViewMenu(RunnerParams & runnerParams)`:
// shows the View menu (where you can select the layout and docked windows visibility
void ShowViewMenu(RunnerParams & runnerParams);

// `ShowAppMenu(RunnerParams & runnerParams)`:
// shows the default App menu (including the Quit item)
void ShowAppMenu(RunnerParams & runnerParams);
// @@md

}
