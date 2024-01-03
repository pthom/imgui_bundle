#include <opencv2/imgcodecs.hpp>
#include "immvision/immvision.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <string>


void FillInspector()
{
    std::vector<std::string> imagefiles = { "dmla.jpg", "house.jpg", "tennis.jpg", "world.png"};
    for (auto imageFile: imagefiles)
    {
        cv::Mat img = cv::imread(DemosAssetsFolder() + "/images/" + imageFile);
        ImmVision::Inspector_AddImage(img, imageFile);
    }
}


void demo_immvision_inspector()
{
    static bool inited = false;
    if (!inited)
    {
        FillInspector();
        inited = true;
    }
    ImGuiMd::RenderUnindented("Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images.");
    ImmVision::Inspector_Show();
}
