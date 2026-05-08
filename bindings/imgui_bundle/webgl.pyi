"""Pyodide-only WebGL bridge for imgui_bundle.

Available only in Pyodide builds (compile-time gated by
``IMGUI_BUNDLE_WITH_WEBGL``). On desktop, importing this submodule raises
``ImportError``; gate with ``imgui_bundle.has_submodule("webgl")``.

Typical usage:

    import imgui_bundle
    if imgui_bundle.has_submodule("webgl"):
        from imgui_bundle import webgl
        from js import document
        gl = document.getElementById("canvas").getContext("webgl2")

        tex = gl.createTexture()
        # ... populate the texture via WebGL ...
        tex_id = webgl.register_texture(tex)
        # ... in the GUI loop ...
        imgui.image(imgui.ImTextureRef(tex_id), ImVec2(256, 256))
        # ... at shutdown ...
        webgl.unregister_texture(tex_id)
        gl.deleteTexture(tex)

See ``_plans/pyodide_webgl_bridge__spec.md`` for the design rationale.
"""

def register_texture(jstexture: object) -> int:
    """Register a JS WebGLTexture with imgui_bundle's renderer.

    Returns an ``ImTextureID`` (int) usable with ``imgui.image()`` via
    ``imgui.ImTextureRef``. The integer is stable for the lifetime of the
    registration; the underlying JS texture is referenced (not copied) by
    imgui_bundle's ``GL.textures`` table.

    The caller still owns the JS texture and is responsible for eventually
    calling ``gl.deleteTexture()`` on it. Call ``unregister_texture(tex_id)``
    first.
    """
    ...

def unregister_texture(tex_id: int) -> None:
    """Release the slot in imgui_bundle's ``GL.textures`` for ``tex_id``.

    Does NOT call ``gl.deleteTexture()`` on the underlying JS texture.
    After this call, the integer ID is invalid and must not be passed to
    ``imgui.image()``.
    """
    ...
