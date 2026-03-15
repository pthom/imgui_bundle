// Rendering test suite for ImmVision: exercises all depth/channel code paths.
// Used as a visual reference before and after the OpenCV removal migration.
//
// To take reference screenshots:
// 1. Build and run on main branch (the reference worktree at imgui_bundle_w2)
// 2. Click through each image in the inspector at various zoom levels
// 3. After migration, run the same program and compare visually

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include "immvision/immvision.h"
#include "immapp/immapp.h"
#include "demo_utils/api_demos.h"
#include <vector>
#include <string>
#include <cmath>
#include <limits>


// =========================================================================
// Synthetic image generators
// =========================================================================

// Horizontal gradient + vertical sine pattern.
// Gradients test colormap scaling and depth conversion.
// Sine wave tests interpolation quality at various zoom levels.
template<typename T>
cv::Mat MakeSyntheticGradient(int w, int h, int channels, double minVal, double maxVal)
{
    int cv_depth = cv::DataType<T>::depth;
    cv::Mat mat(h, w, CV_MAKETYPE(cv_depth, channels));
    for (int y = 0; y < h; y++)
    {
        T* row = mat.ptr<T>(y);
        double vy = 0.5 + 0.3 * std::sin(2.0 * M_PI * y / (double)h * 4.0);
        for (int x = 0; x < w; x++)
        {
            double t = (double)x / (double)(w - 1);
            double val = minVal + (maxVal - minVal) * t * vy;
            for (int c = 0; c < channels; c++)
            {
                // Offset each channel slightly for multi-channel images
                double channel_offset = (channels > 1) ? (c - 1) * (maxVal - minVal) * 0.1 : 0.0;
                double v = val + channel_offset;
                v = std::max(minVal, std::min(maxVal, v));
                row[x * channels + c] = static_cast<T>(v);
            }
        }
    }
    return mat;
}


