from imgui_bundle import immapp
from imgui_bundle.demos_python import demo_imgui_bundle
runner_params, addons = demo_imgui_bundle.make_params()
immapp.run(runner_params=runner_params, add_ons_params=addons)
