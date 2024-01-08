// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui.h                                                                          //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#if defined(__ANDROID__) && defined(HELLOIMGUI_USE_SDL)
// We need to include SDL, so that it can instantiate its main function under Android
#include "SDL.h"
#endif


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/dpi_aware.h included by hello_imgui.h                                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include "imgui.h"

namespace HelloImGui
{
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
// @@md

} // namespace HelloImGui


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
//                       hello_imgui/icons_font_awesome.h included by hello_imgui.h                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Generated by https://github.com/juliettef/IconFontCppHeaders script
// GenerateIconFontCppHeaders.py for language C89 from
// https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.yml
// for use with
// https://github.com/FortAwesome/Font-Awesome/blob/master/webfonts/fa-solid-900.ttf,
// https://github.com/FortAwesome/Font-Awesome/blob/master/webfonts/fa-regular-400.ttf,

#define FONT_ICON_FILE_NAME_FAR "fa-regular-400.ttf"
#define FONT_ICON_FILE_NAME_FAS "fa-solid-900.ttf"

#define ICON_MIN_FA 0xf000
#define ICON_MAX_FA 0xf897
#define ICON_FA_CLOUD_SHOWERS_HEAVY "\xEF\x9D\x80"
#define ICON_FA_CHEVRON_CIRCLE_RIGHT "\xEF\x84\xB8"
#define ICON_FA_DHARMACHAKRA "\xEF\x99\x95"
#define ICON_FA_BROADCAST_TOWER "\xEF\x94\x99"
#define ICON_FA_EXTERNAL_LINK_SQUARE_ALT "\xEF\x8D\xA0"
#define ICON_FA_SMOKING "\xEF\x92\x8D"
#define ICON_FA_PENCIL_ALT "\xEF\x8C\x83"
#define ICON_FA_CHESS_BISHOP "\xEF\x90\xBA"
#define ICON_FA_ICONS "\xEF\xA1\xAD"
#define ICON_FA_TV "\xEF\x89\xAC"
#define ICON_FA_CROP_ALT "\xEF\x95\xA5"
#define ICON_FA_LIST "\xEF\x80\xBA"
#define ICON_FA_BATTERY_QUARTER "\xEF\x89\x83"
#define ICON_FA_TH "\xEF\x80\x8A"
#define ICON_FA_RECYCLE "\xEF\x86\xB8"
#define ICON_FA_SMILE "\xEF\x84\x98"
#define ICON_FA_FAX "\xEF\x86\xAC"
#define ICON_FA_DRAFTING_COMPASS "\xEF\x95\xA8"
#define ICON_FA_USER_INJURED "\xEF\x9C\xA8"
#define ICON_FA_SCREWDRIVER "\xEF\x95\x8A"
#define ICON_FA_CROSSHAIRS "\xEF\x81\x9B"
#define ICON_FA_HAND_PEACE "\xEF\x89\x9B"
#define ICON_FA_FAN "\xEF\xA1\xA3"
#define ICON_FA_GOPURAM "\xEF\x99\xA4"
#define ICON_FA_CARET_UP "\xEF\x83\x98"
#define ICON_FA_SCHOOL "\xEF\x95\x89"
#define ICON_FA_FILE_PDF "\xEF\x87\x81"
#define ICON_FA_USERS_COG "\xEF\x94\x89"
#define ICON_FA_BALANCE_SCALE "\xEF\x89\x8E"
#define ICON_FA_UPLOAD "\xEF\x82\x93"
#define ICON_FA_LAPTOP_MEDICAL "\xEF\xA0\x92"
#define ICON_FA_VENUS "\xEF\x88\xA1"
#define ICON_FA_HEADING "\xEF\x87\x9C"
#define ICON_FA_ARROW_DOWN "\xEF\x81\xA3"
#define ICON_FA_BICYCLE "\xEF\x88\x86"
#define ICON_FA_TIRED "\xEF\x97\x88"
#define ICON_FA_COMMENT_MEDICAL "\xEF\x9F\xB5"
#define ICON_FA_BACON "\xEF\x9F\xA5"
#define ICON_FA_SYNC "\xEF\x80\xA1"
#define ICON_FA_PAPER_PLANE "\xEF\x87\x98"
#define ICON_FA_VOLLEYBALL_BALL "\xEF\x91\x9F"
#define ICON_FA_RIBBON "\xEF\x93\x96"
#define ICON_FA_SQUARE_ROOT_ALT "\xEF\x9A\x98"
#define ICON_FA_SUN "\xEF\x86\x85"
#define ICON_FA_FILE_POWERPOINT "\xEF\x87\x84"
#define ICON_FA_MICROCHIP "\xEF\x8B\x9B"
#define ICON_FA_TRASH_RESTORE_ALT "\xEF\xA0\xAA"
#define ICON_FA_GRADUATION_CAP "\xEF\x86\x9D"
#define ICON_FA_INFO_CIRCLE "\xEF\x81\x9A"
#define ICON_FA_TAGS "\xEF\x80\xAC"
#define ICON_FA_HAND_PAPER "\xEF\x89\x96"
#define ICON_FA_EQUALS "\xEF\x94\xAC"
#define ICON_FA_DIRECTIONS "\xEF\x97\xAB"
#define ICON_FA_FILE_INVOICE "\xEF\x95\xB0"
#define ICON_FA_SEARCH "\xEF\x80\x82"
#define ICON_FA_BIBLE "\xEF\x99\x87"
#define ICON_FA_WEIGHT_HANGING "\xEF\x97\x8D"
#define ICON_FA_CALENDAR_TIMES "\xEF\x89\xB3"
#define ICON_FA_GREATER_THAN_EQUAL "\xEF\x94\xB2"
#define ICON_FA_SLIDERS_H "\xEF\x87\x9E"
#define ICON_FA_EYE_SLASH "\xEF\x81\xB0"
#define ICON_FA_BIRTHDAY_CAKE "\xEF\x87\xBD"
#define ICON_FA_FEATHER_ALT "\xEF\x95\xAB"
#define ICON_FA_DNA "\xEF\x91\xB1"
#define ICON_FA_BASEBALL_BALL "\xEF\x90\xB3"
#define ICON_FA_HOSPITAL "\xEF\x83\xB8"
#define ICON_FA_COINS "\xEF\x94\x9E"
#define ICON_FA_TEMPERATURE_HIGH "\xEF\x9D\xA9"
#define ICON_FA_FONT_AWESOME_LOGO_FULL "\xEF\x93\xA6"
#define ICON_FA_PASSPORT "\xEF\x96\xAB"
#define ICON_FA_SHOPPING_CART "\xEF\x81\xBA"
#define ICON_FA_AWARD "\xEF\x95\x99"
#define ICON_FA_WINDOW_RESTORE "\xEF\x8B\x92"
#define ICON_FA_PHONE "\xEF\x82\x95"
#define ICON_FA_FLAG "\xEF\x80\xA4"
#define ICON_FA_FILE_INVOICE_DOLLAR "\xEF\x95\xB1"
#define ICON_FA_DICE_D6 "\xEF\x9B\x91"
#define ICON_FA_OUTDENT "\xEF\x80\xBB"
#define ICON_FA_LONG_ARROW_ALT_RIGHT "\xEF\x8C\x8B"
#define ICON_FA_PIZZA_SLICE "\xEF\xA0\x98"
#define ICON_FA_ADDRESS_CARD "\xEF\x8A\xBB"
#define ICON_FA_PARAGRAPH "\xEF\x87\x9D"
#define ICON_FA_MALE "\xEF\x86\x83"
#define ICON_FA_HISTORY "\xEF\x87\x9A"
#define ICON_FA_USER_TIE "\xEF\x94\x88"
#define ICON_FA_SEARCH_PLUS "\xEF\x80\x8E"
#define ICON_FA_LIFE_RING "\xEF\x87\x8D"
#define ICON_FA_STEP_FORWARD "\xEF\x81\x91"
#define ICON_FA_MOUSE_POINTER "\xEF\x89\x85"
#define ICON_FA_ALIGN_JUSTIFY "\xEF\x80\xB9"
#define ICON_FA_TOILET_PAPER "\xEF\x9C\x9E"
#define ICON_FA_BATTERY_THREE_QUARTERS "\xEF\x89\x81"
#define ICON_FA_OBJECT_UNGROUP "\xEF\x89\x88"
#define ICON_FA_BRIEFCASE "\xEF\x82\xB1"
#define ICON_FA_OIL_CAN "\xEF\x98\x93"
#define ICON_FA_THERMOMETER_FULL "\xEF\x8B\x87"
#define ICON_FA_SNOWBOARDING "\xEF\x9F\x8E"
#define ICON_FA_UNLINK "\xEF\x84\xA7"
#define ICON_FA_WINDOW_MAXIMIZE "\xEF\x8B\x90"
#define ICON_FA_YEN_SIGN "\xEF\x85\x97"
#define ICON_FA_SHARE_ALT_SQUARE "\xEF\x87\xA1"
#define ICON_FA_STEP_BACKWARD "\xEF\x81\x88"
#define ICON_FA_DRAGON "\xEF\x9B\x95"
#define ICON_FA_MICROPHONE_SLASH "\xEF\x84\xB1"
#define ICON_FA_USER_PLUS "\xEF\x88\xB4"
#define ICON_FA_WRENCH "\xEF\x82\xAD"
#define ICON_FA_AMBULANCE "\xEF\x83\xB9"
#define ICON_FA_ETHERNET "\xEF\x9E\x96"
#define ICON_FA_EGG "\xEF\x9F\xBB"
#define ICON_FA_WIND "\xEF\x9C\xAE"
#define ICON_FA_UNIVERSAL_ACCESS "\xEF\x8A\x9A"
#define ICON_FA_BURN "\xEF\x91\xAA"
#define ICON_FA_RADIATION "\xEF\x9E\xB9"
#define ICON_FA_DICE_ONE "\xEF\x94\xA5"
#define ICON_FA_KEYBOARD "\xEF\x84\x9C"
#define ICON_FA_CHECK_DOUBLE "\xEF\x95\xA0"
#define ICON_FA_HEADPHONES_ALT "\xEF\x96\x8F"
#define ICON_FA_BATTERY_HALF "\xEF\x89\x82"
#define ICON_FA_PROJECT_DIAGRAM "\xEF\x95\x82"
#define ICON_FA_PRAY "\xEF\x9A\x83"
#define ICON_FA_PHONE_ALT "\xEF\xA1\xB9"
#define ICON_FA_BABY_CARRIAGE "\xEF\x9D\xBD"
#define ICON_FA_TH_LIST "\xEF\x80\x8B"
#define ICON_FA_GRIN_TEARS "\xEF\x96\x88"
#define ICON_FA_SORT_AMOUNT_UP "\xEF\x85\xA1"
#define ICON_FA_COFFEE "\xEF\x83\xB4"
#define ICON_FA_TABLET_ALT "\xEF\x8F\xBA"
#define ICON_FA_GRIN_BEAM_SWEAT "\xEF\x96\x83"
#define ICON_FA_HAND_POINT_RIGHT "\xEF\x82\xA4"
#define ICON_FA_GRIN_STARS "\xEF\x96\x87"
#define ICON_FA_CHARGING_STATION "\xEF\x97\xA7"
#define ICON_FA_VOTE_YEA "\xEF\x9D\xB2"
#define ICON_FA_VOLUME_OFF "\xEF\x80\xA6"
#define ICON_FA_SAD_TEAR "\xEF\x96\xB4"
#define ICON_FA_CARET_RIGHT "\xEF\x83\x9A"
#define ICON_FA_BONG "\xEF\x95\x9C"
#define ICON_FA_BONE "\xEF\x97\x97"
#define ICON_FA_WEIGHT "\xEF\x92\x96"
#define ICON_FA_CARET_SQUARE_RIGHT "\xEF\x85\x92"
#define ICON_FA_FISH "\xEF\x95\xB8"
#define ICON_FA_SPIDER "\xEF\x9C\x97"
#define ICON_FA_QRCODE "\xEF\x80\xA9"
#define ICON_FA_SPINNER "\xEF\x84\x90"
#define ICON_FA_ELLIPSIS_H "\xEF\x85\x81"
#define ICON_FA_RUPEE_SIGN "\xEF\x85\x96"
#define ICON_FA_ASSISTIVE_LISTENING_SYSTEMS "\xEF\x8A\xA2"
#define ICON_FA_SMS "\xEF\x9F\x8D"
#define ICON_FA_POUND_SIGN "\xEF\x85\x94"
#define ICON_FA_HAND_POINT_DOWN "\xEF\x82\xA7"
#define ICON_FA_ADJUST "\xEF\x81\x82"
#define ICON_FA_PRINT "\xEF\x80\xAF"
#define ICON_FA_SURPRISE "\xEF\x97\x82"
#define ICON_FA_SORT_NUMERIC_UP "\xEF\x85\xA3"
#define ICON_FA_VIDEO_SLASH "\xEF\x93\xA2"
#define ICON_FA_SUBWAY "\xEF\x88\xB9"
#define ICON_FA_SORT_AMOUNT_DOWN "\xEF\x85\xA0"
#define ICON_FA_WINE_BOTTLE "\xEF\x9C\xAF"
#define ICON_FA_BOOK_READER "\xEF\x97\x9A"
#define ICON_FA_COOKIE "\xEF\x95\xA3"
#define ICON_FA_MONEY_BILL "\xEF\x83\x96"
#define ICON_FA_CHEVRON_DOWN "\xEF\x81\xB8"
#define ICON_FA_CAR_SIDE "\xEF\x97\xA4"
#define ICON_FA_FILTER "\xEF\x82\xB0"
#define ICON_FA_FOLDER_OPEN "\xEF\x81\xBC"
#define ICON_FA_SIGNATURE "\xEF\x96\xB7"
#define ICON_FA_HEARTBEAT "\xEF\x88\x9E"
#define ICON_FA_THUMBTACK "\xEF\x82\x8D"
#define ICON_FA_USER "\xEF\x80\x87"
#define ICON_FA_LAUGH_WINK "\xEF\x96\x9C"
#define ICON_FA_BREAD_SLICE "\xEF\x9F\xAC"
#define ICON_FA_TEXT_HEIGHT "\xEF\x80\xB4"
#define ICON_FA_VOLUME_MUTE "\xEF\x9A\xA9"
#define ICON_FA_GRIN_TONGUE "\xEF\x96\x89"
#define ICON_FA_CAMPGROUND "\xEF\x9A\xBB"
#define ICON_FA_MERCURY "\xEF\x88\xA3"
#define ICON_FA_USER_ASTRONAUT "\xEF\x93\xBB"
#define ICON_FA_HORSE "\xEF\x9B\xB0"
#define ICON_FA_SORT_DOWN "\xEF\x83\x9D"
#define ICON_FA_PERCENTAGE "\xEF\x95\x81"
#define ICON_FA_AIR_FRESHENER "\xEF\x97\x90"
#define ICON_FA_STORE "\xEF\x95\x8E"
#define ICON_FA_COMMENT_DOTS "\xEF\x92\xAD"
#define ICON_FA_SMILE_WINK "\xEF\x93\x9A"
#define ICON_FA_HOTEL "\xEF\x96\x94"
#define ICON_FA_PEPPER_HOT "\xEF\xA0\x96"
#define ICON_FA_CUBES "\xEF\x86\xB3"
#define ICON_FA_DUMPSTER_FIRE "\xEF\x9E\x94"
#define ICON_FA_CLOUD_SUN_RAIN "\xEF\x9D\x83"
#define ICON_FA_GLOBE_ASIA "\xEF\x95\xBE"
#define ICON_FA_VIAL "\xEF\x92\x92"
#define ICON_FA_STROOPWAFEL "\xEF\x95\x91"
#define ICON_FA_CALENDAR_MINUS "\xEF\x89\xB2"
#define ICON_FA_TREE "\xEF\x86\xBB"
#define ICON_FA_SHOWER "\xEF\x8B\x8C"
#define ICON_FA_DRUM_STEELPAN "\xEF\x95\xAA"
#define ICON_FA_FILE_UPLOAD "\xEF\x95\xB4"
#define ICON_FA_MEDKIT "\xEF\x83\xBA"
#define ICON_FA_MINUS "\xEF\x81\xA8"
#define ICON_FA_SHEKEL_SIGN "\xEF\x88\x8B"
#define ICON_FA_USER_NINJA "\xEF\x94\x84"
#define ICON_FA_KAABA "\xEF\x99\xAB"
#define ICON_FA_BELL_SLASH "\xEF\x87\xB6"
#define ICON_FA_SPELL_CHECK "\xEF\xA2\x91"
#define ICON_FA_MAIL_BULK "\xEF\x99\xB4"
#define ICON_FA_MOUNTAIN "\xEF\x9B\xBC"
#define ICON_FA_COUCH "\xEF\x92\xB8"
#define ICON_FA_CHESS "\xEF\x90\xB9"
#define ICON_FA_FILE_EXPORT "\xEF\x95\xAE"
#define ICON_FA_SIGN_LANGUAGE "\xEF\x8A\xA7"
#define ICON_FA_SNOWFLAKE "\xEF\x8B\x9C"
#define ICON_FA_PLAY "\xEF\x81\x8B"
#define ICON_FA_HEADSET "\xEF\x96\x90"
#define ICON_FA_CHART_BAR "\xEF\x82\x80"
#define ICON_FA_WAVE_SQUARE "\xEF\xA0\xBE"
#define ICON_FA_CHART_AREA "\xEF\x87\xBE"
#define ICON_FA_EURO_SIGN "\xEF\x85\x93"
#define ICON_FA_CHESS_KING "\xEF\x90\xBF"
#define ICON_FA_MOBILE "\xEF\x84\x8B"
#define ICON_FA_CLOCK "\xEF\x80\x97"
#define ICON_FA_BOX_OPEN "\xEF\x92\x9E"
#define ICON_FA_DOG "\xEF\x9B\x93"
#define ICON_FA_FUTBOL "\xEF\x87\xA3"
#define ICON_FA_LIRA_SIGN "\xEF\x86\x95"
#define ICON_FA_LIGHTBULB "\xEF\x83\xAB"
#define ICON_FA_BOMB "\xEF\x87\xA2"
#define ICON_FA_MITTEN "\xEF\x9E\xB5"
#define ICON_FA_TRUCK_MONSTER "\xEF\x98\xBB"
#define ICON_FA_RANDOM "\xEF\x81\xB4"
#define ICON_FA_CHESS_ROOK "\xEF\x91\x87"
#define ICON_FA_FIRE_EXTINGUISHER "\xEF\x84\xB4"
#define ICON_FA_ARROWS_ALT_V "\xEF\x8C\xB8"
#define ICON_FA_ICICLES "\xEF\x9E\xAD"
#define ICON_FA_FONT "\xEF\x80\xB1"
#define ICON_FA_CAMERA_RETRO "\xEF\x82\x83"
#define ICON_FA_BLENDER "\xEF\x94\x97"
#define ICON_FA_THUMBS_DOWN "\xEF\x85\xA5"
#define ICON_FA_ROCKET "\xEF\x84\xB5"
#define ICON_FA_COPYRIGHT "\xEF\x87\xB9"
#define ICON_FA_TRAM "\xEF\x9F\x9A"
#define ICON_FA_JEDI "\xEF\x99\xA9"
#define ICON_FA_HOCKEY_PUCK "\xEF\x91\x93"
#define ICON_FA_STOP_CIRCLE "\xEF\x8A\x8D"
#define ICON_FA_BEZIER_CURVE "\xEF\x95\x9B"
#define ICON_FA_FOLDER "\xEF\x81\xBB"
#define ICON_FA_CALENDAR_CHECK "\xEF\x89\xB4"
#define ICON_FA_YIN_YANG "\xEF\x9A\xAD"
#define ICON_FA_COLUMNS "\xEF\x83\x9B"
#define ICON_FA_GLASS_CHEERS "\xEF\x9E\x9F"
#define ICON_FA_GRIN_WINK "\xEF\x96\x8C"
#define ICON_FA_STOP "\xEF\x81\x8D"
#define ICON_FA_MONEY_CHECK_ALT "\xEF\x94\xBD"
#define ICON_FA_COMPASS "\xEF\x85\x8E"
#define ICON_FA_TOOLBOX "\xEF\x95\x92"
#define ICON_FA_LIST_OL "\xEF\x83\x8B"
#define ICON_FA_WINE_GLASS "\xEF\x93\xA3"
#define ICON_FA_HORSE_HEAD "\xEF\x9E\xAB"
#define ICON_FA_USER_ALT_SLASH "\xEF\x93\xBA"
#define ICON_FA_USER_TAG "\xEF\x94\x87"
#define ICON_FA_MICROSCOPE "\xEF\x98\x90"
#define ICON_FA_BRUSH "\xEF\x95\x9D"
#define ICON_FA_BAN "\xEF\x81\x9E"
#define ICON_FA_BARS "\xEF\x83\x89"
#define ICON_FA_CAR_CRASH "\xEF\x97\xA1"
#define ICON_FA_ARROW_ALT_CIRCLE_DOWN "\xEF\x8D\x98"
#define ICON_FA_MONEY_BILL_ALT "\xEF\x8F\x91"
#define ICON_FA_JOURNAL_WHILLS "\xEF\x99\xAA"
#define ICON_FA_CHALKBOARD_TEACHER "\xEF\x94\x9C"
#define ICON_FA_PORTRAIT "\xEF\x8F\xA0"
#define ICON_FA_BALANCE_SCALE_LEFT "\xEF\x94\x95"
#define ICON_FA_HAMMER "\xEF\x9B\xA3"
#define ICON_FA_RETWEET "\xEF\x81\xB9"
#define ICON_FA_HOURGLASS "\xEF\x89\x94"
#define ICON_FA_BORDER_NONE "\xEF\xA1\x90"
#define ICON_FA_FILE_ALT "\xEF\x85\x9C"
#define ICON_FA_SUBSCRIPT "\xEF\x84\xAC"
#define ICON_FA_DONATE "\xEF\x92\xB9"
#define ICON_FA_GLASS_MARTINI_ALT "\xEF\x95\xBB"
#define ICON_FA_CODE_BRANCH "\xEF\x84\xA6"
#define ICON_FA_MEH "\xEF\x84\x9A"
#define ICON_FA_LIST_ALT "\xEF\x80\xA2"
#define ICON_FA_USER_COG "\xEF\x93\xBE"
#define ICON_FA_PRESCRIPTION "\xEF\x96\xB1"
#define ICON_FA_TABLET "\xEF\x84\x8A"
#define ICON_FA_LAUGH_SQUINT "\xEF\x96\x9B"
#define ICON_FA_CREDIT_CARD "\xEF\x82\x9D"
#define ICON_FA_ARCHWAY "\xEF\x95\x97"
#define ICON_FA_HARD_HAT "\xEF\xA0\x87"
#define ICON_FA_TRAFFIC_LIGHT "\xEF\x98\xB7"
#define ICON_FA_COG "\xEF\x80\x93"
#define ICON_FA_HANUKIAH "\xEF\x9B\xA6"
#define ICON_FA_SHUTTLE_VAN "\xEF\x96\xB6"
#define ICON_FA_MONEY_CHECK "\xEF\x94\xBC"
#define ICON_FA_BELL "\xEF\x83\xB3"
#define ICON_FA_CALENDAR_DAY "\xEF\x9E\x83"
#define ICON_FA_TINT_SLASH "\xEF\x97\x87"
#define ICON_FA_PLANE_DEPARTURE "\xEF\x96\xB0"
#define ICON_FA_USER_CHECK "\xEF\x93\xBC"
#define ICON_FA_CHURCH "\xEF\x94\x9D"
#define ICON_FA_SEARCH_MINUS "\xEF\x80\x90"
#define ICON_FA_SHIPPING_FAST "\xEF\x92\x8B"
#define ICON_FA_TINT "\xEF\x81\x83"
#define ICON_FA_ALIGN_RIGHT "\xEF\x80\xB8"
#define ICON_FA_QUOTE_RIGHT "\xEF\x84\x8E"
#define ICON_FA_BEER "\xEF\x83\xBC"
#define ICON_FA_GRIN_ALT "\xEF\x96\x81"
#define ICON_FA_SORT_NUMERIC_DOWN "\xEF\x85\xA2"
#define ICON_FA_FIRE "\xEF\x81\xAD"
#define ICON_FA_FAST_FORWARD "\xEF\x81\x90"
#define ICON_FA_MAP_MARKED_ALT "\xEF\x96\xA0"
#define ICON_FA_CHILD "\xEF\x86\xAE"
#define ICON_FA_KISS_BEAM "\xEF\x96\x97"
#define ICON_FA_TRUCK_LOADING "\xEF\x93\x9E"
#define ICON_FA_EXPAND_ARROWS_ALT "\xEF\x8C\x9E"
#define ICON_FA_CARET_SQUARE_DOWN "\xEF\x85\x90"
#define ICON_FA_CRUTCH "\xEF\x9F\xB7"
#define ICON_FA_OBJECT_GROUP "\xEF\x89\x87"
#define ICON_FA_BIKING "\xEF\xA1\x8A"
#define ICON_FA_ANCHOR "\xEF\x84\xBD"
#define ICON_FA_HAND_POINT_LEFT "\xEF\x82\xA5"
#define ICON_FA_USER_TIMES "\xEF\x88\xB5"
#define ICON_FA_CALCULATOR "\xEF\x87\xAC"
#define ICON_FA_DIZZY "\xEF\x95\xA7"
#define ICON_FA_KISS_WINK_HEART "\xEF\x96\x98"
#define ICON_FA_FILE_MEDICAL "\xEF\x91\xB7"
#define ICON_FA_SWIMMING_POOL "\xEF\x97\x85"
#define ICON_FA_VR_CARDBOARD "\xEF\x9C\xA9"
#define ICON_FA_USER_FRIENDS "\xEF\x94\x80"
#define ICON_FA_FAST_BACKWARD "\xEF\x81\x89"
#define ICON_FA_SATELLITE "\xEF\x9E\xBF"
#define ICON_FA_MINUS_CIRCLE "\xEF\x81\x96"
#define ICON_FA_CHESS_PAWN "\xEF\x91\x83"
#define ICON_FA_DATABASE "\xEF\x87\x80"
#define ICON_FA_LANDMARK "\xEF\x99\xAF"
#define ICON_FA_SWATCHBOOK "\xEF\x97\x83"
#define ICON_FA_HOTDOG "\xEF\xA0\x8F"
#define ICON_FA_SNOWMAN "\xEF\x9F\x90"
#define ICON_FA_LAPTOP "\xEF\x84\x89"
#define ICON_FA_TORAH "\xEF\x9A\xA0"
#define ICON_FA_FROWN_OPEN "\xEF\x95\xBA"
#define ICON_FA_REDO_ALT "\xEF\x8B\xB9"
#define ICON_FA_AD "\xEF\x99\x81"
#define ICON_FA_USER_CIRCLE "\xEF\x8A\xBD"
#define ICON_FA_DIVIDE "\xEF\x94\xA9"
#define ICON_FA_HANDSHAKE "\xEF\x8A\xB5"
#define ICON_FA_CUT "\xEF\x83\x84"
#define ICON_FA_GAMEPAD "\xEF\x84\x9B"
#define ICON_FA_STREET_VIEW "\xEF\x88\x9D"
#define ICON_FA_GREATER_THAN "\xEF\x94\xB1"
#define ICON_FA_PASTAFARIANISM "\xEF\x99\xBB"
#define ICON_FA_MINUS_SQUARE "\xEF\x85\x86"
#define ICON_FA_SAVE "\xEF\x83\x87"
#define ICON_FA_COMMENT_DOLLAR "\xEF\x99\x91"
#define ICON_FA_TRASH_ALT "\xEF\x8B\xAD"
#define ICON_FA_PUZZLE_PIECE "\xEF\x84\xAE"
#define ICON_FA_SORT_ALPHA_UP_ALT "\xEF\xA2\x82"
#define ICON_FA_MENORAH "\xEF\x99\xB6"
#define ICON_FA_CLOUD_SUN "\xEF\x9B\x84"
#define ICON_FA_USER_EDIT "\xEF\x93\xBF"
#define ICON_FA_THEATER_MASKS "\xEF\x98\xB0"
#define ICON_FA_FILE_MEDICAL_ALT "\xEF\x91\xB8"
#define ICON_FA_BOXES "\xEF\x91\xA8"
#define ICON_FA_THERMOMETER_EMPTY "\xEF\x8B\x8B"
#define ICON_FA_EXCLAMATION_TRIANGLE "\xEF\x81\xB1"
#define ICON_FA_GIFT "\xEF\x81\xAB"
#define ICON_FA_COGS "\xEF\x82\x85"
#define ICON_FA_SIGNAL "\xEF\x80\x92"
#define ICON_FA_SHAPES "\xEF\x98\x9F"
#define ICON_FA_CLOUD_RAIN "\xEF\x9C\xBD"
#define ICON_FA_LESS_THAN_EQUAL "\xEF\x94\xB7"
#define ICON_FA_CHEVRON_CIRCLE_LEFT "\xEF\x84\xB7"
#define ICON_FA_MORTAR_PESTLE "\xEF\x96\xA7"
#define ICON_FA_DUMBBELL "\xEF\x91\x8B"
#define ICON_FA_SITEMAP "\xEF\x83\xA8"
#define ICON_FA_BUS_ALT "\xEF\x95\x9E"
#define ICON_FA_FILE_CODE "\xEF\x87\x89"
#define ICON_FA_BATTERY_FULL "\xEF\x89\x80"
#define ICON_FA_CROWN "\xEF\x94\xA1"
#define ICON_FA_EXCHANGE_ALT "\xEF\x8D\xA2"
#define ICON_FA_TRANSGENDER_ALT "\xEF\x88\xA5"
#define ICON_FA_STAR_OF_DAVID "\xEF\x9A\x9A"
#define ICON_FA_CASH_REGISTER "\xEF\x9E\x88"
#define ICON_FA_TOOLS "\xEF\x9F\x99"
#define ICON_FA_EXCLAMATION_CIRCLE "\xEF\x81\xAA"
#define ICON_FA_COMMENTS "\xEF\x82\x86"
#define ICON_FA_BRIEFCASE_MEDICAL "\xEF\x91\xA9"
#define ICON_FA_COMMENTS_DOLLAR "\xEF\x99\x93"
#define ICON_FA_BACKSPACE "\xEF\x95\x9A"
#define ICON_FA_SLASH "\xEF\x9C\x95"
#define ICON_FA_HOT_TUB "\xEF\x96\x93"
#define ICON_FA_SUITCASE_ROLLING "\xEF\x97\x81"
#define ICON_FA_BOLD "\xEF\x80\xB2"
#define ICON_FA_HANDS_HELPING "\xEF\x93\x84"
#define ICON_FA_SLEIGH "\xEF\x9F\x8C"
#define ICON_FA_BOLT "\xEF\x83\xA7"
#define ICON_FA_THERMOMETER_QUARTER "\xEF\x8B\x8A"
#define ICON_FA_TROPHY "\xEF\x82\x91"
#define ICON_FA_USER_ALT "\xEF\x90\x86"
#define ICON_FA_BRAILLE "\xEF\x8A\xA1"
#define ICON_FA_PLUS "\xEF\x81\xA7"
#define ICON_FA_LIST_UL "\xEF\x83\x8A"
#define ICON_FA_SMOKING_BAN "\xEF\x95\x8D"
#define ICON_FA_BOOK "\xEF\x80\xAD"
#define ICON_FA_VOLUME_DOWN "\xEF\x80\xA7"
#define ICON_FA_QUESTION_CIRCLE "\xEF\x81\x99"
#define ICON_FA_CARROT "\xEF\x9E\x87"
#define ICON_FA_BATH "\xEF\x8B\x8D"
#define ICON_FA_GAVEL "\xEF\x83\xA3"
#define ICON_FA_CANDY_CANE "\xEF\x9E\x86"
#define ICON_FA_NETWORK_WIRED "\xEF\x9B\xBF"
#define ICON_FA_CARET_SQUARE_LEFT "\xEF\x86\x91"
#define ICON_FA_PLANE_ARRIVAL "\xEF\x96\xAF"
#define ICON_FA_SHARE_SQUARE "\xEF\x85\x8D"
#define ICON_FA_MEDAL "\xEF\x96\xA2"
#define ICON_FA_THERMOMETER_HALF "\xEF\x8B\x89"
#define ICON_FA_QUESTION "\xEF\x84\xA8"
#define ICON_FA_CAR_BATTERY "\xEF\x97\x9F"
#define ICON_FA_DOOR_CLOSED "\xEF\x94\xAA"
#define ICON_FA_USER_MINUS "\xEF\x94\x83"
#define ICON_FA_MUSIC "\xEF\x80\x81"
#define ICON_FA_HOUSE_DAMAGE "\xEF\x9B\xB1"
#define ICON_FA_CHEVRON_RIGHT "\xEF\x81\x94"
#define ICON_FA_GRIP_HORIZONTAL "\xEF\x96\x8D"
#define ICON_FA_DICE_FOUR "\xEF\x94\xA4"
#define ICON_FA_DEAF "\xEF\x8A\xA4"
#define ICON_FA_MEH_BLANK "\xEF\x96\xA4"
#define ICON_FA_WINDOW_CLOSE "\xEF\x90\x90"
#define ICON_FA_LINK "\xEF\x83\x81"
#define ICON_FA_ATOM "\xEF\x97\x92"
#define ICON_FA_LESS_THAN "\xEF\x94\xB6"
#define ICON_FA_OTTER "\xEF\x9C\x80"
#define ICON_FA_DICE_TWO "\xEF\x94\xA8"
#define ICON_FA_SORT_ALPHA_DOWN_ALT "\xEF\xA2\x81"
#define ICON_FA_EJECT "\xEF\x81\x92"
#define ICON_FA_SKULL "\xEF\x95\x8C"
#define ICON_FA_GRIP_LINES "\xEF\x9E\xA4"
#define ICON_FA_SORT_AMOUNT_DOWN_ALT "\xEF\xA2\x84"
#define ICON_FA_HOSPITAL_SYMBOL "\xEF\x91\xBE"
#define ICON_FA_X_RAY "\xEF\x92\x97"
#define ICON_FA_ARROW_UP "\xEF\x81\xA2"
#define ICON_FA_MONEY_BILL_WAVE "\xEF\x94\xBA"
#define ICON_FA_DOT_CIRCLE "\xEF\x86\x92"
#define ICON_FA_IMAGES "\xEF\x8C\x82"
#define ICON_FA_STAR_HALF "\xEF\x82\x89"
#define ICON_FA_SPLOTCH "\xEF\x96\xBC"
#define ICON_FA_STAR_HALF_ALT "\xEF\x97\x80"
#define ICON_FA_SHIP "\xEF\x88\x9A"
#define ICON_FA_BOOK_DEAD "\xEF\x9A\xB7"
#define ICON_FA_CHECK "\xEF\x80\x8C"
#define ICON_FA_RAINBOW "\xEF\x9D\x9B"
#define ICON_FA_POWER_OFF "\xEF\x80\x91"
#define ICON_FA_LEMON "\xEF\x82\x94"
#define ICON_FA_GLOBE_AMERICAS "\xEF\x95\xBD"
#define ICON_FA_PEACE "\xEF\x99\xBC"
#define ICON_FA_THERMOMETER_THREE_QUARTERS "\xEF\x8B\x88"
#define ICON_FA_WAREHOUSE "\xEF\x92\x94"
#define ICON_FA_TRANSGENDER "\xEF\x88\xA4"
#define ICON_FA_PLUS_SQUARE "\xEF\x83\xBE"
#define ICON_FA_BULLSEYE "\xEF\x85\x80"
#define ICON_FA_COOKIE_BITE "\xEF\x95\xA4"
#define ICON_FA_USERS "\xEF\x83\x80"
#define ICON_FA_DRUMSTICK_BITE "\xEF\x9B\x97"
#define ICON_FA_ASTERISK "\xEF\x81\xA9"
#define ICON_FA_PLUS_CIRCLE "\xEF\x81\x95"
#define ICON_FA_CART_ARROW_DOWN "\xEF\x88\x98"
#define ICON_FA_LEAF "\xEF\x81\xAC"
#define ICON_FA_FLUSHED "\xEF\x95\xB9"
#define ICON_FA_STORE_ALT "\xEF\x95\x8F"
#define ICON_FA_PEOPLE_CARRY "\xEF\x93\x8E"
#define ICON_FA_CHESS_BOARD "\xEF\x90\xBC"
#define ICON_FA_LONG_ARROW_ALT_DOWN "\xEF\x8C\x89"
#define ICON_FA_SAD_CRY "\xEF\x96\xB3"
#define ICON_FA_DIGITAL_TACHOGRAPH "\xEF\x95\xA6"
#define ICON_FA_ANGLE_DOUBLE_DOWN "\xEF\x84\x83"
#define ICON_FA_FILE_EXCEL "\xEF\x87\x83"
#define ICON_FA_TEETH "\xEF\x98\xAE"
#define ICON_FA_HAND_SCISSORS "\xEF\x89\x97"
#define ICON_FA_STETHOSCOPE "\xEF\x83\xB1"
#define ICON_FA_BACKWARD "\xEF\x81\x8A"
#define ICON_FA_SCROLL "\xEF\x9C\x8E"
#define ICON_FA_IGLOO "\xEF\x9E\xAE"
#define ICON_FA_NOTES_MEDICAL "\xEF\x92\x81"
#define ICON_FA_CODE "\xEF\x84\xA1"
#define ICON_FA_SORT_NUMERIC_UP_ALT "\xEF\xA2\x87"
#define ICON_FA_NOT_EQUAL "\xEF\x94\xBE"
#define ICON_FA_SKIING "\xEF\x9F\x89"
#define ICON_FA_CHAIR "\xEF\x9B\x80"
#define ICON_FA_HAND_LIZARD "\xEF\x89\x98"
#define ICON_FA_QUIDDITCH "\xEF\x91\x98"
#define ICON_FA_ANGLE_DOUBLE_LEFT "\xEF\x84\x80"
#define ICON_FA_MOSQUE "\xEF\x99\xB8"
#define ICON_FA_PEN "\xEF\x8C\x84"
#define ICON_FA_HRYVNIA "\xEF\x9B\xB2"
#define ICON_FA_ANGLE_LEFT "\xEF\x84\x84"
#define ICON_FA_ATLAS "\xEF\x95\x98"
#define ICON_FA_PIGGY_BANK "\xEF\x93\x93"
#define ICON_FA_DOLLY_FLATBED "\xEF\x91\xB4"
#define ICON_FA_ARROWS_ALT_H "\xEF\x8C\xB7"
#define ICON_FA_PEN_ALT "\xEF\x8C\x85"
#define ICON_FA_PRAYING_HANDS "\xEF\x9A\x84"
#define ICON_FA_VOLUME_UP "\xEF\x80\xA8"
#define ICON_FA_CLIPBOARD_LIST "\xEF\x91\xAD"
#define ICON_FA_BORDER_ALL "\xEF\xA1\x8C"
#define ICON_FA_MAGIC "\xEF\x83\x90"
#define ICON_FA_FOLDER_MINUS "\xEF\x99\x9D"
#define ICON_FA_DEMOCRAT "\xEF\x9D\x87"
#define ICON_FA_MAGNET "\xEF\x81\xB6"
#define ICON_FA_VIHARA "\xEF\x9A\xA7"
#define ICON_FA_GRIMACE "\xEF\x95\xBF"
#define ICON_FA_CHECK_CIRCLE "\xEF\x81\x98"
#define ICON_FA_SEARCH_DOLLAR "\xEF\x9A\x88"
#define ICON_FA_LONG_ARROW_ALT_LEFT "\xEF\x8C\x8A"
#define ICON_FA_FILE_PRESCRIPTION "\xEF\x95\xB2"
#define ICON_FA_CROW "\xEF\x94\xA0"
#define ICON_FA_EYE_DROPPER "\xEF\x87\xBB"
#define ICON_FA_CROP "\xEF\x84\xA5"
#define ICON_FA_SIGN "\xEF\x93\x99"
#define ICON_FA_ARROW_CIRCLE_DOWN "\xEF\x82\xAB"
#define ICON_FA_VIDEO "\xEF\x80\xBD"
#define ICON_FA_DOWNLOAD "\xEF\x80\x99"
#define ICON_FA_CARET_DOWN "\xEF\x83\x97"
#define ICON_FA_CHEVRON_LEFT "\xEF\x81\x93"
#define ICON_FA_GLOBE_AFRICA "\xEF\x95\xBC"
#define ICON_FA_HAMSA "\xEF\x99\xA5"
#define ICON_FA_CART_PLUS "\xEF\x88\x97"
#define ICON_FA_CLIPBOARD "\xEF\x8C\xA8"
#define ICON_FA_SHOE_PRINTS "\xEF\x95\x8B"
#define ICON_FA_PHONE_SLASH "\xEF\x8F\x9D"
#define ICON_FA_REPLY "\xEF\x8F\xA5"
#define ICON_FA_HOURGLASS_HALF "\xEF\x89\x92"
#define ICON_FA_LONG_ARROW_ALT_UP "\xEF\x8C\x8C"
#define ICON_FA_CHESS_KNIGHT "\xEF\x91\x81"
#define ICON_FA_BARCODE "\xEF\x80\xAA"
#define ICON_FA_DRAW_POLYGON "\xEF\x97\xAE"
#define ICON_FA_WATER "\xEF\x9D\xB3"
#define ICON_FA_WINE_GLASS_ALT "\xEF\x97\x8E"
#define ICON_FA_PHONE_VOLUME "\xEF\x8A\xA0"
#define ICON_FA_GLASS_WHISKEY "\xEF\x9E\xA0"
#define ICON_FA_BOX "\xEF\x91\xA6"
#define ICON_FA_DIAGNOSES "\xEF\x91\xB0"
#define ICON_FA_FILE_IMAGE "\xEF\x87\x85"
#define ICON_FA_VENUS_MARS "\xEF\x88\xA8"
#define ICON_FA_TASKS "\xEF\x82\xAE"
#define ICON_FA_HIKING "\xEF\x9B\xAC"
#define ICON_FA_VECTOR_SQUARE "\xEF\x97\x8B"
#define ICON_FA_QUOTE_LEFT "\xEF\x84\x8D"
#define ICON_FA_MOBILE_ALT "\xEF\x8F\x8D"
#define ICON_FA_USER_SHIELD "\xEF\x94\x85"
#define ICON_FA_BLOG "\xEF\x9E\x81"
#define ICON_FA_MARKER "\xEF\x96\xA1"
#define ICON_FA_HAMBURGER "\xEF\xA0\x85"
#define ICON_FA_REDO "\xEF\x80\x9E"
#define ICON_FA_CLOUD "\xEF\x83\x82"
#define ICON_FA_HAND_HOLDING_USD "\xEF\x93\x80"
#define ICON_FA_CERTIFICATE "\xEF\x82\xA3"
#define ICON_FA_ANGRY "\xEF\x95\x96"
#define ICON_FA_FROG "\xEF\x94\xAE"
#define ICON_FA_CAMERA "\xEF\x80\xB0"
#define ICON_FA_DICE_THREE "\xEF\x94\xA7"
#define ICON_FA_MEMORY "\xEF\x94\xB8"
#define ICON_FA_PEN_SQUARE "\xEF\x85\x8B"
#define ICON_FA_SORT "\xEF\x83\x9C"
#define ICON_FA_PLUG "\xEF\x87\xA6"
#define ICON_FA_SHARE "\xEF\x81\xA4"
#define ICON_FA_ENVELOPE "\xEF\x83\xA0"
#define ICON_FA_LAYER_GROUP "\xEF\x97\xBD"
#define ICON_FA_TRAIN "\xEF\x88\xB8"
#define ICON_FA_BULLHORN "\xEF\x82\xA1"
#define ICON_FA_BABY "\xEF\x9D\xBC"
#define ICON_FA_CONCIERGE_BELL "\xEF\x95\xA2"
#define ICON_FA_CIRCLE "\xEF\x84\x91"
#define ICON_FA_I_CURSOR "\xEF\x89\x86"
#define ICON_FA_CAR "\xEF\x86\xB9"
#define ICON_FA_CAT "\xEF\x9A\xBE"
#define ICON_FA_WALLET "\xEF\x95\x95"
#define ICON_FA_BOOK_MEDICAL "\xEF\x9F\xA6"
#define ICON_FA_H_SQUARE "\xEF\x83\xBD"
#define ICON_FA_HEART "\xEF\x80\x84"
#define ICON_FA_LOCK_OPEN "\xEF\x8F\x81"
#define ICON_FA_STREAM "\xEF\x95\x90"
#define ICON_FA_LOCK "\xEF\x80\xA3"
#define ICON_FA_PARACHUTE_BOX "\xEF\x93\x8D"
#define ICON_FA_TAG "\xEF\x80\xAB"
#define ICON_FA_SMILE_BEAM "\xEF\x96\xB8"
#define ICON_FA_USER_NURSE "\xEF\xA0\xAF"
#define ICON_FA_MICROPHONE_ALT "\xEF\x8F\x89"
#define ICON_FA_SPA "\xEF\x96\xBB"
#define ICON_FA_CHEVRON_CIRCLE_DOWN "\xEF\x84\xBA"
#define ICON_FA_FOLDER_PLUS "\xEF\x99\x9E"
#define ICON_FA_TICKET_ALT "\xEF\x8F\xBF"
#define ICON_FA_BOOK_OPEN "\xEF\x94\x98"
#define ICON_FA_MAP "\xEF\x89\xB9"
#define ICON_FA_COCKTAIL "\xEF\x95\xA1"
#define ICON_FA_CLONE "\xEF\x89\x8D"
#define ICON_FA_ID_CARD_ALT "\xEF\x91\xBF"
#define ICON_FA_CHECK_SQUARE "\xEF\x85\x8A"
#define ICON_FA_CHART_LINE "\xEF\x88\x81"
#define ICON_FA_POO_STORM "\xEF\x9D\x9A"
#define ICON_FA_DOVE "\xEF\x92\xBA"
#define ICON_FA_MARS_STROKE "\xEF\x88\xA9"
#define ICON_FA_ENVELOPE_OPEN "\xEF\x8A\xB6"
#define ICON_FA_WHEELCHAIR "\xEF\x86\x93"
#define ICON_FA_ROBOT "\xEF\x95\x84"
#define ICON_FA_UNDO_ALT "\xEF\x8B\xAA"
#define ICON_FA_CLOUD_MEATBALL "\xEF\x9C\xBB"
#define ICON_FA_TRUCK "\xEF\x83\x91"
#define ICON_FA_FLASK "\xEF\x83\x83"
#define ICON_FA_WON_SIGN "\xEF\x85\x99"
#define ICON_FA_SUPERSCRIPT "\xEF\x84\xAB"
#define ICON_FA_TTY "\xEF\x87\xA4"
#define ICON_FA_USER_MD "\xEF\x83\xB0"
#define ICON_FA_BRAIN "\xEF\x97\x9C"
#define ICON_FA_TABLETS "\xEF\x92\x90"
#define ICON_FA_MOTORCYCLE "\xEF\x88\x9C"
#define ICON_FA_PHONE_SQUARE_ALT "\xEF\xA1\xBB"
#define ICON_FA_ANGLE_UP "\xEF\x84\x86"
#define ICON_FA_BROOM "\xEF\x94\x9A"
#define ICON_FA_DICE_D20 "\xEF\x9B\x8F"
#define ICON_FA_LEVEL_DOWN_ALT "\xEF\x8E\xBE"
#define ICON_FA_PAPERCLIP "\xEF\x83\x86"
#define ICON_FA_USER_CLOCK "\xEF\x93\xBD"
#define ICON_FA_MUG_HOT "\xEF\x9E\xB6"
#define ICON_FA_SORT_ALPHA_UP "\xEF\x85\x9E"
#define ICON_FA_AUDIO_DESCRIPTION "\xEF\x8A\x9E"
#define ICON_FA_FILE_CSV "\xEF\x9B\x9D"
#define ICON_FA_FILE_DOWNLOAD "\xEF\x95\xAD"
#define ICON_FA_SYNC_ALT "\xEF\x8B\xB1"
#define ICON_FA_ANGLE_DOUBLE_UP "\xEF\x84\x82"
#define ICON_FA_HANDS "\xEF\x93\x82"
#define ICON_FA_REPUBLICAN "\xEF\x9D\x9E"
#define ICON_FA_UNIVERSITY "\xEF\x86\x9C"
#define ICON_FA_KHANDA "\xEF\x99\xAD"
#define ICON_FA_GLASSES "\xEF\x94\xB0"
#define ICON_FA_SQUARE "\xEF\x83\x88"
#define ICON_FA_GRIN_SQUINT "\xEF\x96\x85"
#define ICON_FA_CLOSED_CAPTIONING "\xEF\x88\x8A"
#define ICON_FA_RECEIPT "\xEF\x95\x83"
#define ICON_FA_STRIKETHROUGH "\xEF\x83\x8C"
#define ICON_FA_UNLOCK "\xEF\x82\x9C"
#define ICON_FA_ARROW_LEFT "\xEF\x81\xA0"
#define ICON_FA_DICE_SIX "\xEF\x94\xA6"
#define ICON_FA_GRIP_VERTICAL "\xEF\x96\x8E"
#define ICON_FA_PILLS "\xEF\x92\x84"
#define ICON_FA_EXCLAMATION "\xEF\x84\xAA"
#define ICON_FA_PERSON_BOOTH "\xEF\x9D\x96"
#define ICON_FA_CALENDAR_PLUS "\xEF\x89\xB1"
#define ICON_FA_SMOG "\xEF\x9D\x9F"
#define ICON_FA_LOCATION_ARROW "\xEF\x84\xA4"
#define ICON_FA_UMBRELLA "\xEF\x83\xA9"
#define ICON_FA_QURAN "\xEF\x9A\x87"
#define ICON_FA_UNDO "\xEF\x83\xA2"
#define ICON_FA_DUMPSTER "\xEF\x9E\x93"
#define ICON_FA_FUNNEL_DOLLAR "\xEF\x99\xA2"
#define ICON_FA_INDENT "\xEF\x80\xBC"
#define ICON_FA_LANGUAGE "\xEF\x86\xAB"
#define ICON_FA_ARROW_ALT_CIRCLE_UP "\xEF\x8D\x9B"
#define ICON_FA_ROUTE "\xEF\x93\x97"
#define ICON_FA_HEADPHONES "\xEF\x80\xA5"
#define ICON_FA_TIMES "\xEF\x80\x8D"
#define ICON_FA_CLINIC_MEDICAL "\xEF\x9F\xB2"
#define ICON_FA_PLANE "\xEF\x81\xB2"
#define ICON_FA_TORII_GATE "\xEF\x9A\xA1"
#define ICON_FA_LEVEL_UP_ALT "\xEF\x8E\xBF"
#define ICON_FA_BLIND "\xEF\x8A\x9D"
#define ICON_FA_CHEESE "\xEF\x9F\xAF"
#define ICON_FA_PHONE_SQUARE "\xEF\x82\x98"
#define ICON_FA_SHOPPING_BASKET "\xEF\x8A\x91"
#define ICON_FA_ICE_CREAM "\xEF\xA0\x90"
#define ICON_FA_RING "\xEF\x9C\x8B"
#define ICON_FA_CITY "\xEF\x99\x8F"
#define ICON_FA_TEXT_WIDTH "\xEF\x80\xB5"
#define ICON_FA_RSS_SQUARE "\xEF\x85\x83"
#define ICON_FA_PAINT_BRUSH "\xEF\x87\xBC"
#define ICON_FA_BOOKMARK "\xEF\x80\xAE"
#define ICON_FA_PHOTO_VIDEO "\xEF\xA1\xBC"
#define ICON_FA_SIM_CARD "\xEF\x9F\x84"
#define ICON_FA_CLOUD_UPLOAD_ALT "\xEF\x8E\x82"
#define ICON_FA_COMPACT_DISC "\xEF\x94\x9F"
#define ICON_FA_SORT_UP "\xEF\x83\x9E"
#define ICON_FA_SIGN_OUT_ALT "\xEF\x8B\xB5"
#define ICON_FA_SIGN_IN_ALT "\xEF\x8B\xB6"
#define ICON_FA_FORWARD "\xEF\x81\x8E"
#define ICON_FA_SHARE_ALT "\xEF\x87\xA0"
#define ICON_FA_COPY "\xEF\x83\x85"
#define ICON_FA_RSS "\xEF\x82\x9E"
#define ICON_FA_PEN_FANCY "\xEF\x96\xAC"
#define ICON_FA_BIOHAZARD "\xEF\x9E\x80"
#define ICON_FA_BED "\xEF\x88\xB6"
#define ICON_FA_INFO "\xEF\x84\xA9"
#define ICON_FA_TOGGLE_OFF "\xEF\x88\x84"
#define ICON_FA_MAP_MARKER_ALT "\xEF\x8F\x85"
#define ICON_FA_TRACTOR "\xEF\x9C\xA2"
#define ICON_FA_CLOUD_DOWNLOAD_ALT "\xEF\x8E\x81"
#define ICON_FA_ID_BADGE "\xEF\x8B\x81"
#define ICON_FA_SORT_NUMERIC_DOWN_ALT "\xEF\xA2\x86"
#define ICON_FA_RULER_HORIZONTAL "\xEF\x95\x87"
#define ICON_FA_PAINT_ROLLER "\xEF\x96\xAA"
#define ICON_FA_HAT_WIZARD "\xEF\x9B\xA8"
#define ICON_FA_MAP_SIGNS "\xEF\x89\xB7"
#define ICON_FA_MICROPHONE "\xEF\x84\xB0"
#define ICON_FA_FOOTBALL_BALL "\xEF\x91\x8E"
#define ICON_FA_ALLERGIES "\xEF\x91\xA1"
#define ICON_FA_ID_CARD "\xEF\x8B\x82"
#define ICON_FA_USER_LOCK "\xEF\x94\x82"
#define ICON_FA_PLAY_CIRCLE "\xEF\x85\x84"
#define ICON_FA_REMOVE_FORMAT "\xEF\xA1\xBD"
#define ICON_FA_THERMOMETER "\xEF\x92\x91"
#define ICON_FA_REGISTERED "\xEF\x89\x9D"
#define ICON_FA_DOLLAR_SIGN "\xEF\x85\x95"
#define ICON_FA_DUNGEON "\xEF\x9B\x99"
#define ICON_FA_COMPRESS "\xEF\x81\xA6"
#define ICON_FA_SEARCH_LOCATION "\xEF\x9A\x89"
#define ICON_FA_UTENSILS "\xEF\x8B\xA7"
#define ICON_FA_BLENDER_PHONE "\xEF\x9A\xB6"
#define ICON_FA_ANGLE_RIGHT "\xEF\x84\x85"
#define ICON_FA_CHESS_QUEEN "\xEF\x91\x85"
#define ICON_FA_PAGER "\xEF\xA0\x95"
#define ICON_FA_SORT_AMOUNT_UP_ALT "\xEF\xA2\x85"
#define ICON_FA_CLIPBOARD_CHECK "\xEF\x91\xAC"
#define ICON_FA_HOURGLASS_END "\xEF\x89\x93"
#define ICON_FA_TOOTH "\xEF\x97\x89"
#define ICON_FA_BUSINESS_TIME "\xEF\x99\x8A"
#define ICON_FA_PLACE_OF_WORSHIP "\xEF\x99\xBF"
#define ICON_FA_GRIN_TONGUE_SQUINT "\xEF\x96\x8A"
#define ICON_FA_MEH_ROLLING_EYES "\xEF\x96\xA5"
#define ICON_FA_WALKING "\xEF\x95\x94"
#define ICON_FA_EDIT "\xEF\x81\x84"
#define ICON_FA_CARET_LEFT "\xEF\x83\x99"
#define ICON_FA_PAUSE "\xEF\x81\x8C"
#define ICON_FA_DICE "\xEF\x94\xA2"
#define ICON_FA_RUBLE_SIGN "\xEF\x85\x98"
#define ICON_FA_TERMINAL "\xEF\x84\xA0"
#define ICON_FA_RULER_VERTICAL "\xEF\x95\x88"
#define ICON_FA_HAND_POINTER "\xEF\x89\x9A"
#define ICON_FA_TAPE "\xEF\x93\x9B"
#define ICON_FA_SHOPPING_BAG "\xEF\x8A\x90"
#define ICON_FA_SKIING_NORDIC "\xEF\x9F\x8A"
#define ICON_FA_FIST_RAISED "\xEF\x9B\x9E"
#define ICON_FA_CUBE "\xEF\x86\xB2"
#define ICON_FA_CAPSULES "\xEF\x91\xAB"
#define ICON_FA_KIWI_BIRD "\xEF\x94\xB5"
#define ICON_FA_CHEVRON_CIRCLE_UP "\xEF\x84\xB9"
#define ICON_FA_MARS_STROKE_V "\xEF\x88\xAA"
#define ICON_FA_FILE_ARCHIVE "\xEF\x87\x86"
#define ICON_FA_JOINT "\xEF\x96\x95"
#define ICON_FA_MARS_STROKE_H "\xEF\x88\xAB"
#define ICON_FA_ADDRESS_BOOK "\xEF\x8A\xB9"
#define ICON_FA_PROCEDURES "\xEF\x92\x87"
#define ICON_FA_GEM "\xEF\x8E\xA5"
#define ICON_FA_RULER_COMBINED "\xEF\x95\x86"
#define ICON_FA_ALIGN_LEFT "\xEF\x80\xB6"
#define ICON_FA_STAR_AND_CRESCENT "\xEF\x9A\x99"
#define ICON_FA_FIGHTER_JET "\xEF\x83\xBB"
#define ICON_FA_SPACE_SHUTTLE "\xEF\x86\x97"
#define ICON_FA_MAP_PIN "\xEF\x89\xB6"
#define ICON_FA_GLOBE "\xEF\x82\xAC"
#define ICON_FA_ALIGN_CENTER "\xEF\x80\xB7"
#define ICON_FA_SORT_ALPHA_DOWN "\xEF\x85\x9D"
#define ICON_FA_PARKING "\xEF\x95\x80"
#define ICON_FA_CALENDAR "\xEF\x84\xB3"
#define ICON_FA_PALETTE "\xEF\x94\xBF"
#define ICON_FA_GLASS_MARTINI "\xEF\x80\x80"
#define ICON_FA_TIMES_CIRCLE "\xEF\x81\x97"
#define ICON_FA_EYE "\xEF\x81\xAE"
#define ICON_FA_MONUMENT "\xEF\x96\xA6"
#define ICON_FA_TRASH_RESTORE "\xEF\xA0\xA9"
#define ICON_FA_GUITAR "\xEF\x9E\xA6"
#define ICON_FA_GRIN_BEAM "\xEF\x96\x82"
#define ICON_FA_KEY "\xEF\x82\x84"
#define ICON_FA_FIRST_AID "\xEF\x91\xB9"
#define ICON_FA_UMBRELLA_BEACH "\xEF\x97\x8A"
#define ICON_FA_DRUM "\xEF\x95\xA9"
#define ICON_FA_FILE_CONTRACT "\xEF\x95\xAC"
#define ICON_FA_VOICEMAIL "\xEF\xA2\x97"
#define ICON_FA_RESTROOM "\xEF\x9E\xBD"
#define ICON_FA_UNLOCK_ALT "\xEF\x84\xBE"
#define ICON_FA_MICROPHONE_ALT_SLASH "\xEF\x94\xB9"
#define ICON_FA_USER_SECRET "\xEF\x88\x9B"
#define ICON_FA_ARROW_RIGHT "\xEF\x81\xA1"
#define ICON_FA_FILE_VIDEO "\xEF\x87\x88"
#define ICON_FA_ARROW_ALT_CIRCLE_RIGHT "\xEF\x8D\x9A"
#define ICON_FA_CALENDAR_WEEK "\xEF\x9E\x84"
#define ICON_FA_USER_GRADUATE "\xEF\x94\x81"
#define ICON_FA_HAND_MIDDLE_FINGER "\xEF\xA0\x86"
#define ICON_FA_POO "\xEF\x8B\xBE"
#define ICON_FA_LAUGH "\xEF\x96\x99"
#define ICON_FA_TABLE "\xEF\x83\x8E"
#define ICON_FA_POLL "\xEF\x9A\x81"
#define ICON_FA_CAR_ALT "\xEF\x97\x9E"
#define ICON_FA_THUMBS_UP "\xEF\x85\xA4"
#define ICON_FA_SWIMMER "\xEF\x97\x84"
#define ICON_FA_TRADEMARK "\xEF\x89\x9C"
#define ICON_FA_CLOUD_MOON_RAIN "\xEF\x9C\xBC"
#define ICON_FA_VIALS "\xEF\x92\x93"
#define ICON_FA_ERASER "\xEF\x84\xAD"
#define ICON_FA_MARS "\xEF\x88\xA2"
#define ICON_FA_HELICOPTER "\xEF\x94\xB3"
#define ICON_FA_FEATHER "\xEF\x94\xAD"
#define ICON_FA_SQUARE_FULL "\xEF\x91\x9C"
#define ICON_FA_DOLLY "\xEF\x91\xB2"
#define ICON_FA_HAND_HOLDING "\xEF\x92\xBD"
#define ICON_FA_HOURGLASS_START "\xEF\x89\x91"
#define ICON_FA_GRIN_HEARTS "\xEF\x96\x84"
#define ICON_FA_VENUS_DOUBLE "\xEF\x88\xA6"
#define ICON_FA_HASHTAG "\xEF\x8A\x92"
#define ICON_FA_FINGERPRINT "\xEF\x95\xB7"
#define ICON_FA_SEEDLING "\xEF\x93\x98"
#define ICON_FA_HAYKAL "\xEF\x99\xA6"
#define ICON_FA_TSHIRT "\xEF\x95\x93"
#define ICON_FA_PENCIL_RULER "\xEF\x96\xAE"
#define ICON_FA_HDD "\xEF\x82\xA0"
#define ICON_FA_NEWSPAPER "\xEF\x87\xAA"
#define ICON_FA_HOSPITAL_ALT "\xEF\x91\xBD"
#define ICON_FA_USER_SLASH "\xEF\x94\x86"
#define ICON_FA_FILE_WORD "\xEF\x87\x82"
#define ICON_FA_ENVELOPE_SQUARE "\xEF\x86\x99"
#define ICON_FA_GENDERLESS "\xEF\x88\xAD"
#define ICON_FA_DICE_FIVE "\xEF\x94\xA3"
#define ICON_FA_SYNAGOGUE "\xEF\x9A\x9B"
#define ICON_FA_PAW "\xEF\x86\xB0"
#define ICON_FA_HAND_HOLDING_HEART "\xEF\x92\xBE"
#define ICON_FA_CROSS "\xEF\x99\x94"
#define ICON_FA_ARCHIVE "\xEF\x86\x87"
#define ICON_FA_SOLAR_PANEL "\xEF\x96\xBA"
#define ICON_FA_INFINITY "\xEF\x94\xB4"
#define ICON_FA_ANKH "\xEF\x99\x84"
#define ICON_FA_MAP_MARKER "\xEF\x81\x81"
#define ICON_FA_CALENDAR_ALT "\xEF\x81\xB3"
#define ICON_FA_AMERICAN_SIGN_LANGUAGE_INTERPRETING "\xEF\x8A\xA3"
#define ICON_FA_BINOCULARS "\xEF\x87\xA5"
#define ICON_FA_STICKY_NOTE "\xEF\x89\x89"
#define ICON_FA_RUNNING "\xEF\x9C\x8C"
#define ICON_FA_PEN_NIB "\xEF\x96\xAD"
#define ICON_FA_MAP_MARKED "\xEF\x96\x9F"
#define ICON_FA_EXPAND "\xEF\x81\xA5"
#define ICON_FA_TRUCK_PICKUP "\xEF\x98\xBC"
#define ICON_FA_HOLLY_BERRY "\xEF\x9E\xAA"
#define ICON_FA_PRESCRIPTION_BOTTLE "\xEF\x92\x85"
#define ICON_FA_LAPTOP_CODE "\xEF\x97\xBC"
#define ICON_FA_GOLF_BALL "\xEF\x91\x90"
#define ICON_FA_SKULL_CROSSBONES "\xEF\x9C\x94"
#define ICON_FA_TAXI "\xEF\x86\xBA"
#define ICON_FA_COMMENT "\xEF\x81\xB5"
#define ICON_FA_KISS "\xEF\x96\x96"
#define ICON_FA_HIPPO "\xEF\x9B\xAD"
#define ICON_FA_ARROWS_ALT "\xEF\x82\xB2"
#define ICON_FA_UNDERLINE "\xEF\x83\x8D"
#define ICON_FA_ARROW_CIRCLE_UP "\xEF\x82\xAA"
#define ICON_FA_BASKETBALL_BALL "\xEF\x90\xB4"
#define ICON_FA_DESKTOP "\xEF\x84\x88"
#define ICON_FA_PALLET "\xEF\x92\x82"
#define ICON_FA_TOGGLE_ON "\xEF\x88\x85"
#define ICON_FA_STOPWATCH "\xEF\x8B\xB2"
#define ICON_FA_ARROW_ALT_CIRCLE_LEFT "\xEF\x8D\x99"
#define ICON_FA_GAS_PUMP "\xEF\x94\xAF"
#define ICON_FA_EXTERNAL_LINK_ALT "\xEF\x8D\x9D"
#define ICON_FA_FROWN "\xEF\x84\x99"
#define ICON_FA_RULER "\xEF\x95\x85"
#define ICON_FA_FLAG_USA "\xEF\x9D\x8D"
#define ICON_FA_GRIN "\xEF\x96\x80"
#define ICON_FA_ARROW_CIRCLE_LEFT "\xEF\x82\xA8"
#define ICON_FA_HIGHLIGHTER "\xEF\x96\x91"
#define ICON_FA_POLL_H "\xEF\x9A\x82"
#define ICON_FA_SERVER "\xEF\x88\xB3"
#define ICON_FA_BATTERY_EMPTY "\xEF\x89\x84"
#define ICON_FA_SPRAY_CAN "\xEF\x96\xBD"
#define ICON_FA_BOWLING_BALL "\xEF\x90\xB6"
#define ICON_FA_GRIP_LINES_VERTICAL "\xEF\x9E\xA5"
#define ICON_FA_GLOBE_EUROPE "\xEF\x9E\xA2"
#define ICON_FA_WINDOW_MINIMIZE "\xEF\x8B\x91"
#define ICON_FA_MARS_DOUBLE "\xEF\x88\xA7"
#define ICON_FA_PAUSE_CIRCLE "\xEF\x8A\x8B"
#define ICON_FA_HOME "\xEF\x80\x95"
#define ICON_FA_COMMENT_ALT "\xEF\x89\xBA"
#define ICON_FA_UTENSIL_SPOON "\xEF\x8B\xA5"
#define ICON_FA_APPLE_ALT "\xEF\x97\x91"
#define ICON_FA_MOON "\xEF\x86\x86"
#define ICON_FA_CANNABIS "\xEF\x95\x9F"
#define ICON_FA_LAUGH_BEAM "\xEF\x96\x9A"
#define ICON_FA_TEETH_OPEN "\xEF\x98\xAF"
#define ICON_FA_CHART_PIE "\xEF\x88\x80"
#define ICON_FA_SOCKS "\xEF\x9A\x96"
#define ICON_FA_SD_CARD "\xEF\x9F\x82"
#define ICON_FA_ARROW_CIRCLE_RIGHT "\xEF\x82\xA9"
#define ICON_FA_PASTE "\xEF\x83\xAA"
#define ICON_FA_OM "\xEF\x99\xB9"
#define ICON_FA_LUGGAGE_CART "\xEF\x96\x9D"
#define ICON_FA_INDUSTRY "\xEF\x89\xB5"
#define ICON_FA_STAMP "\xEF\x96\xBF"
#define ICON_FA_RADIATION_ALT "\xEF\x9E\xBA"
#define ICON_FA_COMPRESS_ARROWS_ALT "\xEF\x9E\x8C"
#define ICON_FA_ROAD "\xEF\x80\x98"
#define ICON_FA_IMAGE "\xEF\x80\xBE"
#define ICON_FA_BALANCE_SCALE_RIGHT "\xEF\x94\x96"
#define ICON_FA_ANGLE_DOUBLE_RIGHT "\xEF\x84\x81"
#define ICON_FA_CLOUD_MOON "\xEF\x9B\x83"
#define ICON_FA_DOOR_OPEN "\xEF\x94\xAB"
#define ICON_FA_GRIN_TONGUE_WINK "\xEF\x96\x8B"
#define ICON_FA_REPLY_ALL "\xEF\x84\xA2"
#define ICON_FA_TEMPERATURE_LOW "\xEF\x9D\xAB"
#define ICON_FA_INBOX "\xEF\x80\x9C"
#define ICON_FA_FEMALE "\xEF\x86\x82"
#define ICON_FA_SYRINGE "\xEF\x92\x8E"
#define ICON_FA_CIRCLE_NOTCH "\xEF\x87\x8E"
#define ICON_FA_ELLIPSIS_V "\xEF\x85\x82"
#define ICON_FA_SNOWPLOW "\xEF\x9F\x92"
#define ICON_FA_TABLE_TENNIS "\xEF\x91\x9D"
#define ICON_FA_LOW_VISION "\xEF\x8A\xA8"
#define ICON_FA_FILE_IMPORT "\xEF\x95\xAF"
#define ICON_FA_ITALIC "\xEF\x80\xB3"
#define ICON_FA_FILE_SIGNATURE "\xEF\x95\xB3"
#define ICON_FA_CHALKBOARD "\xEF\x94\x9B"
#define ICON_FA_GHOST "\xEF\x9B\xA2"
#define ICON_FA_TACHOMETER_ALT "\xEF\x8F\xBD"
#define ICON_FA_BUS "\xEF\x88\x87"
#define ICON_FA_ANGLE_DOWN "\xEF\x84\x87"
#define ICON_FA_HAND_ROCK "\xEF\x89\x95"
#define ICON_FA_BORDER_STYLE "\xEF\xA1\x93"
#define ICON_FA_STAR_OF_LIFE "\xEF\x98\xA1"
#define ICON_FA_PODCAST "\xEF\x8B\x8E"
#define ICON_FA_TRUCK_MOVING "\xEF\x93\x9F"
#define ICON_FA_BUG "\xEF\x86\x88"
#define ICON_FA_SHIELD_ALT "\xEF\x8F\xAD"
#define ICON_FA_FILL_DRIP "\xEF\x95\xB6"
#define ICON_FA_COMMENT_SLASH "\xEF\x92\xB3"
#define ICON_FA_SUITCASE "\xEF\x83\xB2"
#define ICON_FA_SKATING "\xEF\x9F\x85"
#define ICON_FA_TOILET "\xEF\x9F\x98"
#define ICON_FA_ENVELOPE_OPEN_TEXT "\xEF\x99\x98"
#define ICON_FA_HEART_BROKEN "\xEF\x9E\xA9"
#define ICON_FA_CARET_SQUARE_UP "\xEF\x85\x91"
#define ICON_FA_TH_LARGE "\xEF\x80\x89"
#define ICON_FA_AT "\xEF\x87\xBA"
#define ICON_FA_FILE "\xEF\x85\x9B"
#define ICON_FA_TENGE "\xEF\x9F\x97"
#define ICON_FA_FLAG_CHECKERED "\xEF\x84\x9E"
#define ICON_FA_FILM "\xEF\x80\x88"
#define ICON_FA_FILL "\xEF\x95\xB5"
#define ICON_FA_GRIN_SQUINT_TEARS "\xEF\x96\x86"
#define ICON_FA_PERCENT "\xEF\x8A\x95"
#define ICON_FA_METEOR "\xEF\x9D\x93"
#define ICON_FA_TRASH "\xEF\x87\xB8"
#define ICON_FA_FILE_AUDIO "\xEF\x87\x87"
#define ICON_FA_SATELLITE_DISH "\xEF\x9F\x80"
#define ICON_FA_POOP "\xEF\x98\x99"
#define ICON_FA_STAR "\xEF\x80\x85"
#define ICON_FA_GIFTS "\xEF\x9E\x9C"
#define ICON_FA_FIRE_ALT "\xEF\x9F\xA4"
#define ICON_FA_BUILDING "\xEF\x86\xAD"
#define ICON_FA_PRESCRIPTION_BOTTLE_ALT "\xEF\x92\x86"
#define ICON_FA_MONEY_BILL_WAVE_ALT "\xEF\x94\xBB"
#define ICON_FA_NEUTER "\xEF\x88\xAC"
#define ICON_FA_BAND_AID "\xEF\x91\xA2"
#define ICON_FA_WIFI "\xEF\x87\xAB"
#define ICON_FA_MASK "\xEF\x9B\xBA"
#define ICON_FA_CHEVRON_UP "\xEF\x81\xB7"
#define ICON_FA_HAND_SPOCK "\xEF\x89\x99"
#define ICON_FA_HAND_POINT_UP "\xEF\x82\xA6"
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
    };

    ImGuiStyle TweakedThemeThemeToStyle(const ImGuiTweakedTheme& tweaked_theme);
    void ApplyTweakedTheme(const ImGuiTweakedTheme& tweaked_theme);

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
//                       hello_imgui/hello_imgui_font.h included by hello_imgui.h                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <vector>
#include <array>

