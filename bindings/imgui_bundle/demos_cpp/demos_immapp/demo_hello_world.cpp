#include "immapp/immapp.h"
#include "imgui.h"
int main() { ImmApp::Run([] { ImGui::Text("Start your app in 3 lines!"); }); }
