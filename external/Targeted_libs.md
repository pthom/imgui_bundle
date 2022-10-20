# Libs considered for inclusion in imgui-bundle

(Extract from https://github.com/ocornut/imgui/wiki/Useful-Extensions#text-editors)

### DONE: Text editor
ImGuiColorTextEdit: Colorizing text editor for Dear ImGui (2017-2019)
github/BalazsJako/ImGuiColorTextEdit (no commits since 2019)
-> use https://github.com/pthom/ImGuiColorTextEdit / branch cursor_pos_page

### DONE: Knobs
https://github.com/altschuler/imgui-knobs

### DONE: File browser
https://github.com/dfranx/ImFileDialog
    
#### DONE: Node editor 
https://github.com/thedmd/imgui-node-editor

### Done Spinner
https://github.com/dalerank/imspinner/blob/master/imspinner.h

## immvision
https://github.com/pthom/immvision

## texture inspector ?
https://github.com/andyborrell/imgui_tex_inspect 

### Not compatible: ImGuizmo
https://github/CedricGuillemet/ImGuizmo
API is incompatible. For example, this function does not show the size of the float array inputs.
    IMGUI_API void DecomposeMatrixToComponents(const float* matrix, float* translation, float* rotation, float* scale);

