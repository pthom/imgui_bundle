#include "demo_utils/api_demos.h"
#include "immvision/immvision.h"
#include "immapp/immapp.h"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>


// The parameters for our image processing pipeline
struct SobelParams
{
    enum class Orientation
    {
        Horizontal,
        Vertical
    };
    float blur_size = 1.25f;
    int deriv_order = 1;  // order of the derivative
    int k_size = 7;  // size of the extended Sobel kernel it must be 1, 3, 5, or 7 (or -1 for Scharr)
    Orientation orientation = Orientation::Vertical;
};


// Our image processing pipeline
cv::Mat ComputeSobel(const cv::Mat& image, const SobelParams& params)
{
    cv::Mat gray;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    cv::Mat img_float;
    gray.convertTo(img_float, CV_32F, 1.0 / 255.0);
    cv::Mat blurred;
    cv::GaussianBlur(img_float, blurred, cv::Size(), params.blur_size, params.blur_size);

    double good_scale = 1.0 / std::pow(2.0, (params.k_size - 2 * params.deriv_order - 2));

    int dx, dy;
    if (params.orientation == SobelParams::Orientation::Vertical)
    {
        dx = params.deriv_order;
        dy = 0;
    }
    else
    {
        dx = 0;
        dy = params.deriv_order;
    }
    cv::Mat r;
    cv::Sobel(blurred, r, CV_64F, dx, dy, params.k_size, good_scale);
    return r;
}


// A GUI to edit the parameters for our image processing pipeline
bool GuiSobelParams(SobelParams& params)
{
    bool changed = false;

    // Blur size
    ImGui::SetNextItemWidth(ImmApp::EmSize() * 10);
    if (ImGui::SliderFloat("Blur size", &params.blur_size, 0.5f, 10.0f))
    {
        changed = true;
    }
    ImGui::SameLine();
    ImGui::Text(" | ");
    ImGui::SameLine();

    // Deriv order
    ImGui::Text("Deriv order");
    ImGui::SameLine();
    for (int deriv_order = 1; deriv_order <= 4; ++deriv_order)
    {
        if (ImGui::RadioButton(std::to_string(deriv_order).c_str(), params.deriv_order == deriv_order))
        {
            changed = true;
            params.deriv_order = deriv_order;
        }
        ImGui::SameLine();
    }

    ImGui::Text(" | ");
    ImGui::SameLine();

    ImGui::Text("Orientation");
    ImGui::SameLine();
    if (ImGui::RadioButton("Horizontal", params.orientation == SobelParams::Orientation::Horizontal))
    {
        changed = true;
        params.orientation = SobelParams::Orientation::Horizontal;
    }
    ImGui::SameLine();
    if (ImGui::RadioButton("Vertical", params.orientation == SobelParams::Orientation::Vertical))
    {
        changed = true;
        params.orientation = SobelParams::Orientation::Vertical;
    }

    return changed;
}


// Our Application State contains:
//     - the original & processed image (image & imageSobel)
//     - our parameters for the processing pipeline (sobelParams)
//     - parameters to display the images via ImmVision: they share the same zoom key,
//       so that we can move the two image in sync
struct AppStateProcess {
    cv::Mat image;
    cv::Mat imageSobel;
    SobelParams sobelParams;

    ImmVision::ImageParams immvisionParams;
    ImmVision::ImageParams immvisionParamsSobel;

    AppStateProcess(const std::string& image_file) {
        image = cv::imread(image_file);
        sobelParams = SobelParams();
        imageSobel = ComputeSobel(image, sobelParams);

        immvisionParams = ImmVision::ImageParams();
        immvisionParams.ImageDisplaySize = cv::Size(int(ImmApp::EmSize(22.f)), 0);
        immvisionParams.ZoomKey = "z";

        immvisionParamsSobel = ImmVision::ImageParams();
        immvisionParamsSobel.ImageDisplaySize = cv::Size(int(ImmApp::EmSize(22.f)), 0);
        immvisionParamsSobel.ZoomKey = "z";
        immvisionParamsSobel.ShowOptionsPanel = true;
    }
};


// Our GUI function
//     (which instantiates a static app state at startup)
void demo_immvision_process()
{
    static AppStateProcess appState(DemosAssetsFolder() + "/images/house.jpg");

    ImGuiMd::RenderUnindented(R"(
        This example shows a example of image processing (sobel filter) where you can adjust the params and see their effect in real time.

        * Pan and zoom the image with the mouse and the mouse wheel
        * Apply Colormaps to the filtered image in the options tab.
    )");
    ImGui::Separator();

    if (GuiSobelParams(appState.sobelParams)) {
        appState.imageSobel = ComputeSobel(appState.image, appState.sobelParams);
        appState.immvisionParamsSobel.RefreshImage = true;
    }
    ImmVision::Image("Original", appState.image, &appState.immvisionParams);
    ImGui::SameLine();
    ImmVision::Image("Deriv", appState.imageSobel, &appState.immvisionParamsSobel);
}


// The main function is not present in this file, but it could be written as
//        ImmApp::RunWithMarkdown(demo_immvision_process, "demo_immvision_process");
