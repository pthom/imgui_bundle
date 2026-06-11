// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
//
// imgui_bundle.webgl: Pyodide-only bridge for displaying Python-created
// WebGL textures inside ImGui windows via imgui.image().
//
// Architecture (see _plans/pyodide_webgl_bridge__spec.md for the full story):
//
//   - Python-created `WebGLTexture`s are JS objects, but ImGui's renderer
//     identifies textures by integer IDs that index emscripten's
//     `GL.textures[]` table inside the wheel's wasm runtime.
//   - This file installs two JS helpers on `globalThis` (via EM_ASM, run
//     once at submodule init) that mutate that table from inside the wheel.
//   - The Python-facing nanobind functions `register_texture` /
//     `unregister_texture` call those JS helpers via Pyodide's `js`
//     interop module. We could call into emscripten more directly, but
//     this path is the simplest and the JS-hop cost is negligible for
//     one-time registration.
//
// Why EM_ASM and not EM_JS:
//   Pyodide builds the wheel as a SIDE_MODULE. EM_JS produces an external
//   symbol that fails to link in that mode. EM_ASM inlines the JS at the
//   call site without creating a separate symbol. Same constraint that
//   imgui_impl_sdl2.cpp already documents (see lines 537-540 there).

#include <nanobind/nanobind.h>
#include <emscripten.h>

namespace nb = nanobind;


namespace
{
    // Install once, at submodule init. Idempotent: re-running just
    // overwrites the global properties with identical functions.
    void install_webgl_bridge()
    {
        EM_ASM({
            globalThis._imgui_bundle_register_webgl_texture = function(tex) {
                var id = GL.getNewId(GL.textures);
                GL.textures[id] = tex;
                return id;
            };
            globalThis._imgui_bundle_unregister_webgl_texture = function(id) {
                delete GL.textures[id];
            };
        });
    }
}


void py_init_module_webgl(nb::module_& m)
{
    m.doc() =
        "Pyodide-only WebGL bridge for imgui_bundle.\n"
        "\n"
        "Lets Python-created WebGL2 textures be displayed inside ImGui\n"
        "windows via imgui.image(). See _plans/pyodide_webgl_bridge__spec.md.";

    install_webgl_bridge();

    m.def("register_texture",
        [](nb::object jstexture) -> int {
            nb::module_ js_mod = nb::module_::import_("js");
            nb::object fn = js_mod.attr("_imgui_bundle_register_webgl_texture");
            return nb::cast<int>(fn(jstexture));
        },
        nb::arg("jstexture"),
        "Register a JS WebGLTexture with imgui_bundle's renderer.\n"
        "\n"
        "Returns an ImTextureID (int) usable with imgui.image() via\n"
        "ImTextureRef. The integer is stable for the lifetime of the\n"
        "registration; the underlying JS texture is referenced (not copied)\n"
        "by imgui_bundle's GL.textures table.\n"
        "\n"
        "The caller still owns the JS texture and is responsible for\n"
        "eventually calling gl.deleteTexture() on it. Call\n"
        "unregister_texture(tex_id) first."
    );

    m.def("unregister_texture",
        [](int tex_id) {
            nb::module_ js_mod = nb::module_::import_("js");
            nb::object fn = js_mod.attr("_imgui_bundle_unregister_webgl_texture");
            fn(tex_id);
        },
        nb::arg("tex_id"),
        "Release the slot in imgui_bundle's GL.textures for tex_id.\n"
        "\n"
        "Does NOT call gl.deleteTexture() on the underlying JS texture.\n"
        "After this call, the integer ID is invalid and must not be passed\n"
        "to imgui.image()."
    );
}
