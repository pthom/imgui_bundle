// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
#include <nanobind/nanobind.h>

#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "imgui_impl_opengl2.h"

namespace nb = nanobind;


struct GLFWmonitor;
struct GLFWwindow;
struct GLFWcursor;

// Note: all this code is generated *manually*

void py_init_module_imgui_backends(nb::module_& m)
{
    //
    // <bindings for imgui_impl_opengl3.h
    //
    m.def("opengl3_init",
        ImGui_ImplOpenGL3_Init, nb::arg("glsl_version"));

    m.def("opengl3_shutdown",
        ImGui_ImplOpenGL3_Shutdown);

    m.def("opengl3_new_frame",
        ImGui_ImplOpenGL3_NewFrame);

    m.def("opengl3_render_draw_data",
        ImGui_ImplOpenGL3_RenderDrawData, nb::arg("draw_data"));

    m.def("opengl3_update_texture",
        ImGui_ImplOpenGL3_UpdateTexture);

    m.def("opengl3_create_device_objects",
        ImGui_ImplOpenGL3_CreateDeviceObjects);

    m.def("opengl3_destroy_device_objects",
        ImGui_ImplOpenGL3_DestroyDeviceObjects);


    //
    // <bindings for imgui_impl_opengl2.h
    //
    m.def("opengl2_init",
          ImGui_ImplOpenGL2_Init);

    m.def("opengl2_shutdown",
          ImGui_ImplOpenGL2_Shutdown);

    m.def("opengl2_new_frame",
          ImGui_ImplOpenGL2_NewFrame);

    m.def("opengl2_render_draw_data",
          ImGui_ImplOpenGL2_RenderDrawData, nb::arg("draw_data"));

    m.def("opengl2_update_texture",
          ImGui_ImplOpenGL2_UpdateTexture);

    m.def("opengl2_create_device_objects",
          ImGui_ImplOpenGL2_CreateDeviceObjects);

    m.def("opengl2_destroy_device_objects",
          ImGui_ImplOpenGL2_DestroyDeviceObjects);


    //
    // <bindings for imgui_impl_glfw.h
    //
#ifdef HELLOIMGUI_USE_GLFW3
    auto glfw_init_for_opengl = [](size_t window_address, bool install_callbacks) {
        return ImGui_ImplGlfw_InitForOpenGL((GLFWwindow*)window_address, install_callbacks);
    };
    m.def("glfw_init_for_opengl", glfw_init_for_opengl, nb::arg("window_address"), nb::arg("install_callbacks"));
    m.def("glfw_init_for_open_gl", glfw_init_for_opengl, nb::arg("window_address"), nb::arg("install_callbacks")); // legacy synonym

    m.def("glfw_init_for_vulkan",
          [](size_t window_address, bool install_callbacks) {
              return ImGui_ImplGlfw_InitForVulkan((GLFWwindow*)window_address, install_callbacks);
          }, nb::arg("window_address"), nb::arg("install_callbacks"));

    m.def("glfw_init_for_other",
          [](size_t window_address, bool install_callbacks) {
              return ImGui_ImplGlfw_InitForOther((GLFWwindow*)window_address, install_callbacks);
          }, nb::arg("window_address"), nb::arg("install_callbacks"));

    m.def("glfw_shutdown",
        ImGui_ImplGlfw_Shutdown);

    m.def("glfw_new_frame",
        ImGui_ImplGlfw_NewFrame);

    m.def("glfw_install_callbacks",
          [](size_t window_address) {
              return ImGui_ImplGlfw_InstallCallbacks((GLFWwindow*)window_address);
          }, nb::arg("window_address"));

    m.def("glfw_restore_callbacks",
          [](size_t window_address) {
              return ImGui_ImplGlfw_RestoreCallbacks((GLFWwindow*)window_address);
          }, nb::arg("window_address"));

    m.def("glfw_window_focus_callback",
          [](size_t window_address, int focused) {
              return ImGui_ImplGlfw_WindowFocusCallback((GLFWwindow*)window_address, focused);
          }, nb::arg("window_address"), nb::arg("focused"));

    m.def("glfw_cursor_enter_callback",
          [](size_t window_address, int entered) {
              return ImGui_ImplGlfw_CursorEnterCallback((GLFWwindow*)window_address, entered);
          }, nb::arg("window_address"), nb::arg("entered"));

    m.def("glfw_cursor_pos_callback",
          [](size_t window_address, double x, double y) {
              return ImGui_ImplGlfw_CursorPosCallback((GLFWwindow*)window_address, x, y);
          }, nb::arg("window_address"), nb::arg("x"), nb::arg("y"));

    m.def("glfw_mouse_button_callback",
          [](size_t window_address, int button, int action, int mods) {
              return ImGui_ImplGlfw_MouseButtonCallback((GLFWwindow*)window_address, button, action, mods);
          }, nb::arg("window_address"), nb::arg("button"), nb::arg("action"), nb::arg("mods"));

    m.def("glfw_scroll_callback",
          [](size_t window_address, double xoffset, double yoffset) {
              return ImGui_ImplGlfw_ScrollCallback((GLFWwindow*)window_address, xoffset, yoffset);
          }, nb::arg("window_address"), nb::arg("xoffset"), nb::arg("yoffset"));

    m.def("glfw_key_callback",
          [](size_t window_address, int key, int scancode, int action, int mods) {
              return ImGui_ImplGlfw_KeyCallback((GLFWwindow*)window_address, key, scancode, action, mods);
          }, nb::arg("window_address"), nb::arg("key"), nb::arg("scancode"), nb::arg("action"), nb::arg("mods"));

    m.def("glfw_char_callback",
          [](size_t window_address,  unsigned int c) {
              return ImGui_ImplGlfw_CharCallback((GLFWwindow*)window_address, c);
          }, nb::arg("window_address"), nb::arg("c"));

    m.def("glfw_monitor_callback",
          [](size_t monitor_address,  int c) {
              return ImGui_ImplGlfw_MonitorCallback((GLFWmonitor*)monitor_address, c);
          }, nb::arg("window_address"), nb::arg("c"));
#endif // HELLOIMGUI_USE_GLFW3
}
