#include "immapp/immapp.h"
#include "immvision/immvision.h"
#include <opencv2/imgcodecs.hpp>
#include "demo_utils/demo_utils.h"


void gui()
{
    static bool inited = false;
    static cv::Mat bear, tennis;
    static ImmVision::ImageParams params;

    cv::Size imageDisplaySize(0, (int)ImmApp::EmSize(20.f));

    if (!inited)
    {
        std::string assetsDir = "assets/images/";
        bear = cv::imread(assetsDir + "bear_transparent.png", cv::IMREAD_UNCHANGED);
        params.ImageDisplaySize = imageDisplaySize;
        tennis = cv::imread(assetsDir + "tennis.jpg");
        inited = true;
    }

    RenderMdUnindented("ImmVision::ImageDisplay() will simply display an image");
    ImmVision::ImageDisplay("Tennis", tennis, imageDisplaySize);

    RenderMdUnindented(R"(
        immvision.image() will display an image, while providing lots of visualization options.<br>
        Open the options panel by clicking on the settings button at the bottom right corner of the image)");
    ImmVision::Image("Bear", bear, &params);
}


int main()
{
    HelloImGui::SimpleRunnerParams runnerParams;
    runnerParams.guiFunction = gui; runnerParams.windowSize = {1000, 800};

    ImmApp::AddOnsParams addOnsParams; addOnsParams.withMarkdown = true;

    ImmApp::Run(runnerParams, addOnsParams);
}
