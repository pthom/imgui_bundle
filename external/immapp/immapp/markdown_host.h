#pragma once
// The markdown host services that only ImmApp can provide (code blocks rendered with
// ImGuiColorTextEdit). ImmApp::Run installs them; call this yourself when you initialize
// markdown without the runner (see sandbox_md_without_hello_imgui.cpp).
namespace ImmApp
{
    void InstallMarkdownHostServices();
}
