#include "immvision/immvision.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <string>

// Adds many other images to the inspector (test suite with various depth & types)
void ImmVisionMakeTestSuite();


// Add two images to the inspector at startup
void FillInspector()
{
    std::vector<std::string> imagefiles = { "house.jpg", "tennis.jpg"};
    for (auto imageFile: imagefiles)
    {
        ImmVision::ImageBuffer img = ImmVision::ImRead(DemosAssetsFolder() + "/images/" + imageFile);
        ImmVision::Inspector_AddImage(img, imageFile);
    }
}


void demo_immvision_inspector()
{
    static bool inited = false;
    if (!inited)
    {
        ImmVision::UseRgbColorOrder();
        FillInspector();
        inited = true;
    }

    ImGuiMd::RenderUnindented("Call *immvision.inspector_add_image()* anywhere - for example, at different steps inside an image processing algorithm. Later, call *immvision.inspector_show()*, and it will show all the collected images.");

    if (ImGui::Button("Add Test Images"))
        ImmVisionMakeTestSuite();

    ImmVision::Inspector_Show();
}
