#include "imgui_bundle/imgui_bundle.h"
#include "immvision/immvision.h"
#include <opencv2/highgui.hpp>

int main()
{
    cv::Mat house = cv::imread("resources/house.jpg");
    cv::Mat tennis = cv::imread("resources/tennis.jpg");

    auto gui = [&](){
        int w = 200;
        ImmVision::ImageDisplay("m", house, cv::Size(w, 0));
        ImGui::PushID(1);
        ImmVision::ImageDisplay("m", tennis, cv::Size(w, 0));
        ImGui::PopID();
    };

    ImGuiBundle::Run(gui);
}