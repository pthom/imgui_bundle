#include <opencv2/imgcodecs.hpp>
#include "immvision/immvision.h"
#include "immapp/immapp.h"
#include "hello_imgui/hello_imgui.h"
#include <vector>
#include <string>


void FillInspector()
{
    std::vector<std::string> imagefiles = { "dmla.jpg", "house.jpg", "tennis.jpg", "world.jpg"};
    for (auto imageFile: imagefiles)
    {
        cv::Mat img = cv::imread(std::string("assets/images/") + imageFile);
        ImmVision::Inspector_AddImage(img, imageFile);
    }
}


void gui()
{
    static bool inited = false;
    if (!inited)
    {
        FillInspector();
        inited = true;
    }

    ImmVision::Inspector_Show();
}


int main()
{
    ImmApp::Run(gui, "inspector", false, false, {1000, 800});
}