void FillInspectorRendering()
{
    //std::string assetsDir = "/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/imgui_bundle/bindings/imgui_bundle/demos_assets/images/"; //DemosAssetsFolder() + "/images/";
    std::string assetsDir = DemosAssetsFolder() + "/images/";

    // =========================================================================
    // File-based images (real-world content)
    // =========================================================================
    std::string zoomKey = "zk";

    cv::Mat house = cv::imread(assetsDir + "house.jpg");
    if (!house.empty())
    {
        ImmVision::Inspector_AddImage(house, "house_bgr_u8", zoomKey);

        cv::Mat gray;
        cv::cvtColor(house, gray, cv::COLOR_BGR2GRAY);
        ImmVision::Inspector_AddImage(gray, "house_gray_u8", zoomKey);

        // Floyd-Steinberg dithered halftone (tests INTER_AREA downscale on dithered content)
        {
            cv::Mat fs;
            gray.convertTo(fs, CV_32FC1);
            for (int y = 0; y < fs.rows; y++)
            {
                for (int x = 0; x < fs.cols; x++)
                {
                    float old_val = fs.at<float>(y, x);
                    float new_val = old_val > 127.5f ? 255.f : 0.f;
                    float err = old_val - new_val;
                    fs.at<float>(y, x) = new_val;
                    if (x + 1 < fs.cols)                          fs.at<float>(y,     x + 1) += err * 7.f / 16.f;
                    if (y + 1 < fs.rows && x > 0)                 fs.at<float>(y + 1, x - 1) += err * 3.f / 16.f;
                    if (y + 1 < fs.rows)                           fs.at<float>(y + 1, x    ) += err * 5.f / 16.f;
                    if (y + 1 < fs.rows && x + 1 < fs.cols)       fs.at<float>(y + 1, x + 1) += err * 1.f / 16.f;
                }
            }
            cv::Mat halftone;
            fs.convertTo(halftone, CV_8UC1);
            ImmVision::Inspector_AddImage(halftone, "house_gray_halftone", zoomKey);
        }

        cv::Mat blur;
        cv::GaussianBlur(gray, blur, cv::Size(), 7.);
        ImmVision::Inspector_AddImage(blur, "house_blur_u8", zoomKey);

        cv::Mat floatMat;
        blur.convertTo(floatMat, CV_64FC1);
        floatMat = floatMat / 255.;
        ImmVision::Inspector_AddImage(floatMat, "house_f64", zoomKey);
    }

    cv::Mat bear = cv::imread(assetsDir + "bear_transparent.png", cv::IMREAD_UNCHANGED);
    if (!bear.empty())
        ImmVision::Inspector_AddImage(bear, "bear_bgra_u8");

    cv::Mat tennis = cv::imread(assetsDir + "tennis.jpg");
    if (!tennis.empty())
        ImmVision::Inspector_AddImage(tennis, "tennis_bgr_u8");

    // =========================================================================
    // Synthetic: uint8 variants
    // =========================================================================

    // 3-channel gradient (basic color display)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<uint8_t>(200, 150, 3, 0, 255),
        "synth_u8_3ch");

    // 1-channel (colormap path)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<uint8_t>(200, 150, 1, 0, 255),
        "synth_u8_1ch");

    // 2-channel (the "fake 3-channel" path in converted_to_rgba_image)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<uint8_t>(200, 150, 2, 0, 255),
        "synth_u8_2ch");

    // 4-channel RGBA with gradient alpha (tests alpha checkerboard overlay)
    {
        cv::Mat rgba(150, 200, CV_8UC4);
        for (int y = 0; y < 150; y++)
        {
            uint8_t* row = rgba.ptr<uint8_t>(y);
            for (int x = 0; x < 200; x++)
            {
                row[x * 4 + 0] = (uint8_t)(x * 255 / 199); // B
                row[x * 4 + 1] = (uint8_t)(y * 255 / 149); // G
                row[x * 4 + 2] = 128;                        // R
                row[x * 4 + 3] = (uint8_t)(x * 255 / 199); // A: transparent left, opaque right
            }
        }
        ImmVision::Inspector_AddImage(rgba, "synth_u8_4ch_rgba");
    }

    // =========================================================================
    // Synthetic: signed/unsigned integer depths
    // =========================================================================

    // int8: signed byte (-128 to 127)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<int8_t>(200, 150, 1, -128, 127),
        "synth_s8_1ch");

    // uint16: large dynamic range (0 to 65535)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<uint16_t>(200, 150, 1, 0, 65535),
        "synth_u16_1ch");

    // int16: signed (-32768 to 32767)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<int16_t>(200, 150, 1, -32768, 32767),
        "synth_s16_1ch");

    // int32: wide range
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<int32_t>(200, 150, 1, -100000, 100000),
        "synth_s32_1ch");

    // =========================================================================
    // Synthetic: float depths
    // =========================================================================

    // float32, 1 channel (depth maps, scientific data)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<float>(200, 150, 1, -1.0f, 1.0f),
        "synth_f32_1ch");

    // float32, 3 channels (HDR-like)
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<float>(200, 150, 3, 0.0f, 1.0f),
        "synth_f32_3ch");

    // float64, 1 channel
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<double>(200, 150, 1, -1.0, 1.0),
        "synth_f64_1ch");

    // float64, 3 channels
    ImmVision::Inspector_AddImage(
        MakeSyntheticGradient<double>(200, 150, 3, 0.0, 1.0),
        "synth_f64_3ch");

    // =========================================================================
    // Synthetic: edge cases
    // =========================================================================

    // Checkerboard: sharp edges test interpolation artifacts (especially INTER_AREA)
    {
        cv::Mat checker(200, 200, CV_8UC1);
        for (int y = 0; y < 200; y++)
        {
            uint8_t* row = checker.ptr<uint8_t>(y);
            for (int x = 0; x < 200; x++)
                row[x] = ((x / 8) + (y / 8)) % 2 == 0 ? 255 : 0;
        }
        ImmVision::Inspector_AddImage(checker, "synth_checker_u8");
    }

    // Halftone-like binary pattern (dithering, downscale quality)
    {
        cv::Mat halftone(300, 300, CV_8UC1);
        for (int y = 0; y < 300; y++)
        {
            uint8_t* row = halftone.ptr<uint8_t>(y);
            for (int x = 0; x < 300; x++)
            {
                // Bayer-like dithering threshold
                double intensity = (double)x / 299.0;
                int threshold = ((x % 4) * 4 + (y % 4)) * 255 / 16;
                row[x] = (intensity * 255 > threshold) ? 255 : 0;
            }
        }
        ImmVision::Inspector_AddImage(halftone, "synth_halftone");
    }

    // Float32 with special values: NaN, +Inf, -Inf
    {
        cv::Mat special(100, 100, CV_32FC1);
        for (int y = 0; y < 100; y++)
        {
            float* row = special.ptr<float>(y);
            for (int x = 0; x < 100; x++)
            {
                if (x < 25)
                    row[x] = (float)y / 99.0f;                          // normal gradient
                else if (x < 50)
                    row[x] = std::nanf("");                              // NaN region
                else if (x < 75)
                    row[x] = std::numeric_limits<float>::infinity();     // +Inf
                else
                    row[x] = -std::numeric_limits<float>::infinity();    // -Inf
            }
        }
        ImmVision::Inspector_AddImage(special, "synth_f32_special");
    }
}


void demo_immvision_rendering_test()
{
    static bool inited = false;
    if (!inited)
    {
        ImmVision::UseBgrColorOrder();
        FillInspectorRendering();
        inited = true;
    }

    ImGui::TextWrapped(
        "Rendering test suite: exercises all depth/channel combinations.\n"
        "Check each image at fit-to-window, 1:1, ~5x, ~50x, and ~80x zoom.\n"
        "Compare against reference screenshots from the main branch."
    );
    ImmVision::Inspector_Show();
}

#ifndef IMGUI_BUNDLE_BUILD_DEMO_AS_LIBRARY
int main(int, char*[])
{
    ChdirBesideAssetsFolder();
    ImmVision::UseBgrColorOrder();

    HelloImGui::RunnerParams params;
    params.appWindowParams.windowGeometry.size = {1200, 900};
    params.appWindowParams.windowTitle = "ImmVision Rendering Test Suite";
    params.callbacks.ShowGui = []() {
        demo_immvision_rendering_test();
    };
    HelloImGui::Run(params);
    return 0;
}
#endif
