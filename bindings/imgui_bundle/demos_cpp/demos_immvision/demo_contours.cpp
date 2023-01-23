// Adaptation of https://docs.opencv.org/4.x/df/d0d/tutorial_find_contours.html

#include "imgui.h"
#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include "demo_utils/api_demos.h"

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>


struct BlurData
{
    cv::Mat src_gray;
    cv::Mat contours;
    int thresh = 100;

    BlurData(const std::string& imageFile)
    {
        auto& self = *this;
        cv::Mat img = cv::imread(imageFile);
        cv::resize(img, img, cv::Size(), 0.5, 0.5);
        cv::cvtColor(img, self.src_gray, cv::COLOR_BGR2GRAY);
        self.update_contours();
    }

    void update_contours()
    {
        auto& self = *this;
        cv::RNG rng = cv::RNG(12345);
        cv::Mat canny_output;
        Canny(self.src_gray, canny_output, self.thresh, self.thresh * 2 );
        std::vector<std::vector<cv::Point> > contours;
        std::vector<cv::Vec4i> hierarchy;
        findContours( canny_output, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_SIMPLE );
        self.contours = cv::Mat::zeros(canny_output.size(), CV_8UC3 );
        for( size_t i = 0; i< contours.size(); i++ )
        {
            cv::Scalar color = cv::Scalar(rng.uniform(0, 256), rng.uniform(0,256), rng.uniform(0,256) );
            cv::drawContours(self.contours, contours, (int)i, color, 2, cv::LINE_8, hierarchy, 0 );
        }

    }
};


void gui_blur(BlurData& blur_data)
{
    const int min_thresh = 20, max_tresh = 500;
    cv::Size imageDisplaySize(400, 0);
    bool changed = ImGui::SliderInt("Canny thresh", &blur_data.thresh, min_thresh, max_tresh);
    if (changed)
        blur_data.update_contours();

    ImmVision::ImageDisplay("img", blur_data.src_gray, imageDisplaySize);
    ImGui::SameLine();
    ImmVision::ImageDisplay("contours", blur_data.contours, imageDisplaySize, changed);
};


void demo_contours()
{
    static BlurData blur_data(DemosAssetsFolder() + "/images/house.jpg");
    gui_blur(blur_data);
}


#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char**)
{
    ImmApp::Run(demo_contours, "blur", true);
    //ImmApp::Run(demo_contours, "blur", false, false, {800, 600});
    return 0;
}
#endif