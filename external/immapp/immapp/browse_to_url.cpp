// A platform specific utility to open an url in a browser
// (especially useful with emscripten version)
// Specific per platform includes for BrowseToUrl
#if defined(__EMSCRIPTEN__)
#include <emscripten.h>
#elif defined(_WIN32)
#include <windows.h>
#include <shellapi.h>
#elif defined(__APPLE__)
#include <TargetConditionals.h>
#endif

#include <cstdlib>
#include <cstdio>


namespace ImmApp
{
    void BrowseToUrl(const char *url)
    {
#if defined(__EMSCRIPTEN__)
        char js_command[1024];
        snprintf(js_command, 1024, "window.open(\"%s\");", url);
        emscripten_run_script(js_command);
#elif defined(_WIN32)
        ShellExecuteA( NULL, "open", url, NULL, NULL, SW_SHOWNORMAL );
#elif TARGET_OS_IPHONE
        // Nothing on iOS
#elif TARGET_OS_OSX
        char cmd[1024];
        snprintf(cmd, 1024, "open %s", url);
        system(cmd);
#elif defined(__linux__)
        char cmd[1024];
        snprintf(cmd, 1024, "xdg-open %s", url);
        int r = system(cmd);
        (void) r;
#endif
    }
}
