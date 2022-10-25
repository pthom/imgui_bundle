* Q: Editable mode does not work
  A: You should upgrade pip: `pip install -U pip`

* High DPI support: How to enlarge widgets
  Change `ImGui::GetIO().FontGlobalScale` (C++), `imgui.get_io().font_global_scale`

* IDE support with Visual Studio Code / Visual studio does autocomplete my code (i.e. it does not find the stubs):
  It may take some time for Visual Studio code to find the stubs. You can try to change the setting "python.languageServer"
  to "default", and then change it back to "pylance". This might speed up the process a bit.