namespace HelloImGui
{
    using ImWcharPair = std::array<ImWchar, 2>;

    // @@md#Fonts
    //
    // When loading fonts, use HelloImGui::LoadFont(fontFilename, fontSize, fontLoadingParams)
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

        // the ranges of glyphs to load:
        //    - if empty, the default glyph range will be used
        //    - you can specify several ranges
        //    - intervals bounds are inclusive
        // (will be translated and stored as a static ImWChar* inside fontConfig)
        std::vector<ImWcharPair> glyphRanges = {};

        // ImGui native font config to use
        ImFontConfig fontConfig = ImFontConfig();

        // if true, the font will be loaded and then FontAwesome icons will be merged to it
        // (deprecated, use mergeToLastFont instead, and load in two steps)
        bool mergeFontAwesome = false;
        ImFontConfig fontConfigFontAwesome = ImFontConfig();
    };

    // When loading fonts, use HelloImGui::LoadFont(FontLoadingParams)
    // ===============================================================
    // instead of ImGui::GetIO().Fonts->AddFontFromFileTTF(), because it will
    // automatically adjust the font size to account for HighDPI, and will spare
    // you headaches when trying to get consistent font size across different OSes.
    // see FontLoadingParams and ImFontConfig
    ImFont* LoadFont(const std::string & fontFilename, float fontSize,
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
//See https://raw.githubusercontent.com/pthom/hello_imgui/master/src/hello_imgui/doc_src/hello_imgui_diagram.png
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
    // This is the "clearColor", visible if defaultImGuiWindowType!=ProvideFullScreenWindow.
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


namespace HelloImGui
{

/**
@@md#VoidFunction_AnyEventCallback

**VoidFunctionPointer** can hold any void(void) function.
```cpp
using VoidFunction = std::function<void(void)>
```

**AnyEventCallback** can hold any bool(void *) function.
  It is designed to handle callbacks for a specific backend.
```cpp
using AnyEventCallback = std::function<bool(void * backendEvent)>
```

**AppendCallback** can compose two callbacks. Use this when you want to set a callback and keep the (maybe) preexisting one.
@@md
**/
using VoidFunction = std::function<void(void)>;
using AnyEventCallback = std::function<bool(void * backendEvent)>;
VoidFunction AppendCallback(const VoidFunction& previousCallback, const VoidFunction& newCallback);


inline VoidFunction EmptyVoidFunction() { return {}; }
inline AnyEventCallback EmptyEventCallback() {return {}; }


// @@md#MobileCallbacks
//
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

// @@md#RunnerCallbacks
//
// RunnerCallbacks is a struct that contains the callbacks
// that are called by the application
//
struct RunnerCallbacks
{
    // --------------- GUI Callbacks -------------------

    // `ShowGui`: Fill it with a function that will add your widgets.
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


    // --------------- Startup sequence callbacks -------------------

    // `PostInit`: You can here add a function that will be called once after OpenGL
    //  and ImGui are inited, but before the backend callback are initialized.
    //  If you, for instance, want to add your own glfw callbacks,
    //  you should use this function to do so.
    VoidFunction PostInit = EmptyVoidFunction();

    // `LoadAdditionalFonts`: default=_LoadDefaultFont_WithFontAwesome*.
    //  A function that is called once, when fonts are ready to be loaded.
    //  By default, _LoadDefaultFont_WithFontAwesome_ is called,
    //  but you can copy and customize it.
    //  (LoadDefaultFont_WithFontAwesome will load fonts from assets/fonts/
    //  but reverts to the ImGui embedded font if not found)
    VoidFunction LoadAdditionalFonts =
        (VoidFunction)(ImGuiDefaultSettings::LoadDefaultFont_WithFontAwesomeIcons);

    // `SetupImGuiConfig`: default=_ImGuiDefaultSettings::SetupDefaultImGuiConfig*.
    //  If needed, change ImGui config via SetupImGuiConfig
    //  (enable docking, gamepad, etc)
    VoidFunction SetupImGuiConfig =
        (VoidFunction)(ImGuiDefaultSettings::SetupDefaultImGuiConfig);

    // `SetupImGuiStyle`: default=_ImGuiDefaultSettings::SetupDefaultImGuiConfig*.
    //  If needed, set your own style by providing your own SetupImGuiStyle callback
    VoidFunction SetupImGuiStyle =
        (VoidFunction)(ImGuiDefaultSettings::SetupDefaultImGuiStyle);

    // `RegisterTests`: A function that is called once ImGuiTestEngine is ready
    // to be filled with tests and automations definitions.
    VoidFunction RegisterTests = EmptyVoidFunction();


    // --------------- Exit sequence callbacks -------------------

    // `BeforeExit`: You can here add a function that will be called once before exiting
    //  (when OpenGL and ImGui are still inited)
    VoidFunction BeforeExit = EmptyVoidFunction();

    // `BeforeExit_PostCleanup`: You can here add a function that will be called once
    // before exiting (after OpenGL and ImGui have been stopped)
    VoidFunction BeforeExit_PostCleanup = EmptyVoidFunction();


    // --------------- Callbacks in the render loop -------------------

    // `PreNewFrame`: You can here add a function that will be called at each frame,
    //  and before the call to ImGui::NewFrame().
    //  It is a good place to dynamically add new fonts, or new dockable windows.
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
    ImGuiDir_ direction;

    // `ratio`: _float, default=0.25f_.
    //  Ratio of the initialDock size that should be used by the new dock space.
    float ratio = 0.25f;

    // `nodeFlags`: *ImGuiDockNodeFlags_ (enum)*.
    //  Flags to apply to the new dock space
    //  (enable/disable resizing, splitting, tab bar, etc.)
    ImGuiDockNodeFlags nodeFlags = ImGuiDockNodeFlags_None;

    // Constructor
    DockingSplit(const DockSpaceName& initialDock_ = "", const DockSpaceName& newDock_ = "",
                 ImGuiDir_ direction_ = ImGuiDir_Down, float ratio_ = 0.25f,
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
//                       hello_imgui/runner_params.h continued                                                  //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace HelloImGui
{

// Platform backend type (SDL, GLFW)
enum class BackendType
{
    FirstAvailable,
    Sdl,
    Glfw,
};

// @@md#IniFolderType

// IniFolderType is an enum which describle where is the base path to store
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


// @@md#FpsIdling
//
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

    // `enableIdling`: _bool, default=true_.
    //  Set this to false to disable idling
    //  (this can be changed dynamically during execution)
    bool  enableIdling = true;

    // `isIdling`: bool (dynamically updated during execution)
    //  This bool will be updated during the application execution,
    //  and will be set to true when it is idling.
    bool  isIdling = false;

    // `rememberEnableIdling`: _bool, default=true_.
    //  If true, the last value of enableIdling is restored from the settings at startup.
    bool  rememberEnableIdling = true;
};
// @@md


// @@md#RunnerParams
//
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
    // `backendType`: _enum BackendType, default=BackendType::FirstAvailable_
    // Select the wanted platform backend type between `Sdl`, `Glfw`.
    // Only useful when multiple backend are compiled and available.
    BackendType backendType = BackendType::FirstAvailable;


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


// @@md#SimpleRunnerParams
//
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
    ScreenSize windowSize = DefaultWindowSize;

    // `fpsIdle`: _float, default=9_.
    //  FPS of the application when idle (set to 0 for full speed).
    float fpsIdle = 9.f;

    // `enableIdling`: _bool, default=true_.
    //  Set this to false to disable idling at startup
    bool  enableIdling = true;

    RunnerParams ToRunnerParams() const;
};
// @@md

}  // namespace HelloImGui
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui/hello_imgui_widgets.h included by hello_imgui.h                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Some additional widgets and utilities for ImGui


namespace HelloImGui
{
    void BeginGroupColumn(); // calls ImGui::BeginGroup()
    void EndGroupColumn();   // calls ImGui::EndGroup() + ImGui::SameLine()
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       hello_imgui.h continued                                                                //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#include <cstddef>
#include <cstdint>

#ifdef HELLOIMGUI_USE_SDL
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
