#include <pybind11/pybind11.h>

#include "imgui/backends/imgui_impl_glfw.h"
#include "imgui/backends/imgui_impl_opengl3.h"
namespace py = pybind11;


struct GLFWmonitor;
struct GLFWwindow;
struct GLFWcursor;

// Note: all this code is generated *manually*

void py_init_module_imgui_backends(py::module& m)
{
    m.def("open_gl3_init",
        ImGui_ImplOpenGL3_Init, py::arg("glsl_version") = py::none());

    m.def("open_gl3_shutdown",
        ImGui_ImplOpenGL3_Shutdown);

    m.def("open_gl3_new_frame",
        ImGui_ImplOpenGL3_NewFrame);

    m.def("open_gl3_render_draw_data",
        ImGui_ImplOpenGL3_RenderDrawData, py::arg("draw_data"));

    m.def("open_gl3_create_fonts_texture",
        ImGui_ImplOpenGL3_CreateFontsTexture);

    m.def("open_gl3_destroy_fonts_texture",
        ImGui_ImplOpenGL3_DestroyFontsTexture);

    m.def("open_gl3_create_device_objects",
        ImGui_ImplOpenGL3_CreateDeviceObjects);

    m.def("open_gl3_destroy_device_objects",
        ImGui_ImplOpenGL3_DestroyDeviceObjects);
    ////////////////////    </generated_from:imgui_impl_opengl3.h>    ////////////////////


    ////////////////////    <generated_from:imgui_impl_glfw.h>    ////////////////////
    m.def("glfw_init_for_open_gl",
        [](size_t window_address, bool install_callbacks) {
            return ImGui_ImplGlfw_InitForOpenGL((GLFWwindow*)window_address, install_callbacks);
    }, py::arg("window_address"), py::arg("install_callbacks"));

    m.def("glfw_init_for_vulkan",
          [](size_t window_address, bool install_callbacks) {
              return ImGui_ImplGlfw_InitForVulkan((GLFWwindow*)window_address, install_callbacks);
          }, py::arg("window_address"), py::arg("install_callbacks"));

    m.def("glfw_init_for_other",
          [](size_t window_address, bool install_callbacks) {
              return ImGui_ImplGlfw_InitForOther((GLFWwindow*)window_address, install_callbacks);
          }, py::arg("window_address"), py::arg("install_callbacks"));

    m.def("glfw_shutdown",
        ImGui_ImplGlfw_Shutdown);

    m.def("glfw_new_frame",
        ImGui_ImplGlfw_NewFrame);

    m.def("glfw_install_callbacks",
          [](size_t window_address) {
              return ImGui_ImplGlfw_InstallCallbacks((GLFWwindow*)window_address);
          }, py::arg("window_address"));

    m.def("glfw_restore_callbacks",
          [](size_t window_address) {
              return ImGui_ImplGlfw_RestoreCallbacks((GLFWwindow*)window_address);
          }, py::arg("window_address"));

    m.def("glfw_restore_callbacks",
          [](size_t window_address, int focused) {
              return ImGui_ImplGlfw_WindowFocusCallback((GLFWwindow*)window_address, focused);
          }, py::arg("window_address"), py::arg("focused"));

    m.def("glfw_cursor_enter_callback",
          [](size_t window_address, int entered) {
              return ImGui_ImplGlfw_CursorEnterCallback((GLFWwindow*)window_address, entered);
          }, py::arg("window_address"), py::arg("entered"));

    m.def("glfw_cursor_pos_callback",
          [](size_t window_address, double x, double y) {
              return ImGui_ImplGlfw_CursorPosCallback((GLFWwindow*)window_address, x, y);
          }, py::arg("window_address"), py::arg("x"), py::arg("y"));

    m.def("glfw_mouse_button_callback",
          [](size_t window_address, int button, int action, int mods) {
              return ImGui_ImplGlfw_MouseButtonCallback((GLFWwindow*)window_address, button, action, mods);
          }, py::arg("window_address"), py::arg("button"), py::arg("action"), py::arg("mods"));

    m.def("glfw_scroll_callback",
          [](size_t window_address, double xoffset, double yoffset) {
              return ImGui_ImplGlfw_ScrollCallback((GLFWwindow*)window_address, xoffset, yoffset);
          }, py::arg("window_address"), py::arg("xoffset"), py::arg("yoffset"));

    m.def("glfw_key_callback",
          [](size_t window_address, int key, int scancode, int action, int mods) {
              return ImGui_ImplGlfw_KeyCallback((GLFWwindow*)window_address, key, scancode, action, mods);
          }, py::arg("window_address"), py::arg("key"), py::arg("scancode"), py::arg("action"), py::arg("mods"));

    m.def("glfw_char_callback",
          [](size_t window_address,  unsigned int c) {
              return ImGui_ImplGlfw_CharCallback((GLFWwindow*)window_address, c);
          }, py::arg("window_address"), py::arg("c"));

    m.def("glfw_monitor_callback",
          [](size_t monitor_address,  int c) {
              return ImGui_ImplGlfw_MonitorCallback((GLFWmonitor*)monitor_address, c);
          }, py::arg("window_address"), py::arg("c"));
}
