#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include <opencv2/imgcodecs.hpp>

int main()
{
    cv::Mat house = cv::imread("assets/images/house.jpg");
    cv::Mat tennis = cv::imread("assets/images/tennis.jpg");

    auto gui = [&](){
        int w = 200;
        ImmVision::ImageDisplay("m", house, cv::Size(w, 0));
        ImGui::PushID(1);
        ImmVision::ImageDisplay("m", tennis, cv::Size(w, 0));
        ImGui::PopID();
    };

    ImmApp::Run(gui);
}