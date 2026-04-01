// Clipboard support for Emscripten + SDL2.
//
// SDL2's Emscripten backend does not implement clipboard (SDL_SetClipboardText/
// SDL_GetClipboardText only read/write an internal C buffer, never touching the
// browser clipboard). With GLFW (pongasoft/emscripten-glfw), clipboard already
// works via its own event listeners, so this code is SDL2-only.
//
// On Mac, SDL2/Emscripten doesn't forward the Meta (Cmd) key to ImGui properly.
// We detect Cmd+C/X/V/A in a JS keydown listener and translate them to Ctrl+key
// for ImGui via AddKeyEvent (called in PreNewFrame so ImGui sees them in the
// current frame's NewFrame).
//
// For paste from external (browser clipboard), we listen for the browser 'paste'
// event and update Module._clipboardText. ImGui reads it via GetClipboardText.

#include "imgui.h"
#include "js_clipboard_tricks.h"

#if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)

#include <emscripten.h>
#include <string>

static std::string gClipboardBuffer;

static const char* JsClipboard_GetClipboardText(ImGuiContext*)
{
    char* jsText = (char*)EM_ASM_PTR({
        if (!Module._clipboardText) return 0;
        var text = Module._clipboardText;
        var len = lengthBytesUTF8(text) + 1;
        var buf = _malloc(len);
        stringToUTF8(text, buf, len);
        return buf;
    });
    if (jsText) {
        gClipboardBuffer = jsText;
        free(jsText);
    }
    return gClipboardBuffer.c_str();
}

static void JsClipboard_SetClipboardTextImpl(const char* text)
{
    gClipboardBuffer = text ? text : "";
    EM_ASM({
        var str = UTF8ToString($0);
        Module._clipboardText = str;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(str).catch(function(e) {});
        }
    }, text);
}

static void JsClipboard_SetClipboardTextFn(ImGuiContext*, const char* text)
{
    JsClipboard_SetClipboardTextImpl(text);
}


void JsClipboard_Install()
{
    EM_ASM({
        Module._clipboardText = '';
        Module._clipboardPasteRequest = '';

        // Paste: browser clipboard -> Module._clipboardText + flag for injection
        document.addEventListener('paste', function(event) {
            var text = event.clipboardData.getData('text/plain');
            if (text) {
                Module._clipboardText = text;
                Module._clipboardPasteRequest = text;
            }
        });
    });

    auto& platformIO = ImGui::GetPlatformIO();
    platformIO.Platform_GetClipboardTextFn = JsClipboard_GetClipboardText;
    platformIO.Platform_SetClipboardTextFn = JsClipboard_SetClipboardTextFn;
}


// Called each frame. Injects pasted text as input characters.
// This handles Cmd+V on Mac where the key event may not reach ImGui.
void JsClipboard_ProcessPasteRequest()
{
    char* pastedText = (char*)EM_ASM_PTR({
        if (!Module._clipboardPasteRequest || Module._clipboardPasteRequest.length === 0)
            return 0;
        var text = Module._clipboardPasteRequest;
        Module._clipboardPasteRequest = '';
        var len = lengthBytesUTF8(text) + 1;
        var buf = _malloc(len);
        stringToUTF8(text, buf, len);
        return buf;
    });
    if (pastedText) {
        ImGui::GetIO().AddInputCharactersUTF8(pastedText);
        free(pastedText);
    }
}


void JsClipboard_SetClipboardText(const char* str)
{
    JsClipboard_SetClipboardTextImpl(str);
}

#endif // defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)
