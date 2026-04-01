#pragma once

// Clipboard support for Emscripten + SDL2.
// See js_clipboard_tricks.cpp for details.

#if defined(__EMSCRIPTEN__) && defined(HELLOIMGUI_USE_SDL2)

// Install JS event listeners and override ImGui's clipboard callbacks.
// Call once after ImGui context is initialized (e.g. in PostInit callback).
void JsClipboard_Install();

// Call each frame (e.g. in PostNewFrame) to handle paste events that
// didn't reach ImGui via key events (Cmd+V on Mac).
void JsClipboard_ProcessPasteRequest();

// Push text to the browser clipboard (legacy API, used by snippets.cpp).
void JsClipboard_SetClipboardText(const char* str);

#endif
