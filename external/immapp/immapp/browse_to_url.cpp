// A platform specific utility to open an url in a browser
// (especially useful with emscripten version)
// Specific per platform includes for BrowseToUrl
#if defined(__EMSCRIPTEN__)
#include <emscripten.h>
#include <cstdio> // snprintf
#elif defined(_WIN32)
#include <windows.h>
#include <shellapi.h>
#elif defined(__APPLE__)
#include <TargetConditionals.h>
#include <unistd.h>   // fork, execlp, _exit
#include <sys/wait.h> // waitpid
#elif defined(__linux__)
#include <unistd.h>
#include <sys/wait.h>
#endif


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
        {
            // fork+execlp instead of system("open <url>"):
            // system() passes the string through /bin/sh, so metacharacters in url
            // (semicolons, backticks, ...) would be interpreted as shell commands.
            // execlp passes url as a raw argv element — no shell, no parsing.
            pid_t pid = fork();
            if (pid == 0)
            {
                execlp("open", "open", url, nullptr);
                _exit(1);
            }
            else if (pid > 0)
                waitpid(pid, nullptr, 0);
        }
#elif defined(__linux__)
        {
            // Same rationale as macOS above.
            pid_t pid = fork();
            if (pid == 0)
            {
                execlp("xdg-open", "xdg-open", url, nullptr);
                _exit(1);
            }
            else if (pid > 0)
                waitpid(pid, nullptr, 0);
        }
#endif
    }
}
