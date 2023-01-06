#include "imgui.h"
#include "js_clipboard_tricks.h"
#ifdef __EMSCRIPTEN__
#include <emscripten.h>

// The clipboard handling features take inspiration from sokol
// https://github.com/floooh/sokol


///////////////////////////////////////////////////////////////////////////////
// Export clipboard to browser
///////////////////////////////////////////////////////////////////////////////

#ifdef __cplusplus
extern "C"
{
#endif


EM_JS(void, sapp_js_write_clipboard, (const char* c_str), {
    var str = UTF8ToString(c_str);
    var ta = document.createElement('textarea');
    ta.setAttribute('autocomplete', 'off');
    ta.setAttribute('autocorrect', 'off');
    ta.setAttribute('autocapitalize', 'off');
    ta.setAttribute('spellcheck', 'false');
    ta.style.left = -100 + 'px';
    ta.style.top = -100 + 'px';
    ta.style.height = 1;
    ta.style.width = 1;
    ta.value = str;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    //console.log("Set clipboard to " + str);
});

#ifdef __cplusplus
}
#endif

void JsClipboard_SetClipboardText(const char* str)
{
    sapp_js_write_clipboard(str);
}


///////////////////////////////////////////////////////////////////////////////
// Import clipboard from browser (broken, needs repair)
///////////////////////////////////////////////////////////////////////////////

#ifdef IMGUIBUNDLE_CLIPBOARD_IMPORT_FROM_BROWSER

    EM_JS(void, sapp_add_js_hook_clipboard, (void), {
        // See also https://whatwebcando.today/clipboard.html
        // for the new async api with user permissions dialog
        Module.sokol_paste = function(event) {
            // console.log("Got paste event ");
            var pasted_str = event.clipboardData.getData('text');
            ccall('_sapp_emsc_onpaste', 'void', ['string'], [pasted_str]);
        };
        // console.log("sapp_add_js_hook_clipboard 4");
        window.addEventListener('paste', Module.sokol_paste);
    });

    EM_JS(void, sapp_remove_js_hook_clipboard, (void), {
        window.removeEventListener('paste', Module.sokol_paste);
    });

    void EMSCRIPTEN_KEEPALIVE _sapp_emsc_onpaste(const char *str)
    {
        // std::cout << "_sapp_emsc_onpaste " << str << std::endl;
        ImGui::SetClipboardText(str);
    }


    void JsClipboard_AddJsHook()
    {
        sapp_add_js_hook_clipboard();
    }
#endif // IMGUIBUNDLE_CLIPBOARD_IMPORT_FROM_BROWSER

#endif // __EMSCRIPTEN__
