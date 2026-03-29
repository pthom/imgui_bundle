"""Launch the full demo for ImGui Bundle.

Also available at
https://traineq.org/ImGuiBundle/emscripten/bin/demo_imgui_bundle.html

There are *lots* of demos,
the code source of each demo is available.
"""
from imgui_bundle import immapp
from imgui_bundle.demos_python import demo_imgui_bundle
runner_params, addons = demo_imgui_bundle.make_params()
immapp.run(runner_params=runner_params, add_ons_params=addons)
