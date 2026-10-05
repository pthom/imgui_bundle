#pragma once

// Clipboard support for Emscripten: SDL2 (a bridge to the browser's clipboard), and GLFW (the copy written at once,
// for iOS). See js_clipboard_tricks.cpp for details.

#if defined(__EMSCRIPTEN__) && (defined(HELLOIMGUI_USE_SDL2) || defined(HELLOIMGUI_USE_GLFW3))
// Install the clipboard callbacks. Call once after the ImGui context is initialized (e.g. in PostInit).
void JsClipboard_Install();
#endif

#if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)

// Inject pasted text as input characters (handles Cmd+V on Mac).
// Call each frame in PostNewFrame.
void JsClipboard_ProcessPasteRequest();

// Push text to the browser clipboard (legacy API, used by snippets.cpp).
void JsClipboard_SetClipboardText(const char* str);

#endif
