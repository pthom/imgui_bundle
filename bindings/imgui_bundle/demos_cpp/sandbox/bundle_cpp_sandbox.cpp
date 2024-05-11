#include "hello_imgui/hello_imgui.h"
#include "imgui.h"
#include "imgui_internal.h"
#include "immvision/immvision.h"
#include <opencv2/opencv.hpp>


void Gui2()
{
    static ImVec2 vecSize(400, 200);
    static cv::Mat image = cv::imread(
        "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/fiatlight/src/fiatlight_assets/images/house.jpg");

    auto fn_show_imgui_fig = []() {
        cv::Size cvSize((int) vecSize.x, (int) vecSize.y);
        ImmVision::ImageDisplay("##sss", image, cvSize);
    };

    vecSize = HelloImGui::WidgetWithResizeHandle("fig", fn_show_imgui_fig);
}

int main()
{
    HelloImGui::RunnerParams runnerParams;
    runnerParams.callbacks.ShowGui = Gui2;
    HelloImGui::Run(runnerParams);
    return 0;
}
