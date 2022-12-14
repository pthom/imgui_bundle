#include <opencv2/imgcodecs.hpp>
#include "immvision/immvision.h"
#include "immapp/immapp.h"
#include "demo_utils.h"
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
    RenderMdUnindented("Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images.");
    ImmVision::Inspector_Show();
}


int main()
{
    ImmApp::RunWithMarkdown(gui, "inspector", false, false, {1000, 800});
}
