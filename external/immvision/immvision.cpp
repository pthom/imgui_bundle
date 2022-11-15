// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp                                                 //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.h included by src/immvision/internal/cv/colormap.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/image.h included by src/immvision/internal/cv/colormap.h                 //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include "imgui.h"
#include <opencv2/core.hpp>
#include <vector>
#include <string>


// IMMVISION_API is a marker for public API functions. IMMVISION_STRUCT_API is a marker for public API structs (in comment lines)
// Usage of ImmVision as a shared library is not recommended. No guaranty of ABI stability is provided
#ifndef IMMVISION_API
#define IMMVISION_API
#endif


namespace ImmVision
{

    // Scale the Colormap according to the Image  stats
    struct ColormapScaleFromStatsData                                                            // IMMVISION_API_STRUCT
    {
        // Are we using the stats on the full image?
        // If ActiveOnFullImage and ActiveOnROI are both false, then ColormapSettingsData.ColormapScaleMin/Max will be used
        bool ActiveOnFullImage = true;
        // Are we using the stats on the ROI?
        // If ActiveOnFullImage and ActiveOnROI are both false, then ColormapSettingsData.ColormapScaleMin/Max will be used
        // Note: ActiveOnROI and ActiveOnFullImage cannot be true at the same time!
        bool   ActiveOnROI = false;
        // If active (either on ROI or on Image), how many sigmas around the mean should the Colormap be applied
        double NbSigmas = 1.5;
        // If UseStatsMin is true, then ColormapScaleMin will be calculated from the matrix min value instead of a sigma based value
        bool UseStatsMin = false;
        // If UseStatsMin is true, then ColormapScaleMax will be calculated from the matrix max value instead of a sigma based value
        bool UseStatsMax = false;
    };


    // Colormap Settings (useful for matrices with one channel, in order to see colors mapping float values)
    struct ColormapSettingsData                                                                 // IMMVISION_API_STRUCT
    {
        // Colormap, see available Colormaps with AvailableColormaps()
        // Work only with 1 channel matrices, i.e len(shape)==2
        std::string Colormap = "None";

        // ColormapScaleMin and ColormapScaleMax indicate how the Colormap is applied:
        //     - Values in [ColormapScaleMin, ColomapScaleMax] will use the full colormap.
        //     - Values outside this interval will be clamped before coloring
        // by default, the initial values are ignored, and they will be updated automatically
        // via the options in ColormapScaleFromStats
        double ColormapScaleMin = 0.;
        double ColormapScaleMax = 1.;

        // If ColormapScaleFromStats.ActiveOnFullImage or ColormapScaleFromStats.ActiveOnROI,
        // then ColormapScaleMin/Max are ignored, and the scaling is done according to the image stats.
        // ColormapScaleFromStats.ActiveOnFullImage is true by default
        ColormapScaleFromStatsData ColormapScaleFromStats = ColormapScaleFromStatsData();


        // Internal value: stores the name of the Colormap that is hovered by the mouse
        std::string internal_ColormapHovered = "";
    };


    // Contains information about the mouse inside an image
    struct MouseInformation                                                                     // IMMVISION_API_STRUCT
    {
        // Is the mouse hovering the image
        bool IsMouseHovering = false;

        // Mouse position in the original image/matrix
        // This position is given with float coordinates, and will be (-1., -1.) if the mouse is not hovering the image
        cv::Point2d MousePosition = cv::Point2d(-1., -1.);
        // Mouse position in the displayed portion of the image (the original image can be zoomed,
        // and only show a subset if it may be shown).
        // This position is given with integer coordinates, and will be (-1, -1) if the mouse is not hovering the image
        cv::Point MousePosition_Displayed = cv::Point(-1, -1);

        //
        // Note: you can query ImGui::IsMouseDown(mouse_button) (c++) or imgui.is_mouse_down(mouse_button) (Python)
        //
    };


    // Set of display parameters and options for an Image
    struct ImageParams                                                                           // IMMVISION_API_STRUCT
    {
        //
        // ImageParams store the parameters for a displayed image
        // (as well as user selected watched pixels, selected channel, etc.)
        // Its default constructor will give them reasonable choices, which you can adapt to your needs.
        // Its values will be updated when the user pans or zooms the image, adds watched pixels, etc.
        //

        //
        // Refresh Images Textures
        //

        // Refresh Image: images textures are cached. Set to true if your image matrix/buffer has changed
        // (for example, for live video images)
        bool RefreshImage = false;

        //
        // Display size and title
        //

        // Size of the displayed image (can be different from the matrix size)
        // If you specify only the width or height (e.g (300, 0), then the other dimension
        // will be calculated automatically, respecting the original image w/h ratio.
        cv::Size ImageDisplaySize = cv::Size();

        //
        // Zoom and Pan (represented by an affine transform matrix, of size 3x3)
        //

        // ZoomPanMatrix can be created using MakeZoomPanMatrix to create a view centered around a given point
        cv::Matx33d ZoomPanMatrix = cv::Matx33d::eye();
        // If displaying several images, those with the same ZoomKey will zoom and pan together
        std::string ZoomKey = "";

        //
        // Colormap Settings (useful for matrices with one channel, in order to see colors mapping float values)
        //
        // ColormapSettings stores all the parameter concerning the Colormap
        ColormapSettingsData ColormapSettings = ColormapSettingsData();
        // If displaying several images, those with the same ColormapKey will adjust together
        std::string ColormapKey = "";

        //
        // Zoom and pan with the mouse
        //
        bool PanWithMouse = true;
        bool ZoomWithMouseWheel = true;

        // Color Order: RGB or RGBA versus BGR or BGRA (Note: by default OpenCV uses BGR and BGRA)
        bool IsColorOrderBGR = true;

        //
        // Image display options
        //
        // if SelectedChannel >= 0 then only this channel is displayed
        int  SelectedChannel = -1;
        // Show a "school paper" background grid
        bool ShowSchoolPaperBackground = true;
        // show a checkerboard behind transparent portions of 4 channels RGBA images
        bool ShowAlphaChannelCheckerboard = true;
        // Grid displayed when the zoom is high
        bool ShowGrid = true;
        // Pixel values show when the zoom is high
        bool DrawValuesOnZoomedPixels = true;

        //
        // Image display options
        //
        // Show matrix type and size
        bool ShowImageInfo = true;
        // Show pixel values
        bool ShowPixelInfo = true;
        // Show buttons that enable to zoom in/out (the mouse wheel also zoom)
        bool ShowZoomButtons = true;
        // Open the options panel
        bool ShowOptionsPanel = false;
        // If set to true, then the option panel will be displayed in a transient tooltip window
        bool ShowOptionsInTooltip = false;
        // If set to false, then the Options button will not be displayed
        bool ShowOptionsButton = true;

        //
        // Watched Pixels
        //
        // List of Watched Pixel coordinates
        std::vector<cv::Point> WatchedPixels = std::vector<cv::Point>();
        // Shall we add a watched pixel on double click
        bool AddWatchedPixelOnDoubleClick = true;
        // Shall the watched pixels be drawn on the image
        bool HighlightWatchedPixels = true;

        // Mouse position information. These values are filled after displaying an image
        MouseInformation MouseInfo = MouseInformation();
    };


    // Create ImageParams that display the image only, with no decoration, and no user interaction
    IMMVISION_API ImageParams FactorImageParamsDisplayOnly();


    // Create a zoom/pan matrix centered around a given point of interest
    IMMVISION_API cv::Matx33d MakeZoomPanMatrix(
                        const cv::Point2d & zoomCenter,
                        double zoomRatio,
                        const cv::Size displayedImageSize
    );

    IMMVISION_API cv::Matx33d MakeZoomPanMatrix_ScaleOne(
        cv::Size imageSize,
        const cv::Size displayedImageSize
    );

    IMMVISION_API cv::Matx33d MakeZoomPanMatrix_FullView(
        cv::Size imageSize,
        const cv::Size displayedImageSize
    );


    // Display an image, with full user control: zoom, pan, watch pixels, etc.
    //
    // :param label_id
    //     A legend that will be displayed.
    //     Important notes:
    //         - With ImGui and ImmVision, widgets *must* have a unique Ids.
    //           For this widget, the id is given by this label.
    //           Two widgets (for example) two images *cannot* have the same label or the same id!
    //
    //           If they do, they might not refresh correctly!
    //           To circumvent this, you can:
    //              - Call `ImGui::PushID("some_unique_string")` at the start of your function,
    //                and `ImGui::PopID()` at the end.
    //              - Or modify your label like this:
    //                  "MyLabel##some_unique_id"
    //                  (the part after "##" will not be displayed but will be part of the id)
    //        - To display an empty legend, use "##_some_unique_id"
    //
    // :param mat
    //     An image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.
    //
    // :param params
    //     Complete options (as modifiable inputs), and outputs (mouse position, watched pixels, etc)
    //     @see ImageParams structure.
    //     The ImageParams may be modified by this function: you can extract from them
    //     the mouse position, watched pixels, etc.
    //     Important note:
    //         ImageParams is an input-output parameter, passed as a pointer.
    //         Its scope should be wide enough so that it is preserved from frame to frame.
    //         !! If you cannot zoom/pan in a displayed image, extend the scope of the ImageParams !!
    //
    // - This function requires that both imgui and OpenGL were initialized.
    //   (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
    IMMVISION_API void Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);


    // Only, display the image, with no decoration, and no user interaction (by default)
    //
    // Parameters:
    // :param label
    //     A legend that will be displayed.
    //     Important notes:
    //         - With ImGui and ImmVision, widgets must have a unique Ids. For this widget, the id is given by this label.
    //           Two widgets (for example) two images *cannot* have the same label or the same id!
    //           If they do, they might not refresh correctly!
    //           To circumvent this, you can modify your label like this:
    //              "MyLabel##some_unique_id"    (the part after "##" will not be displayed but will be part of the id)
    //        - To display an empty legend, use "##_some_unique_id"
    //
    // :param Mat:
    //     An image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.
    //
    // :param imageDisplaySize:
    //     Size of the displayed image (can be different from the mat size)
    //     If you specify only the width or height (e.g (300, 0), then the other dimension
    //     will be calculated automatically, respecting the original image w/h ratio.
    //
    // :param refreshImage:
    //     images textures are cached. Set to true if your image matrix/buffer has changed
    //     (for example, for live video images)
    //
    // :param showOptionsButton:
    //     If true, show an option button that opens the option panel.
    //     In that case, it also becomes possible to zoom & pan, add watched pixel by double-clicking, etc.
    //
    // :param isBgrOrBgra:
    //     set to true if the color order of the image is BGR or BGRA (as in OpenCV, by default)
    //
    // :return:
    //      The mouse position in `mat` original image coordinates, as double values.
    //      (i.e. it does not matter if imageDisplaySize is different from mat.size())
    //      It will return (-1., -1.) if the mouse is not hovering the image.
    //
    //      Note: use ImGui::IsMouseDown(mouse_button) (C++) or imgui.is_mouse_down(mouse_button) (Python)
    //            to query more information about the mouse.
    //
    // Note: this function requires that both imgui and OpenGL were initialized.
    //       (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
    //
    IMMVISION_API cv::Point2d ImageDisplay(
        const std::string& label_id,
        const cv::Mat& mat,
        const cv::Size& imageDisplaySize = cv::Size(),
        bool refreshImage = false,
        bool showOptionsButton = false,
        bool isBgrOrBgra = true
        );


    // Return the list of the available color maps
    // Taken from https://github.com/yuki-koyama/tinycolormap, thanks to Yuki Koyama
    IMMVISION_API std::vector<std::string> AvailableColormaps();


    // Clears the internal texture cache of immvision (this is done automatically at exit time)
    //
    // Note: this function requires that both imgui and OpenGL were initialized.
    //       (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
    IMMVISION_API void ClearTextureCache();

    // Returns the RGBA image currently displayed by ImmVision::Image or ImmVision::ImageDisplay
    // Note: this image must be currently displayed. This function will return the transformed image
    // (i.e with ColorMap, Zoom, etc.)
    IMMVISION_API cv::Mat GetCachedRgbaImage(const std::string& label_id);

    // Return immvision version info
    IMMVISION_API std::string VersionInfo();


} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.h continued                                         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/insertion_order_map.h included by src/immvision/internal/cv/colormap.h//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <unordered_map>
#include <utility>
#include <algorithm>


namespace ImmVision
{
    template<typename Key, typename Value>
    class insertion_order_map
    {
    public:

        bool contains(const Key& k) const { return _map.find(k) != _map.end(); }

        bool empty() const { return _keys.empty(); }

        void clear() { _keys.clear(); _map.clear(); }

        void insert(const Key& k, const Value& v)
        {
            assert(!contains(k));
            _keys.push_back(k);
            _map[k] = v;
        }

        void insert(const Key& k, Value&& v)
        {
            assert(!contains(k));
            _keys.push_back(k);
            _map[k] = std::move(v);
        }


        Value& get(const Key& k)
        {
            assert(contains(k));
            return _map.at(k);
        }

        const Value& get(const Key& k) const
        {
            assert(contains(k));
            return _map.at(k);
        }

        void erase(const Key& k)
        {
            assert(contains(k));
            _map.erase(_map.find(k));
            _keys.erase(std::remove(_keys.begin(), _keys.end(), 5), _keys.end());
        }

        const std::vector<Key>& insertion_order_keys() const
        {
            return _keys;
        }

        const std::vector<std::pair<const Key&, const Value&>> items() const
        {
            std::vector<std::pair<const Key&, const Value&>> r;
            for (const auto& k : insertion_order_keys())
                r.push_back({k, get(k)});
            return r;
        }

        std::vector<std::pair<const Key&, Value&>> items()
        {
            std::vector<std::pair<const Key&, Value&>> r;
            for (const auto& k : insertion_order_keys())
                r.push_back({k, get(k)});
            return r;
        }

    private:
        std::unordered_map<Key, Value> _map;
        std::vector<Key> _keys;
    };



} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.h continued                                         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <map>

// Uses https://github.com/jgreitemann/colormap
// Many thanks to Yuki Koyama

// Uses https://github.com/Neargye/magic_enum
// Many thanks to Daniil Goncharov


namespace ImmVision
{
    namespace Colormap
    {
        //
        // Base operations for ColormapScaleSettings
        //
        bool IsNone(const ColormapSettingsData& a);
        bool IsEqual(const ColormapSettingsData& v1, const ColormapSettingsData& v2);
        bool IsEqual(const ColormapScaleFromStatsData& v1, const ColormapScaleFromStatsData& v2);
        bool CanColormap(const cv::Mat &image);
        ColormapSettingsData ComputeInitialColormapSettings(const cv::Mat& m);


        //
        // Colormaps images and textures
        //
        std::vector<std::string> AvailableColormaps();

        const insertion_order_map<std::string, cv::Mat>& ColormapsImages();
        const insertion_order_map<std::string, unsigned int>& ColormapsTextures();
        void ClearColormapsTexturesCache();

        //
        // Apply Colormap
        //
        cv::Mat_<cv::Vec4b> ApplyColormap(const cv::Mat& m, const ColormapSettingsData& settings);


        //
        // Interactive update during pan and zoom, full init on new Image
        //
        void UpdateRoiStatsInteractively(
            const cv::Mat &image,
            const cv::Rect& roi,
            ColormapSettingsData* inout_settings);
        void InitStatsOnNewImage(
            const cv::Mat &image,
            const cv::Rect& roi,
            ColormapSettingsData* inout_settings);

        //
        // GUI
        //
        void GuiShowColormapSettingsData(
            const cv::Mat &image,
            const cv::Rect& roi,
            float availableGuiWidth,
            ColormapSettingsData* inout_settings);

    } // namespace Colormap

} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/tinycolormap.hpp included by src/immvision/internal/cv/colormap.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
 MIT License

 Copyright (c) 2018-2020 Yuki Koyama

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

 -------------------------------------------------------------------------------

 The lookup table for Turbo is derived by Shot511 in his PR,
 https://github.com/yuki-koyama/tinycolormap/pull/27 , from
 https://gist.github.com/mikhailov-work/6a308c20e494d9e0ccc29036b28faa7a , which
 is released by Anton Mikhailov, copyrighted by Google LLC, and licensed under
 the Apache 2.0 license. To the best of our knowledge, the Apache 2.0 license is
 compatible with the MIT license, and thus we release the merged entire code
 under the MIT license. The license notice for Anton's code is posted here:

 Copyright 2019 Google LLC.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 */

#ifndef TINYCOLORMAP_HPP_
#define TINYCOLORMAP_HPP_

#include <cmath>
#include <cstdint>

#if defined(TINYCOLORMAP_WITH_EIGEN)
#include <Eigen/Core>
#endif

#if defined(TINYCOLORMAP_WITH_QT5)
#include <QColor>
#endif

#if defined(TINYCOLORMAP_WITH_QT5) && defined(TINYCOLORMAP_WITH_EIGEN)
#include <QImage>
#include <QString>
#endif

#if defined(TINYCOLORMAP_WITH_GLM)
#include <glm/vec3.hpp>
#endif

namespace tinycolormap
{
    //////////////////////////////////////////////////////////////////////////////////
    // Interface
    //////////////////////////////////////////////////////////////////////////////////

    enum class ColormapType
    {
        None, Gray, Parula, Heat, Jet, Turbo, Hot, Magma, Inferno, Plasma, Viridis, Cividis, Github, Cubehelix
    };

    struct Color
    {
        explicit constexpr Color(double gray) noexcept : data{ gray, gray, gray } {}
        constexpr Color(double r, double g, double b) noexcept : data{ r, g, b } {}

        double data[3];

        double& r() noexcept { return data[0]; }
        double& g() noexcept { return data[1]; }
        double& b() noexcept { return data[2]; }
        constexpr double r() const noexcept { return data[0]; }
        constexpr double g() const noexcept { return data[1]; }
        constexpr double b() const noexcept { return data[2]; }

        constexpr uint8_t ri() const noexcept { return static_cast<uint8_t>(data[0] * 255.0); }
        constexpr uint8_t gi() const noexcept { return static_cast<uint8_t>(data[1] * 255.0); }
        constexpr uint8_t bi() const noexcept { return static_cast<uint8_t>(data[2] * 255.0); }

        double& operator[](std::size_t n) noexcept { return data[n]; }
        constexpr double operator[](std::size_t n) const noexcept { return data[n]; }
        double& operator()(std::size_t n) noexcept { return data[n]; }
        constexpr double operator()(std::size_t n) const noexcept { return data[n]; }

        friend constexpr Color operator+(const Color& c0, const Color& c1) noexcept
        {
            return { c0.r() + c1.r(), c0.g() + c1.g(), c0.b() + c1.b() };
        }

        friend constexpr Color operator*(double s, const Color& c) noexcept
        {
            return { s * c.r(), s * c.g(), s * c.b() };
        }

#if defined(TINYCOLORMAP_WITH_QT5)
        QColor ConvertToQColor() const { return QColor(data[0] * 255.0, data[1] * 255.0, data[2] * 255.0); }
#endif
#if defined(TINYCOLORMAP_WITH_EIGEN)
        Eigen::Vector3d ConvertToEigen() const { return Eigen::Vector3d(data[0], data[1], data[2]); }
#endif
#if defined(TINYCOLORMAP_WITH_GLM)
        glm::vec3 ConvertToGLM() const { return glm::vec3(data[0], data[1], data[2]); }
#endif
    };

    inline Color GetColor(double x, ColormapType type = ColormapType::Viridis);
    inline Color GetQuantizedColor(double x, unsigned int num_levels, ColormapType type = ColormapType::Viridis);
    inline Color constexpr GetNoneColor(double x) noexcept;
    inline Color GetParulaColor(double x);
    inline Color GetHeatColor(double x);
    inline Color GetJetColor(double x);
    inline Color GetTurboColor(double x);
    inline Color GetHotColor(double x);
    inline constexpr Color GetGrayColor(double x) noexcept;
    inline Color GetMagmaColor(double x);
    inline Color GetInfernoColor(double x);
    inline Color GetPlasmaColor(double x);
    inline Color GetViridisColor(double x);
    inline Color GetCividisColor(double x);
    inline Color GetGithubColor(double x);
    inline Color GetCubehelixColor(double x);

#if defined(TINYCOLORMAP_WITH_QT5) && defined(TINYCOLORMAP_WITH_EIGEN)
    inline QImage CreateMatrixVisualization(const Eigen::MatrixXd& matrix);
    inline void ExportMatrixVisualization(const Eigen::MatrixXd& matrix, const std::string& path);
#endif

    //////////////////////////////////////////////////////////////////////////////////
    // Private Implementation - public usage is not intended
    //////////////////////////////////////////////////////////////////////////////////

    namespace internal
    {
        inline constexpr double Clamp01(double x) noexcept
        {
            return (x < 0.0) ? 0.0 : (x > 1.0) ? 1.0 : x;
        }

        // A helper function to calculate linear interpolation
        template <std::size_t N>
        Color CalcLerp(double x, const Color (&data)[N])
        {
            const double a  = Clamp01(x) * (N - 1);
            const double i  = std::floor(a);
            const double t  = a - i;
            const Color& c0 = data[static_cast<std::size_t>(i)];
            const Color& c1 = data[static_cast<std::size_t>(std::ceil(a))];

            return (1.0 - t) * c0 + t * c1;
        }

        inline double QuantizeArgument(double x, unsigned int num_levels)
        {
            // Clamp num_classes to range [1, 255].
            num_levels = (std::max)(1u, (std::min)(num_levels, 255u));

            const double interval_length = 255.0 / num_levels;

            // Calculate index of the interval to which the given x belongs to.
            // Substracting eps prevents getting out of bounds index.
            constexpr double eps = 0.0005;
            const unsigned int index = static_cast<unsigned int>((x * 255.0 - eps) / interval_length);

            // Calculate upper and lower bounds of the given interval.
            const unsigned int upper_boundary = static_cast<unsigned int>(index * interval_length + interval_length);
            const unsigned int lower_boundary = static_cast<unsigned int>(upper_boundary - interval_length);

            // Get middle "coordinate" of the given interval and move it back to [0.0, 1.0] interval.
            const double xx = static_cast<double>(upper_boundary + lower_boundary) * 0.5 / 255.0;

            return xx;
        }
    }

    //////////////////////////////////////////////////////////////////////////////////
    // Public Implementation
    //////////////////////////////////////////////////////////////////////////////////

    inline Color GetColor(double x, ColormapType type)
    {
        switch (type)
        {
            case ColormapType::None:
                return GetNoneColor(x);
            case ColormapType::Parula:
                return GetParulaColor(x);
            case ColormapType::Heat:
                return GetHeatColor(x);
            case ColormapType::Jet:
                return GetJetColor(x);
            case ColormapType::Turbo:
                return GetTurboColor(x);
            case ColormapType::Hot:
                return GetHotColor(x);
            case ColormapType::Gray:
                return GetGrayColor(x);
            case ColormapType::Magma:
                return GetMagmaColor(x);
            case ColormapType::Inferno:
                return GetInfernoColor(x);
            case ColormapType::Plasma:
                return GetPlasmaColor(x);
            case ColormapType::Viridis:
                return GetViridisColor(x);
            case ColormapType::Cividis:
                return GetCividisColor(x);
            case ColormapType::Github:
                return GetGithubColor(x);
            case ColormapType::Cubehelix:
                return GetCubehelixColor(x);
            default:
                break;
        }

        return GetViridisColor(x);
    }

    inline Color GetQuantizedColor(double x, unsigned int num_levels, ColormapType type)
    {
        return GetColor(internal::QuantizeArgument(x, num_levels), type);
    }

    inline Color constexpr GetNoneColor(double x) noexcept
    {
        return Color{ internal::Clamp01(x) };
    }

    inline Color GetParulaColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.2081, 0.1663, 0.5292 },
                { 0.2091, 0.1721, 0.5411 },
                { 0.2101, 0.1779, 0.553   },
                { 0.2109, 0.1837, 0.565   },
                { 0.2116, 0.1895, 0.5771 },
                { 0.2121, 0.1954, 0.5892 },
                { 0.2124, 0.2013, 0.6013 },
                { 0.2125, 0.2072, 0.6135 },
                { 0.2123, 0.2132, 0.6258 },
                { 0.2118, 0.2192, 0.6381 },
                { 0.2111, 0.2253, 0.6505 },
                { 0.2099, 0.2315, 0.6629 },
                { 0.2084, 0.2377, 0.6753 },
                { 0.2063, 0.244, 0.6878   },
                { 0.2038, 0.2503, 0.7003 },
                { 0.2006, 0.2568, 0.7129 },
                { 0.1968, 0.2632, 0.7255 },
                { 0.1921, 0.2698, 0.7381 },
                { 0.1867, 0.2764, 0.7507 },
                { 0.1802, 0.2832, 0.7634 },
                { 0.1728, 0.2902, 0.7762 },
                { 0.1641, 0.2975, 0.789   },
                { 0.1541, 0.3052, 0.8017 },
                { 0.1427, 0.3132, 0.8145 },
                { 0.1295, 0.3217, 0.8269 },
                { 0.1147, 0.3306, 0.8387 },
                { 0.0986, 0.3397, 0.8495 },
                { 0.0816, 0.3486, 0.8588 },
                { 0.0646, 0.3572, 0.8664 },
                { 0.0482, 0.3651, 0.8722 },
                { 0.0329, 0.3724, 0.8765 },
                { 0.0213, 0.3792, 0.8796 },
                { 0.0136, 0.3853, 0.8815 },
                { 0.0086, 0.3911, 0.8827 },
                { 0.006,  0.3965, 0.8833 },
                { 0.0051, 0.4017, 0.8834 },
                { 0.0054, 0.4066, 0.8831 },
                { 0.0067, 0.4113, 0.8825 },
                { 0.0089, 0.4159, 0.8816 },
                { 0.0116, 0.4203, 0.8805 },
                { 0.0148, 0.4246, 0.8793 },
                { 0.0184, 0.4288, 0.8779 },
                { 0.0223, 0.4329, 0.8763 },
                { 0.0264, 0.437, 0.8747   },
                { 0.0306, 0.441, 0.8729   },
                { 0.0349, 0.4449, 0.8711 },
                { 0.0394, 0.4488, 0.8692 },
                { 0.0437, 0.4526, 0.8672 },
                { 0.0477, 0.4564, 0.8652 },
                { 0.0514, 0.4602, 0.8632 },
                { 0.0549, 0.464, 0.8611   },
                { 0.0582, 0.4677, 0.8589 },
                { 0.0612, 0.4714, 0.8568 },
                { 0.064,  0.4751, 0.8546 },
                { 0.0666, 0.4788, 0.8525 },
                { 0.0689, 0.4825, 0.8503 },
                { 0.071,  0.4862, 0.8481 },
                { 0.0729, 0.4899, 0.846   },
                { 0.0746, 0.4937, 0.8439 },
                { 0.0761, 0.4974, 0.8418 },
                { 0.0773, 0.5012, 0.8398 },
                { 0.0782, 0.5051, 0.8378 },
                { 0.0789, 0.5089, 0.8359 },
                { 0.0794, 0.5129, 0.8341 },
                { 0.0795, 0.5169, 0.8324 },
                { 0.0793, 0.521, 0.8308   },
                { 0.0788, 0.5251, 0.8293 },
                { 0.0778, 0.5295, 0.828   },
                { 0.0764, 0.5339, 0.827   },
                { 0.0746, 0.5384, 0.8261 },
                { 0.0724, 0.5431, 0.8253 },
                { 0.0698, 0.5479, 0.8247 },
                { 0.0668, 0.5527, 0.8243 },
                { 0.0636, 0.5577, 0.8239 },
                { 0.06,   0.5627, 0.8237 },
                { 0.0562, 0.5677, 0.8234 },
                { 0.0523, 0.5727, 0.8231 },
                { 0.0484, 0.5777, 0.8228 },
                { 0.0445, 0.5826, 0.8223 },
                { 0.0408, 0.5874, 0.8217 },
                { 0.0372, 0.5922, 0.8209 },
                { 0.0342, 0.5968, 0.8198 },
                { 0.0317, 0.6012, 0.8186 },
                { 0.0296, 0.6055, 0.8171 },
                { 0.0279, 0.6097, 0.8154 },
                { 0.0265, 0.6137, 0.8135 },
                { 0.0255, 0.6176, 0.8114 },
                { 0.0248, 0.6214, 0.8091 },
                { 0.0243, 0.625, 0.8066   },
                { 0.0239, 0.6285, 0.8039 },
                { 0.0237, 0.6319, 0.801   },
                { 0.0235, 0.6352, 0.798   },
                { 0.0233, 0.6384, 0.7948 },
                { 0.0231, 0.6415, 0.7916 },
                { 0.023,  0.6445, 0.7881 },
                { 0.0229, 0.6474, 0.7846 },
                { 0.0227, 0.6503, 0.781, },
                { 0.0227, 0.6531, 0.7773 },
                { 0.0232, 0.6558, 0.7735 },
                { 0.0238, 0.6585, 0.7696 },
                { 0.0246, 0.6611, 0.7656 },
                { 0.0263, 0.6637, 0.7615 },
                { 0.0282, 0.6663, 0.7574 },
                { 0.0306, 0.6688, 0.7532 },
                { 0.0338, 0.6712, 0.749   },
                { 0.0373, 0.6737, 0.7446 },
                { 0.0418, 0.6761, 0.7402 },
                { 0.0467, 0.6784, 0.7358 },
                { 0.0516, 0.6808, 0.7313 },
                { 0.0574, 0.6831, 0.7267 },
                { 0.0629, 0.6854, 0.7221 },
                { 0.0692, 0.6877, 0.7173 },
                { 0.0755, 0.6899, 0.7126 },
                { 0.082,  0.6921, 0.7078 },
                { 0.0889, 0.6943, 0.7029 },
                { 0.0956, 0.6965, 0.6979 },
                { 0.1031, 0.6986, 0.6929 },
                { 0.1104, 0.7007, 0.6878 },
                { 0.118,  0.7028, 0.6827 },
                { 0.1258, 0.7049, 0.6775 },
                { 0.1335, 0.7069, 0.6723 },
                { 0.1418, 0.7089, 0.6669 },
                { 0.1499, 0.7109, 0.6616 },
                { 0.1585, 0.7129, 0.6561 },
                { 0.1671, 0.7148, 0.6507 },
                { 0.1758, 0.7168, 0.6451 },
                { 0.1849, 0.7186, 0.6395 },
                { 0.1938, 0.7205, 0.6338 },
                { 0.2033, 0.7223, 0.6281 },
                { 0.2128, 0.7241, 0.6223 },
                { 0.2224, 0.7259, 0.6165 },
                { 0.2324, 0.7275, 0.6107 },
                { 0.2423, 0.7292, 0.6048 },
                { 0.2527, 0.7308, 0.5988 },
                { 0.2631, 0.7324, 0.5929 },
                { 0.2735, 0.7339, 0.5869 },
                { 0.2845, 0.7354, 0.5809 },
                { 0.2953, 0.7368, 0.5749 },
                { 0.3064, 0.7381, 0.5689 },
                { 0.3177, 0.7394, 0.563   },
                { 0.3289, 0.7406, 0.557   },
                { 0.3405, 0.7417, 0.5512 },
                { 0.352,  0.7428, 0.5453 },
                { 0.3635, 0.7438, 0.5396 },
                { 0.3753, 0.7446, 0.5339 },
                { 0.3869, 0.7454, 0.5283 },
                { 0.3986, 0.7461, 0.5229 },
                { 0.4103, 0.7467, 0.5175 },
                { 0.4218, 0.7473, 0.5123 },
                { 0.4334, 0.7477, 0.5072 },
                { 0.4447, 0.7482, 0.5021 },
                { 0.4561, 0.7485, 0.4972 },
                { 0.4672, 0.7487, 0.4924 },
                { 0.4783, 0.7489, 0.4877 },
                { 0.4892, 0.7491, 0.4831 },
                { 0.5,    0.7491, 0.4786 },
                { 0.5106, 0.7492, 0.4741 },
                { 0.5212, 0.7492, 0.4698 },
                { 0.5315, 0.7491, 0.4655 },
                { 0.5418, 0.749, 0.4613   },
                { 0.5519, 0.7489, 0.4571 },
                { 0.5619, 0.7487, 0.4531 },
                { 0.5718, 0.7485, 0.449   },
                { 0.5816, 0.7482, 0.4451 },
                { 0.5913, 0.7479, 0.4412 },
                { 0.6009, 0.7476, 0.4374 },
                { 0.6103, 0.7473, 0.4335 },
                { 0.6197, 0.7469, 0.4298 },
                { 0.629,  0.7465, 0.4261 },
                { 0.6382, 0.746, 0.4224   },
                { 0.6473, 0.7456, 0.4188 },
                { 0.6564, 0.7451, 0.4152 },
                { 0.6653, 0.7446, 0.4116 },
                { 0.6742, 0.7441, 0.4081 },
                { 0.683,  0.7435, 0.4046 },
                { 0.6918, 0.743, 0.4011   },
                { 0.7004, 0.7424, 0.3976 },
                { 0.7091, 0.7418, 0.3942 },
                { 0.7176, 0.7412, 0.3908 },
                { 0.7261, 0.7405, 0.3874 },
                { 0.7346, 0.7399, 0.384   },
                { 0.743,  0.7392, 0.3806 },
                { 0.7513, 0.7385, 0.3773 },
                { 0.7596, 0.7378, 0.3739 },
                { 0.7679, 0.7372, 0.3706 },
                { 0.7761, 0.7364, 0.3673 },
                { 0.7843, 0.7357, 0.3639 },
                { 0.7924, 0.735, 0.3606   },
                { 0.8005, 0.7343, 0.3573 },
                { 0.8085, 0.7336, 0.3539 },
                { 0.8166, 0.7329, 0.3506 },
                { 0.8246, 0.7322, 0.3472 },
                { 0.8325, 0.7315, 0.3438 },
                { 0.8405, 0.7308, 0.3404 },
                { 0.8484, 0.7301, 0.337   },
                { 0.8563, 0.7294, 0.3336 },
                { 0.8642, 0.7288, 0.33    },
                { 0.872,  0.7282, 0.3265 },
                { 0.8798, 0.7276, 0.3229 },
                { 0.8877, 0.7271, 0.3193 },
                { 0.8954, 0.7266, 0.3156 },
                { 0.9032, 0.7262, 0.3117 },
                { 0.911,  0.7259, 0.3078 },
                { 0.9187, 0.7256, 0.3038 },
                { 0.9264, 0.7256, 0.2996 },
                { 0.9341, 0.7256, 0.2953 },
                { 0.9417, 0.7259, 0.2907 },
                { 0.9493, 0.7264, 0.2859 },
                { 0.9567, 0.7273, 0.2808 },
                { 0.9639, 0.7285, 0.2754 },
                { 0.9708, 0.7303, 0.2696 },
                { 0.9773, 0.7326, 0.2634 },
                { 0.9831, 0.7355, 0.257   },
                { 0.9882, 0.739, 0.2504   },
                { 0.9922, 0.7431, 0.2437 },
                { 0.9952, 0.7476, 0.2373 },
                { 0.9973, 0.7524, 0.231   },
                { 0.9986, 0.7573, 0.2251 },
                { 0.9991, 0.7624, 0.2195 },
                { 0.999,  0.7675, 0.2141 },
                { 0.9985, 0.7726, 0.209   },
                { 0.9976, 0.7778, 0.2042 },
                { 0.9964, 0.7829, 0.1995 },
                { 0.995,  0.788, 0.1949   },
                { 0.9933, 0.7931, 0.1905 },
                { 0.9914, 0.7981, 0.1863 },
                { 0.9894, 0.8032, 0.1821 },
                { 0.9873, 0.8083, 0.178   },
                { 0.9851, 0.8133, 0.174   },
                { 0.9828, 0.8184, 0.17    },
                { 0.9805, 0.8235, 0.1661 },
                { 0.9782, 0.8286, 0.1622 },
                { 0.9759, 0.8337, 0.1583 },
                { 0.9736, 0.8389, 0.1544 },
                { 0.9713, 0.8441, 0.1505 },
                { 0.9692, 0.8494, 0.1465 },
                { 0.9672, 0.8548, 0.1425 },
                { 0.9654, 0.8603, 0.1385 },
                { 0.9638, 0.8659, 0.1343 },
                { 0.9623, 0.8716, 0.1301 },
                { 0.9611, 0.8774, 0.1258 },
                { 0.96,   0.8834, 0.1215 },
                { 0.9593, 0.8895, 0.1171 },
                { 0.9588, 0.8958, 0.1126 },
                { 0.9586, 0.9022, 0.1082 },
                { 0.9587, 0.9088, 0.1036 },
                { 0.9591, 0.9155, 0.099   },
                { 0.9599, 0.9225, 0.0944 },
                { 0.961,  0.9296, 0.0897 },
                { 0.9624, 0.9368, 0.085   },
                { 0.9641, 0.9443, 0.0802 },
                { 0.9662, 0.9518, 0.0753 },
                { 0.9685, 0.9595, 0.0703 },
                { 0.971,  0.9673, 0.0651 },
                { 0.9736, 0.9752, 0.0597 },
                { 0.9763, 0.9831, 0.0538 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetHeatColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.0, 0.0, 1.0 },
                { 0.0, 1.0, 1.0 },
                { 0.0, 1.0, 0.0 },
                { 1.0, 1.0, 0.0 },
                { 1.0, 0.0, 0.0 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetJetColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.0, 0.0, 0.5 },
                { 0.0, 0.0, 1.0 },
                { 0.0, 0.5, 1.0 },
                { 0.0, 1.0, 1.0 },
                { 0.5, 1.0, 0.5 },
                { 1.0, 1.0, 0.0 },
                { 1.0, 0.5, 0.0 },
                { 1.0, 0.0, 0.0 },
                { 0.5, 0.0, 0.0 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetTurboColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.18995, 0.07176, 0.23217 },
                { 0.19483, 0.08339, 0.26149 },
                { 0.19956, 0.09498, 0.29024 },
                { 0.20415, 0.10652, 0.31844 },
                { 0.20860, 0.11802, 0.34607 },
                { 0.21291, 0.12947, 0.37314 },
                { 0.21708, 0.14087, 0.39964 },
                { 0.22111, 0.15223, 0.42558 },
                { 0.22500, 0.16354, 0.45096 },
                { 0.22875, 0.17481, 0.47578 },
                { 0.23236, 0.18603, 0.50004 },
                { 0.23582, 0.19720, 0.52373 },
                { 0.23915, 0.20833, 0.54686 },
                { 0.24234, 0.21941, 0.56942 },
                { 0.24539, 0.23044, 0.59142 },
                { 0.24830, 0.24143, 0.61286 },
                { 0.25107, 0.25237, 0.63374 },
                { 0.25369, 0.26327, 0.65406 },
                { 0.25618, 0.27412, 0.67381 },
                { 0.25853, 0.28492, 0.69300 },
                { 0.26074, 0.29568, 0.71162 },
                { 0.26280, 0.30639, 0.72968 },
                { 0.26473, 0.31706, 0.74718 },
                { 0.26652, 0.32768, 0.76412 },
                { 0.26816, 0.33825, 0.78050 },
                { 0.26967, 0.34878, 0.79631 },
                { 0.27103, 0.35926, 0.81156 },
                { 0.27226, 0.36970, 0.82624 },
                { 0.27334, 0.38008, 0.84037 },
                { 0.27429, 0.39043, 0.85393 },
                { 0.27509, 0.40072, 0.86692 },
                { 0.27576, 0.41097, 0.87936 },
                { 0.27628, 0.42118, 0.89123 },
                { 0.27667, 0.43134, 0.90254 },
                { 0.27691, 0.44145, 0.91328 },
                { 0.27701, 0.45152, 0.92347 },
                { 0.27698, 0.46153, 0.93309 },
                { 0.27680, 0.47151, 0.94214 },
                { 0.27648, 0.48144, 0.95064 },
                { 0.27603, 0.49132, 0.95857 },
                { 0.27543, 0.50115, 0.96594 },
                { 0.27469, 0.51094, 0.97275 },
                { 0.27381, 0.52069, 0.97899 },
                { 0.27273, 0.53040, 0.98461 },
                { 0.27106, 0.54015, 0.98930 },
                { 0.26878, 0.54995, 0.99303 },
                { 0.26592, 0.55979, 0.99583 },
                { 0.26252, 0.56967, 0.99773 },
                { 0.25862, 0.57958, 0.99876 },
                { 0.25425, 0.58950, 0.99896 },
                { 0.24946, 0.59943, 0.99835 },
                { 0.24427, 0.60937, 0.99697 },
                { 0.23874, 0.61931, 0.99485 },
                { 0.23288, 0.62923, 0.99202 },
                { 0.22676, 0.63913, 0.98851 },
                { 0.22039, 0.64901, 0.98436 },
                { 0.21382, 0.65886, 0.97959 },
                { 0.20708, 0.66866, 0.97423 },
                { 0.20021, 0.67842, 0.96833 },
                { 0.19326, 0.68812, 0.96190 },
                { 0.18625, 0.69775, 0.95498 },
                { 0.17923, 0.70732, 0.94761 },
                { 0.17223, 0.71680, 0.93981 },
                { 0.16529, 0.72620, 0.93161 },
                { 0.15844, 0.73551, 0.92305 },
                { 0.15173, 0.74472, 0.91416 },
                { 0.14519, 0.75381, 0.90496 },
                { 0.13886, 0.76279, 0.89550 },
                { 0.13278, 0.77165, 0.88580 },
                { 0.12698, 0.78037, 0.87590 },
                { 0.12151, 0.78896, 0.86581 },
                { 0.11639, 0.79740, 0.85559 },
                { 0.11167, 0.80569, 0.84525 },
                { 0.10738, 0.81381, 0.83484 },
                { 0.10357, 0.82177, 0.82437 },
                { 0.10026, 0.82955, 0.81389 },
                { 0.09750, 0.83714, 0.80342 },
                { 0.09532, 0.84455, 0.79299 },
                { 0.09377, 0.85175, 0.78264 },
                { 0.09287, 0.85875, 0.77240 },
                { 0.09267, 0.86554, 0.76230 },
                { 0.09320, 0.87211, 0.75237 },
                { 0.09451, 0.87844, 0.74265 },
                { 0.09662, 0.88454, 0.73316 },
                { 0.09958, 0.89040, 0.72393 },
                { 0.10342, 0.89600, 0.71500 },
                { 0.10815, 0.90142, 0.70599 },
                { 0.11374, 0.90673, 0.69651 },
                { 0.12014, 0.91193, 0.68660 },
                { 0.12733, 0.91701, 0.67627 },
                { 0.13526, 0.92197, 0.66556 },
                { 0.14391, 0.92680, 0.65448 },
                { 0.15323, 0.93151, 0.64308 },
                { 0.16319, 0.93609, 0.63137 },
                { 0.17377, 0.94053, 0.61938 },
                { 0.18491, 0.94484, 0.60713 },
                { 0.19659, 0.94901, 0.59466 },
                { 0.20877, 0.95304, 0.58199 },
                { 0.22142, 0.95692, 0.56914 },
                { 0.23449, 0.96065, 0.55614 },
                { 0.24797, 0.96423, 0.54303 },
                { 0.26180, 0.96765, 0.52981 },
                { 0.27597, 0.97092, 0.51653 },
                { 0.29042, 0.97403, 0.50321 },
                { 0.30513, 0.97697, 0.48987 },
                { 0.32006, 0.97974, 0.47654 },
                { 0.33517, 0.98234, 0.46325 },
                { 0.35043, 0.98477, 0.45002 },
                { 0.36581, 0.98702, 0.43688 },
                { 0.38127, 0.98909, 0.42386 },
                { 0.39678, 0.99098, 0.41098 },
                { 0.41229, 0.99268, 0.39826 },
                { 0.42778, 0.99419, 0.38575 },
                { 0.44321, 0.99551, 0.37345 },
                { 0.45854, 0.99663, 0.36140 },
                { 0.47375, 0.99755, 0.34963 },
                { 0.48879, 0.99828, 0.33816 },
                { 0.50362, 0.99879, 0.32701 },
                { 0.51822, 0.99910, 0.31622 },
                { 0.53255, 0.99919, 0.30581 },
                { 0.54658, 0.99907, 0.29581 },
                { 0.56026, 0.99873, 0.28623 },
                { 0.57357, 0.99817, 0.27712 },
                { 0.58646, 0.99739, 0.26849 },
                { 0.59891, 0.99638, 0.26038 },
                { 0.61088, 0.99514, 0.25280 },
                { 0.62233, 0.99366, 0.24579 },
                { 0.63323, 0.99195, 0.23937 },
                { 0.64362, 0.98999, 0.23356 },
                { 0.65394, 0.98775, 0.22835 },
                { 0.66428, 0.98524, 0.22370 },
                { 0.67462, 0.98246, 0.21960 },
                { 0.68494, 0.97941, 0.21602 },
                { 0.69525, 0.97610, 0.21294 },
                { 0.70553, 0.97255, 0.21032 },
                { 0.71577, 0.96875, 0.20815 },
                { 0.72596, 0.96470, 0.20640 },
                { 0.73610, 0.96043, 0.20504 },
                { 0.74617, 0.95593, 0.20406 },
                { 0.75617, 0.95121, 0.20343 },
                { 0.76608, 0.94627, 0.20311 },
                { 0.77591, 0.94113, 0.20310 },
                { 0.78563, 0.93579, 0.20336 },
                { 0.79524, 0.93025, 0.20386 },
                { 0.80473, 0.92452, 0.20459 },
                { 0.81410, 0.91861, 0.20552 },
                { 0.82333, 0.91253, 0.20663 },
                { 0.83241, 0.90627, 0.20788 },
                { 0.84133, 0.89986, 0.20926 },
                { 0.85010, 0.89328, 0.21074 },
                { 0.85868, 0.88655, 0.21230 },
                { 0.86709, 0.87968, 0.21391 },
                { 0.87530, 0.87267, 0.21555 },
                { 0.88331, 0.86553, 0.21719 },
                { 0.89112, 0.85826, 0.21880 },
                { 0.89870, 0.85087, 0.22038 },
                { 0.90605, 0.84337, 0.22188 },
                { 0.91317, 0.83576, 0.22328 },
                { 0.92004, 0.82806, 0.22456 },
                { 0.92666, 0.82025, 0.22570 },
                { 0.93301, 0.81236, 0.22667 },
                { 0.93909, 0.80439, 0.22744 },
                { 0.94489, 0.79634, 0.22800 },
                { 0.95039, 0.78823, 0.22831 },
                { 0.95560, 0.78005, 0.22836 },
                { 0.96049, 0.77181, 0.22811 },
                { 0.96507, 0.76352, 0.22754 },
                { 0.96931, 0.75519, 0.22663 },
                { 0.97323, 0.74682, 0.22536 },
                { 0.97679, 0.73842, 0.22369 },
                { 0.98000, 0.73000, 0.22161 },
                { 0.98289, 0.72140, 0.21918 },
                { 0.98549, 0.71250, 0.21650 },
                { 0.98781, 0.70330, 0.21358 },
                { 0.98986, 0.69382, 0.21043 },
                { 0.99163, 0.68408, 0.20706 },
                { 0.99314, 0.67408, 0.20348 },
                { 0.99438, 0.66386, 0.19971 },
                { 0.99535, 0.65341, 0.19577 },
                { 0.99607, 0.64277, 0.19165 },
                { 0.99654, 0.63193, 0.18738 },
                { 0.99675, 0.62093, 0.18297 },
                { 0.99672, 0.60977, 0.17842 },
                { 0.99644, 0.59846, 0.17376 },
                { 0.99593, 0.58703, 0.16899 },
                { 0.99517, 0.57549, 0.16412 },
                { 0.99419, 0.56386, 0.15918 },
                { 0.99297, 0.55214, 0.15417 },
                { 0.99153, 0.54036, 0.14910 },
                { 0.98987, 0.52854, 0.14398 },
                { 0.98799, 0.51667, 0.13883 },
                { 0.98590, 0.50479, 0.13367 },
                { 0.98360, 0.49291, 0.12849 },
                { 0.98108, 0.48104, 0.12332 },
                { 0.97837, 0.46920, 0.11817 },
                { 0.97545, 0.45740, 0.11305 },
                { 0.97234, 0.44565, 0.10797 },
                { 0.96904, 0.43399, 0.10294 },
                { 0.96555, 0.42241, 0.09798 },
                { 0.96187, 0.41093, 0.09310 },
                { 0.95801, 0.39958, 0.08831 },
                { 0.95398, 0.38836, 0.08362 },
                { 0.94977, 0.37729, 0.07905 },
                { 0.94538, 0.36638, 0.07461 },
                { 0.94084, 0.35566, 0.07031 },
                { 0.93612, 0.34513, 0.06616 },
                { 0.93125, 0.33482, 0.06218 },
                { 0.92623, 0.32473, 0.05837 },
                { 0.92105, 0.31489, 0.05475 },
                { 0.91572, 0.30530, 0.05134 },
                { 0.91024, 0.29599, 0.04814 },
                { 0.90463, 0.28696, 0.04516 },
                { 0.89888, 0.27824, 0.04243 },
                { 0.89298, 0.26981, 0.03993 },
                { 0.88691, 0.26152, 0.03753 },
                { 0.88066, 0.25334, 0.03521 },
                { 0.87422, 0.24526, 0.03297 },
                { 0.86760, 0.23730, 0.03082 },
                { 0.86079, 0.22945, 0.02875 },
                { 0.85380, 0.22170, 0.02677 },
                { 0.84662, 0.21407, 0.02487 },
                { 0.83926, 0.20654, 0.02305 },
                { 0.83172, 0.19912, 0.02131 },
                { 0.82399, 0.19182, 0.01966 },
                { 0.81608, 0.18462, 0.01809 },
                { 0.80799, 0.17753, 0.01660 },
                { 0.79971, 0.17055, 0.01520 },
                { 0.79125, 0.16368, 0.01387 },
                { 0.78260, 0.15693, 0.01264 },
                { 0.77377, 0.15028, 0.01148 },
                { 0.76476, 0.14374, 0.01041 },
                { 0.75556, 0.13731, 0.00942 },
                { 0.74617, 0.13098, 0.00851 },
                { 0.73661, 0.12477, 0.00769 },
                { 0.72686, 0.11867, 0.00695 },
                { 0.71692, 0.11268, 0.00629 },
                { 0.70680, 0.10680, 0.00571 },
                { 0.69650, 0.10102, 0.00522 },
                { 0.68602, 0.09536, 0.00481 },
                { 0.67535, 0.08980, 0.00449 },
                { 0.66449, 0.08436, 0.00424 },
                { 0.65345, 0.07902, 0.00408 },
                { 0.64223, 0.07380, 0.00401 },
                { 0.63082, 0.06868, 0.00401 },
                { 0.61923, 0.06367, 0.00410 },
                { 0.60746, 0.05878, 0.00427 },
                { 0.59550, 0.05399, 0.00453 },
                { 0.58336, 0.04931, 0.00486 },
                { 0.57103, 0.04474, 0.00529 },
                { 0.55852, 0.04028, 0.00579 },
                { 0.54583, 0.03593, 0.00638 },
                { 0.53295, 0.03169, 0.00705 },
                { 0.51989, 0.02756, 0.00780 },
                { 0.50664, 0.02354, 0.00863 },
                { 0.49321, 0.01963, 0.00955 },
                { 0.47960, 0.01583, 0.01055 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetHotColor(double x)
    {
        x = internal::Clamp01(x);

        constexpr Color r{ 1.0, 0.0, 0.0 };
        constexpr Color g{ 0.0, 1.0, 0.0 };
        constexpr Color b{ 0.0, 0.0, 1.0 };

        if (x < 0.4)
        {
            const double t = x / 0.4;
            return t * r;
        }
        else if (x < 0.8)
        {
            const double t = (x - 0.4) / (0.8 - 0.4);
            return r + t * g;
        }
        else
        {
            const double t = (x - 0.8) / (1.0 - 0.8);
            return r + g + t * b;
        }
    }

    inline constexpr Color GetGrayColor(double x) noexcept
    {
        return Color{ 1.0 - internal::Clamp01(x) };
    }

    inline Color GetMagmaColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.001462, 0.000466, 0.013866 },
                { 0.002258, 0.001295, 0.018331 },
                { 0.003279, 0.002305, 0.023708 },
                { 0.004512, 0.003490, 0.029965 },
                { 0.005950, 0.004843, 0.037130 },
                { 0.007588, 0.006356, 0.044973 },
                { 0.009426, 0.008022, 0.052844 },
                { 0.011465, 0.009828, 0.060750 },
                { 0.013708, 0.011771, 0.068667 },
                { 0.016156, 0.013840, 0.076603 },
                { 0.018815, 0.016026, 0.084584 },
                { 0.021692, 0.018320, 0.092610 },
                { 0.024792, 0.020715, 0.100676 },
                { 0.028123, 0.023201, 0.108787 },
                { 0.031696, 0.025765, 0.116965 },
                { 0.035520, 0.028397, 0.125209 },
                { 0.039608, 0.031090, 0.133515 },
                { 0.043830, 0.033830, 0.141886 },
                { 0.048062, 0.036607, 0.150327 },
                { 0.052320, 0.039407, 0.158841 },
                { 0.056615, 0.042160, 0.167446 },
                { 0.060949, 0.044794, 0.176129 },
                { 0.065330, 0.047318, 0.184892 },
                { 0.069764, 0.049726, 0.193735 },
                { 0.074257, 0.052017, 0.202660 },
                { 0.078815, 0.054184, 0.211667 },
                { 0.083446, 0.056225, 0.220755 },
                { 0.088155, 0.058133, 0.229922 },
                { 0.092949, 0.059904, 0.239164 },
                { 0.097833, 0.061531, 0.248477 },
                { 0.102815, 0.063010, 0.257854 },
                { 0.107899, 0.064335, 0.267289 },
                { 0.113094, 0.065492, 0.276784 },
                { 0.118405, 0.066479, 0.286321 },
                { 0.123833, 0.067295, 0.295879 },
                { 0.129380, 0.067935, 0.305443 },
                { 0.135053, 0.068391, 0.315000 },
                { 0.140858, 0.068654, 0.324538 },
                { 0.146785, 0.068738, 0.334011 },
                { 0.152839, 0.068637, 0.343404 },
                { 0.159018, 0.068354, 0.352688 },
                { 0.165308, 0.067911, 0.361816 },
                { 0.171713, 0.067305, 0.370771 },
                { 0.178212, 0.066576, 0.379497 },
                { 0.184801, 0.065732, 0.387973 },
                { 0.191460, 0.064818, 0.396152 },
                { 0.198177, 0.063862, 0.404009 },
                { 0.204935, 0.062907, 0.411514 },
                { 0.211718, 0.061992, 0.418647 },
                { 0.218512, 0.061158, 0.425392 },
                { 0.225302, 0.060445, 0.431742 },
                { 0.232077, 0.059889, 0.437695 },
                { 0.238826, 0.059517, 0.443256 },
                { 0.245543, 0.059352, 0.448436 },
                { 0.252220, 0.059415, 0.453248 },
                { 0.258857, 0.059706, 0.457710 },
                { 0.265447, 0.060237, 0.461840 },
                { 0.271994, 0.060994, 0.465660 },
                { 0.278493, 0.061978, 0.469190 },
                { 0.284951, 0.063168, 0.472451 },
                { 0.291366, 0.064553, 0.475462 },
                { 0.297740, 0.066117, 0.478243 },
                { 0.304081, 0.067835, 0.480812 },
                { 0.310382, 0.069702, 0.483186 },
                { 0.316654, 0.071690, 0.485380 },
                { 0.322899, 0.073782, 0.487408 },
                { 0.329114, 0.075972, 0.489287 },
                { 0.335308, 0.078236, 0.491024 },
                { 0.341482, 0.080564, 0.492631 },
                { 0.347636, 0.082946, 0.494121 },
                { 0.353773, 0.085373, 0.495501 },
                { 0.359898, 0.087831, 0.496778 },
                { 0.366012, 0.090314, 0.497960 },
                { 0.372116, 0.092816, 0.499053 },
                { 0.378211, 0.095332, 0.500067 },
                { 0.384299, 0.097855, 0.501002 },
                { 0.390384, 0.100379, 0.501864 },
                { 0.396467, 0.102902, 0.502658 },
                { 0.402548, 0.105420, 0.503386 },
                { 0.408629, 0.107930, 0.504052 },
                { 0.414709, 0.110431, 0.504662 },
                { 0.420791, 0.112920, 0.505215 },
                { 0.426877, 0.115395, 0.505714 },
                { 0.432967, 0.117855, 0.506160 },
                { 0.439062, 0.120298, 0.506555 },
                { 0.445163, 0.122724, 0.506901 },
                { 0.451271, 0.125132, 0.507198 },
                { 0.457386, 0.127522, 0.507448 },
                { 0.463508, 0.129893, 0.507652 },
                { 0.469640, 0.132245, 0.507809 },
                { 0.475780, 0.134577, 0.507921 },
                { 0.481929, 0.136891, 0.507989 },
                { 0.488088, 0.139186, 0.508011 },
                { 0.494258, 0.141462, 0.507988 },
                { 0.500438, 0.143719, 0.507920 },
                { 0.506629, 0.145958, 0.507806 },
                { 0.512831, 0.148179, 0.507648 },
                { 0.519045, 0.150383, 0.507443 },
                { 0.525270, 0.152569, 0.507192 },
                { 0.531507, 0.154739, 0.506895 },
                { 0.537755, 0.156894, 0.506551 },
                { 0.544015, 0.159033, 0.506159 },
                { 0.550287, 0.161158, 0.505719 },
                { 0.556571, 0.163269, 0.505230 },
                { 0.562866, 0.165368, 0.504692 },
                { 0.569172, 0.167454, 0.504105 },
                { 0.575490, 0.169530, 0.503466 },
                { 0.581819, 0.171596, 0.502777 },
                { 0.588158, 0.173652, 0.502035 },
                { 0.594508, 0.175701, 0.501241 },
                { 0.600868, 0.177743, 0.500394 },
                { 0.607238, 0.179779, 0.499492 },
                { 0.613617, 0.181811, 0.498536 },
                { 0.620005, 0.183840, 0.497524 },
                { 0.626401, 0.185867, 0.496456 },
                { 0.632805, 0.187893, 0.495332 },
                { 0.639216, 0.189921, 0.494150 },
                { 0.645633, 0.191952, 0.492910 },
                { 0.652056, 0.193986, 0.491611 },
                { 0.658483, 0.196027, 0.490253 },
                { 0.664915, 0.198075, 0.488836 },
                { 0.671349, 0.200133, 0.487358 },
                { 0.677786, 0.202203, 0.485819 },
                { 0.684224, 0.204286, 0.484219 },
                { 0.690661, 0.206384, 0.482558 },
                { 0.697098, 0.208501, 0.480835 },
                { 0.703532, 0.210638, 0.479049 },
                { 0.709962, 0.212797, 0.477201 },
                { 0.716387, 0.214982, 0.475290 },
                { 0.722805, 0.217194, 0.473316 },
                { 0.729216, 0.219437, 0.471279 },
                { 0.735616, 0.221713, 0.469180 },
                { 0.742004, 0.224025, 0.467018 },
                { 0.748378, 0.226377, 0.464794 },
                { 0.754737, 0.228772, 0.462509 },
                { 0.761077, 0.231214, 0.460162 },
                { 0.767398, 0.233705, 0.457755 },
                { 0.773695, 0.236249, 0.455289 },
                { 0.779968, 0.238851, 0.452765 },
                { 0.786212, 0.241514, 0.450184 },
                { 0.792427, 0.244242, 0.447543 },
                { 0.798608, 0.247040, 0.444848 },
                { 0.804752, 0.249911, 0.442102 },
                { 0.810855, 0.252861, 0.439305 },
                { 0.816914, 0.255895, 0.436461 },
                { 0.822926, 0.259016, 0.433573 },
                { 0.828886, 0.262229, 0.430644 },
                { 0.834791, 0.265540, 0.427671 },
                { 0.840636, 0.268953, 0.424666 },
                { 0.846416, 0.272473, 0.421631 },
                { 0.852126, 0.276106, 0.418573 },
                { 0.857763, 0.279857, 0.415496 },
                { 0.863320, 0.283729, 0.412403 },
                { 0.868793, 0.287728, 0.409303 },
                { 0.874176, 0.291859, 0.406205 },
                { 0.879464, 0.296125, 0.403118 },
                { 0.884651, 0.300530, 0.400047 },
                { 0.889731, 0.305079, 0.397002 },
                { 0.894700, 0.309773, 0.393995 },
                { 0.899552, 0.314616, 0.391037 },
                { 0.904281, 0.319610, 0.388137 },
                { 0.908884, 0.324755, 0.385308 },
                { 0.913354, 0.330052, 0.382563 },
                { 0.917689, 0.335500, 0.379915 },
                { 0.921884, 0.341098, 0.377376 },
                { 0.925937, 0.346844, 0.374959 },
                { 0.929845, 0.352734, 0.372677 },
                { 0.933606, 0.358764, 0.370541 },
                { 0.937221, 0.364929, 0.368567 },
                { 0.940687, 0.371224, 0.366762 },
                { 0.944006, 0.377643, 0.365136 },
                { 0.947180, 0.384178, 0.363701 },
                { 0.950210, 0.390820, 0.362468 },
                { 0.953099, 0.397563, 0.361438 },
                { 0.955849, 0.404400, 0.360619 },
                { 0.958464, 0.411324, 0.360014 },
                { 0.960949, 0.418323, 0.359630 },
                { 0.963310, 0.425390, 0.359469 },
                { 0.965549, 0.432519, 0.359529 },
                { 0.967671, 0.439703, 0.359810 },
                { 0.969680, 0.446936, 0.360311 },
                { 0.971582, 0.454210, 0.361030 },
                { 0.973381, 0.461520, 0.361965 },
                { 0.975082, 0.468861, 0.363111 },
                { 0.976690, 0.476226, 0.364466 },
                { 0.978210, 0.483612, 0.366025 },
                { 0.979645, 0.491014, 0.367783 },
                { 0.981000, 0.498428, 0.369734 },
                { 0.982279, 0.505851, 0.371874 },
                { 0.983485, 0.513280, 0.374198 },
                { 0.984622, 0.520713, 0.376698 },
                { 0.985693, 0.528148, 0.379371 },
                { 0.986700, 0.535582, 0.382210 },
                { 0.987646, 0.543015, 0.385210 },
                { 0.988533, 0.550446, 0.388365 },
                { 0.989363, 0.557873, 0.391671 },
                { 0.990138, 0.565296, 0.395122 },
                { 0.990871, 0.572706, 0.398714 },
                { 0.991558, 0.580107, 0.402441 },
                { 0.992196, 0.587502, 0.406299 },
                { 0.992785, 0.594891, 0.410283 },
                { 0.993326, 0.602275, 0.414390 },
                { 0.993834, 0.609644, 0.418613 },
                { 0.994309, 0.616999, 0.422950 },
                { 0.994738, 0.624350, 0.427397 },
                { 0.995122, 0.631696, 0.431951 },
                { 0.995480, 0.639027, 0.436607 },
                { 0.995810, 0.646344, 0.441361 },
                { 0.996096, 0.653659, 0.446213 },
                { 0.996341, 0.660969, 0.451160 },
                { 0.996580, 0.668256, 0.456192 },
                { 0.996775, 0.675541, 0.461314 },
                { 0.996925, 0.682828, 0.466526 },
                { 0.997077, 0.690088, 0.471811 },
                { 0.997186, 0.697349, 0.477182 },
                { 0.997254, 0.704611, 0.482635 },
                { 0.997325, 0.711848, 0.488154 },
                { 0.997351, 0.719089, 0.493755 },
                { 0.997351, 0.726324, 0.499428 },
                { 0.997341, 0.733545, 0.505167 },
                { 0.997285, 0.740772, 0.510983 },
                { 0.997228, 0.747981, 0.516859 },
                { 0.997138, 0.755190, 0.522806 },
                { 0.997019, 0.762398, 0.528821 },
                { 0.996898, 0.769591, 0.534892 },
                { 0.996727, 0.776795, 0.541039 },
                { 0.996571, 0.783977, 0.547233 },
                { 0.996369, 0.791167, 0.553499 },
                { 0.996162, 0.798348, 0.559820 },
                { 0.995932, 0.805527, 0.566202 },
                { 0.995680, 0.812706, 0.572645 },
                { 0.995424, 0.819875, 0.579140 },
                { 0.995131, 0.827052, 0.585701 },
                { 0.994851, 0.834213, 0.592307 },
                { 0.994524, 0.841387, 0.598983 },
                { 0.994222, 0.848540, 0.605696 },
                { 0.993866, 0.855711, 0.612482 },
                { 0.993545, 0.862859, 0.619299 },
                { 0.993170, 0.870024, 0.626189 },
                { 0.992831, 0.877168, 0.633109 },
                { 0.992440, 0.884330, 0.640099 },
                { 0.992089, 0.891470, 0.647116 },
                { 0.991688, 0.898627, 0.654202 },
                { 0.991332, 0.905763, 0.661309 },
                { 0.990930, 0.912915, 0.668481 },
                { 0.990570, 0.920049, 0.675675 },
                { 0.990175, 0.927196, 0.682926 },
                { 0.989815, 0.934329, 0.690198 },
                { 0.989434, 0.941470, 0.697519 },
                { 0.989077, 0.948604, 0.704863 },
                { 0.988717, 0.955742, 0.712242 },
                { 0.988367, 0.962878, 0.719649 },
                { 0.988033, 0.970012, 0.727077 },
                { 0.987691, 0.977154, 0.734536 },
                { 0.987387, 0.984288, 0.742002 },
                { 0.987053, 0.991438, 0.749504 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetInfernoColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.001462, 0.000466, 0.013866 },
                { 0.002267, 0.001270, 0.018570 },
                { 0.003299, 0.002249, 0.024239 },
                { 0.004547, 0.003392, 0.030909 },
                { 0.006006, 0.004692, 0.038558 },
                { 0.007676, 0.006136, 0.046836 },
                { 0.009561, 0.007713, 0.055143 },
                { 0.011663, 0.009417, 0.063460 },
                { 0.013995, 0.011225, 0.071862 },
                { 0.016561, 0.013136, 0.080282 },
                { 0.019373, 0.015133, 0.088767 },
                { 0.022447, 0.017199, 0.097327 },
                { 0.025793, 0.019331, 0.105930 },
                { 0.029432, 0.021503, 0.114621 },
                { 0.033385, 0.023702, 0.123397 },
                { 0.037668, 0.025921, 0.132232 },
                { 0.042253, 0.028139, 0.141141 },
                { 0.046915, 0.030324, 0.150164 },
                { 0.051644, 0.032474, 0.159254 },
                { 0.056449, 0.034569, 0.168414 },
                { 0.061340, 0.036590, 0.177642 },
                { 0.066331, 0.038504, 0.186962 },
                { 0.071429, 0.040294, 0.196354 },
                { 0.076637, 0.041905, 0.205799 },
                { 0.081962, 0.043328, 0.215289 },
                { 0.087411, 0.044556, 0.224813 },
                { 0.092990, 0.045583, 0.234358 },
                { 0.098702, 0.046402, 0.243904 },
                { 0.104551, 0.047008, 0.253430 },
                { 0.110536, 0.047399, 0.262912 },
                { 0.116656, 0.047574, 0.272321 },
                { 0.122908, 0.047536, 0.281624 },
                { 0.129285, 0.047293, 0.290788 },
                { 0.135778, 0.046856, 0.299776 },
                { 0.142378, 0.046242, 0.308553 },
                { 0.149073, 0.045468, 0.317085 },
                { 0.155850, 0.044559, 0.325338 },
                { 0.162689, 0.043554, 0.333277 },
                { 0.169575, 0.042489, 0.340874 },
                { 0.176493, 0.041402, 0.348111 },
                { 0.183429, 0.040329, 0.354971 },
                { 0.190367, 0.039309, 0.361447 },
                { 0.197297, 0.038400, 0.367535 },
                { 0.204209, 0.037632, 0.373238 },
                { 0.211095, 0.037030, 0.378563 },
                { 0.217949, 0.036615, 0.383522 },
                { 0.224763, 0.036405, 0.388129 },
                { 0.231538, 0.036405, 0.392400 },
                { 0.238273, 0.036621, 0.396353 },
                { 0.244967, 0.037055, 0.400007 },
                { 0.251620, 0.037705, 0.403378 },
                { 0.258234, 0.038571, 0.406485 },
                { 0.264810, 0.039647, 0.409345 },
                { 0.271347, 0.040922, 0.411976 },
                { 0.277850, 0.042353, 0.414392 },
                { 0.284321, 0.043933, 0.416608 },
                { 0.290763, 0.045644, 0.418637 },
                { 0.297178, 0.047470, 0.420491 },
                { 0.303568, 0.049396, 0.422182 },
                { 0.309935, 0.051407, 0.423721 },
                { 0.316282, 0.053490, 0.425116 },
                { 0.322610, 0.055634, 0.426377 },
                { 0.328921, 0.057827, 0.427511 },
                { 0.335217, 0.060060, 0.428524 },
                { 0.341500, 0.062325, 0.429425 },
                { 0.347771, 0.064616, 0.430217 },
                { 0.354032, 0.066925, 0.430906 },
                { 0.360284, 0.069247, 0.431497 },
                { 0.366529, 0.071579, 0.431994 },
                { 0.372768, 0.073915, 0.432400 },
                { 0.379001, 0.076253, 0.432719 },
                { 0.385228, 0.078591, 0.432955 },
                { 0.391453, 0.080927, 0.433109 },
                { 0.397674, 0.083257, 0.433183 },
                { 0.403894, 0.085580, 0.433179 },
                { 0.410113, 0.087896, 0.433098 },
                { 0.416331, 0.090203, 0.432943 },
                { 0.422549, 0.092501, 0.432714 },
                { 0.428768, 0.094790, 0.432412 },
                { 0.434987, 0.097069, 0.432039 },
                { 0.441207, 0.099338, 0.431594 },
                { 0.447428, 0.101597, 0.431080 },
                { 0.453651, 0.103848, 0.430498 },
                { 0.459875, 0.106089, 0.429846 },
                { 0.466100, 0.108322, 0.429125 },
                { 0.472328, 0.110547, 0.428334 },
                { 0.478558, 0.112764, 0.427475 },
                { 0.484789, 0.114974, 0.426548 },
                { 0.491022, 0.117179, 0.425552 },
                { 0.497257, 0.119379, 0.424488 },
                { 0.503493, 0.121575, 0.423356 },
                { 0.509730, 0.123769, 0.422156 },
                { 0.515967, 0.125960, 0.420887 },
                { 0.522206, 0.128150, 0.419549 },
                { 0.528444, 0.130341, 0.418142 },
                { 0.534683, 0.132534, 0.416667 },
                { 0.540920, 0.134729, 0.415123 },
                { 0.547157, 0.136929, 0.413511 },
                { 0.553392, 0.139134, 0.411829 },
                { 0.559624, 0.141346, 0.410078 },
                { 0.565854, 0.143567, 0.408258 },
                { 0.572081, 0.145797, 0.406369 },
                { 0.578304, 0.148039, 0.404411 },
                { 0.584521, 0.150294, 0.402385 },
                { 0.590734, 0.152563, 0.400290 },
                { 0.596940, 0.154848, 0.398125 },
                { 0.603139, 0.157151, 0.395891 },
                { 0.609330, 0.159474, 0.393589 },
                { 0.615513, 0.161817, 0.391219 },
                { 0.621685, 0.164184, 0.388781 },
                { 0.627847, 0.166575, 0.386276 },
                { 0.633998, 0.168992, 0.383704 },
                { 0.640135, 0.171438, 0.381065 },
                { 0.646260, 0.173914, 0.378359 },
                { 0.652369, 0.176421, 0.375586 },
                { 0.658463, 0.178962, 0.372748 },
                { 0.664540, 0.181539, 0.369846 },
                { 0.670599, 0.184153, 0.366879 },
                { 0.676638, 0.186807, 0.363849 },
                { 0.682656, 0.189501, 0.360757 },
                { 0.688653, 0.192239, 0.357603 },
                { 0.694627, 0.195021, 0.354388 },
                { 0.700576, 0.197851, 0.351113 },
                { 0.706500, 0.200728, 0.347777 },
                { 0.712396, 0.203656, 0.344383 },
                { 0.718264, 0.206636, 0.340931 },
                { 0.724103, 0.209670, 0.337424 },
                { 0.729909, 0.212759, 0.333861 },
                { 0.735683, 0.215906, 0.330245 },
                { 0.741423, 0.219112, 0.326576 },
                { 0.747127, 0.222378, 0.322856 },
                { 0.752794, 0.225706, 0.319085 },
                { 0.758422, 0.229097, 0.315266 },
                { 0.764010, 0.232554, 0.311399 },
                { 0.769556, 0.236077, 0.307485 },
                { 0.775059, 0.239667, 0.303526 },
                { 0.780517, 0.243327, 0.299523 },
                { 0.785929, 0.247056, 0.295477 },
                { 0.791293, 0.250856, 0.291390 },
                { 0.796607, 0.254728, 0.287264 },
                { 0.801871, 0.258674, 0.283099 },
                { 0.807082, 0.262692, 0.278898 },
                { 0.812239, 0.266786, 0.274661 },
                { 0.817341, 0.270954, 0.270390 },
                { 0.822386, 0.275197, 0.266085 },
                { 0.827372, 0.279517, 0.261750 },
                { 0.832299, 0.283913, 0.257383 },
                { 0.837165, 0.288385, 0.252988 },
                { 0.841969, 0.292933, 0.248564 },
                { 0.846709, 0.297559, 0.244113 },
                { 0.851384, 0.302260, 0.239636 },
                { 0.855992, 0.307038, 0.235133 },
                { 0.860533, 0.311892, 0.230606 },
                { 0.865006, 0.316822, 0.226055 },
                { 0.869409, 0.321827, 0.221482 },
                { 0.873741, 0.326906, 0.216886 },
                { 0.878001, 0.332060, 0.212268 },
                { 0.882188, 0.337287, 0.207628 },
                { 0.886302, 0.342586, 0.202968 },
                { 0.890341, 0.347957, 0.198286 },
                { 0.894305, 0.353399, 0.193584 },
                { 0.898192, 0.358911, 0.188860 },
                { 0.902003, 0.364492, 0.184116 },
                { 0.905735, 0.370140, 0.179350 },
                { 0.909390, 0.375856, 0.174563 },
                { 0.912966, 0.381636, 0.169755 },
                { 0.916462, 0.387481, 0.164924 },
                { 0.919879, 0.393389, 0.160070 },
                { 0.923215, 0.399359, 0.155193 },
                { 0.926470, 0.405389, 0.150292 },
                { 0.929644, 0.411479, 0.145367 },
                { 0.932737, 0.417627, 0.140417 },
                { 0.935747, 0.423831, 0.135440 },
                { 0.938675, 0.430091, 0.130438 },
                { 0.941521, 0.436405, 0.125409 },
                { 0.944285, 0.442772, 0.120354 },
                { 0.946965, 0.449191, 0.115272 },
                { 0.949562, 0.455660, 0.110164 },
                { 0.952075, 0.462178, 0.105031 },
                { 0.954506, 0.468744, 0.099874 },
                { 0.956852, 0.475356, 0.094695 },
                { 0.959114, 0.482014, 0.089499 },
                { 0.961293, 0.488716, 0.084289 },
                { 0.963387, 0.495462, 0.079073 },
                { 0.965397, 0.502249, 0.073859 },
                { 0.967322, 0.509078, 0.068659 },
                { 0.969163, 0.515946, 0.063488 },
                { 0.970919, 0.522853, 0.058367 },
                { 0.972590, 0.529798, 0.053324 },
                { 0.974176, 0.536780, 0.048392 },
                { 0.975677, 0.543798, 0.043618 },
                { 0.977092, 0.550850, 0.039050 },
                { 0.978422, 0.557937, 0.034931 },
                { 0.979666, 0.565057, 0.031409 },
                { 0.980824, 0.572209, 0.028508 },
                { 0.981895, 0.579392, 0.026250 },
                { 0.982881, 0.586606, 0.024661 },
                { 0.983779, 0.593849, 0.023770 },
                { 0.984591, 0.601122, 0.023606 },
                { 0.985315, 0.608422, 0.024202 },
                { 0.985952, 0.615750, 0.025592 },
                { 0.986502, 0.623105, 0.027814 },
                { 0.986964, 0.630485, 0.030908 },
                { 0.987337, 0.637890, 0.034916 },
                { 0.987622, 0.645320, 0.039886 },
                { 0.987819, 0.652773, 0.045581 },
                { 0.987926, 0.660250, 0.051750 },
                { 0.987945, 0.667748, 0.058329 },
                { 0.987874, 0.675267, 0.065257 },
                { 0.987714, 0.682807, 0.072489 },
                { 0.987464, 0.690366, 0.079990 },
                { 0.987124, 0.697944, 0.087731 },
                { 0.986694, 0.705540, 0.095694 },
                { 0.986175, 0.713153, 0.103863 },
                { 0.985566, 0.720782, 0.112229 },
                { 0.984865, 0.728427, 0.120785 },
                { 0.984075, 0.736087, 0.129527 },
                { 0.983196, 0.743758, 0.138453 },
                { 0.982228, 0.751442, 0.147565 },
                { 0.981173, 0.759135, 0.156863 },
                { 0.980032, 0.766837, 0.166353 },
                { 0.978806, 0.774545, 0.176037 },
                { 0.977497, 0.782258, 0.185923 },
                { 0.976108, 0.789974, 0.196018 },
                { 0.974638, 0.797692, 0.206332 },
                { 0.973088, 0.805409, 0.216877 },
                { 0.971468, 0.813122, 0.227658 },
                { 0.969783, 0.820825, 0.238686 },
                { 0.968041, 0.828515, 0.249972 },
                { 0.966243, 0.836191, 0.261534 },
                { 0.964394, 0.843848, 0.273391 },
                { 0.962517, 0.851476, 0.285546 },
                { 0.960626, 0.859069, 0.298010 },
                { 0.958720, 0.866624, 0.310820 },
                { 0.956834, 0.874129, 0.323974 },
                { 0.954997, 0.881569, 0.337475 },
                { 0.953215, 0.888942, 0.351369 },
                { 0.951546, 0.896226, 0.365627 },
                { 0.950018, 0.903409, 0.380271 },
                { 0.948683, 0.910473, 0.395289 },
                { 0.947594, 0.917399, 0.410665 },
                { 0.946809, 0.924168, 0.426373 },
                { 0.946392, 0.930761, 0.442367 },
                { 0.946403, 0.937159, 0.458592 },
                { 0.946903, 0.943348, 0.474970 },
                { 0.947937, 0.949318, 0.491426 },
                { 0.949545, 0.955063, 0.507860 },
                { 0.951740, 0.960587, 0.524203 },
                { 0.954529, 0.965896, 0.540361 },
                { 0.957896, 0.971003, 0.556275 },
                { 0.961812, 0.975924, 0.571925 },
                { 0.966249, 0.980678, 0.587206 },
                { 0.971162, 0.985282, 0.602154 },
                { 0.976511, 0.989753, 0.616760 },
                { 0.982257, 0.994109, 0.631017 },
                { 0.988362, 0.998364, 0.644924 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetPlasmaColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.050383, 0.029803, 0.527975 },
                { 0.063536, 0.028426, 0.533124 },
                { 0.075353, 0.027206, 0.538007 },
                { 0.086222, 0.026125, 0.542658 },
                { 0.096379, 0.025165, 0.547103 },
                { 0.105980, 0.024309, 0.551368 },
                { 0.115124, 0.023556, 0.555468 },
                { 0.123903, 0.022878, 0.559423 },
                { 0.132381, 0.022258, 0.563250 },
                { 0.140603, 0.021687, 0.566959 },
                { 0.148607, 0.021154, 0.570562 },
                { 0.156421, 0.020651, 0.574065 },
                { 0.164070, 0.020171, 0.577478 },
                { 0.171574, 0.019706, 0.580806 },
                { 0.178950, 0.019252, 0.584054 },
                { 0.186213, 0.018803, 0.587228 },
                { 0.193374, 0.018354, 0.590330 },
                { 0.200445, 0.017902, 0.593364 },
                { 0.207435, 0.017442, 0.596333 },
                { 0.214350, 0.016973, 0.599239 },
                { 0.221197, 0.016497, 0.602083 },
                { 0.227983, 0.016007, 0.604867 },
                { 0.234715, 0.015502, 0.607592 },
                { 0.241396, 0.014979, 0.610259 },
                { 0.248032, 0.014439, 0.612868 },
                { 0.254627, 0.013882, 0.615419 },
                { 0.261183, 0.013308, 0.617911 },
                { 0.267703, 0.012716, 0.620346 },
                { 0.274191, 0.012109, 0.622722 },
                { 0.280648, 0.011488, 0.625038 },
                { 0.287076, 0.010855, 0.627295 },
                { 0.293478, 0.010213, 0.629490 },
                { 0.299855, 0.009561, 0.631624 },
                { 0.306210, 0.008902, 0.633694 },
                { 0.312543, 0.008239, 0.635700 },
                { 0.318856, 0.007576, 0.637640 },
                { 0.325150, 0.006915, 0.639512 },
                { 0.331426, 0.006261, 0.641316 },
                { 0.337683, 0.005618, 0.643049 },
                { 0.343925, 0.004991, 0.644710 },
                { 0.350150, 0.004382, 0.646298 },
                { 0.356359, 0.003798, 0.647810 },
                { 0.362553, 0.003243, 0.649245 },
                { 0.368733, 0.002724, 0.650601 },
                { 0.374897, 0.002245, 0.651876 },
                { 0.381047, 0.001814, 0.653068 },
                { 0.387183, 0.001434, 0.654177 },
                { 0.393304, 0.001114, 0.655199 },
                { 0.399411, 0.000859, 0.656133 },
                { 0.405503, 0.000678, 0.656977 },
                { 0.411580, 0.000577, 0.657730 },
                { 0.417642, 0.000564, 0.658390 },
                { 0.423689, 0.000646, 0.658956 },
                { 0.429719, 0.000831, 0.659425 },
                { 0.435734, 0.001127, 0.659797 },
                { 0.441732, 0.001540, 0.660069 },
                { 0.447714, 0.002080, 0.660240 },
                { 0.453677, 0.002755, 0.660310 },
                { 0.459623, 0.003574, 0.660277 },
                { 0.465550, 0.004545, 0.660139 },
                { 0.471457, 0.005678, 0.659897 },
                { 0.477344, 0.006980, 0.659549 },
                { 0.483210, 0.008460, 0.659095 },
                { 0.489055, 0.010127, 0.658534 },
                { 0.494877, 0.011990, 0.657865 },
                { 0.500678, 0.014055, 0.657088 },
                { 0.506454, 0.016333, 0.656202 },
                { 0.512206, 0.018833, 0.655209 },
                { 0.517933, 0.021563, 0.654109 },
                { 0.523633, 0.024532, 0.652901 },
                { 0.529306, 0.027747, 0.651586 },
                { 0.534952, 0.031217, 0.650165 },
                { 0.540570, 0.034950, 0.648640 },
                { 0.546157, 0.038954, 0.647010 },
                { 0.551715, 0.043136, 0.645277 },
                { 0.557243, 0.047331, 0.643443 },
                { 0.562738, 0.051545, 0.641509 },
                { 0.568201, 0.055778, 0.639477 },
                { 0.573632, 0.060028, 0.637349 },
                { 0.579029, 0.064296, 0.635126 },
                { 0.584391, 0.068579, 0.632812 },
                { 0.589719, 0.072878, 0.630408 },
                { 0.595011, 0.077190, 0.627917 },
                { 0.600266, 0.081516, 0.625342 },
                { 0.605485, 0.085854, 0.622686 },
                { 0.610667, 0.090204, 0.619951 },
                { 0.615812, 0.094564, 0.617140 },
                { 0.620919, 0.098934, 0.614257 },
                { 0.625987, 0.103312, 0.611305 },
                { 0.631017, 0.107699, 0.608287 },
                { 0.636008, 0.112092, 0.605205 },
                { 0.640959, 0.116492, 0.602065 },
                { 0.645872, 0.120898, 0.598867 },
                { 0.650746, 0.125309, 0.595617 },
                { 0.655580, 0.129725, 0.592317 },
                { 0.660374, 0.134144, 0.588971 },
                { 0.665129, 0.138566, 0.585582 },
                { 0.669845, 0.142992, 0.582154 },
                { 0.674522, 0.147419, 0.578688 },
                { 0.679160, 0.151848, 0.575189 },
                { 0.683758, 0.156278, 0.571660 },
                { 0.688318, 0.160709, 0.568103 },
                { 0.692840, 0.165141, 0.564522 },
                { 0.697324, 0.169573, 0.560919 },
                { 0.701769, 0.174005, 0.557296 },
                { 0.706178, 0.178437, 0.553657 },
                { 0.710549, 0.182868, 0.550004 },
                { 0.714883, 0.187299, 0.546338 },
                { 0.719181, 0.191729, 0.542663 },
                { 0.723444, 0.196158, 0.538981 },
                { 0.727670, 0.200586, 0.535293 },
                { 0.731862, 0.205013, 0.531601 },
                { 0.736019, 0.209439, 0.527908 },
                { 0.740143, 0.213864, 0.524216 },
                { 0.744232, 0.218288, 0.520524 },
                { 0.748289, 0.222711, 0.516834 },
                { 0.752312, 0.227133, 0.513149 },
                { 0.756304, 0.231555, 0.509468 },
                { 0.760264, 0.235976, 0.505794 },
                { 0.764193, 0.240396, 0.502126 },
                { 0.768090, 0.244817, 0.498465 },
                { 0.771958, 0.249237, 0.494813 },
                { 0.775796, 0.253658, 0.491171 },
                { 0.779604, 0.258078, 0.487539 },
                { 0.783383, 0.262500, 0.483918 },
                { 0.787133, 0.266922, 0.480307 },
                { 0.790855, 0.271345, 0.476706 },
                { 0.794549, 0.275770, 0.473117 },
                { 0.798216, 0.280197, 0.469538 },
                { 0.801855, 0.284626, 0.465971 },
                { 0.805467, 0.289057, 0.462415 },
                { 0.809052, 0.293491, 0.458870 },
                { 0.812612, 0.297928, 0.455338 },
                { 0.816144, 0.302368, 0.451816 },
                { 0.819651, 0.306812, 0.448306 },
                { 0.823132, 0.311261, 0.444806 },
                { 0.826588, 0.315714, 0.441316 },
                { 0.830018, 0.320172, 0.437836 },
                { 0.833422, 0.324635, 0.434366 },
                { 0.836801, 0.329105, 0.430905 },
                { 0.840155, 0.333580, 0.427455 },
                { 0.843484, 0.338062, 0.424013 },
                { 0.846788, 0.342551, 0.420579 },
                { 0.850066, 0.347048, 0.417153 },
                { 0.853319, 0.351553, 0.413734 },
                { 0.856547, 0.356066, 0.410322 },
                { 0.859750, 0.360588, 0.406917 },
                { 0.862927, 0.365119, 0.403519 },
                { 0.866078, 0.369660, 0.400126 },
                { 0.869203, 0.374212, 0.396738 },
                { 0.872303, 0.378774, 0.393355 },
                { 0.875376, 0.383347, 0.389976 },
                { 0.878423, 0.387932, 0.386600 },
                { 0.881443, 0.392529, 0.383229 },
                { 0.884436, 0.397139, 0.379860 },
                { 0.887402, 0.401762, 0.376494 },
                { 0.890340, 0.406398, 0.373130 },
                { 0.893250, 0.411048, 0.369768 },
                { 0.896131, 0.415712, 0.366407 },
                { 0.898984, 0.420392, 0.363047 },
                { 0.901807, 0.425087, 0.359688 },
                { 0.904601, 0.429797, 0.356329 },
                { 0.907365, 0.434524, 0.352970 },
                { 0.910098, 0.439268, 0.349610 },
                { 0.912800, 0.444029, 0.346251 },
                { 0.915471, 0.448807, 0.342890 },
                { 0.918109, 0.453603, 0.339529 },
                { 0.920714, 0.458417, 0.336166 },
                { 0.923287, 0.463251, 0.332801 },
                { 0.925825, 0.468103, 0.329435 },
                { 0.928329, 0.472975, 0.326067 },
                { 0.930798, 0.477867, 0.322697 },
                { 0.933232, 0.482780, 0.319325 },
                { 0.935630, 0.487712, 0.315952 },
                { 0.937990, 0.492667, 0.312575 },
                { 0.940313, 0.497642, 0.309197 },
                { 0.942598, 0.502639, 0.305816 },
                { 0.944844, 0.507658, 0.302433 },
                { 0.947051, 0.512699, 0.299049 },
                { 0.949217, 0.517763, 0.295662 },
                { 0.951344, 0.522850, 0.292275 },
                { 0.953428, 0.527960, 0.288883 },
                { 0.955470, 0.533093, 0.285490 },
                { 0.957469, 0.538250, 0.282096 },
                { 0.959424, 0.543431, 0.278701 },
                { 0.961336, 0.548636, 0.275305 },
                { 0.963203, 0.553865, 0.271909 },
                { 0.965024, 0.559118, 0.268513 },
                { 0.966798, 0.564396, 0.265118 },
                { 0.968526, 0.569700, 0.261721 },
                { 0.970205, 0.575028, 0.258325 },
                { 0.971835, 0.580382, 0.254931 },
                { 0.973416, 0.585761, 0.251540 },
                { 0.974947, 0.591165, 0.248151 },
                { 0.976428, 0.596595, 0.244767 },
                { 0.977856, 0.602051, 0.241387 },
                { 0.979233, 0.607532, 0.238013 },
                { 0.980556, 0.613039, 0.234646 },
                { 0.981826, 0.618572, 0.231287 },
                { 0.983041, 0.624131, 0.227937 },
                { 0.984199, 0.629718, 0.224595 },
                { 0.985301, 0.635330, 0.221265 },
                { 0.986345, 0.640969, 0.217948 },
                { 0.987332, 0.646633, 0.214648 },
                { 0.988260, 0.652325, 0.211364 },
                { 0.989128, 0.658043, 0.208100 },
                { 0.989935, 0.663787, 0.204859 },
                { 0.990681, 0.669558, 0.201642 },
                { 0.991365, 0.675355, 0.198453 },
                { 0.991985, 0.681179, 0.195295 },
                { 0.992541, 0.687030, 0.192170 },
                { 0.993032, 0.692907, 0.189084 },
                { 0.993456, 0.698810, 0.186041 },
                { 0.993814, 0.704741, 0.183043 },
                { 0.994103, 0.710698, 0.180097 },
                { 0.994324, 0.716681, 0.177208 },
                { 0.994474, 0.722691, 0.174381 },
                { 0.994553, 0.728728, 0.171622 },
                { 0.994561, 0.734791, 0.168938 },
                { 0.994495, 0.740880, 0.166335 },
                { 0.994355, 0.746995, 0.163821 },
                { 0.994141, 0.753137, 0.161404 },
                { 0.993851, 0.759304, 0.159092 },
                { 0.993482, 0.765499, 0.156891 },
                { 0.993033, 0.771720, 0.154808 },
                { 0.992505, 0.777967, 0.152855 },
                { 0.991897, 0.784239, 0.151042 },
                { 0.991209, 0.790537, 0.149377 },
                { 0.990439, 0.796859, 0.147870 },
                { 0.989587, 0.803205, 0.146529 },
                { 0.988648, 0.809579, 0.145357 },
                { 0.987621, 0.815978, 0.144363 },
                { 0.986509, 0.822401, 0.143557 },
                { 0.985314, 0.828846, 0.142945 },
                { 0.984031, 0.835315, 0.142528 },
                { 0.982653, 0.841812, 0.142303 },
                { 0.981190, 0.848329, 0.142279 },
                { 0.979644, 0.854866, 0.142453 },
                { 0.977995, 0.861432, 0.142808 },
                { 0.976265, 0.868016, 0.143351 },
                { 0.974443, 0.874622, 0.144061 },
                { 0.972530, 0.881250, 0.144923 },
                { 0.970533, 0.887896, 0.145919 },
                { 0.968443, 0.894564, 0.147014 },
                { 0.966271, 0.901249, 0.148180 },
                { 0.964021, 0.907950, 0.149370 },
                { 0.961681, 0.914672, 0.150520 },
                { 0.959276, 0.921407, 0.151566 },
                { 0.956808, 0.928152, 0.152409 },
                { 0.954287, 0.934908, 0.152921 },
                { 0.951726, 0.941671, 0.152925 },
                { 0.949151, 0.948435, 0.152178 },
                { 0.946602, 0.955190, 0.150328 },
                { 0.944152, 0.961916, 0.146861 },
                { 0.941896, 0.968590, 0.140956 },
                { 0.940015, 0.975158, 0.131326 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetViridisColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.267004, 0.004874, 0.329415 },
                { 0.268510, 0.009605, 0.335427 },
                { 0.269944, 0.014625, 0.341379 },
                { 0.271305, 0.019942, 0.347269 },
                { 0.272594, 0.025563, 0.353093 },
                { 0.273809, 0.031497, 0.358853 },
                { 0.274952, 0.037752, 0.364543 },
                { 0.276022, 0.044167, 0.370164 },
                { 0.277018, 0.050344, 0.375715 },
                { 0.277941, 0.056324, 0.381191 },
                { 0.278791, 0.062145, 0.386592 },
                { 0.279566, 0.067836, 0.391917 },
                { 0.280267, 0.073417, 0.397163 },
                { 0.280894, 0.078907, 0.402329 },
                { 0.281446, 0.084320, 0.407414 },
                { 0.281924, 0.089666, 0.412415 },
                { 0.282327, 0.094955, 0.417331 },
                { 0.282656, 0.100196, 0.422160 },
                { 0.282910, 0.105393, 0.426902 },
                { 0.283091, 0.110553, 0.431554 },
                { 0.283197, 0.115680, 0.436115 },
                { 0.283229, 0.120777, 0.440584 },
                { 0.283187, 0.125848, 0.444960 },
                { 0.283072, 0.130895, 0.449241 },
                { 0.282884, 0.135920, 0.453427 },
                { 0.282623, 0.140926, 0.457517 },
                { 0.282290, 0.145912, 0.461510 },
                { 0.281887, 0.150881, 0.465405 },
                { 0.281412, 0.155834, 0.469201 },
                { 0.280868, 0.160771, 0.472899 },
                { 0.280255, 0.165693, 0.476498 },
                { 0.279574, 0.170599, 0.479997 },
                { 0.278826, 0.175490, 0.483397 },
                { 0.278012, 0.180367, 0.486697 },
                { 0.277134, 0.185228, 0.489898 },
                { 0.276194, 0.190074, 0.493001 },
                { 0.275191, 0.194905, 0.496005 },
                { 0.274128, 0.199721, 0.498911 },
                { 0.273006, 0.204520, 0.501721 },
                { 0.271828, 0.209303, 0.504434 },
                { 0.270595, 0.214069, 0.507052 },
                { 0.269308, 0.218818, 0.509577 },
                { 0.267968, 0.223549, 0.512008 },
                { 0.266580, 0.228262, 0.514349 },
                { 0.265145, 0.232956, 0.516599 },
                { 0.263663, 0.237631, 0.518762 },
                { 0.262138, 0.242286, 0.520837 },
                { 0.260571, 0.246922, 0.522828 },
                { 0.258965, 0.251537, 0.524736 },
                { 0.257322, 0.256130, 0.526563 },
                { 0.255645, 0.260703, 0.528312 },
                { 0.253935, 0.265254, 0.529983 },
                { 0.252194, 0.269783, 0.531579 },
                { 0.250425, 0.274290, 0.533103 },
                { 0.248629, 0.278775, 0.534556 },
                { 0.246811, 0.283237, 0.535941 },
                { 0.244972, 0.287675, 0.537260 },
                { 0.243113, 0.292092, 0.538516 },
                { 0.241237, 0.296485, 0.539709 },
                { 0.239346, 0.300855, 0.540844 },
                { 0.237441, 0.305202, 0.541921 },
                { 0.235526, 0.309527, 0.542944 },
                { 0.233603, 0.313828, 0.543914 },
                { 0.231674, 0.318106, 0.544834 },
                { 0.229739, 0.322361, 0.545706 },
                { 0.227802, 0.326594, 0.546532 },
                { 0.225863, 0.330805, 0.547314 },
                { 0.223925, 0.334994, 0.548053 },
                { 0.221989, 0.339161, 0.548752 },
                { 0.220057, 0.343307, 0.549413 },
                { 0.218130, 0.347432, 0.550038 },
                { 0.216210, 0.351535, 0.550627 },
                { 0.214298, 0.355619, 0.551184 },
                { 0.212395, 0.359683, 0.551710 },
                { 0.210503, 0.363727, 0.552206 },
                { 0.208623, 0.367752, 0.552675 },
                { 0.206756, 0.371758, 0.553117 },
                { 0.204903, 0.375746, 0.553533 },
                { 0.203063, 0.379716, 0.553925 },
                { 0.201239, 0.383670, 0.554294 },
                { 0.199430, 0.387607, 0.554642 },
                { 0.197636, 0.391528, 0.554969 },
                { 0.195860, 0.395433, 0.555276 },
                { 0.194100, 0.399323, 0.555565 },
                { 0.192357, 0.403199, 0.555836 },
                { 0.190631, 0.407061, 0.556089 },
                { 0.188923, 0.410910, 0.556326 },
                { 0.187231, 0.414746, 0.556547 },
                { 0.185556, 0.418570, 0.556753 },
                { 0.183898, 0.422383, 0.556944 },
                { 0.182256, 0.426184, 0.557120 },
                { 0.180629, 0.429975, 0.557282 },
                { 0.179019, 0.433756, 0.557430 },
                { 0.177423, 0.437527, 0.557565 },
                { 0.175841, 0.441290, 0.557685 },
                { 0.174274, 0.445044, 0.557792 },
                { 0.172719, 0.448791, 0.557885 },
                { 0.171176, 0.452530, 0.557965 },
                { 0.169646, 0.456262, 0.558030 },
                { 0.168126, 0.459988, 0.558082 },
                { 0.166617, 0.463708, 0.558119 },
                { 0.165117, 0.467423, 0.558141 },
                { 0.163625, 0.471133, 0.558148 },
                { 0.162142, 0.474838, 0.558140 },
                { 0.160665, 0.478540, 0.558115 },
                { 0.159194, 0.482237, 0.558073 },
                { 0.157729, 0.485932, 0.558013 },
                { 0.156270, 0.489624, 0.557936 },
                { 0.154815, 0.493313, 0.557840 },
                { 0.153364, 0.497000, 0.557724 },
                { 0.151918, 0.500685, 0.557587 },
                { 0.150476, 0.504369, 0.557430 },
                { 0.149039, 0.508051, 0.557250 },
                { 0.147607, 0.511733, 0.557049 },
                { 0.146180, 0.515413, 0.556823 },
                { 0.144759, 0.519093, 0.556572 },
                { 0.143343, 0.522773, 0.556295 },
                { 0.141935, 0.526453, 0.555991 },
                { 0.140536, 0.530132, 0.555659 },
                { 0.139147, 0.533812, 0.555298 },
                { 0.137770, 0.537492, 0.554906 },
                { 0.136408, 0.541173, 0.554483 },
                { 0.135066, 0.544853, 0.554029 },
                { 0.133743, 0.548535, 0.553541 },
                { 0.132444, 0.552216, 0.553018 },
                { 0.131172, 0.555899, 0.552459 },
                { 0.129933, 0.559582, 0.551864 },
                { 0.128729, 0.563265, 0.551229 },
                { 0.127568, 0.566949, 0.550556 },
                { 0.126453, 0.570633, 0.549841 },
                { 0.125394, 0.574318, 0.549086 },
                { 0.124395, 0.578002, 0.548287 },
                { 0.123463, 0.581687, 0.547445 },
                { 0.122606, 0.585371, 0.546557 },
                { 0.121831, 0.589055, 0.545623 },
                { 0.121148, 0.592739, 0.544641 },
                { 0.120565, 0.596422, 0.543611 },
                { 0.120092, 0.600104, 0.542530 },
                { 0.119738, 0.603785, 0.541400 },
                { 0.119512, 0.607464, 0.540218 },
                { 0.119423, 0.611141, 0.538982 },
                { 0.119483, 0.614817, 0.537692 },
                { 0.119699, 0.618490, 0.536347 },
                { 0.120081, 0.622161, 0.534946 },
                { 0.120638, 0.625828, 0.533488 },
                { 0.121380, 0.629492, 0.531973 },
                { 0.122312, 0.633153, 0.530398 },
                { 0.123444, 0.636809, 0.528763 },
                { 0.124780, 0.640461, 0.527068 },
                { 0.126326, 0.644107, 0.525311 },
                { 0.128087, 0.647749, 0.523491 },
                { 0.130067, 0.651384, 0.521608 },
                { 0.132268, 0.655014, 0.519661 },
                { 0.134692, 0.658636, 0.517649 },
                { 0.137339, 0.662252, 0.515571 },
                { 0.140210, 0.665859, 0.513427 },
                { 0.143303, 0.669459, 0.511215 },
                { 0.146616, 0.673050, 0.508936 },
                { 0.150148, 0.676631, 0.506589 },
                { 0.153894, 0.680203, 0.504172 },
                { 0.157851, 0.683765, 0.501686 },
                { 0.162016, 0.687316, 0.499129 },
                { 0.166383, 0.690856, 0.496502 },
                { 0.170948, 0.694384, 0.493803 },
                { 0.175707, 0.697900, 0.491033 },
                { 0.180653, 0.701402, 0.488189 },
                { 0.185783, 0.704891, 0.485273 },
                { 0.191090, 0.708366, 0.482284 },
                { 0.196571, 0.711827, 0.479221 },
                { 0.202219, 0.715272, 0.476084 },
                { 0.208030, 0.718701, 0.472873 },
                { 0.214000, 0.722114, 0.469588 },
                { 0.220124, 0.725509, 0.466226 },
                { 0.226397, 0.728888, 0.462789 },
                { 0.232815, 0.732247, 0.459277 },
                { 0.239374, 0.735588, 0.455688 },
                { 0.246070, 0.738910, 0.452024 },
                { 0.252899, 0.742211, 0.448284 },
                { 0.259857, 0.745492, 0.444467 },
                { 0.266941, 0.748751, 0.440573 },
                { 0.274149, 0.751988, 0.436601 },
                { 0.281477, 0.755203, 0.432552 },
                { 0.288921, 0.758394, 0.428426 },
                { 0.296479, 0.761561, 0.424223 },
                { 0.304148, 0.764704, 0.419943 },
                { 0.311925, 0.767822, 0.415586 },
                { 0.319809, 0.770914, 0.411152 },
                { 0.327796, 0.773980, 0.406640 },
                { 0.335885, 0.777018, 0.402049 },
                { 0.344074, 0.780029, 0.397381 },
                { 0.352360, 0.783011, 0.392636 },
                { 0.360741, 0.785964, 0.387814 },
                { 0.369214, 0.788888, 0.382914 },
                { 0.377779, 0.791781, 0.377939 },
                { 0.386433, 0.794644, 0.372886 },
                { 0.395174, 0.797475, 0.367757 },
                { 0.404001, 0.800275, 0.362552 },
                { 0.412913, 0.803041, 0.357269 },
                { 0.421908, 0.805774, 0.351910 },
                { 0.430983, 0.808473, 0.346476 },
                { 0.440137, 0.811138, 0.340967 },
                { 0.449368, 0.813768, 0.335384 },
                { 0.458674, 0.816363, 0.329727 },
                { 0.468053, 0.818921, 0.323998 },
                { 0.477504, 0.821444, 0.318195 },
                { 0.487026, 0.823929, 0.312321 },
                { 0.496615, 0.826376, 0.306377 },
                { 0.506271, 0.828786, 0.300362 },
                { 0.515992, 0.831158, 0.294279 },
                { 0.525776, 0.833491, 0.288127 },
                { 0.535621, 0.835785, 0.281908 },
                { 0.545524, 0.838039, 0.275626 },
                { 0.555484, 0.840254, 0.269281 },
                { 0.565498, 0.842430, 0.262877 },
                { 0.575563, 0.844566, 0.256415 },
                { 0.585678, 0.846661, 0.249897 },
                { 0.595839, 0.848717, 0.243329 },
                { 0.606045, 0.850733, 0.236712 },
                { 0.616293, 0.852709, 0.230052 },
                { 0.626579, 0.854645, 0.223353 },
                { 0.636902, 0.856542, 0.216620 },
                { 0.647257, 0.858400, 0.209861 },
                { 0.657642, 0.860219, 0.203082 },
                { 0.668054, 0.861999, 0.196293 },
                { 0.678489, 0.863742, 0.189503 },
                { 0.688944, 0.865448, 0.182725 },
                { 0.699415, 0.867117, 0.175971 },
                { 0.709898, 0.868751, 0.169257 },
                { 0.720391, 0.870350, 0.162603 },
                { 0.730889, 0.871916, 0.156029 },
                { 0.741388, 0.873449, 0.149561 },
                { 0.751884, 0.874951, 0.143228 },
                { 0.762373, 0.876424, 0.137064 },
                { 0.772852, 0.877868, 0.131109 },
                { 0.783315, 0.879285, 0.125405 },
                { 0.793760, 0.880678, 0.120005 },
                { 0.804182, 0.882046, 0.114965 },
                { 0.814576, 0.883393, 0.110347 },
                { 0.824940, 0.884720, 0.106217 },
                { 0.835270, 0.886029, 0.102646 },
                { 0.845561, 0.887322, 0.099702 },
                { 0.855810, 0.888601, 0.097452 },
                { 0.866013, 0.889868, 0.095953 },
                { 0.876168, 0.891125, 0.095250 },
                { 0.886271, 0.892374, 0.095374 },
                { 0.896320, 0.893616, 0.096335 },
                { 0.906311, 0.894855, 0.098125 },
                { 0.916242, 0.896091, 0.100717 },
                { 0.926106, 0.897330, 0.104071 },
                { 0.935904, 0.898570, 0.108131 },
                { 0.945636, 0.899815, 0.112838 },
                { 0.955300, 0.901065, 0.118128 },
                { 0.964894, 0.902323, 0.123941 },
                { 0.974417, 0.903590, 0.130215 },
                { 0.983868, 0.904867, 0.136897 },
                { 0.993248, 0.906157, 0.143936 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetCividisColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.0000, 0.1262, 0.3015 },
                { 0.0000, 0.1292, 0.3077 },
                { 0.0000, 0.1321, 0.3142 },
                { 0.0000, 0.1350, 0.3205 },
                { 0.0000, 0.1379, 0.3269 },
                { 0.0000, 0.1408, 0.3334 },
                { 0.0000, 0.1437, 0.3400 },
                { 0.0000, 0.1465, 0.3467 },
                { 0.0000, 0.1492, 0.3537 },
                { 0.0000, 0.1519, 0.3606 },
                { 0.0000, 0.1546, 0.3676 },
                { 0.0000, 0.1574, 0.3746 },
                { 0.0000, 0.1601, 0.3817 },
                { 0.0000, 0.1629, 0.3888 },
                { 0.0000, 0.1657, 0.3960 },
                { 0.0000, 0.1685, 0.4031 },
                { 0.0000, 0.1714, 0.4102 },
                { 0.0000, 0.1743, 0.4172 },
                { 0.0000, 0.1773, 0.4241 },
                { 0.0000, 0.1798, 0.4307 },
                { 0.0000, 0.1817, 0.4347 },
                { 0.0000, 0.1834, 0.4363 },
                { 0.0000, 0.1852, 0.4368 },
                { 0.0000, 0.1872, 0.4368 },
                { 0.0000, 0.1901, 0.4365 },
                { 0.0000, 0.1930, 0.4361 },
                { 0.0000, 0.1958, 0.4356 },
                { 0.0000, 0.1987, 0.4349 },
                { 0.0000, 0.2015, 0.4343 },
                { 0.0000, 0.2044, 0.4336 },
                { 0.0000, 0.2073, 0.4329 },
                { 0.0055, 0.2101, 0.4322 },
                { 0.0236, 0.2130, 0.4314 },
                { 0.0416, 0.2158, 0.4308 },
                { 0.0576, 0.2187, 0.4301 },
                { 0.0710, 0.2215, 0.4293 },
                { 0.0827, 0.2244, 0.4287 },
                { 0.0932, 0.2272, 0.4280 },
                { 0.1030, 0.2300, 0.4274 },
                { 0.1120, 0.2329, 0.4268 },
                { 0.1204, 0.2357, 0.4262 },
                { 0.1283, 0.2385, 0.4256 },
                { 0.1359, 0.2414, 0.4251 },
                { 0.1431, 0.2442, 0.4245 },
                { 0.1500, 0.2470, 0.4241 },
                { 0.1566, 0.2498, 0.4236 },
                { 0.1630, 0.2526, 0.4232 },
                { 0.1692, 0.2555, 0.4228 },
                { 0.1752, 0.2583, 0.4224 },
                { 0.1811, 0.2611, 0.4220 },
                { 0.1868, 0.2639, 0.4217 },
                { 0.1923, 0.2667, 0.4214 },
                { 0.1977, 0.2695, 0.4212 },
                { 0.2030, 0.2723, 0.4209 },
                { 0.2082, 0.2751, 0.4207 },
                { 0.2133, 0.2780, 0.4205 },
                { 0.2183, 0.2808, 0.4204 },
                { 0.2232, 0.2836, 0.4203 },
                { 0.2281, 0.2864, 0.4202 },
                { 0.2328, 0.2892, 0.4201 },
                { 0.2375, 0.2920, 0.4200 },
                { 0.2421, 0.2948, 0.4200 },
                { 0.2466, 0.2976, 0.4200 },
                { 0.2511, 0.3004, 0.4201 },
                { 0.2556, 0.3032, 0.4201 },
                { 0.2599, 0.3060, 0.4202 },
                { 0.2643, 0.3088, 0.4203 },
                { 0.2686, 0.3116, 0.4205 },
                { 0.2728, 0.3144, 0.4206 },
                { 0.2770, 0.3172, 0.4208 },
                { 0.2811, 0.3200, 0.4210 },
                { 0.2853, 0.3228, 0.4212 },
                { 0.2894, 0.3256, 0.4215 },
                { 0.2934, 0.3284, 0.4218 },
                { 0.2974, 0.3312, 0.4221 },
                { 0.3014, 0.3340, 0.4224 },
                { 0.3054, 0.3368, 0.4227 },
                { 0.3093, 0.3396, 0.4231 },
                { 0.3132, 0.3424, 0.4236 },
                { 0.3170, 0.3453, 0.4240 },
                { 0.3209, 0.3481, 0.4244 },
                { 0.3247, 0.3509, 0.4249 },
                { 0.3285, 0.3537, 0.4254 },
                { 0.3323, 0.3565, 0.4259 },
                { 0.3361, 0.3593, 0.4264 },
                { 0.3398, 0.3622, 0.4270 },
                { 0.3435, 0.3650, 0.4276 },
                { 0.3472, 0.3678, 0.4282 },
                { 0.3509, 0.3706, 0.4288 },
                { 0.3546, 0.3734, 0.4294 },
                { 0.3582, 0.3763, 0.4302 },
                { 0.3619, 0.3791, 0.4308 },
                { 0.3655, 0.3819, 0.4316 },
                { 0.3691, 0.3848, 0.4322 },
                { 0.3727, 0.3876, 0.4331 },
                { 0.3763, 0.3904, 0.4338 },
                { 0.3798, 0.3933, 0.4346 },
                { 0.3834, 0.3961, 0.4355 },
                { 0.3869, 0.3990, 0.4364 },
                { 0.3905, 0.4018, 0.4372 },
                { 0.3940, 0.4047, 0.4381 },
                { 0.3975, 0.4075, 0.4390 },
                { 0.4010, 0.4104, 0.4400 },
                { 0.4045, 0.4132, 0.4409 },
                { 0.4080, 0.4161, 0.4419 },
                { 0.4114, 0.4189, 0.4430 },
                { 0.4149, 0.4218, 0.4440 },
                { 0.4183, 0.4247, 0.4450 },
                { 0.4218, 0.4275, 0.4462 },
                { 0.4252, 0.4304, 0.4473 },
                { 0.4286, 0.4333, 0.4485 },
                { 0.4320, 0.4362, 0.4496 },
                { 0.4354, 0.4390, 0.4508 },
                { 0.4388, 0.4419, 0.4521 },
                { 0.4422, 0.4448, 0.4534 },
                { 0.4456, 0.4477, 0.4547 },
                { 0.4489, 0.4506, 0.4561 },
                { 0.4523, 0.4535, 0.4575 },
                { 0.4556, 0.4564, 0.4589 },
                { 0.4589, 0.4593, 0.4604 },
                { 0.4622, 0.4622, 0.4620 },
                { 0.4656, 0.4651, 0.4635 },
                { 0.4689, 0.4680, 0.4650 },
                { 0.4722, 0.4709, 0.4665 },
                { 0.4756, 0.4738, 0.4679 },
                { 0.4790, 0.4767, 0.4691 },
                { 0.4825, 0.4797, 0.4701 },
                { 0.4861, 0.4826, 0.4707 },
                { 0.4897, 0.4856, 0.4714 },
                { 0.4934, 0.4886, 0.4719 },
                { 0.4971, 0.4915, 0.4723 },
                { 0.5008, 0.4945, 0.4727 },
                { 0.5045, 0.4975, 0.4730 },
                { 0.5083, 0.5005, 0.4732 },
                { 0.5121, 0.5035, 0.4734 },
                { 0.5158, 0.5065, 0.4736 },
                { 0.5196, 0.5095, 0.4737 },
                { 0.5234, 0.5125, 0.4738 },
                { 0.5272, 0.5155, 0.4739 },
                { 0.5310, 0.5186, 0.4739 },
                { 0.5349, 0.5216, 0.4738 },
                { 0.5387, 0.5246, 0.4739 },
                { 0.5425, 0.5277, 0.4738 },
                { 0.5464, 0.5307, 0.4736 },
                { 0.5502, 0.5338, 0.4735 },
                { 0.5541, 0.5368, 0.4733 },
                { 0.5579, 0.5399, 0.4732 },
                { 0.5618, 0.5430, 0.4729 },
                { 0.5657, 0.5461, 0.4727 },
                { 0.5696, 0.5491, 0.4723 },
                { 0.5735, 0.5522, 0.4720 },
                { 0.5774, 0.5553, 0.4717 },
                { 0.5813, 0.5584, 0.4714 },
                { 0.5852, 0.5615, 0.4709 },
                { 0.5892, 0.5646, 0.4705 },
                { 0.5931, 0.5678, 0.4701 },
                { 0.5970, 0.5709, 0.4696 },
                { 0.6010, 0.5740, 0.4691 },
                { 0.6050, 0.5772, 0.4685 },
                { 0.6089, 0.5803, 0.4680 },
                { 0.6129, 0.5835, 0.4673 },
                { 0.6168, 0.5866, 0.4668 },
                { 0.6208, 0.5898, 0.4662 },
                { 0.6248, 0.5929, 0.4655 },
                { 0.6288, 0.5961, 0.4649 },
                { 0.6328, 0.5993, 0.4641 },
                { 0.6368, 0.6025, 0.4632 },
                { 0.6408, 0.6057, 0.4625 },
                { 0.6449, 0.6089, 0.4617 },
                { 0.6489, 0.6121, 0.4609 },
                { 0.6529, 0.6153, 0.4600 },
                { 0.6570, 0.6185, 0.4591 },
                { 0.6610, 0.6217, 0.4583 },
                { 0.6651, 0.6250, 0.4573 },
                { 0.6691, 0.6282, 0.4562 },
                { 0.6732, 0.6315, 0.4553 },
                { 0.6773, 0.6347, 0.4543 },
                { 0.6813, 0.6380, 0.4532 },
                { 0.6854, 0.6412, 0.4521 },
                { 0.6895, 0.6445, 0.4511 },
                { 0.6936, 0.6478, 0.4499 },
                { 0.6977, 0.6511, 0.4487 },
                { 0.7018, 0.6544, 0.4475 },
                { 0.7060, 0.6577, 0.4463 },
                { 0.7101, 0.6610, 0.4450 },
                { 0.7142, 0.6643, 0.4437 },
                { 0.7184, 0.6676, 0.4424 },
                { 0.7225, 0.6710, 0.4409 },
                { 0.7267, 0.6743, 0.4396 },
                { 0.7308, 0.6776, 0.4382 },
                { 0.7350, 0.6810, 0.4368 },
                { 0.7392, 0.6844, 0.4352 },
                { 0.7434, 0.6877, 0.4338 },
                { 0.7476, 0.6911, 0.4322 },
                { 0.7518, 0.6945, 0.4307 },
                { 0.7560, 0.6979, 0.4290 },
                { 0.7602, 0.7013, 0.4273 },
                { 0.7644, 0.7047, 0.4258 },
                { 0.7686, 0.7081, 0.4241 },
                { 0.7729, 0.7115, 0.4223 },
                { 0.7771, 0.7150, 0.4205 },
                { 0.7814, 0.7184, 0.4188 },
                { 0.7856, 0.7218, 0.4168 },
                { 0.7899, 0.7253, 0.4150 },
                { 0.7942, 0.7288, 0.4129 },
                { 0.7985, 0.7322, 0.4111 },
                { 0.8027, 0.7357, 0.4090 },
                { 0.8070, 0.7392, 0.4070 },
                { 0.8114, 0.7427, 0.4049 },
                { 0.8157, 0.7462, 0.4028 },
                { 0.8200, 0.7497, 0.4007 },
                { 0.8243, 0.7532, 0.3984 },
                { 0.8287, 0.7568, 0.3961 },
                { 0.8330, 0.7603, 0.3938 },
                { 0.8374, 0.7639, 0.3915 },
                { 0.8417, 0.7674, 0.3892 },
                { 0.8461, 0.7710, 0.3869 },
                { 0.8505, 0.7745, 0.3843 },
                { 0.8548, 0.7781, 0.3818 },
                { 0.8592, 0.7817, 0.3793 },
                { 0.8636, 0.7853, 0.3766 },
                { 0.8681, 0.7889, 0.3739 },
                { 0.8725, 0.7926, 0.3712 },
                { 0.8769, 0.7962, 0.3684 },
                { 0.8813, 0.7998, 0.3657 },
                { 0.8858, 0.8035, 0.3627 },
                { 0.8902, 0.8071, 0.3599 },
                { 0.8947, 0.8108, 0.3569 },
                { 0.8992, 0.8145, 0.3538 },
                { 0.9037, 0.8182, 0.3507 },
                { 0.9082, 0.8219, 0.3474 },
                { 0.9127, 0.8256, 0.3442 },
                { 0.9172, 0.8293, 0.3409 },
                { 0.9217, 0.8330, 0.3374 },
                { 0.9262, 0.8367, 0.3340 },
                { 0.9308, 0.8405, 0.3306 },
                { 0.9353, 0.8442, 0.3268 },
                { 0.9399, 0.8480, 0.3232 },
                { 0.9444, 0.8518, 0.3195 },
                { 0.9490, 0.8556, 0.3155 },
                { 0.9536, 0.8593, 0.3116 },
                { 0.9582, 0.8632, 0.3076 },
                { 0.9628, 0.8670, 0.3034 },
                { 0.9674, 0.8708, 0.2990 },
                { 0.9721, 0.8746, 0.2947 },
                { 0.9767, 0.8785, 0.2901 },
                { 0.9814, 0.8823, 0.2856 },
                { 0.9860, 0.8862, 0.2807 },
                { 0.9907, 0.8901, 0.2759 },
                { 0.9954, 0.8940, 0.2708 },
                { 1.0000, 0.8979, 0.2655 },
                { 1.0000, 0.9018, 0.2600 },
                { 1.0000, 0.9057, 0.2593 },
                { 1.0000, 0.9094, 0.2634 },
                { 1.0000, 0.9131, 0.2680 },
                { 1.0000, 0.9169, 0.2731 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetGithubColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.933333, 0.933333, 0.933333 },
                { 0.776470, 0.894117, 0.545098 },
                { 0.482352, 0.788235, 0.435294 },
                { 0.137254, 0.603921, 0.231372 },
                { 0.098039, 0.380392, 0.152941 }
            };

        return internal::CalcLerp(x, data);
    }

    inline Color GetCubehelixColor(double x)
    {
        constexpr Color data[] =
            {
                { 0.000000, 0.000000, 0.000000 },
                { 0.006716, 0.002119, 0.005970 },
                { 0.013252, 0.004287, 0.012162 },
                { 0.019599, 0.006514, 0.018563 },
                { 0.025748, 0.008803, 0.025162 },
                { 0.031691, 0.011164, 0.031946 },
                { 0.037421, 0.013600, 0.038902 },
                { 0.042932, 0.016118, 0.046016 },
                { 0.048217, 0.018724, 0.053275 },
                { 0.053271, 0.021423, 0.060666 },
                { 0.058090, 0.024220, 0.068173 },
                { 0.062670, 0.027119, 0.075781 },
                { 0.067008, 0.030126, 0.083478 },
                { 0.071101, 0.033243, 0.091246 },
                { 0.074947, 0.036475, 0.099072 },
                { 0.078546, 0.039824, 0.106939 },
                { 0.081898, 0.043295, 0.114834 },
                { 0.085002, 0.046889, 0.122740 },
                { 0.087860, 0.050609, 0.130643 },
                { 0.090474, 0.054457, 0.138527 },
                { 0.092845, 0.058434, 0.146378 },
                { 0.094978, 0.062542, 0.154180 },
                { 0.096875, 0.066781, 0.161918 },
                { 0.098542, 0.071152, 0.169579 },
                { 0.099984, 0.075655, 0.177147 },
                { 0.101205, 0.080290, 0.184609 },
                { 0.102212, 0.085055, 0.191951 },
                { 0.103013, 0.089951, 0.199159 },
                { 0.103615, 0.094975, 0.206221 },
                { 0.104025, 0.100126, 0.213124 },
                { 0.104252, 0.105403, 0.219855 },
                { 0.104305, 0.110801, 0.226402 },
                { 0.104194, 0.116320, 0.232755 },
                { 0.103929, 0.121956, 0.238903 },
                { 0.103519, 0.127705, 0.244834 },
                { 0.102976, 0.133564, 0.250541 },
                { 0.102310, 0.139529, 0.256012 },
                { 0.101534, 0.145596, 0.261240 },
                { 0.100659, 0.151759, 0.266217 },
                { 0.099697, 0.158016, 0.270935 },
                { 0.098661, 0.164359, 0.275388 },
                { 0.097563, 0.170785, 0.279569 },
                { 0.096415, 0.177287, 0.283474 },
                { 0.095232, 0.183860, 0.287097 },
                { 0.094026, 0.190498, 0.290434 },
                { 0.092810, 0.197194, 0.293483 },
                { 0.091597, 0.203943, 0.296240 },
                { 0.090402, 0.210739, 0.298703 },
                { 0.089237, 0.217573, 0.300873 },
                { 0.088115, 0.224441, 0.302747 },
                { 0.087051, 0.231334, 0.304327 },
                { 0.086056, 0.238247, 0.305612 },
                { 0.085146, 0.245171, 0.306606 },
                { 0.084331, 0.252101, 0.307310 },
                { 0.083626, 0.259028, 0.307728 },
                { 0.083043, 0.265946, 0.307863 },
                { 0.082594, 0.272848, 0.307720 },
                { 0.082291, 0.279726, 0.307304 },
                { 0.082148, 0.286573, 0.306621 },
                { 0.082174, 0.293383, 0.305677 },
                { 0.082381, 0.300147, 0.304480 },
                { 0.082780, 0.306860, 0.303037 },
                { 0.083383, 0.313514, 0.301356 },
                { 0.084198, 0.320102, 0.299448 },
                { 0.085235, 0.326618, 0.297320 },
                { 0.086504, 0.333055, 0.294984 },
                { 0.088014, 0.339406, 0.292449 },
                { 0.089772, 0.345666, 0.289728 },
                { 0.091787, 0.351829, 0.286831 },
                { 0.094066, 0.357887, 0.283771 },
                { 0.096615, 0.363836, 0.280560 },
                { 0.099441, 0.369671, 0.277211 },
                { 0.102549, 0.375385, 0.273736 },
                { 0.105944, 0.380974, 0.270151 },
                { 0.109630, 0.386433, 0.266468 },
                { 0.113611, 0.391757, 0.262703 },
                { 0.117891, 0.396943, 0.258868 },
                { 0.122472, 0.401985, 0.254979 },
                { 0.127356, 0.406881, 0.251051 },
                { 0.132543, 0.411627, 0.247099 },
                { 0.138035, 0.416220, 0.243137 },
                { 0.143832, 0.420656, 0.239182 },
                { 0.149933, 0.424934, 0.235247 },
                { 0.156336, 0.429052, 0.231350 },
                { 0.163040, 0.433007, 0.227504 },
                { 0.170042, 0.436798, 0.223726 },
                { 0.177339, 0.440423, 0.220029 },
                { 0.184927, 0.443882, 0.216431 },
                { 0.192802, 0.447175, 0.212944 },
                { 0.200958, 0.450301, 0.209585 },
                { 0.209391, 0.453260, 0.206367 },
                { 0.218092, 0.456053, 0.203306 },
                { 0.227057, 0.458680, 0.200415 },
                { 0.236277, 0.461144, 0.197707 },
                { 0.245744, 0.463444, 0.195197 },
                { 0.255451, 0.465584, 0.192898 },
                { 0.265388, 0.467565, 0.190822 },
                { 0.275545, 0.469391, 0.188982 },
                { 0.285913, 0.471062, 0.187389 },
                { 0.296481, 0.472584, 0.186055 },
                { 0.307239, 0.473959, 0.184992 },
                { 0.318175, 0.475191, 0.184208 },
                { 0.329277, 0.476285, 0.183716 },
                { 0.340534, 0.477243, 0.183523 },
                { 0.351934, 0.478072, 0.183638 },
                { 0.363463, 0.478776, 0.184071 },
                { 0.375109, 0.479360, 0.184829 },
                { 0.386858, 0.479829, 0.185918 },
                { 0.398697, 0.480190, 0.187345 },
                { 0.410613, 0.480448, 0.189115 },
                { 0.422591, 0.480609, 0.191235 },
                { 0.434618, 0.480679, 0.193708 },
                { 0.446680, 0.480665, 0.196538 },
                { 0.458762, 0.480574, 0.199728 },
                { 0.470850, 0.480412, 0.203280 },
                { 0.482930, 0.480186, 0.207197 },
                { 0.494987, 0.479903, 0.211478 },
                { 0.507008, 0.479572, 0.216124 },
                { 0.518978, 0.479198, 0.221136 },
                { 0.530883, 0.478789, 0.226510 },
                { 0.542708, 0.478353, 0.232247 },
                { 0.554441, 0.477898, 0.238342 },
                { 0.566067, 0.477430, 0.244794 },
                { 0.577573, 0.476958, 0.251597 },
                { 0.588945, 0.476490, 0.258747 },
                { 0.600171, 0.476032, 0.266239 },
                { 0.611237, 0.475592, 0.274067 },
                { 0.622132, 0.475178, 0.282223 },
                { 0.632842, 0.474798, 0.290702 },
                { 0.643357, 0.474459, 0.299495 },
                { 0.653665, 0.474168, 0.308593 },
                { 0.663755, 0.473933, 0.317987 },
                { 0.673616, 0.473761, 0.327668 },
                { 0.683239, 0.473658, 0.337626 },
                { 0.692613, 0.473632, 0.347849 },
                { 0.701729, 0.473690, 0.358327 },
                { 0.710579, 0.473838, 0.369047 },
                { 0.719155, 0.474083, 0.379998 },
                { 0.727448, 0.474430, 0.391167 },
                { 0.735453, 0.474886, 0.402541 },
                { 0.743162, 0.475457, 0.414106 },
                { 0.750569, 0.476148, 0.425849 },
                { 0.757669, 0.476964, 0.437755 },
                { 0.764458, 0.477911, 0.449811 },
                { 0.770932, 0.478994, 0.462001 },
                { 0.777086, 0.480216, 0.474310 },
                { 0.782918, 0.481583, 0.486725 },
                { 0.788426, 0.483098, 0.499228 },
                { 0.793609, 0.484765, 0.511805 },
                { 0.798465, 0.486587, 0.524441 },
                { 0.802993, 0.488567, 0.537119 },
                { 0.807196, 0.490708, 0.549824 },
                { 0.811072, 0.493013, 0.562540 },
                { 0.814625, 0.495483, 0.575253 },
                { 0.817855, 0.498121, 0.587945 },
                { 0.820767, 0.500927, 0.600602 },
                { 0.823364, 0.503903, 0.613208 },
                { 0.825649, 0.507050, 0.625748 },
                { 0.827628, 0.510368, 0.638207 },
                { 0.829305, 0.513857, 0.650570 },
                { 0.830688, 0.517516, 0.662822 },
                { 0.831781, 0.521346, 0.674949 },
                { 0.832593, 0.525345, 0.686938 },
                { 0.833130, 0.529511, 0.698773 },
                { 0.833402, 0.533844, 0.710443 },
                { 0.833416, 0.538342, 0.721933 },
                { 0.833181, 0.543001, 0.733232 },
                { 0.832708, 0.547820, 0.744327 },
                { 0.832006, 0.552795, 0.755206 },
                { 0.831086, 0.557924, 0.765859 },
                { 0.829958, 0.563202, 0.776274 },
                { 0.828633, 0.568627, 0.786443 },
                { 0.827124, 0.574193, 0.796354 },
                { 0.825442, 0.579897, 0.805999 },
                { 0.823599, 0.585733, 0.815370 },
                { 0.821608, 0.591698, 0.824459 },
                { 0.819482, 0.597785, 0.833258 },
                { 0.817233, 0.603990, 0.841761 },
                { 0.814875, 0.610307, 0.849963 },
                { 0.812421, 0.616730, 0.857858 },
                { 0.809884, 0.623252, 0.865441 },
                { 0.807278, 0.629869, 0.872709 },
                { 0.804617, 0.636573, 0.879658 },
                { 0.801914, 0.643359, 0.886286 },
                { 0.799183, 0.650218, 0.892592 },
                { 0.796438, 0.657146, 0.898574 },
                { 0.793692, 0.664134, 0.904231 },
                { 0.790959, 0.671176, 0.909565 },
                { 0.788253, 0.678264, 0.914576 },
                { 0.785586, 0.685392, 0.919267 },
                { 0.782973, 0.692553, 0.923639 },
                { 0.780425, 0.699738, 0.927695 },
                { 0.777957, 0.706942, 0.931441 },
                { 0.775579, 0.714157, 0.934879 },
                { 0.773305, 0.721375, 0.938016 },
                { 0.771147, 0.728589, 0.940857 },
                { 0.769116, 0.735793, 0.943409 },
                { 0.767224, 0.742979, 0.945678 },
                { 0.765481, 0.750140, 0.947673 },
                { 0.763898, 0.757269, 0.949402 },
                { 0.762485, 0.764360, 0.950874 },
                { 0.761251, 0.771405, 0.952098 },
                { 0.760207, 0.778399, 0.953084 },
                { 0.759360, 0.785335, 0.953843 },
                { 0.758718, 0.792207, 0.954386 },
                { 0.758290, 0.799008, 0.954724 },
                { 0.758082, 0.805734, 0.954869 },
                { 0.758101, 0.812378, 0.954833 },
                { 0.758353, 0.818934, 0.954629 },
                { 0.758842, 0.825399, 0.954270 },
                { 0.759575, 0.831767, 0.953769 },
                { 0.760554, 0.838033, 0.953140 },
                { 0.761784, 0.844192, 0.952397 },
                { 0.763267, 0.850242, 0.951554 },
                { 0.765006, 0.856178, 0.950625 },
                { 0.767001, 0.861997, 0.949624 },
                { 0.769255, 0.867695, 0.948567 },
                { 0.771766, 0.873270, 0.947467 },
                { 0.774535, 0.878718, 0.946340 },
                { 0.777561, 0.884039, 0.945201 },
                { 0.780841, 0.889230, 0.944063 },
                { 0.784374, 0.894289, 0.942942 },
                { 0.788156, 0.899216, 0.941853 },
                { 0.792184, 0.904010, 0.940809 },
                { 0.796453, 0.908669, 0.939825 },
                { 0.800958, 0.913194, 0.938916 },
                { 0.805694, 0.917586, 0.938095 },
                { 0.810654, 0.921845, 0.937376 },
                { 0.815832, 0.925971, 0.936772 },
                { 0.821221, 0.929967, 0.936297 },
                { 0.826811, 0.933833, 0.935962 },
                { 0.832595, 0.937572, 0.935781 },
                { 0.838565, 0.941187, 0.935766 },
                { 0.844709, 0.944679, 0.935927 },
                { 0.851018, 0.948053, 0.936275 },
                { 0.857482, 0.951311, 0.936822 },
                { 0.864090, 0.954457, 0.937578 },
                { 0.870830, 0.957495, 0.938550 },
                { 0.877690, 0.960430, 0.939749 },
                { 0.884659, 0.963266, 0.941183 },
                { 0.891723, 0.966009, 0.942858 },
                { 0.898871, 0.968662, 0.944783 },
                { 0.906088, 0.971233, 0.946962 },
                { 0.913362, 0.973726, 0.949402 },
                { 0.920679, 0.976147, 0.952108 },
                { 0.928026, 0.978504, 0.955083 },
                { 0.935387, 0.980802, 0.958331 },
                { 0.942750, 0.983048, 0.961854 },
                { 0.950101, 0.985249, 0.965654 },
                { 0.957424, 0.987412, 0.969733 },
                { 0.964706, 0.989543, 0.974090 },
                { 0.971932, 0.991652, 0.978724 },
                { 0.979088, 0.993744, 0.983635 },
                { 0.986161, 0.995828, 0.988820 },
                { 0.993136, 0.997910, 0.994276 },
                { 1.000000, 1.000000, 1.000000 }
            };

        return internal::CalcLerp(x, data);
    }

#if defined(TINYCOLORMAP_WITH_QT5) && defined(TINYCOLORMAP_WITH_EIGEN)
    inline QImage CreateMatrixVisualization(const Eigen::MatrixXd& matrix)
    {
        const int w = matrix.cols();
        const int h = matrix.rows();
        const double max_coeff = matrix.maxCoeff();
        const double min_coeff = matrix.minCoeff();
        const Eigen::MatrixXd normalized = (1.0 / (max_coeff - min_coeff)) * (matrix - Eigen::MatrixXd::Constant(h, w, min_coeff));

        QImage image(w, h, QImage::Format_ARGB32);
        for (int x = 0; x < w; ++ x)
        {
            for (int y = 0; y < h; ++ y)
            {
                const QColor color = tinycolormap::GetColor(normalized(y, x)).ConvertToQColor();
                image.setPixel(x, y, color.rgb());
            }
        }

        return image;
    }

    inline void ExportMatrixVisualization(const Eigen::MatrixXd& matrix, const std::string& path)
    {
        CreateMatrixVisualization(matrix).save(QString::fromStdString(path));
    }
#endif
}

#endif

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/magic_enum.hpp included by src/immvision/internal/cv/colormap.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  __  __             _        ______                          _____
// |  \/  |           (_)      |  ____|                        / ____|_     _
// | \  / | __ _  __ _ _  ___  | |__   _ __  _   _ _ __ ___   | |   _| |_ _| |_
// | |\/| |/ _` |/ _` | |/ __| |  __| | '_ \| | | | '_ ` _ \  | |  |_   _|_   _|
// | |  | | (_| | (_| | | (__  | |____| | | | |_| | | | | | | | |____|_|   |_|
// |_|  |_|\__,_|\__, |_|\___| |______|_| |_|\__,_|_| |_| |_|  \_____|
//                __/ | https://github.com/Neargye/magic_enum
//               |___/  version 0.7.3
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>.
// SPDX-License-Identifier: MIT
// Copyright (c) 2019 - 2022 Daniil Goncharov <neargye@gmail.com>.
//
// Permission is hereby  granted, free of charge, to any  person obtaining a copy
// of this software and associated  documentation files (the "Software"), to deal
// in the Software  without restriction, including without  limitation the rights
// to  use, copy,  modify, merge,  publish, distribute,  sublicense, and/or  sell
// copies  of  the Software,  and  to  permit persons  to  whom  the Software  is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE  IS PROVIDED "AS  IS", WITHOUT WARRANTY  OF ANY KIND,  EXPRESS OR
// IMPLIED,  INCLUDING BUT  NOT  LIMITED TO  THE  WARRANTIES OF  MERCHANTABILITY,
// FITNESS FOR  A PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT  SHALL THE
// AUTHORS  OR COPYRIGHT  HOLDERS  BE  LIABLE FOR  ANY  CLAIM,  DAMAGES OR  OTHER
// LIABILITY, WHETHER IN AN ACTION OF  CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE  OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#ifndef NEARGYE_MAGIC_ENUM_HPP
#define NEARGYE_MAGIC_ENUM_HPP

#define MAGIC_ENUM_VERSION_MAJOR 0
#define MAGIC_ENUM_VERSION_MINOR 7
#define MAGIC_ENUM_VERSION_PATCH 3

#include <array>
#include <cassert>
#include <cstddef>
#include <iosfwd>
#include <limits>
#include <type_traits>
#include <variant>

#if defined(MAGIC_ENUM_CONFIG_FILE)
#include MAGIC_ENUM_CONFIG_FILE
#endif

#if !defined(MAGIC_ENUM_USING_ALIAS_OPTIONAL)
#include <optional>
#endif
#if !defined(MAGIC_ENUM_USING_ALIAS_STRING)
#endif
#if !defined(MAGIC_ENUM_USING_ALIAS_STRING_VIEW)
#include <string_view>
#endif

#if defined(__clang__)
#  pragma clang diagnostic push
#  pragma clang diagnostic ignored "-Wunused-const-variable"
#elif defined(__GNUC__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wmaybe-uninitialized" // May be used uninitialized 'return {};'.
#elif defined(_MSC_VER)
#  pragma warning(push)
#  pragma warning(disable : 26495) // Variable 'static_string<N>::chars_' is uninitialized.
#  pragma warning(disable : 28020) // Arithmetic overflow: Using operator '-' on a 4 byte value and then casting the result to a 8 byte value.
#  pragma warning(disable : 26451) // The expression '0<=_Param_(1)&&_Param_(1)<=1-1' is not true at this call.
#endif

// Checks magic_enum compiler compatibility.
#if defined(__clang__) && __clang_major__ >= 5 || defined(__GNUC__) && __GNUC__ >= 9 || defined(_MSC_VER) && _MSC_VER >= 1910
#  undef  MAGIC_ENUM_SUPPORTED
#  define MAGIC_ENUM_SUPPORTED 1
#endif

// Checks magic_enum compiler aliases compatibility.
#if defined(__clang__) && __clang_major__ >= 5 || defined(__GNUC__) && __GNUC__ >= 9 || defined(_MSC_VER) && _MSC_VER >= 1920
#  undef  MAGIC_ENUM_SUPPORTED_ALIASES
#  define MAGIC_ENUM_SUPPORTED_ALIASES 1
#endif

// Enum value must be greater or equals than MAGIC_ENUM_RANGE_MIN. By default MAGIC_ENUM_RANGE_MIN = -128.
// If need another min range for all enum types by default, redefine the macro MAGIC_ENUM_RANGE_MIN.
#if !defined(MAGIC_ENUM_RANGE_MIN)
#  define MAGIC_ENUM_RANGE_MIN -128
#endif

// Enum value must be less or equals than MAGIC_ENUM_RANGE_MAX. By default MAGIC_ENUM_RANGE_MAX = 128.
// If need another max range for all enum types by default, redefine the macro MAGIC_ENUM_RANGE_MAX.
#if !defined(MAGIC_ENUM_RANGE_MAX)
#  define MAGIC_ENUM_RANGE_MAX 128
#endif

namespace magic_enum {

// If need another optional type, define the macro MAGIC_ENUM_USING_ALIAS_OPTIONAL.
#if defined(MAGIC_ENUM_USING_ALIAS_OPTIONAL)
    MAGIC_ENUM_USING_ALIAS_OPTIONAL
#else
    using std::optional;
#endif

// If need another string_view type, define the macro MAGIC_ENUM_USING_ALIAS_STRING_VIEW.
#if defined(MAGIC_ENUM_USING_ALIAS_STRING_VIEW)
    MAGIC_ENUM_USING_ALIAS_STRING_VIEW
#else
    using std::string_view;
#endif

// If need another string type, define the macro MAGIC_ENUM_USING_ALIAS_STRING.
#if defined(MAGIC_ENUM_USING_ALIAS_STRING)
    MAGIC_ENUM_USING_ALIAS_STRING
#else
    using std::string;
#endif

    namespace customize {

// Enum value must be in range [MAGIC_ENUM_RANGE_MIN, MAGIC_ENUM_RANGE_MAX]. By default MAGIC_ENUM_RANGE_MIN = -128, MAGIC_ENUM_RANGE_MAX = 128.
// If need another range for all enum types by default, redefine the macro MAGIC_ENUM_RANGE_MIN and MAGIC_ENUM_RANGE_MAX.
// If need another range for specific enum type, add specialization enum_range for necessary enum type.
        template <typename E>
        struct enum_range {
            static_assert(std::is_enum_v<E>, "magic_enum::customize::enum_range requires enum type.");
            static constexpr int min = MAGIC_ENUM_RANGE_MIN;
            static constexpr int max = MAGIC_ENUM_RANGE_MAX;
            static_assert(max > min, "magic_enum::customize::enum_range requires max > min.");
        };

        static_assert(MAGIC_ENUM_RANGE_MAX > MAGIC_ENUM_RANGE_MIN, "MAGIC_ENUM_RANGE_MAX must be greater than MAGIC_ENUM_RANGE_MIN.");
        static_assert((MAGIC_ENUM_RANGE_MAX - MAGIC_ENUM_RANGE_MIN) < (std::numeric_limits<std::uint16_t>::max)(), "MAGIC_ENUM_RANGE must be less than UINT16_MAX.");

        namespace detail {
            enum class default_customize_tag {};
            enum class invalid_customize_tag {};
        } // namespace magic_enum::customize::detail

        using customize_t = std::variant<string_view, detail::default_customize_tag, detail::invalid_customize_tag>;

// Default customize.
        inline constexpr auto default_tag = detail::default_customize_tag{};
// Invalid customize.
        inline constexpr auto invalid_tag = detail::invalid_customize_tag{};

// If need custom names for enum, add specialization enum_name for necessary enum type.
        template <typename E>
        constexpr customize_t enum_name(E) noexcept {
            return default_tag;
        }

// If need custom type name for enum, add specialization enum_type_name for necessary enum type.
        template <typename E>
        constexpr customize_t enum_type_name() noexcept {
            return default_tag;
        }

    } // namespace magic_enum::customize

    namespace detail {

        template <auto V, typename = std::enable_if_t<std::is_enum_v<std::decay_t<decltype(V)>>>>
        using enum_constant = std::integral_constant<std::decay_t<decltype(V)>, V>;

        template <typename... T>
        inline constexpr bool always_false_v = false;

        template <typename T>
        struct supported
#if defined(MAGIC_ENUM_SUPPORTED) && MAGIC_ENUM_SUPPORTED || defined(MAGIC_ENUM_NO_CHECK_SUPPORT)
            : std::true_type {};
#else
        : std::false_type {};
#endif

        template <typename T, typename = void>
        struct has_is_flags : std::false_type {};

        template <typename T>
        struct has_is_flags<T, std::void_t<decltype(customize::enum_range<T>::is_flags)>> : std::bool_constant<std::is_same_v<bool, std::decay_t<decltype(customize::enum_range<T>::is_flags)>>> {};

        template <typename T, typename = void>
        struct range_min : std::integral_constant<int, MAGIC_ENUM_RANGE_MIN> {};

        template <typename T>
        struct range_min<T, std::void_t<decltype(customize::enum_range<T>::min)>> : std::integral_constant<decltype(customize::enum_range<T>::min), customize::enum_range<T>::min> {};

        template <typename T, typename = void>
        struct range_max : std::integral_constant<int, MAGIC_ENUM_RANGE_MAX> {};

        template <typename T>
        struct range_max<T, std::void_t<decltype(customize::enum_range<T>::max)>> : std::integral_constant<decltype(customize::enum_range<T>::max), customize::enum_range<T>::max> {};

        template <std::size_t N>
        class static_string {
        public:
            constexpr explicit static_string(string_view str) noexcept : static_string{str, std::make_index_sequence<N>{}} {
                assert(str.size() == N);
            }

            constexpr const char* data() const noexcept { return chars_; }

            constexpr std::size_t size() const noexcept { return N; }

            constexpr operator string_view() const noexcept { return {data(), size()}; }

        private:
            template <std::size_t... I>
            constexpr static_string(string_view str, std::index_sequence<I...>) noexcept : chars_{str[I]..., '\0'} {}

            char chars_[N + 1];
        };

        template <>
        class static_string<0> {
        public:
            constexpr explicit static_string() = default;

            constexpr explicit static_string(string_view) noexcept {}

            constexpr const char* data() const noexcept { return nullptr; }

            constexpr std::size_t size() const noexcept { return 0; }

            constexpr operator string_view() const noexcept { return {}; }
        };

        constexpr string_view pretty_name(string_view name) noexcept {
            for (std::size_t i = name.size(); i > 0; --i) {
                if (!((name[i - 1] >= '0' && name[i - 1] <= '9') ||
                      (name[i - 1] >= 'a' && name[i - 1] <= 'z') ||
                      (name[i - 1] >= 'A' && name[i - 1] <= 'Z') ||
                      #if defined(MAGIC_ENUM_ENABLE_NONASCII)
                      (name[i - 1] & 0x80) ||
                      #endif
                      (name[i - 1] == '_'))) {
                    name.remove_prefix(i);
                    break;
                }
            }

            if (name.size() > 0 && ((name.front() >= 'a' && name.front() <= 'z') ||
                                    (name.front() >= 'A' && name.front() <= 'Z') ||
                                    #if defined(MAGIC_ENUM_ENABLE_NONASCII)
                                    (name.front() & 0x80) ||
                                    #endif
                                    (name.front() == '_'))) {
                return name;
            }

            return {}; // Invalid name.
        }

        class case_insensitive {
            static constexpr char to_lower(char c) noexcept {
                return (c >= 'A' && c <= 'Z') ? static_cast<char>(c + ('a' - 'A')) : c;
            }

        public:
            template <typename L, typename R>
            constexpr auto operator()([[maybe_unused]] L lhs, [[maybe_unused]] R rhs) const noexcept -> std::enable_if_t<std::is_same_v<std::decay_t<L>, char> && std::is_same_v<std::decay_t<R>, char>, bool> {
#if defined(MAGIC_ENUM_ENABLE_NONASCII)
                static_assert(always_false_v<L, R>, "magic_enum::case_insensitive not supported Non-ASCII feature.");
    return false;
#else
                return to_lower(lhs) == to_lower(rhs);
#endif
            }
        };

        constexpr std::size_t find(string_view str, char c) noexcept {
#if defined(__clang__) && __clang_major__ < 9 && defined(__GLIBCXX__) || defined(_MSC_VER) && _MSC_VER < 1920 && !defined(__clang__)
            // https://stackoverflow.com/questions/56484834/constexpr-stdstring-viewfind-last-of-doesnt-work-on-clang-8-with-libstdc
// https://developercommunity.visualstudio.com/content/problem/360432/vs20178-regression-c-failed-in-test.html
  constexpr bool workaround = true;
#else
            constexpr bool workaround = false;
#endif

            if constexpr (workaround) {
                for (std::size_t i = 0; i < str.size(); ++i) {
                    if (str[i] == c) {
                        return i;
                    }
                }

                return string_view::npos;
            } else {
                return str.find_first_of(c);
            }
        }

        template <typename T, std::size_t N, std::size_t... I>
        constexpr std::array<std::remove_cv_t<T>, N> to_array(T (&a)[N], std::index_sequence<I...>) noexcept {
            return {{a[I]...}};
        }

        template <typename BinaryPredicate>
        constexpr bool is_default_predicate() noexcept {
            return std::is_same_v<std::decay_t<BinaryPredicate>, std::equal_to<string_view::value_type>> ||
                   std::is_same_v<std::decay_t<BinaryPredicate>, std::equal_to<>>;
        }

        template <typename BinaryPredicate>
        constexpr bool is_nothrow_invocable() {
            return is_default_predicate<BinaryPredicate>() ||
                   std::is_nothrow_invocable_r_v<bool, BinaryPredicate, char, char>;
        }

        template <typename BinaryPredicate>
        constexpr bool cmp_equal(string_view lhs, string_view rhs, [[maybe_unused]] BinaryPredicate&& p) noexcept(is_nothrow_invocable<BinaryPredicate>()) {
#if defined(_MSC_VER) && _MSC_VER < 1920 && !defined(__clang__)
            // https://developercommunity.visualstudio.com/content/problem/360432/vs20178-regression-c-failed-in-test.html
  // https://developercommunity.visualstudio.com/content/problem/232218/c-constexpr-string-view.html
  constexpr bool workaround = true;
#else
            constexpr bool workaround = false;
#endif

            if constexpr (!is_default_predicate<BinaryPredicate>() || workaround) {
                if (lhs.size() != rhs.size()) {
                    return false;
                }

                const auto size = lhs.size();
                for (std::size_t i = 0; i < size; ++i) {
                    if (!p(lhs[i], rhs[i])) {
                        return false;
                    }
                }

                return true;
            } else {
                return lhs == rhs;
            }
        }

        template <typename L, typename R>
        constexpr bool cmp_less(L lhs, R rhs) noexcept {
            static_assert(std::is_integral_v<L> && std::is_integral_v<R>, "magic_enum::detail::cmp_less requires integral type.");

            if constexpr (std::is_signed_v<L> == std::is_signed_v<R>) {
                // If same signedness (both signed or both unsigned).
                return lhs < rhs;
            } else if constexpr (std::is_same_v<L, bool>) { // bool special case
                return static_cast<R>(lhs) < rhs;
            } else if constexpr (std::is_same_v<R, bool>) { // bool special case
                return lhs < static_cast<L>(rhs);
            } else if constexpr (std::is_signed_v<R>) {
                // If 'right' is negative, then result is 'false', otherwise cast & compare.
                return rhs > 0 && lhs < static_cast<std::make_unsigned_t<R>>(rhs);
            } else {
                // If 'left' is negative, then result is 'true', otherwise cast & compare.
                return lhs < 0 || static_cast<std::make_unsigned_t<L>>(lhs) < rhs;
            }
        }

        template <typename I>
        constexpr I log2(I value) noexcept {
            static_assert(std::is_integral_v<I>, "magic_enum::detail::log2 requires integral type.");

            if constexpr (std::is_same_v<I, bool>) { // bool special case
                return assert(false), value;
            } else {
                auto ret = I{0};
                for (; value > I{1}; value >>= I{1}, ++ret) {}

                return ret;
            }
        }

        template <typename T>
        inline constexpr bool is_enum_v = std::is_enum_v<T> && std::is_same_v<T, std::decay_t<T>>;

        template <typename E>
        constexpr auto n() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::n requires enum type.");

            [[maybe_unused]] constexpr auto custom = customize::enum_type_name<E>();
            static_assert(std::is_same_v<std::decay_t<decltype(custom)>, customize::customize_t>, "magic_enum::customize requires customize_t type.");
            if constexpr (custom.index() == 0) {
                constexpr auto name = std::get<string_view>(custom);
                static_assert(!name.empty(), "magic_enum::customize requires not empty string.");
                return static_string<name.size()>{name};
            } else if constexpr (custom.index() == 1 && supported<E>::value) {
#if defined(__clang__) || defined(__GNUC__)
                constexpr auto name = pretty_name({__PRETTY_FUNCTION__, sizeof(__PRETTY_FUNCTION__) - 2});
#elif defined(_MSC_VER)
                constexpr auto name = pretty_name({__FUNCSIG__, sizeof(__FUNCSIG__) - 17});
#else
    constexpr auto name = string_view{};
#endif
                return static_string<name.size()>{name};
            } else {
                return static_string<0>{}; // Unsupported compiler or Invalid customize.
            }
        }

        template <typename E>
        inline constexpr auto type_name_v = n<E>();

        template <typename E, E V>
        constexpr auto n() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::n requires enum type.");

            [[maybe_unused]] constexpr auto custom = customize::enum_name<E>(V);
            static_assert(std::is_same_v<std::decay_t<decltype(custom)>, customize::customize_t>, "magic_enum::customize requires customize_t type.");
            if constexpr (custom.index() == 0) {
                constexpr auto name = std::get<string_view>(custom);
                static_assert(!name.empty(), "magic_enum::customize requires not empty string.");
                return static_string<name.size()>{name};
            } else if constexpr (custom.index() == 1 && supported<E>::value) {
#if defined(__clang__) || defined(__GNUC__)
                constexpr auto name = pretty_name({__PRETTY_FUNCTION__, sizeof(__PRETTY_FUNCTION__) - 2});
#elif defined(_MSC_VER)
                constexpr auto name = pretty_name({__FUNCSIG__, sizeof(__FUNCSIG__) - 17});
#else
    constexpr auto name = string_view{};
#endif
                return static_string<name.size()>{name};
            } else {
                return static_string<0>{}; // Unsupported compiler or Invalid customize.
            }
        }

        template <typename E, E V>
        inline constexpr auto enum_name_v = n<E, V>();

        template <typename E, auto V>
        constexpr bool is_valid() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::is_valid requires enum type.");

            return n<E, static_cast<E>(V)>().size() != 0;
        }

        template <typename E, int O, bool IsFlags, typename U = std::underlying_type_t<E>>
        constexpr E value(std::size_t i) noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::value requires enum type.");

            if constexpr (std::is_same_v<U, bool>) { // bool special case
                static_assert(O == 0, "magic_enum::detail::value requires valid offset.");

                return static_cast<E>(i);
            } else if constexpr (IsFlags) {
                return static_cast<E>(U{1} << static_cast<U>(static_cast<int>(i) + O));
            } else {
                return static_cast<E>(static_cast<int>(i) + O);
            }
        }

        template <typename E, bool IsFlags, typename U = std::underlying_type_t<E>>
        constexpr int reflected_min() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::reflected_min requires enum type.");

            if constexpr (IsFlags) {
                return 0;
            } else {
                constexpr auto lhs = range_min<E>::value;
                constexpr auto rhs = (std::numeric_limits<U>::min)();

                if constexpr (cmp_less(rhs, lhs)) {
                    return lhs;
                } else {
                    return rhs;
                }
            }
        }

        template <typename E, bool IsFlags, typename U = std::underlying_type_t<E>>
        constexpr int reflected_max() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::reflected_max requires enum type.");

            if constexpr (IsFlags) {
                return std::numeric_limits<U>::digits - 1;
            } else {
                constexpr auto lhs = range_max<E>::value;
                constexpr auto rhs = (std::numeric_limits<U>::max)();

                if constexpr (cmp_less(lhs, rhs)) {
                    return lhs;
                } else {
                    return rhs;
                }
            }
        }

        template <typename E, bool IsFlags>
        inline constexpr auto reflected_min_v = reflected_min<E, IsFlags>();

        template <typename E, bool IsFlags>
        inline constexpr auto reflected_max_v = reflected_max<E, IsFlags>();

        template <std::size_t N>
        constexpr std::size_t values_count(const bool (&valid)[N]) noexcept {
            auto count = std::size_t{0};
            for (std::size_t i = 0; i < N; ++i) {
                if (valid[i]) {
                    ++count;
                }
            }

            return count;
        }

        template <typename E, bool IsFlags, int Min, std::size_t... I>
        constexpr auto values(std::index_sequence<I...>) noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::values requires enum type.");
            constexpr bool valid[sizeof...(I)] = {is_valid<E, value<E, Min, IsFlags>(I)>()...};
            constexpr std::size_t count = values_count(valid);

            if constexpr (count > 0) {
                E values[count] = {};
                for (std::size_t i = 0, v = 0; v < count; ++i) {
                    if (valid[i]) {
                        values[v++] = value<E, Min, IsFlags>(i);
                    }
                }

                return to_array(values, std::make_index_sequence<count>{});
            } else {
                return std::array<E, 0>{};
            }
        }

        template <typename E, bool IsFlags, typename U = std::underlying_type_t<E>>
        constexpr auto values() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::values requires enum type.");
            constexpr auto min = reflected_min_v<E, IsFlags>;
            constexpr auto max = reflected_max_v<E, IsFlags>;
            constexpr auto range_size = max - min + 1;
            static_assert(range_size > 0, "magic_enum::enum_range requires valid size.");
            static_assert(range_size < (std::numeric_limits<std::uint16_t>::max)(), "magic_enum::enum_range requires valid size.");

            return values<E, IsFlags, reflected_min_v<E, IsFlags>>(std::make_index_sequence<range_size>{});
        }

        template <typename E, typename U = std::underlying_type_t<E>>
        constexpr bool is_flags_enum() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::is_flags_enum requires enum type.");

            if constexpr (has_is_flags<E>::value) {
                return customize::enum_range<E>::is_flags;
            } else if constexpr (std::is_same_v<U, bool>) { // bool special case
                return false;
            } else {
#if defined(MAGIC_ENUM_NO_CHECK_FLAGS)
                return false;
#else
                constexpr auto flags_values = values<E, true>();
                constexpr auto default_values = values<E, false>();
                if (flags_values.size() == 0 || default_values.size() > flags_values.size()) {
                    return false;
                }
                for (std::size_t i = 0; i < default_values.size(); ++i) {
                    const auto v = static_cast<U>(default_values[i]);
                    if (v != 0 && (v & (v - 1)) != 0) {
                        return false;
                    }
                }
                return flags_values.size() > 0;
#endif
            }
        }

        template <typename E>
        inline constexpr bool is_flags_v = is_flags_enum<E>();

        template <typename E>
        inline constexpr std::array values_v = values<E, is_flags_v<E>>();

        template <typename E, typename D = std::decay_t<E>>
        using values_t = decltype((values_v<D>));

        template <typename E>
        inline constexpr auto count_v = values_v<E>.size();

        template <typename E, typename U = std::underlying_type_t<E>>
        inline constexpr auto min_v = (count_v<E> > 0) ? static_cast<U>(values_v<E>.front()) : U{0};

        template <typename E, typename U = std::underlying_type_t<E>>
        inline constexpr auto max_v = (count_v<E> > 0) ? static_cast<U>(values_v<E>.back()) : U{0};

        template <typename E, std::size_t... I>
        constexpr auto names(std::index_sequence<I...>) noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::names requires enum type.");

            return std::array<string_view, sizeof...(I)>{{enum_name_v<E, values_v<E>[I]>...}};
        }

        template <typename E>
        inline constexpr std::array names_v = names<E>(std::make_index_sequence<count_v<E>>{});

        template <typename E, typename D = std::decay_t<E>>
        using names_t = decltype((names_v<D>));

        template <typename E, std::size_t... I>
        constexpr auto entries(std::index_sequence<I...>) noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::entries requires enum type.");

            return std::array<std::pair<E, string_view>, sizeof...(I)>{{{values_v<E>[I], enum_name_v<E, values_v<E>[I]>}...}};
        }

        template <typename E>
        inline constexpr std::array entries_v = entries<E>(std::make_index_sequence<count_v<E>>{});

        template <typename E, typename D = std::decay_t<E>>
        using entries_t = decltype((entries_v<D>));

        template <typename E, typename U = std::underlying_type_t<E>>
        constexpr bool is_sparse() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::is_sparse requires enum type.");

            if constexpr (count_v<E> == 0) {
                return false;
            } else if constexpr (std::is_same_v<U, bool>) { // bool special case
                return false;
            } else {
                constexpr auto max = is_flags_v<E> ? log2(max_v<E>) : max_v<E>;
                constexpr auto min = is_flags_v<E> ? log2(min_v<E>) : min_v<E>;
                constexpr auto range_size = max - min + 1;

                return range_size != count_v<E>;
            }
        }

        template <typename E>
        inline constexpr bool is_sparse_v = is_sparse<E>();

        template <typename E, typename U = std::underlying_type_t<E>>
        constexpr U values_ors() noexcept {
            static_assert(is_enum_v<E>, "magic_enum::detail::values_ors requires enum type.");

            auto ors = U{0};
            for (std::size_t i = 0; i < count_v<E>; ++i) {
                ors |= static_cast<U>(values_v<E>[i]);
            }

            return ors;
        }

        template <bool, typename R>
        struct enable_if_enum {};

        template <typename R>
        struct enable_if_enum<true, R> {
            using type = R;
            static_assert(supported<R>::value, "magic_enum unsupported compiler (https://github.com/Neargye/magic_enum#compiler-compatibility).");
        };

        template <typename T, typename R, typename BinaryPredicate = std::equal_to<>>
        using enable_if_t = typename enable_if_enum<std::is_enum_v<std::decay_t<T>> && std::is_invocable_r_v<bool, BinaryPredicate, char, char>, R>::type;

        template <typename T, typename Enable = std::enable_if_t<std::is_enum_v<std::decay_t<T>>>>
        using enum_concept = T;

        template <typename T, bool = std::is_enum_v<T>>
        struct is_scoped_enum : std::false_type {};

        template <typename T>
        struct is_scoped_enum<T, true> : std::bool_constant<!std::is_convertible_v<T, std::underlying_type_t<T>>> {};

        template <typename T, bool = std::is_enum_v<T>>
        struct is_unscoped_enum : std::false_type {};

        template <typename T>
        struct is_unscoped_enum<T, true> : std::bool_constant<std::is_convertible_v<T, std::underlying_type_t<T>>> {};

        template <typename T, bool = std::is_enum_v<std::decay_t<T>>>
        struct underlying_type {};

        template <typename T>
        struct underlying_type<T, true> : std::underlying_type<std::decay_t<T>> {};

        template <typename Value, typename = void>
        struct constexpr_hash_t;

        template <typename Value>
        struct constexpr_hash_t<Value, std::enable_if_t<is_enum_v<Value>>> {
            constexpr auto operator()(Value value) const noexcept {
                using U = typename underlying_type<Value>::type;
                if constexpr (std::is_same_v<U, bool>) { // bool special case
                    return static_cast<std::size_t>(value);
                } else {
                    return static_cast<U>(value);
                }
            }
            using secondary_hash = constexpr_hash_t;
        };

        template <typename Value>
        struct constexpr_hash_t<Value, std::enable_if_t<std::is_same_v<Value, string_view>>> {
            static constexpr std::uint32_t crc_table[256] {
                0x00000000L, 0x77073096L, 0xee0e612cL, 0x990951baL, 0x076dc419L, 0x706af48fL, 0xe963a535L, 0x9e6495a3L,
                0x0edb8832L, 0x79dcb8a4L, 0xe0d5e91eL, 0x97d2d988L, 0x09b64c2bL, 0x7eb17cbdL, 0xe7b82d07L, 0x90bf1d91L,
                0x1db71064L, 0x6ab020f2L, 0xf3b97148L, 0x84be41deL, 0x1adad47dL, 0x6ddde4ebL, 0xf4d4b551L, 0x83d385c7L,
                0x136c9856L, 0x646ba8c0L, 0xfd62f97aL, 0x8a65c9ecL, 0x14015c4fL, 0x63066cd9L, 0xfa0f3d63L, 0x8d080df5L,
                0x3b6e20c8L, 0x4c69105eL, 0xd56041e4L, 0xa2677172L, 0x3c03e4d1L, 0x4b04d447L, 0xd20d85fdL, 0xa50ab56bL,
                0x35b5a8faL, 0x42b2986cL, 0xdbbbc9d6L, 0xacbcf940L, 0x32d86ce3L, 0x45df5c75L, 0xdcd60dcfL, 0xabd13d59L,
                0x26d930acL, 0x51de003aL, 0xc8d75180L, 0xbfd06116L, 0x21b4f4b5L, 0x56b3c423L, 0xcfba9599L, 0xb8bda50fL,
                0x2802b89eL, 0x5f058808L, 0xc60cd9b2L, 0xb10be924L, 0x2f6f7c87L, 0x58684c11L, 0xc1611dabL, 0xb6662d3dL,
                0x76dc4190L, 0x01db7106L, 0x98d220bcL, 0xefd5102aL, 0x71b18589L, 0x06b6b51fL, 0x9fbfe4a5L, 0xe8b8d433L,
                0x7807c9a2L, 0x0f00f934L, 0x9609a88eL, 0xe10e9818L, 0x7f6a0dbbL, 0x086d3d2dL, 0x91646c97L, 0xe6635c01L,
                0x6b6b51f4L, 0x1c6c6162L, 0x856530d8L, 0xf262004eL, 0x6c0695edL, 0x1b01a57bL, 0x8208f4c1L, 0xf50fc457L,
                0x65b0d9c6L, 0x12b7e950L, 0x8bbeb8eaL, 0xfcb9887cL, 0x62dd1ddfL, 0x15da2d49L, 0x8cd37cf3L, 0xfbd44c65L,
                0x4db26158L, 0x3ab551ceL, 0xa3bc0074L, 0xd4bb30e2L, 0x4adfa541L, 0x3dd895d7L, 0xa4d1c46dL, 0xd3d6f4fbL,
                0x4369e96aL, 0x346ed9fcL, 0xad678846L, 0xda60b8d0L, 0x44042d73L, 0x33031de5L, 0xaa0a4c5fL, 0xdd0d7cc9L,
                0x5005713cL, 0x270241aaL, 0xbe0b1010L, 0xc90c2086L, 0x5768b525L, 0x206f85b3L, 0xb966d409L, 0xce61e49fL,
                0x5edef90eL, 0x29d9c998L, 0xb0d09822L, 0xc7d7a8b4L, 0x59b33d17L, 0x2eb40d81L, 0xb7bd5c3bL, 0xc0ba6cadL,
                0xedb88320L, 0x9abfb3b6L, 0x03b6e20cL, 0x74b1d29aL, 0xead54739L, 0x9dd277afL, 0x04db2615L, 0x73dc1683L,
                0xe3630b12L, 0x94643b84L, 0x0d6d6a3eL, 0x7a6a5aa8L, 0xe40ecf0bL, 0x9309ff9dL, 0x0a00ae27L, 0x7d079eb1L,
                0xf00f9344L, 0x8708a3d2L, 0x1e01f268L, 0x6906c2feL, 0xf762575dL, 0x806567cbL, 0x196c3671L, 0x6e6b06e7L,
                0xfed41b76L, 0x89d32be0L, 0x10da7a5aL, 0x67dd4accL, 0xf9b9df6fL, 0x8ebeeff9L, 0x17b7be43L, 0x60b08ed5L,
                0xd6d6a3e8L, 0xa1d1937eL, 0x38d8c2c4L, 0x4fdff252L, 0xd1bb67f1L, 0xa6bc5767L, 0x3fb506ddL, 0x48b2364bL,
                0xd80d2bdaL, 0xaf0a1b4cL, 0x36034af6L, 0x41047a60L, 0xdf60efc3L, 0xa867df55L, 0x316e8eefL, 0x4669be79L,
                0xcb61b38cL, 0xbc66831aL, 0x256fd2a0L, 0x5268e236L, 0xcc0c7795L, 0xbb0b4703L, 0x220216b9L, 0x5505262fL,
                0xc5ba3bbeL, 0xb2bd0b28L, 0x2bb45a92L, 0x5cb36a04L, 0xc2d7ffa7L, 0xb5d0cf31L, 0x2cd99e8bL, 0x5bdeae1dL,
                0x9b64c2b0L, 0xec63f226L, 0x756aa39cL, 0x026d930aL, 0x9c0906a9L, 0xeb0e363fL, 0x72076785L, 0x05005713L,
                0x95bf4a82L, 0xe2b87a14L, 0x7bb12baeL, 0x0cb61b38L, 0x92d28e9bL, 0xe5d5be0dL, 0x7cdcefb7L, 0x0bdbdf21L,
                0x86d3d2d4L, 0xf1d4e242L, 0x68ddb3f8L, 0x1fda836eL, 0x81be16cdL, 0xf6b9265bL, 0x6fb077e1L, 0x18b74777L,
                0x88085ae6L, 0xff0f6a70L, 0x66063bcaL, 0x11010b5cL, 0x8f659effL, 0xf862ae69L, 0x616bffd3L, 0x166ccf45L,
                0xa00ae278L, 0xd70dd2eeL, 0x4e048354L, 0x3903b3c2L, 0xa7672661L, 0xd06016f7L, 0x4969474dL, 0x3e6e77dbL,
                0xaed16a4aL, 0xd9d65adcL, 0x40df0b66L, 0x37d83bf0L, 0xa9bcae53L, 0xdebb9ec5L, 0x47b2cf7fL, 0x30b5ffe9L,
                0xbdbdf21cL, 0xcabac28aL, 0x53b39330L, 0x24b4a3a6L, 0xbad03605L, 0xcdd70693L, 0x54de5729L, 0x23d967bfL,
                0xb3667a2eL, 0xc4614ab8L, 0x5d681b02L, 0x2a6f2b94L, 0xb40bbe37L, 0xc30c8ea1L, 0x5a05df1bL, 0x2d02ef8dL
            };
            constexpr std::uint32_t operator()(string_view value) const noexcept {
                auto crc = static_cast<std::uint32_t>(0xffffffffL);
                for (const auto c : value) {
                    crc = (crc >> 8) ^ crc_table[(crc ^ static_cast<std::uint32_t>(c)) & 0xff];
                }
                return crc ^ 0xffffffffL;
            }

            struct secondary_hash {
                constexpr std::uint32_t operator()(string_view value) const noexcept {
                    auto acc = static_cast<std::uint64_t>(2166136261ULL);
                    for (const auto c : value) {
                        acc = ((acc ^ static_cast<std::uint64_t>(c)) * static_cast<std::uint64_t>(16777619ULL)) & std::numeric_limits<std::uint32_t>::max();
                    }
                    return static_cast<std::uint32_t>(acc);
                }
            };
        };

        template <typename Hash>
        constexpr static Hash hash_v{};

        template <auto* GlobValues, typename Hash>
        constexpr auto calculate_cases(std::size_t Page) noexcept {
            constexpr std::array values = *GlobValues;
            constexpr std::size_t size = values.size();

            using switch_t = std::invoke_result_t<Hash, typename decltype(values)::value_type>;
            static_assert(std::is_integral_v<switch_t> && !std::is_same_v<switch_t, bool>);
            const std::size_t values_to = (std::min)(static_cast<std::size_t>(256), size - Page);

            std::array<switch_t, 256> result{};
            auto fill = result.begin();
            for (auto first = values.begin() + Page, last = values.begin() + Page + values_to; first != last; ) {
                *fill++ = hash_v<Hash>(*first++);
            }

            // dead cases, try to avoid case collisions
            for (switch_t last_value = result[values_to - 1]; fill != result.end() && last_value != (std::numeric_limits<switch_t>::max)(); *fill++ = ++last_value) {
            }

            auto it = result.begin();
            for (auto last_value = (std::numeric_limits<switch_t>::min)(); fill != result.end(); *fill++ = last_value++) {
                while (last_value == *it) {
                    ++last_value, ++it;
                }
            }

            return result;
        }

        template <typename R, typename F, typename... Args>
        constexpr R invoke_r(F&& f, Args&&... args) noexcept(std::is_nothrow_invocable_r_v<R, F, Args...>) {
            if constexpr (std::is_void_v<R>) {
                std::forward<F>(f)(std::forward<Args>(args)...);
            } else {
                return static_cast<R>(std::forward<F>(f)(std::forward<Args>(args)...));
            }
        }

        enum class case_call_t {
            index, value
        };

        template <typename T = void>
        inline constexpr auto default_result_type_lambda = []() noexcept(std::is_nothrow_default_constructible_v<T>) { return T{}; };

        template <>
        inline constexpr auto default_result_type_lambda<void> = []() noexcept {};

        template <auto* Arr, typename Hash>
        constexpr bool no_duplicate() noexcept {
            using value_t = std::decay_t<decltype((*Arr)[0])>;
            using hash_value_t = std::invoke_result_t<Hash, value_t>;
            std::array<hash_value_t, Arr->size()> hashes{};
            std::size_t size = 0;
            for (auto elem : *Arr) {
                hashes[size] = hash_v<Hash>(elem);
                for (auto i = size++; i > 0; --i) {
                    if (hashes[i] < hashes[i - 1]) {
                        auto tmp = hashes[i];
                        hashes[i] = hashes[i - 1];
                        hashes[i - 1] = tmp;
                    } else if (hashes[i] == hashes[i - 1]) {
                        return false;
                    } else {
                        break;
                    }
                }
            }
            return true;
        }

#define MAGIC_ENUM_FOR_EACH_256(T) T(0)T(1)T(2)T(3)T(4)T(5)T(6)T(7)T(8)T(9)T(10)T(11)T(12)T(13)T(14)T(15)T(16)T(17)T(18)T(19)T(20)T(21)T(22)T(23)T(24)T(25)T(26)T(27)T(28)T(29)T(30)T(31)          \
  T(32)T(33)T(34)T(35)T(36)T(37)T(38)T(39)T(40)T(41)T(42)T(43)T(44)T(45)T(46)T(47)T(48)T(49)T(50)T(51)T(52)T(53)T(54)T(55)T(56)T(57)T(58)T(59)T(60)T(61)T(62)T(63)                                 \
  T(64)T(65)T(66)T(67)T(68)T(69)T(70)T(71)T(72)T(73)T(74)T(75)T(76)T(77)T(78)T(79)T(80)T(81)T(82)T(83)T(84)T(85)T(86)T(87)T(88)T(89)T(90)T(91)T(92)T(93)T(94)T(95)                                 \
  T(96)T(97)T(98)T(99)T(100)T(101)T(102)T(103)T(104)T(105)T(106)T(107)T(108)T(109)T(110)T(111)T(112)T(113)T(114)T(115)T(116)T(117)T(118)T(119)T(120)T(121)T(122)T(123)T(124)T(125)T(126)T(127)     \
  T(128)T(129)T(130)T(131)T(132)T(133)T(134)T(135)T(136)T(137)T(138)T(139)T(140)T(141)T(142)T(143)T(144)T(145)T(146)T(147)T(148)T(149)T(150)T(151)T(152)T(153)T(154)T(155)T(156)T(157)T(158)T(159) \
  T(160)T(161)T(162)T(163)T(164)T(165)T(166)T(167)T(168)T(169)T(170)T(171)T(172)T(173)T(174)T(175)T(176)T(177)T(178)T(179)T(180)T(181)T(182)T(183)T(184)T(185)T(186)T(187)T(188)T(189)T(190)T(191) \
  T(192)T(193)T(194)T(195)T(196)T(197)T(198)T(199)T(200)T(201)T(202)T(203)T(204)T(205)T(206)T(207)T(208)T(209)T(210)T(211)T(212)T(213)T(214)T(215)T(216)T(217)T(218)T(219)T(220)T(221)T(222)T(223) \
  T(224)T(225)T(226)T(227)T(228)T(229)T(230)T(231)T(232)T(233)T(234)T(235)T(236)T(237)T(238)T(239)T(240)T(241)T(242)T(243)T(244)T(245)T(246)T(247)T(248)T(249)T(250)T(251)T(252)T(253)T(254)T(255)

#define MAGIC_ENUM_CASE(val)                                                                                                      \
  case cases[val]:                                                                                                                \
    if constexpr ((val) + Page < size) {                                                                                          \
      if (!pred(values[val + Page], searched)) {                                                                                  \
        break;                                                                                                                    \
      }                                                                                                                           \
      if constexpr (CallValue == case_call_t::index) {                                                                            \
        if constexpr (std::is_invocable_r_v<result_t, Lambda, std::integral_constant<std::size_t, val + Page>>) {                 \
          return detail::invoke_r<result_t>(std::forward<Lambda>(lambda), std::integral_constant<std::size_t, val + Page>{});     \
        } else if constexpr (std::is_invocable_v<Lambda, std::integral_constant<std::size_t, val + Page>>) {                      \
          assert(false && "magic_enum::detail::constexpr_switch wrong result type.");                                             \
        }                                                                                                                         \
      } else if constexpr (CallValue == case_call_t::value) {                                                                     \
        if constexpr (std::is_invocable_r_v<result_t, Lambda, enum_constant<values[val + Page]>>) {                               \
          return detail::invoke_r<result_t>(std::forward<Lambda>(lambda), enum_constant<values[val + Page]>{});                   \
        } else if constexpr (std::is_invocable_r_v<result_t, Lambda, enum_constant<values[val + Page]>>) {                        \
          assert(false && "magic_enum::detail::constexpr_switch wrong result type.");                                             \
        }                                                                                                                         \
      }                                                                                                                           \
      break;                                                                                                                      \
    } else [[fallthrough]];

        template <auto* GlobValues,
            case_call_t CallValue,
            std::size_t Page = 0,
            typename Hash = constexpr_hash_t<typename std::decay_t<decltype(*GlobValues)>::value_type>,
            typename Lambda, typename ResultGetterType = decltype(default_result_type_lambda<>),
            typename BinaryPredicate = std::equal_to<>>
        constexpr std::invoke_result_t<ResultGetterType> constexpr_switch(
            Lambda&& lambda,
            typename std::decay_t<decltype(*GlobValues)>::value_type searched,
            ResultGetterType&& def = default_result_type_lambda<>,
            BinaryPredicate&& pred = {}) {
            using result_t = std::invoke_result_t<ResultGetterType>;
            using hash_t = std::conditional_t<no_duplicate<GlobValues, Hash>(), Hash, typename Hash::secondary_hash>;
            constexpr std::array values = *GlobValues;
            constexpr std::size_t size = values.size();
            constexpr std::array cases = calculate_cases<GlobValues, hash_t>(Page);

            switch (hash_v<hash_t>(searched)) {
                MAGIC_ENUM_FOR_EACH_256(MAGIC_ENUM_CASE)
                default:
                    if constexpr (size > 256 + Page) {
                        return constexpr_switch<GlobValues, CallValue, Page + 256, Hash>(std::forward<Lambda>(lambda), searched, std::forward<ResultGetterType>(def));
                    }
                    break;
            }
            return def();
        }

#undef MAGIC_ENUM_FOR_EACH_256
#undef MAGIC_ENUM_CASE

        template <typename E, typename Lambda, std::size_t... I>
        constexpr auto for_each(Lambda&& lambda, std::index_sequence<I...>) {
            static_assert(is_enum_v<E>, "magic_enum::detail::for_each requires enum type.");
            constexpr bool has_void_return = (std::is_void_v<std::invoke_result_t<Lambda, enum_constant<values_v<E>[I]>>> || ...);
            constexpr bool all_same_return = (std::is_same_v<std::invoke_result_t<Lambda, enum_constant<values_v<E>[0]>>, std::invoke_result_t<Lambda, enum_constant<values_v<E>[I]>>> && ...);

            if constexpr (has_void_return) {
                (lambda(enum_constant<values_v<E>[I]>{}), ...);
            } else if constexpr (all_same_return) {
                return std::array{lambda(enum_constant<values_v<E>[I]>{})...};
            } else {
                return std::tuple{lambda(enum_constant<values_v<E>[I]>{})...};
            }
        }

    } // namespace magic_enum::detail

// Checks is magic_enum supported compiler.
    inline constexpr bool is_magic_enum_supported = detail::supported<void>::value;

    template <typename T>
    using Enum = detail::enum_concept<T>;

// Checks whether T is an Unscoped enumeration type.
// Provides the member constant value which is equal to true, if T is an [Unscoped enumeration](https://en.cppreference.com/w/cpp/language/enum#Unscoped_enumeration) type. Otherwise, value is equal to false.
    template <typename T>
    struct is_unscoped_enum : detail::is_unscoped_enum<T> {};

    template <typename T>
    inline constexpr bool is_unscoped_enum_v = is_unscoped_enum<T>::value;

// Checks whether T is an Scoped enumeration type.
// Provides the member constant value which is equal to true, if T is an [Scoped enumeration](https://en.cppreference.com/w/cpp/language/enum#Scoped_enumerations) type. Otherwise, value is equal to false.
    template <typename T>
    struct is_scoped_enum : detail::is_scoped_enum<T> {};

    template <typename T>
    inline constexpr bool is_scoped_enum_v = is_scoped_enum<T>::value;

// If T is a complete enumeration type, provides a member typedef type that names the underlying type of T.
// Otherwise, if T is not an enumeration type, there is no member type. Otherwise (T is an incomplete enumeration type), the program is ill-formed.
    template <typename T>
    struct underlying_type : detail::underlying_type<T> {};

    template <typename T>
    using underlying_type_t = typename underlying_type<T>::type;

    template <auto V>
    using enum_constant = detail::enum_constant<V>;

// Returns type name of enum.
    template <typename E>
    [[nodiscard]] constexpr auto enum_type_name() noexcept -> detail::enable_if_t<E, string_view> {
        constexpr string_view name = detail::type_name_v<std::decay_t<E>>;
        static_assert(!name.empty(), "magic_enum::enum_type_name enum type does not have a name.");

        return name;
    }

// Returns number of enum values.
    template <typename E>
    [[nodiscard]] constexpr auto enum_count() noexcept -> detail::enable_if_t<E, std::size_t> {
        return detail::count_v<std::decay_t<E>>;
    }

// Returns enum value at specified index.
// No bounds checking is performed: the behavior is undefined if index >= number of enum values.
    template <typename E>
    [[nodiscard]] constexpr auto enum_value(std::size_t index) noexcept -> detail::enable_if_t<E, std::decay_t<E>> {
        using D = std::decay_t<E>;

        if constexpr (detail::is_sparse_v<D>) {
            return assert((index < detail::count_v<D>)), detail::values_v<D>[index];
        } else {
            constexpr bool is_flag = detail::is_flags_v<D>;
            constexpr auto min = is_flag ? detail::log2(detail::min_v<D>) : detail::min_v<D>;

            return assert((index < detail::count_v<D>)), detail::value<D, min, is_flag>(index);
        }
    }

// Returns enum value at specified index.
    template <typename E, std::size_t I>
    [[nodiscard]] constexpr auto enum_value() noexcept -> detail::enable_if_t<E, std::decay_t<E>> {
        using D = std::decay_t<E>;
        static_assert(I < detail::count_v<D>, "magic_enum::enum_value out of range.");

        return enum_value<D>(I);
    }

// Returns std::array with enum values, sorted by enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_values() noexcept -> detail::enable_if_t<E, detail::values_t<E>> {
        return detail::values_v<std::decay_t<E>>;
    }

// Returns integer value from enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_integer(E value) noexcept -> detail::enable_if_t<E, underlying_type_t<E>> {
        return static_cast<underlying_type_t<E>>(value);
    }


// Returns underlying value from enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_underlying(E value) noexcept -> detail::enable_if_t<E, underlying_type_t<E>> {
        return static_cast<underlying_type_t<E>>(value);
    }

// Obtains index in enum values from enum value.
// Returns optional with index.
    template <typename E>
    [[nodiscard]] constexpr auto enum_index(E value) noexcept -> detail::enable_if_t<E, optional<std::size_t>> {
        using D = std::decay_t<E>;
        using U = underlying_type_t<D>;

        if constexpr (detail::count_v<D> == 0) {
            return {}; // Empty enum.
        } else if constexpr (detail::is_sparse_v<D> || detail::is_flags_v<D>) {
            return detail::constexpr_switch<&detail::values_v<D>, detail::case_call_t::index>(
                [](std::size_t i) { return optional<std::size_t>{i}; },
                value,
                detail::default_result_type_lambda<optional<std::size_t>>);
        } else {
            const auto v = static_cast<U>(value);
            if (v >= detail::min_v<D> && v <= detail::max_v<D>) {
                return static_cast<std::size_t>(v - detail::min_v<D>);
            }
            return {}; // Invalid value or out of range.
        }
    }

// Returns name from static storage enum variable.
// This version is much lighter on the compile times and is not restricted to the enum_range limitation.
    template <auto V>
    [[nodiscard]] constexpr auto enum_name() noexcept -> detail::enable_if_t<decltype(V), string_view> {
        constexpr string_view name = detail::enum_name_v<std::decay_t<decltype(V)>, V>;
        static_assert(!name.empty(), "magic_enum::enum_name enum value does not have a name.");

        return name;
    }

// Returns name from enum value.
// If enum value does not have name or value out of range, returns empty string.
    template <typename E>
    [[nodiscard]] constexpr auto enum_name(E value) noexcept -> detail::enable_if_t<E, string_view> {
        using D = std::decay_t<E>;

        if (const auto i = enum_index<D>(value)) {
            return detail::names_v<D>[*i];
        }
        return {};
    }

// Returns name from enum-flags value.
// If enum-flags value does not have name or value out of range, returns empty string.
    template <typename E>
    [[nodiscard]] auto enum_flags_name(E value) -> detail::enable_if_t<E, string> {
        using D = std::decay_t<E>;
        using U = underlying_type_t<D>;

        if constexpr (detail::is_flags_v<D>) {
            string name;
            auto check_value = U{0};
            for (std::size_t i = 0; i < detail::count_v<D>; ++i) {
                if (const auto v = static_cast<U>(enum_value<D>(i)); (static_cast<U>(value) & v) != 0) {
                    check_value |= v;
                    const auto n = detail::names_v<D>[i];
                    if (!name.empty()) {
                        name.append(1, '|');
                    }
                    name.append(n.data(), n.size());
                }
            }

            if (check_value != 0 && check_value == static_cast<U>(value)) {
                return name;
            }

            return {}; // Invalid value or out of range.
        } else {
            return string{enum_name(value)};
        }
    }

// Returns std::array with names, sorted by enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_names() noexcept -> detail::enable_if_t<E, detail::names_t<E>> {
        return detail::names_v<std::decay_t<E>>;
    }

// Returns std::array with pairs (value, name), sorted by enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_entries() noexcept -> detail::enable_if_t<E, detail::entries_t<E>> {
        return detail::entries_v<std::decay_t<E>>;
    }

// Obtains enum value from integer value.
// Returns optional with enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_cast(underlying_type_t<E> value) noexcept -> detail::enable_if_t<E, optional<std::decay_t<E>>> {
        using D = std::decay_t<E>;
        using U = underlying_type_t<D>;

        if constexpr (detail::count_v<D> == 0) {
            return {}; // Empty enum.
        } else if constexpr (detail::is_sparse_v<D>) {
            if constexpr (detail::is_flags_v<D>) {
                constexpr auto count = detail::count_v<D>;
                auto check_value = U{0};
                for (std::size_t i = 0; i < count; ++i) {
                    if (const auto v = static_cast<U>(enum_value<D>(i)); (value & v) != 0) {
                        check_value |= v;
                    }
                }

                if (check_value != 0 && check_value == value) {
                    return static_cast<D>(value);
                }
                return {}; // Invalid value or out of range.
            } else {
                return detail::constexpr_switch<&detail::values_v<D>, detail::case_call_t::value>(
                    [](D v) { return optional<D>{v}; },
                    static_cast<D>(value),
                    detail::default_result_type_lambda<optional<D>>);
            }
        } else {
            constexpr auto min = detail::min_v<D>;
            constexpr auto max = detail::is_flags_v<D> ? detail::values_ors<D>() : detail::max_v<D>;

            if (value >= min && value <= max) {
                return static_cast<D>(value);
            }
            return {}; // Invalid value or out of range.
        }
    }

// Allows you to write magic_enum::enum_cast<foo>("bar", magic_enum::case_insensitive);
    inline constexpr auto case_insensitive = detail::case_insensitive{};

// Obtains enum value from name.
// Returns optional with enum value.
    template <typename E, typename BinaryPredicate = std::equal_to<>>
    [[nodiscard]] constexpr auto enum_cast(string_view value, [[maybe_unused]] BinaryPredicate&& p = {}) noexcept(detail::is_nothrow_invocable<BinaryPredicate>()) -> detail::enable_if_t<E, optional<std::decay_t<E>>, BinaryPredicate> {
        static_assert(std::is_invocable_r_v<bool, BinaryPredicate, char, char>, "magic_enum::enum_cast requires bool(char, char) invocable predicate.");
        using D = std::decay_t<E>;
        using U = underlying_type_t<D>;

        if constexpr (detail::count_v<D> == 0) {
            return {}; // Empty enum.
        } else if constexpr (detail::is_flags_v<D>) {
            auto result = U{0};
            while (!value.empty()) {
                const auto d = detail::find(value, '|');
                const auto s = (d == string_view::npos) ? value : value.substr(0, d);
                auto f = U{0};
                for (std::size_t i = 0; i < detail::count_v<D>; ++i) {
                    if (detail::cmp_equal(s, detail::names_v<D>[i], p)) {
                        f = static_cast<U>(enum_value<D>(i));
                        result |= f;
                        break;
                    }
                }
                if (f == U{0}) {
                    return {}; // Invalid value or out of range.
                }
                value.remove_prefix((d == string_view::npos) ? value.size() : d + 1);
            }

            if (result != U{0}) {
                return static_cast<D>(result);
            }
            return {}; // Invalid value or out of range.
        } else if constexpr (detail::count_v<D> > 0) {
            if constexpr (detail::is_default_predicate<BinaryPredicate>()) {
                return detail::constexpr_switch<&detail::names_v<D>, detail::case_call_t::index>(
                    [](std::size_t i) { return optional<D>{detail::values_v<D>[i]}; },
                    value,
                    detail::default_result_type_lambda<optional<D>>,
                    [&p](string_view lhs, string_view rhs) { return detail::cmp_equal(lhs, rhs, p); });
            } else {
                for (std::size_t i = 0; i < detail::count_v<D>; ++i) {
                    if (detail::cmp_equal(value, detail::names_v<D>[i], p)) {
                        return enum_value<D>(i);
                    }
                }
                return {}; // Invalid value or out of range.
            }
        }
    }

// Obtains index in enum values from static storage enum variable.
    template <auto V>
    [[nodiscard]] constexpr auto enum_index() noexcept -> detail::enable_if_t<decltype(V), std::size_t> {
        constexpr auto index = enum_index<std::decay_t<decltype(V)>>(V);
        static_assert(index, "magic_enum::enum_index enum value does not have a index.");

        return *index;
    }

// Checks whether enum contains enumerator with such enum value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_contains(E value) noexcept -> detail::enable_if_t<E, bool> {
        using D = std::decay_t<E>;
        using U = underlying_type_t<D>;

        return static_cast<bool>(enum_cast<D>(static_cast<U>(value)));
    }

// Checks whether enum contains enumerator with such integer value.
    template <typename E>
    [[nodiscard]] constexpr auto enum_contains(underlying_type_t<E> value) noexcept -> detail::enable_if_t<E, bool> {
        using D = std::decay_t<E>;

        return static_cast<bool>(enum_cast<D>(value));
    }

// Checks whether enum contains enumerator with such name.
    template <typename E, typename BinaryPredicate = std::equal_to<>>
    [[nodiscard]] constexpr auto enum_contains(string_view value, BinaryPredicate&& p = {}) noexcept(detail::is_nothrow_invocable<BinaryPredicate>()) -> detail::enable_if_t<E, bool, BinaryPredicate> {
        static_assert(std::is_invocable_r_v<bool, BinaryPredicate, char, char>, "magic_enum::enum_contains requires bool(char, char) invocable predicate.");
        using D = std::decay_t<E>;

        return static_cast<bool>(enum_cast<D>(value, std::forward<BinaryPredicate>(p)));
    }

    template <typename Result = void, typename E, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, E value) -> detail::enable_if_t<E, Result> {
        using D = std::decay_t<E>;

        return detail::constexpr_switch<&detail::values_v<D>, detail::case_call_t::value>(
            std::forward<Lambda>(lambda),
            value,
            detail::default_result_type_lambda<Result>);
    }

    template <typename Result, typename E, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, E value, Result&& result) -> detail::enable_if_t<E, Result> {
        using D = std::decay_t<E>;

        return detail::constexpr_switch<&detail::values_v<D>, detail::case_call_t::value>(
            std::forward<Lambda>(lambda),
            value,
            [&result] { return std::forward<Result>(result); });
    }

    template <typename E, typename Result = void, typename BinaryPredicate = std::equal_to<>, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, string_view name, BinaryPredicate&& p = {}) -> detail::enable_if_t<E, Result, BinaryPredicate> {
        static_assert(std::is_invocable_r_v<bool, BinaryPredicate, char, char>, "magic_enum::enum_switch requires bool(char, char) invocable predicate.");
        using D = std::decay_t<E>;

        if (const auto v = enum_cast<D>(name, std::forward<BinaryPredicate>(p))) {
            return enum_switch<Result, D>(std::forward<Lambda>(lambda), *v);
        }
        return detail::default_result_type_lambda<Result>();
    }

    template <typename E, typename Result, typename BinaryPredicate = std::equal_to<>, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, string_view name, Result&& result, BinaryPredicate&& p = {}) -> detail::enable_if_t<E, Result, BinaryPredicate> {
        static_assert(std::is_invocable_r_v<bool, BinaryPredicate, char, char>, "magic_enum::enum_switch requires bool(char, char) invocable predicate.");
        using D = std::decay_t<E>;

        if (const auto v = enum_cast<D>(name, std::forward<BinaryPredicate>(p))) {
            return enum_switch<Result, D>(std::forward<Lambda>(lambda), *v, std::forward<Result>(result));
        }
        return std::forward<Result>(result);
    }

    template <typename E, typename Result = void, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, underlying_type_t<E> value) -> detail::enable_if_t<E, Result> {
        using D = std::decay_t<E>;

        if (const auto v = enum_cast<D>(value)) {
            return enum_switch<Result, D>(std::forward<Lambda>(lambda), *v);
        }
        return detail::default_result_type_lambda<Result>();
    }

    template <typename E, typename Result, typename Lambda>
    constexpr auto enum_switch(Lambda&& lambda, underlying_type_t<E> value, Result&& result) -> detail::enable_if_t<E, Result> {
        using D = std::decay_t<E>;

        if (const auto v = enum_cast<D>(value)) {
            return enum_switch<Result, D>(std::forward<Lambda>(lambda), *v, std::forward<Result>(result));
        }
        return std::forward<Result>(result);
    }

    template <typename E, typename Lambda>
    constexpr auto enum_for_each(Lambda&& lambda) {
        using D = std::decay_t<E>;
        static_assert(std::is_enum_v<D>, "magic_enum::enum_for_each requires enum type.");

        return detail::for_each<D>(std::forward<Lambda>(lambda), std::make_index_sequence<detail::count_v<D>>{});
    }

    namespace detail {

        template <typename E>
        constexpr optional<std::uintmax_t> fuse_one_enum(optional<std::uintmax_t> hash, E value) noexcept {
            if (hash) {
                if (const auto index = enum_index(value)) {
                    return (*hash << log2(enum_count<E>() + 1)) | *index;
                }
            }
            return {};
        }

        template <typename E>
        constexpr optional<std::uintmax_t> fuse_enum(E value) noexcept {
            return fuse_one_enum(0, value);
        }

        template <typename E, typename... Es>
        constexpr optional<std::uintmax_t> fuse_enum(E head, Es... tail) noexcept {
            return fuse_one_enum(fuse_enum(tail...), head);
        }

        template <typename... Es>
        constexpr auto typesafe_fuse_enum(Es... values) noexcept {
            enum class enum_fuse_t : std::uintmax_t;
            const auto fuse = fuse_enum(values...);
            if (fuse) {
                return optional<enum_fuse_t>{static_cast<enum_fuse_t>(*fuse)};
            }
            return optional<enum_fuse_t>{};
        }

    } // namespace magic_enum::detail

// Returns a bijective mix of several enum values. This can be used to emulate 2D switch/case statements.
    template <typename... Es>
    [[nodiscard]] constexpr auto enum_fuse(Es... values) noexcept {
        static_assert((std::is_enum_v<std::decay_t<Es>> && ...), "magic_enum::enum_fuse requires enum type.");
        static_assert(sizeof...(Es) >= 2, "magic_enum::enum_fuse requires at least 2 values.");
        static_assert((detail::log2(enum_count<Es>() + 1) + ...) <= (sizeof(std::uintmax_t) * 8), "magic_enum::enum_fuse does not work for large enums");
#if defined(MAGIC_ENUM_NO_TYPESAFE_ENUM_FUSE)
        const auto fuse = detail::fuse_enum<std::decay_t<Es>...>(values...);
#else
        const auto fuse = detail::typesafe_fuse_enum<std::decay_t<Es>...>(values...);
#endif
        return assert(fuse), fuse;
    }

    namespace ostream_operators {

        template <typename Char, typename Traits, typename E, detail::enable_if_t<E, int> = 0>
        std::basic_ostream<Char, Traits>& operator<<(std::basic_ostream<Char, Traits>& os, E value) {
            using D = std::decay_t<E>;
            using U = underlying_type_t<D>;

            if constexpr (detail::supported<D>::value) {
                if (const auto name = enum_flags_name<D>(value); !name.empty()) {
                    for (const auto c : name) {
                        os.put(c);
                    }
                    return os;
                }
            }
            return (os << static_cast<U>(value));
        }

        template <typename Char, typename Traits, typename E, detail::enable_if_t<E, int> = 0>
        std::basic_ostream<Char, Traits>& operator<<(std::basic_ostream<Char, Traits>& os, optional<E> value) {
            return value ? (os << *value) : os;
        }

    } // namespace magic_enum::ostream_operators

    namespace istream_operators {

        template <typename Char, typename Traits, typename E, detail::enable_if_t<E, int> = 0>
        std::basic_istream<Char, Traits>& operator>>(std::basic_istream<Char, Traits>& is, E& value) {
            using D = std::decay_t<E>;

            std::basic_string<Char, Traits> s;
            is >> s;
            if (const auto v = enum_cast<D>(s)) {
                value = *v;
            } else {
                is.setstate(std::basic_ios<Char>::failbit);
            }
            return is;
        }

    } // namespace magic_enum::istream_operators

    namespace iostream_operators {

        using namespace ostream_operators;
        using namespace istream_operators;

    } // namespace magic_enum::iostream_operators

    namespace bitwise_operators {

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E operator~(E rhs) noexcept {
            return static_cast<E>(~static_cast<underlying_type_t<E>>(rhs));
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E operator|(E lhs, E rhs) noexcept {
            return static_cast<E>(static_cast<underlying_type_t<E>>(lhs) | static_cast<underlying_type_t<E>>(rhs));
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E operator&(E lhs, E rhs) noexcept {
            return static_cast<E>(static_cast<underlying_type_t<E>>(lhs) & static_cast<underlying_type_t<E>>(rhs));
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E operator^(E lhs, E rhs) noexcept {
            return static_cast<E>(static_cast<underlying_type_t<E>>(lhs) ^ static_cast<underlying_type_t<E>>(rhs));
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E& operator|=(E& lhs, E rhs) noexcept {
            return lhs = (lhs | rhs);
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E& operator&=(E& lhs, E rhs) noexcept {
            return lhs = (lhs & rhs);
        }

        template <typename E, detail::enable_if_t<E, int> = 0>
        constexpr E& operator^=(E& lhs, E rhs) noexcept {
            return lhs = (lhs ^ rhs);
        }

    } // namespace magic_enum::bitwise_operators

} // namespace magic_enum

#if defined(__clang__)
#  pragma clang diagnostic pop
#elif defined(__GNUC__)
#  pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#  pragma warning(pop)
#endif

#endif // NEARGYE_MAGIC_ENUM_HPP

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/math_utils.h included by src/immvision/internal/cv/colormap.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace MathUtils
    {
        int RoundInt(double v);
        double MaximumValue(const std::vector<double> &v);
        double MinimumValue(const std::vector<double> &v);

        inline double Lerp(double a, double b, double x) noexcept
        {
            return (a + (b - a) * x);
        }
        inline double UnLerp(double a, double b, double x) noexcept
        {
            return (x - a) / (b - a);
        }

        inline std::vector<double> arange(double a, double b, double step)
        {
            std::vector<double> r;
            double v = a;
            while (v < b)
            {
                r.push_back(v);
                v += step;
            }
            return r;
        }
    } // namespace MathUtils


} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_texture.h included by src/immvision/internal/cv/colormap.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <memory>

namespace ImmVision
{
    /// GlTexture holds a OpenGL Texture (created via glGenTextures)
    /// You can blit (i.e transfer) image buffer onto it.
    /// The linked OpenGL texture lifetime is linked to this.
    /// GlTexture is not copiable (since it holds a reference to a texture stored on the GPU)
    struct GlTexture
    {
        GlTexture();
        virtual ~GlTexture();

        // non copiable
        GlTexture(const GlTexture& ) = delete;
        GlTexture& operator=(const GlTexture& ) = delete;

        void Draw(const ImVec2& size = ImVec2(0, 0), const ImVec2& uv0 = ImVec2(0, 0), const ImVec2& uv1 = ImVec2(1,1), const ImVec4& tint_col = ImVec4(1,1,1,1), const ImVec4& border_col = ImVec4(0,0,0,0)) const;
        bool DrawButton(const ImVec2& size = ImVec2(0, 0), const ImVec2& uv0 = ImVec2(0, 0),  const ImVec2& uv1 = ImVec2(1,1), int frame_padding = -1, const ImVec4& bg_col = ImVec4(0,0,0,0), const ImVec4& tint_col = ImVec4(1,1,1,1)) const;
        void Draw_DisableDragWindow(const ImVec2& size = ImVec2(0, 0)) const;

        void Blit_RGBA_Buffer(unsigned char *image_data, int image_width, int image_height);

        // members
        ImVec2 mImageSize;
        unsigned int mImTextureId;
    };


    struct GlTextureCv : public GlTexture
    {
        GlTextureCv() = default;
        GlTextureCv(const cv::Mat& mat, bool isBgrOrBgra);
        ~GlTextureCv() override = default;

        void BlitMat(const cv::Mat& mat, bool isBgrOrBgra);
    };

} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/imgui_imm.h included by src/immvision/internal/cv/colormap.cpp           //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// Some extensions to ImGui, specific to ImmVision
namespace ImGuiImm
{
    // A slider that works for float, double, and long double
    // Internally, it calls ImGui::SliderFloat (so that the accuracy may be a little reduced)
    // Be sure to cast all your params when calling, especially v_min and v_max
    template<typename AnyFloat>
    bool SliderAnyFloat(
        const char*label,
        AnyFloat* v,
        AnyFloat v_min = AnyFloat(0.),
        AnyFloat v_max = AnyFloat(1.),
        float width = 200.f,
        bool logarithmic = false,
        int nb_decimals = 6);

    template<typename AnyFloat>
    bool SliderAnyFloatLogarithmic(
        const char*label,
        AnyFloat* v,
        AnyFloat v_min = AnyFloat(0.),
        AnyFloat v_max = AnyFloat(1.),
        float width = 200.f,
        int nb_decimals = 6);


    ImVec2 ComputeDisplayImageSize(ImVec2 askedImageSize, ImVec2 realImageSize);
    cv::Size ComputeDisplayImageSize(cv::Size askedImageSize, cv::Size realImageSize);

    void PushDisabled();
    void PopDisabled();
    void SameLineAlignRight(float rightMargin = 0.f, float alignRegionWidth = -1.f);

    // cf https://github.com/ocornut/imgui/issues/1496#issuecomment-655048353
    void BeginGroupPanel(const char* name, const ImVec2& size = ImVec2(0.0f, 0.0f));
    void EndGroupPanel();

    void BeginGroupPanel_FlagBorder(const char* name, bool draw_border, const ImVec2& size = ImVec2(0.0f, 0.0f));
    void EndGroupPanel_FlagBorder();
    ImVec2 GroupPanel_FlagBorder_LastKnownSize(const char* name);

    // Draw a fixed width Separator
    // useful when ImGui::Separator() overflows to the right
    void SeparatorFixedWidth(float width);

    void BeginGroupFixedWidth(float width);
    void EndGroupFixedWidth();
}



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/colormap.cpp continued                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define IMGUI_DEFINE_MATH_OPERATORS
#include "imgui_internal.h"


namespace ImmVision
{
    namespace Colormap
    {
        //
        // Base operations for ColormapSettingsData
        //
        bool IsNone(const ColormapSettingsData& a)
        {
            ColormapSettingsData empty;
            return IsEqual(a, empty);
        }


        bool IsEqual(const ColormapSettingsData& v1, const ColormapSettingsData& v2)
        {
            if (v1.Colormap != v2.Colormap)
                return false;
            if (fabs(v1.ColormapScaleMax - v2.ColormapScaleMax) > 1E-6)
                return false;
            if (fabs(v1.ColormapScaleMin - v2.ColormapScaleMin) > 1E-6)
                return false;
            if (v1.internal_ColormapHovered != v2.internal_ColormapHovered)
                return false;
            if (!IsEqual(v1.ColormapScaleFromStats, v2.ColormapScaleFromStats))
                return false;
            return true;
        }


        bool IsEqual(const ColormapScaleFromStatsData& v1, const ColormapScaleFromStatsData& v2)
        {
            if (v1.ActiveOnFullImage != v2.ActiveOnFullImage)
                return false;
            if (v1.ActiveOnROI != v2.ActiveOnROI)
                return false;
            if (fabs(v1.NbSigmas - v2.NbSigmas) > 1E-6)
                return false;
            if (v1.UseStatsMin != v2.UseStatsMin)
                return false;
            if (v1.UseStatsMax != v2.UseStatsMax)
                return false;
            return true;
        }


        bool CanColormap(const cv::Mat &image)
        {
            return image.channels() == 1;
        }


        ColormapSettingsData ComputeInitialColormapSettings(const cv::Mat& m)
        {
            (void)m;
            ColormapSettingsData r;
            return r;
        }



        //
        // Colormaps images and textures
        //


        using ColormapType = tinycolormap::ColormapType;


        std::vector<std::string> AvailableColormaps()
        {
            std::vector<std::string> r;
            magic_enum::enum_for_each<ColormapType>([&r] (auto val) {
                ColormapType type = val;
                const char* name = magic_enum::enum_name(type).data();
                r.push_back(name);
            });
            return r;
        }


        cv::Mat MakeColormapImage(tinycolormap::ColormapType colorType)
        {
            int w = 256, h = 15;
            cv::Mat_<cv::Vec3b> m(cv::Size(w, h));
            for (int x = 0; x < w; ++x)
            {
                double k = MathUtils::UnLerp(0., (double)w, (double)x);
                auto col = tinycolormap::GetColor(k, colorType);
                for (int y = 0; y < h; ++y)
                    m(y, x) = cv::Vec3b( col.bi(), col.gi(), col.ri() );
            }

            return std::move(m);
        }


        const insertion_order_map<std::string, cv::Mat>& ColormapsImages()
        {
            static insertion_order_map<std::string, cv::Mat> cache;
            if (cache.empty())
            {
                magic_enum::enum_for_each<ColormapType>([] (auto val) {
                    ColormapType type = val;
                    const char* name = magic_enum::enum_name(type).data();
                    cache.insert(name, MakeColormapImage(type));
                });
            }
            return cache;
        }


        static insertion_order_map<std::string, std::unique_ptr<GlTextureCv>> sColormapsTexturesCache;


        void FillTextureCache()
        {
            if (sColormapsTexturesCache.empty())
            {
                auto images = ColormapsImages();
                for (const auto& k: images.insertion_order_keys())
                {
                    cv::Mat& m = images.get(k);
                    auto texture = std::make_unique<GlTextureCv>(m, true);
                    sColormapsTexturesCache.insert(k, std::move(texture));
                }
            }
        }


        const insertion_order_map<std::string, unsigned int>& ColormapsTextures()
        {
            FillTextureCache();

            static insertion_order_map<std::string, unsigned int> cache;
            if (cache.empty())
            {
                for (const auto& k: sColormapsTexturesCache.insertion_order_keys())
                    cache.insert(k, sColormapsTexturesCache.get(k)->mImTextureId);
            }
            return cache;
        }


        void ClearColormapsTexturesCache()
        {
            sColormapsTexturesCache.clear();
        }



        //
        // Apply Colormap
        //


        template<typename _Tp>
        cv::Mat_<cv::Vec4b> _ApplyColormap(const cv::Mat &m, const ColormapSettingsData& settings)
        {
            assert(CanColormap(m));

            std::string colormapName = settings.internal_ColormapHovered.empty() ? settings.Colormap : settings.internal_ColormapHovered;

            auto _colormapType = magic_enum::enum_cast<ColormapType>(colormapName);
            if (!_colormapType.has_value())
            {
                fprintf(stderr, "_ApplyColormap: bad colormap name: %s\n", settings.Colormap.c_str());
                assert(false);
            }
            auto colormapType = _colormapType.value();

            std::array<cv::Vec4b, 256> colorLut;
            for (size_t i = 0; i < 256; ++i)
            {
                double x = (double) i / 255.;
                 auto c = tinycolormap::GetColor(x, colormapType);
                colorLut[i] = { c.ri(), c.gi(), c.bi(), 255 };
            }

            double minValue = settings.ColormapScaleMin;
            double maxValue = settings.ColormapScaleMax;
            auto fnGetColor = [&](_Tp value) -> cv::Vec4b
            {
                double k = (value - minValue) / (maxValue - minValue);
                k = std::clamp(k, 0., 1.);
                size_t idx = (size_t)(k * 255.);
                return colorLut[idx];
            };

            cv::Mat_<cv::Vec4b> rgba(m.size());
            for (int y = 0; y < m.rows; ++y)
            {
                cv::Vec4b *dst = &rgba(y, 0);
                const _Tp* src = &m.at<_Tp>(y, 0);
                for (int x = 0; x < m.cols; ++x)
                {
                    *dst = fnGetColor(*src);
                    ++dst;
                    ++src;
                }
            }
            return rgba;
        }


        cv::Mat_<cv::Vec4b> ApplyColormap(const cv::Mat &m, const ColormapSettingsData& settings)
        {
            if (m.depth() == CV_8U)
                return _ApplyColormap<uchar>(m, settings);
            else if (m.depth() == CV_8S)
                return _ApplyColormap<char>(m, settings);
            else if (m.depth() == CV_16U)
                return _ApplyColormap<uint16_t>(m, settings);
            else if (m.depth() == CV_16S)
                return _ApplyColormap<int16_t>(m, settings);
            else if (m.depth() == CV_32S)
                return _ApplyColormap<int32_t>(m, settings);
            if (m.depth() == CV_32F)
                return _ApplyColormap<float>(m, settings);
            else if (m.depth() == CV_64F)
                return _ApplyColormap<double>(m, settings);
#ifdef CV_16F
            else if (m.depth() == CV_16F)
                return _ApplyColormap<cv::float16_t>(m, settings);
#endif
            else
            {
                assert(false);
                throw std::runtime_error("ApplyColormap: bad depth");
            }
        }


        //
        // Interactive update during pan and zoom
        //
        struct ImageStats
        {
            double mean, stdev;
            double min, max;
        };

        ImageStats FillImageStats(const cv::Mat& m)
        {
            assert(m.channels() == 1);
            ImageStats r;
            cv::minMaxLoc(m, &r.min, &r.max);
            cv::Scalar mean, deviation;
            cv::meanStdDev(m, mean, deviation);
            r.mean = mean[0];
            r.stdev = deviation[0];
            return r;
        }




        void ApplyColormapStatsToMinMax(const cv::Mat& m, std::optional<cv::Rect> roi, ColormapSettingsData* inout_settings)
        {
            bool isRoi = roi.has_value();

            ImageStats imageStats;
            if (isRoi)
                imageStats = FillImageStats(m(roi.value()));
            else
                imageStats = FillImageStats(m);

            if (inout_settings->ColormapScaleFromStats.UseStatsMin)
                inout_settings->ColormapScaleMin = imageStats.min;
            else
                inout_settings->ColormapScaleMin =
                    imageStats.mean - (double) inout_settings->ColormapScaleFromStats.NbSigmas * imageStats.stdev;

            if (inout_settings->ColormapScaleFromStats.UseStatsMax)
                inout_settings->ColormapScaleMax = imageStats.max;
            else
                inout_settings->ColormapScaleMax =
                    imageStats.mean + (double) inout_settings->ColormapScaleFromStats.NbSigmas * imageStats.stdev;
        }


        void AssertColormapScaleFromStats_ActiveMostOne(ColormapSettingsData* const settings)
        {
            if (settings->ColormapScaleFromStats.ActiveOnFullImage && settings->ColormapScaleFromStats.ActiveOnROI)
            {
                std::string msg = "ActiveOnFullImage and ActiveOnFullImage cannot be true together!";
                fprintf(stderr, "%s", msg.c_str());
                throw std::runtime_error(msg.c_str());
            }
        }

        void UpdateRoiStatsInteractively(
            const cv::Mat &image,
            const cv::Rect& roi,
            ColormapSettingsData* inout_settings)
        {
            if (image.channels() != 1)
                return;

            assert(!roi.empty());
            AssertColormapScaleFromStats_ActiveMostOne(inout_settings);

            if (inout_settings->ColormapScaleFromStats.ActiveOnROI)
                ApplyColormapStatsToMinMax(image, roi, inout_settings);
        }


        void InitStatsOnNewImage(
            const cv::Mat &image,
            const cv::Rect& roi,
            ColormapSettingsData* inout_settings)
        {
            if (image.channels() != 1)
                return;

            assert(!roi.empty());
            AssertColormapScaleFromStats_ActiveMostOne(inout_settings);

            if (inout_settings->ColormapScaleFromStats.ActiveOnROI)
                ApplyColormapStatsToMinMax(image, roi, inout_settings);
            else if (inout_settings->ColormapScaleFromStats.ActiveOnFullImage)
                ApplyColormapStatsToMinMax(image, std::nullopt, inout_settings);
        }



        //
        // GUI
        //
        void GuiChooseColormap(ColormapSettingsData* inout_params)
        {
            static std::optional<std::string> lastUnselectedColormap;
            FillTextureCache();

            inout_params->internal_ColormapHovered = "";
            for (const auto& kv: sColormapsTexturesCache.items())
            {
                std::string colormapName = kv.first;
                bool wasSelected = (colormapName == inout_params->Colormap);

                ImVec4 colorNormal(0.7f, 0.7f, 0.7f, 1.f);
                ImVec4 colorSelected(1.f, 1.f, 0.2f, 1.f);
                ImVec4 colorHovered = colorSelected;
                colorHovered.w = 0.65f;

                float widthText = 75.f;
                ImVec2 sizeTexture(200.f, 15.f);

                bool isHovered;
                {
                    auto posWidget = ImGui::GetCursorScreenPos();
                    auto posMouse = ImGui::GetMousePos();
                    ImRect bounding(posWidget, posWidget + ImVec2(sizeTexture.x + widthText, 15.f));
                    isHovered = bounding.Contains(posMouse);
                }

                ImVec4 color;
                if (wasSelected)
                    color = colorSelected;
                else if (isHovered)
                    color = colorHovered;
                else
                    color = colorNormal;

                auto pos = ImGui::GetCursorPos();
                ImGui::TextColored(color, "%s", colormapName.c_str());
                pos.x += widthText;
                ImGui::SetCursorPos(pos);
                if (wasSelected)
                    kv.second->DrawButton(sizeTexture);
                else
                kv.second->Draw(sizeTexture);
                if (ImGui::IsItemHovered())
                {
                    if (!lastUnselectedColormap.has_value())
                        inout_params->internal_ColormapHovered = colormapName;
                    if (lastUnselectedColormap.has_value() && (*lastUnselectedColormap != colormapName))
                        inout_params->internal_ColormapHovered = colormapName;
                }
                if (ImGui::IsItemHovered() && ImGui::IsMouseClicked(0))
                {
                    if (wasSelected)
                    {
                        inout_params->Colormap = "None";
                        lastUnselectedColormap = colormapName;
                    }
                    else
                    {
                        inout_params->Colormap = colormapName;
                        lastUnselectedColormap = std::nullopt;
                    }
                }
            }
        }


        void DrawColorTabsSubtitles(const std::string &title, float availableGuiWidth)
        {
            ImVec4 textColor = ImGui::GetStyleColorVec4(ImGuiCol_Text);
            ImVec4 backColor = ImGui::GetStyleColorVec4(ImGuiCol_TabActive);
            backColor.w = 0.3f;

            // background rect
            {
                ImVec2 tl = ImGui::GetCursorScreenPos();
                ImVec2 br = tl;
                br.x += availableGuiWidth - 10.f;
                br.y += ImGui::GetFontSize() + 2.f;
                ImU32 col = ImGui::GetColorU32(backColor);
                float rounding = 4.f;
                ImGui::GetWindowDrawList()->AddRectFilled(tl, br, col, rounding);
            }
            std::string fullTitle = std::string("          Colormap Scale ") + title;

            ImGui::TextColored(textColor, "%s", fullTitle.c_str());
        }


        void GuiImageStats(const cv::Mat& m, std::optional<cv::Rect> roi, ColormapSettingsData* inout_settings, float availableGuiWidth)
        {
            ImageStats imageStats;
            bool isRoi = roi.has_value();
            if (isRoi)
            {
                imageStats = FillImageStats(m(roi.value()));
                ImGui::PushID("ROI");
                DrawColorTabsSubtitles("From ROI Stats", availableGuiWidth);
                ImGui::Text("ROI: Pos(%i, %i), Size(%i, %i)", roi->x, roi->y, roi->width, roi->height);
            }
            else
            {
                imageStats = FillImageStats(m);
                ImGui::PushID("Full");
                DrawColorTabsSubtitles("From Image Stats", availableGuiWidth);
            }

            bool *activeFlag;
            bool *otherActiveFlag;
            std::string activeLabel;
            if (isRoi)
            {
                activeLabel = "Active##Roi";
                activeFlag = & inout_settings->ColormapScaleFromStats.ActiveOnROI;
                otherActiveFlag = & inout_settings->ColormapScaleFromStats.ActiveOnFullImage;
            }
            else
            {
                activeLabel = "Active##Full";
                activeFlag = & inout_settings->ColormapScaleFromStats.ActiveOnFullImage;
                otherActiveFlag = & inout_settings->ColormapScaleFromStats.ActiveOnROI;
            }

            ImGui::Checkbox(activeLabel.c_str(), activeFlag);
            if (*activeFlag)
                *otherActiveFlag = false;

            if (!(*activeFlag))
            {
                ImGui::PopID();
                return;
            }

            ImGui::Text("Image Stats");
            ImGui::Text("mean=%4lf stdev=%4lf", imageStats.mean, imageStats.stdev);
            ImGui::Text("min=%.4lf max=%.4lf", imageStats.min, imageStats.max);
            ImGui::TextColored(ImVec4(1.f, 1.f, 0.5f, 1.f), "Current ColormapScale: Min=%.4lf Max=%.4lf",
                               inout_settings->ColormapScaleMin, inout_settings->ColormapScaleMax);

            bool changed = false;

            ImGui::NewLine();
            ImGui::Text("Number of sigmas");
            changed |= ImGuiImm::SliderAnyFloat("##Number of sigmas", &inout_settings->ColormapScaleFromStats.NbSigmas, 0., 8., 150.f);

            ImGui::NewLine();
            ImGui::TextWrapped("If UseStats[Min|Max] is true, then ColormapScale[Min|Max] will be calculated from the matrix [min|max] value instead of a sigma based value");
            changed |= ImGui::Checkbox("Use stats min", &inout_settings->ColormapScaleFromStats.UseStatsMin);
            ImGui::SameLine();
            changed |= ImGui::Checkbox("Use stats max", &inout_settings->ColormapScaleFromStats.UseStatsMax);

            if (isRoi)
            {
                ImVec4 col(1.f, 0.6f, 0.6f, 1.f);
                ImGui::TextColored(col, "Warning, if using \"number of sigmas\" on a ROI");
                ImGui::TextColored(col, "the colormap scale will vary immediately");
                ImGui::TextColored(col, "whenever you zoom in/out or pan");
            }
            if (changed)
                ApplyColormapStatsToMinMax(m, roi, inout_settings);
            ImGui::PopID();
        }


        void GuiShowColormapSettingsData(
            const cv::Mat &image,
            const cv::Rect& roi,
            float availableGuiWidth,
            ColormapSettingsData* inout_settings
            )
        {
            ImGuiTabBarFlags tab_bar_flags = ImGuiTabBarFlags_None;
            if (ImGui::BeginTabBar("##TabBar", tab_bar_flags))
            {
                if (ImGui::BeginTabItem("From Image Stats"))
                {
                    GuiImageStats(image, std::nullopt, inout_settings, availableGuiWidth);
                    ImGui::EndTabItem();
                }
                if (ImGui::BeginTabItem("From ROI Stats"))
                {
                    GuiImageStats(image, roi, inout_settings, availableGuiWidth);
                    ImGui::EndTabItem();
                }
                if (ImGui::BeginTabItem("Min - Max"))
                {
                    DrawColorTabsSubtitles("Min - Max manual values", availableGuiWidth);

                    ImGuiImm::SliderAnyFloatLogarithmic("Scale min", &inout_settings->ColormapScaleMin, -255., 255.);
                    ImGuiImm::SliderAnyFloatLogarithmic("Scale max", &inout_settings->ColormapScaleMax, -255., 255.);
                    ImGui::EndTabItem();
                }
                ImGui::EndTabBar();
            }

            ImGuiImm::SeparatorFixedWidth(availableGuiWidth);

            GuiChooseColormap(inout_settings);
        }


    } // namespace Colormap
} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/cv_drawing_utils.cpp                                         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/cv_drawing_utils.h included by src/immvision/internal/cv/cv_drawing_utils.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <opencv2/core/core.hpp>

namespace ImmVision
{

    namespace CvDrawingUtils
    {
        enum class Colors
        {
            Black,
            Red,
            Green,
            Blue,
            White,
            Yellow,
            Cyan,
            Violet,
            Orange
        };

        cv::Scalar ColorsToScalar(Colors value);

        inline cv::Scalar Black()
        { return {0, 0, 0, 255}; }

        inline cv::Scalar Red()
        { return {0, 0, 255, 255}; }

        inline cv::Scalar Green()
        { return {0, 255, 0, 255}; }

        inline cv::Scalar Blue()
        { return {255, 0, 0, 255}; }

        inline cv::Scalar White()
        { return {255, 255, 255, 255}; }

        inline cv::Scalar Yellow()
        { return {0, 255, 255, 255}; }

        inline cv::Scalar Cyan()
        { return {255, 255, 0, 255}; }

        inline cv::Scalar Violet()
        { return {200, 50, 200, 255}; }

        inline cv::Scalar Orange()
        { return {255, 128, 0, 255}; }


        void line(cv::Mat &image,
                  const cv::Point2d &a,
                  const cv::Point2d &b,
                  cv::Scalar color,
                  int thickness = 1);

        void ellipse(cv::Mat &image,
                     const cv::Point2d &center,
                     const cv::Size2d &size,
                     const cv::Scalar &color,
                     double angle = 0.,
                     double start_angle = 0.,
                     double end_angle = 360.,
                     int thickness = 1);

        void circle(cv::Mat &image,
                    const cv::Point2d &center,
                    double radius,
                    cv::Scalar color,
                    int thickness = 1);

        void rectangle(cv::Mat &image,
                       const cv::Point2d &pt1,
                       const cv::Point2d &pt2,
                       const cv::Scalar &color,
                       bool fill = false,
                       int thickness = 1);


        void rectangle_size(cv::Mat &img,
                            const cv::Point2d &pt,
                            const cv::Size2d &size,
                            const cv::Scalar &color,
                            bool fill = false,
                            int thickness = 1);

        void text(cv::Mat &img,
                  const cv::Point2d &position,
                  const std::string &msg,
                  const cv::Scalar &color,
                  bool center_around_point = false,
                  bool add_cartouche = false,
                  double fontScale = 0.4,
                  int thickness = 1);

        void cross_hole(cv::Mat &img,
                        const cv::Point2d &position,
                        const cv::Scalar &color,
                        double size = 2.,
                        double size_hole = 2.,
                        int thickness = 1);

        void draw_named_feature(cv::Mat &img,
                                const cv::Point2d &position,
                                const std::string &name,
                                const cv::Scalar &color,
                                bool add_cartouche = false,
                                double size = 3.,
                                double size_hole = 2.,
                                int thickness = 1);

        void draw_transparent_pixel(
            cv::Mat &img_rgba,
            const cv::Point2d &position,
            const cv::Scalar &color,
            double alpha
        );

        void draw_grid(
            cv::Mat& img_rgba,
            cv::Scalar lineColor,
            double alpha,
            double x_spacing, double y_spacing,
            double x_start, double y_start,
            double x_end, double y_end
        );

        cv::Mat stack_images_vertically(const cv::Mat &img1, const cv::Mat &img2);
        cv::Mat stack_images_horizontally(const cv::Mat &img1, const cv::Mat &img2);

        cv::Mat make_alpha_channel_checkerboard_image(const cv::Size& size, int squareSize = 30);

        using Image_RGB = cv::Mat;
        using Image_RGBA = cv::Mat;

        Image_RGB overlay_alpha_image_precise(const cv::Mat &background_rgb_or_rgba,
                                              const Image_RGBA &overlay_rgba,
                                              double alpha);
        Image_RGBA converted_to_rgba_image(const cv::Mat &inputMat, bool isBgrOrBgra);

    }  // namespace CvDrawingUtils
}  // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/cv_drawing_utils.cpp continued                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/string_utils.h included by src/immvision/internal/cv/cv_drawing_utils.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace StringUtils
    {
        std::string LowerString(const std::string& s);
        std::string JoinStrings(const std::vector<std::string>&v, const std::string& separator);
        std::vector<std::string> SplitString(const std::string& s, const char separator);
        std::string IndentLine(const std::string& s, int indentSize);
        std::string IndentLines(const std::string& s, int indentSize);


        std::string ToString(const std::string& s);
        std::string ToString(const double& v);
        std::string ToString(const float& v);
        std::string ToString(const int& v);
        std::string ToString(bool v);

        template<typename _Tp>
        std::string ToString(const cv::Point_<_Tp>& v)
        {
            return std::string("(") + std::to_string(v.x) + ", " + std::to_string(v.y) + ")";
        }
        template<typename _Tp>
        std::string ToString(const cv::Size_<_Tp>& v)
        {
            return std::string("(") + std::to_string(v.width) + " x " + std::to_string(v.height) + ")";
        }

        template<typename _Tp>
        std::string ToString(const std::vector<_Tp>& v)
        {
            std::vector<std::string> strs;
            for (const auto& x : v)
                strs.push_back(ToString(x));
            std::string r = "[" + JoinStrings(strs, ", ") + "]";
            return r;
        }

        template<typename _Tp, int _rows,int _cols>
        std::string ToString(const cv::Matx<_Tp, _rows, _cols>& m)
        {
            std::vector<std::string> lines;
            for (int i = 0; i < _rows; ++i)
            {
                std::vector<_Tp> lineValues;
                for (int j = 0; j < _cols; ++j)
                    lineValues.push_back(m(i, j));

                std::string lineString = ToString(lineValues);
                if (i != 0)
                    lineString = std::string("   ") + lineString;
                lines.push_back(lineString);
            }
            std::string r = "\n  [";
            r += JoinStrings(lines, ",\n");
            r += "]";
            return r;
        }

    } // namespace StringUtils
} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/cv_drawing_utils.cpp continued                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <opencv2/imgproc/imgproc.hpp>

#ifndef CV_16F // for old versions of OpenCV
#define CV_16F 7
#endif


namespace ImmVision
{
    namespace CvDrawingUtils
    {
        namespace
        {
            int drawing_shift = 3;
            double drawing_shift_pow = 8.; // = pow(2., drawing_shift);

        }  // namespace


        const std::unordered_map<Colors, cv::Scalar> ColorsValues{
            {Colors::Black,  {0.,   0.,   0.,   255.}},
            {Colors::Red,    {0.,   0.,   255., 255.}},
            {Colors::Green,  {0.,   255., 0.,   255.}},
            {Colors::Blue,   {255., 0.,   0.,   255.}},
            {Colors::White,  {255., 255., 255., 255.}},
            {Colors::Yellow, {0.,   255., 255., 255.}},
            {Colors::Cyan,   {0.,   255., 255., 255.}},
            {Colors::Violet, {200., 50.,  200., 255.}},
            {Colors::Orange, {0.,   128., 255., 255.}}};

        cv::Scalar ColorsToScalar(Colors value)
        { return ColorsValues.at(value); }

        cv::Point _ToCvPoint_Shift(const cv::Point2d &pt)
        {
            cv::Point pt_tuple;
            pt_tuple.x = MathUtils::RoundInt(static_cast<double>(pt.x) * drawing_shift_pow);
            pt_tuple.y = MathUtils::RoundInt(static_cast<double>(pt.y) * drawing_shift_pow);
            return pt_tuple;
        }

        cv::Point _ToCvPoint_NoShift(const cv::Point2d &pt)
        {
            cv::Point pt_tuple;
            pt_tuple.x = MathUtils::RoundInt(static_cast<double>(pt.x));
            pt_tuple.y = MathUtils::RoundInt(static_cast<double>(pt.y));
            return pt_tuple;
        }

        cv::Size _ToCvSize_WithShift(const cv::Size2d s)
        {
            return {MathUtils::RoundInt(static_cast<double>(s.width) * drawing_shift_pow),
                    MathUtils::RoundInt(static_cast<double>(s.height) * drawing_shift_pow)};
        }

        Image_RGB overlay_alpha_image_precise(const cv::Mat &background_rgb_or_rgba, const Image_RGBA &overlay_rgba, double alpha)
        {
            /*
            cf minute physics brilliant clip "Computer color is broken" :
            https://www.youtube.com/watch?v=LKnqECcg6Gw the RGB values are square rooted by the sensor (in
            order to keep accuracy for lower luminancy), we need to undo this before averaging. This gives
            results that are nicer than photoshop itself !
            */
            assert( (background_rgb_or_rgba.type() == CV_8UC3) || (background_rgb_or_rgba.type() == CV_8UC4));
            assert(overlay_rgba.type() == CV_8UC4);

            cv::Mat background_rgb;
            {
                if (background_rgb_or_rgba.channels() == 4)
                    cv::cvtColor(background_rgb_or_rgba, background_rgb, cv::COLOR_BGRA2BGR);
                else if (background_rgb_or_rgba.channels() == 3)
                    background_rgb = background_rgb_or_rgba;
                else
                    throw("Only CV_8UC3 or CV_8UC4 background are supported!");
            }


            std::vector<cv::Mat> overlay_rgb_channels;
            cv::split(overlay_rgba, overlay_rgb_channels);

            cv::Mat overlay_alpha_3;
            {
                cv::Mat overlay_alpha_int = overlay_rgb_channels[3];
                cv::Mat overlay_alpha_float;
                overlay_alpha_int.convertTo(overlay_alpha_float, CV_64F);
                overlay_alpha_float = overlay_alpha_float * (alpha / 255.);

                std::vector<cv::Mat> v{overlay_alpha_float, overlay_alpha_float, overlay_alpha_float};
                cv::merge(v, overlay_alpha_3);
            }

            cv::Mat overlay_rgb_squared;
            {
                cv::Mat overlay_rgb_int;
                std::vector<cv::Mat> v{overlay_rgb_channels[0], overlay_rgb_channels[1], overlay_rgb_channels[2]};
                cv::merge(v, overlay_rgb_int);

                cv::Mat overlay_rgb_float;
                overlay_rgb_int.convertTo(overlay_rgb_float, CV_64F);
                overlay_rgb_squared = overlay_rgb_float.mul(overlay_rgb_float);
            }

            cv::Mat background_rgb_squared;
            {
                cv::Mat background_rgb_float;
                background_rgb.convertTo(background_rgb_float, CV_64F);
                background_rgb_squared = background_rgb_float.mul(background_rgb_float);
            }

            cv::Mat out_rgb_squared;
            {
                out_rgb_squared = overlay_rgb_squared.mul(overlay_alpha_3) +
                                  background_rgb_squared.mul(cv::Scalar(1., 1., 1.) - overlay_alpha_3);
            }

            cv::Mat out_rgb_float;
            {
                cv::sqrt(out_rgb_squared, out_rgb_float);
            }

            cv::Mat out_rgb;
            {
                out_rgb_float.convertTo(out_rgb, CV_8U);
            }

            if (background_rgb_or_rgba.type() == CV_8UC3)
                return out_rgb;
            else // background_rgb_or_rgba.type() == CV_8UC4
            {
                cv::Mat out_rgba;
                cv::cvtColor(out_rgb, out_rgba, cv::COLOR_BGR2BGRA);
                return out_rgba;
            }
        }


        cv::Mat ToFloatMat(const cv::Mat &mat_uchar)
        {
            std::vector<cv::Mat> channels_uchar;
            cv::split(mat_uchar, channels_uchar);
            std::vector<cv::Mat> channels_float;
            for (const auto &channel_uchar: channels_uchar)
            {
                cv::Mat channel_float;
                channel_uchar.convertTo(channel_float, CV_32FC1);
                channels_float.push_back(channel_float);
            }
            cv::Mat mat_float;
            cv::merge(channels_float, mat_float);
            return mat_float;
        }

        std::pair<cv::Mat, cv::Mat> split_alpha_channel(const cv::Mat img_with_alpha)
        {
            std::vector<cv::Mat> channels;
            cv::split(img_with_alpha, channels);
            cv::Mat rgb, alpha;
            alpha = channels[3];
            channels.pop_back();
            cv::merge(channels, rgb);
            return {rgb, alpha};
        }

        void line(cv::Mat &image,
                  const cv::Point2d &a,
                  const cv::Point2d &b,
                  cv::Scalar color,
                  int thickness /*= 1*/)
        {
            cv::line(image,
                     _ToCvPoint_Shift(a),
                     _ToCvPoint_Shift(b),
                     color,
                     thickness,
                     cv::LINE_AA,
                     drawing_shift);
        }

        void ellipse(cv::Mat &image,
                     const cv::Point2d &center,
                     const cv::Size2d &size,
                     const cv::Scalar &color,
                     double angle /*= 0.*/,
                     double start_angle /*=0.*/,
                     double end_angle /*=360.*/,
                     int thickness /*= 1*/)
        {
            cv::ellipse(image,
                        _ToCvPoint_Shift(center),
                        _ToCvSize_WithShift(size),
                        angle,
                        start_angle,
                        end_angle,
                        color,
                        thickness,
                        cv::LINE_AA,
                        drawing_shift);
        }

        void circle(cv::Mat &image,
                    const cv::Point2d &center,
                    double radius,
                    cv::Scalar color,
                    int thickness /*= 1*/)
        {
            ellipse(image, center, {radius, radius}, color, 0., 0., 360., thickness);
        }

        void rectangle(cv::Mat &image,
                       const cv::Point2d &pt1,
                       const cv::Point2d &pt2,
                       const cv::Scalar &color,
                       bool fill /*= false*/,
                       int thickness /*= 1*/)
        {
            if (fill)
                thickness = -1;
            cv::rectangle(image,
                          _ToCvPoint_Shift(pt1),
                          _ToCvPoint_Shift(pt2),
                          color,
                          thickness,
                          cv::LINE_AA,
                          drawing_shift);
        }

        cv::Scalar _ContrastColor(const cv::Scalar &color)
        {
            return {255. - color[0], 255. - color[1], 255. - color[2], color[3]};
        }

        void rectangle_size(cv::Mat &img,
                            const cv::Point2d &pt,
                            const cv::Size2d &size,
                            const cv::Scalar &color,
                            bool fill /*= false*/,
                            int thickness /*= 1*/)
        {
            cv::Point2d pt2(pt.x + size.width, pt.y + size.height);
            rectangle(img, pt, pt2, color, fill, thickness);
        }

        double _text_line_height(double fontScale, int thickness)
        {
            auto fontFace = cv::FONT_HERSHEY_SIMPLEX;
            int baseLine_dummy;
            cv::Size size = cv::getTextSize("ABC", fontFace, fontScale, thickness, &baseLine_dummy);
            return (double)size.height;
        }

        int text_oneline(cv::Mat &img,
                         const cv::Point2d &position,
                         const std::string &text,
                         const cv::Scalar &color,
                         bool center_around_point /*= false*/,
                         bool add_cartouche /*= false*/,
                         double fontScale /*= 0.4*/,
                         int thickness /*= 1*/)
        {
            auto fontFace = cv::FONT_HERSHEY_SIMPLEX;
            int baseLine_dummy;
            cv::Size size = cv::getTextSize(text, fontFace, fontScale, thickness, &baseLine_dummy);
            cv::Point position2 = _ToCvPoint_NoShift(position);
            cv::Point position3;
            if (center_around_point)
                position3 = {position2.x - size.width / 2, position2.y + size.height / 2};
            else
                position3 = position2;
            if (add_cartouche)
            {
                cv::Point position4 = {position3.x, position3.y - size.height};
                rectangle_size(img, position4, size, _ContrastColor(color), true);
            }
            cv::putText(img, text, position3, fontFace, fontScale, color, thickness, cv::LINE_AA);
            return size.height;
        }

        void text(cv::Mat &img,
                  const cv::Point2d &position,
                  const std::string &msg,
                  const cv::Scalar &color,
                  bool center_around_point /*= false*/,
                  bool add_cartouche /*= false*/,
                  double fontScale /*= 0.4*/,
                  int thickness /*= 1*/)
        {
            auto lines = StringUtils::SplitString(msg, '\n');

            double line_height = _text_line_height(fontScale, thickness) + 3.;
            cv::Point2d linePosition = position;
            linePosition.y -= line_height * (double)(lines.size() - 1.) / 2.;
            for (const auto &line: lines)
            {
                text_oneline(
                    img, linePosition, line, color, center_around_point, add_cartouche, fontScale, thickness);
                linePosition.y += line_height;
            }
        }

        void cross_hole(cv::Mat &img,
                        const cv::Point2d &position,
                        const cv::Scalar &color,
                        double size /*= 2.*/,
                        double size_hole /*= 2.*/,
                        int thickness /*= 1*/)
        {
            for (double xSign: std::vector<double>{-1., 1.})
            {
                for (double ySign: std::vector<double>{-1., 1.})
                {
                    cv::Point2d a{position.x + xSign * size_hole, position.y + ySign * size_hole};
                    cv::Point2d b{position.x + xSign * (size_hole + size),
                                  position.y + ySign * (size_hole + size)};
                    line(img, a, b, color, thickness);
                }
            }
        }

        void draw_ellipse(cv::Mat &img,
                          const cv::Point2d &center,
                          const cv::Size2d &size,
                          const cv::Scalar &color,
                          int thickness /*= 1*/,
                          int lineType /*= cv::LINE_8*/,
                          int shift /*= 0*/)
        {
            cv::ellipse(img, center, size, 0., 0., 360., color, thickness, lineType, shift);
        }

        void draw_named_feature(cv::Mat &img,
                                const cv::Point2d &position,
                                const std::string &name,
                                const cv::Scalar &color,
                                bool add_cartouche /*= false*/,
                                double size /*= 3.*/,
                                double size_hole /*= 2.*/,
                                int thickness /*= 1*/)
        {
            if (add_cartouche)
                for (auto x : std::vector<double>{-1., 1.})
                    for (auto y : std::vector<double>{-1., 1.})
                        cross_hole(img, position + cv::Point2d(x, y), _ContrastColor(color), size, size_hole, thickness);

            cross_hole(img, position, color, size, size_hole, thickness);
            double delta_y = size_hole + size + 6.;
            cv::Point2d text_position = {position.x, position.y - delta_y};
            text(img, text_position, name, color, true, add_cartouche);
        }

        cv::Mat stack_images_vertically(const cv::Mat &img1, const cv::Mat &img2)
        {
            cv::Mat img(cv::Size(img1.cols, img1.rows + img2.rows), img1.type());
            img1.copyTo(img(cv::Rect(0, 0, img1.cols, img1.rows)));
            img2.copyTo(img(cv::Rect(0, img1.rows, img2.cols, img2.rows)));
            return img;
        }

        cv::Mat stack_images_horizontally(const cv::Mat &img1, const cv::Mat &img2)
        {
            cv::Mat img(cv::Size(img1.cols + img2.cols, img1.rows), img1.type());
            img1.copyTo(img(cv::Rect(0, 0, img1.cols, img1.rows)));
            img2.copyTo(img(cv::Rect(img1.cols, 0, img2.cols, img2.rows)));
            return img;
        }

        auto is_depth_unsigned_integer = [](int depth) {
            return ((depth == CV_8U) || (depth == CV_16U));
        };
        auto is_depth_signed_integer = [](int depth) {
            return ((depth == CV_8S) || (depth == CV_16S) || (depth == CV_32S));
        };
        auto is_depth_integer = [](int depth) {
            return is_depth_signed_integer(depth) || is_depth_unsigned_integer(depth);
        };
        auto is_depth_integer_not_uchar(int depth) {
            return is_depth_integer(depth) && (depth != CV_8U);
        }
        auto is_depth_float = [](int depth) {
            return ((depth == CV_16F) || (depth == CV_32F) || (depth == CV_64F));
        };

        Image_RGBA converted_to_rgba_image(const cv::Mat &inputMat, bool isBgrOrBgra)
        {

            cv::Mat mat = inputMat;

            if (!inputMat.isContinuous())
                mat = inputMat.clone();
            if (is_depth_integer_not_uchar(mat.depth()))
            {
                cv::Mat m64;
                inputMat.convertTo(m64, CV_64F);
                mat = m64;
            }


            cv::Mat mat_rgba;
            int nbChannels = mat.channels();
            if (nbChannels == 1)
            {
                int depth = mat.depth(); (void)depth;
                if (mat.depth() == CV_8U)
                    cv::cvtColor(mat, mat_rgba, cv::COLOR_GRAY2BGRA);
                else if (is_depth_float(depth))
                {
                    cv::Mat grey_uchar;
                    cv::Mat float_times_255 = mat * 255.;
                    float_times_255.convertTo(grey_uchar, CV_8UC1);
                    cv::cvtColor(grey_uchar, mat_rgba, cv::COLOR_GRAY2BGRA);
                }
            }
            else if (nbChannels == 2)
            {
                // Add a third channel, with values = 0
                cv::Mat mat3Channels_lastZero;
                {
                    std::vector<cv::Mat> channels;
                    cv::split(inputMat, channels);
                    cv::Mat channel3(channels.front().size(), channels.front().type());
                    channel3 = cv::Scalar(0., 0., 0., 0.);
                    channels.push_back(channel3);
                    cv::merge(channels, mat3Channels_lastZero);
                }
                if ( mat.depth() == CV_8U)
                    cv::cvtColor(mat3Channels_lastZero, mat_rgba, cv::COLOR_BGR2BGRA);
                else if ((mat.depth() == CV_16F) || (mat.depth() == CV_32F) || (mat.depth() == CV_64F))
                {
                    cv::Mat grey_uchar;
                    cv::Mat float_times_255 = mat3Channels_lastZero * 255.;
                    float_times_255.convertTo(grey_uchar, CV_8UC3);
                    cv::cvtColor(grey_uchar, mat_rgba, cv::COLOR_BGR2BGRA);
                }
            }
            else if (nbChannels == 3)
            {
                if (mat.depth() == CV_8U && isBgrOrBgra)
                    cv::cvtColor(mat, mat_rgba, cv::COLOR_BGR2RGBA);
                else if (mat.depth() == CV_8U && !isBgrOrBgra)
                    cv::cvtColor(mat, mat_rgba, cv::COLOR_RGB2RGBA);
                else if ((mat.depth() == CV_16F) || (mat.depth() == CV_32F) || (mat.depth() == CV_64F))
                {
                    cv::Mat grey_uchar;
                    cv::Mat float_times_255 = mat * 255.;
                    float_times_255.convertTo(grey_uchar, CV_8UC3);
                    cv::cvtColor(grey_uchar, mat_rgba, cv::COLOR_RGB2RGBA);
                }
                else
                    throw std::runtime_error("unsupported image format");
            }
            else if (nbChannels == 4)
            {
                if (mat.depth() == CV_8U && isBgrOrBgra)
                    cv::cvtColor(mat, mat_rgba, cv::COLOR_BGRA2RGBA);
                else if (mat.depth() == CV_8U && !isBgrOrBgra)
                    mat_rgba = mat;
                else if ((mat.depth() == CV_16F) || (mat.depth() == CV_32F) || (mat.depth() == CV_64F))
                {
                    cv::Mat grey_uchar;
                    cv::Mat float_times_255 = mat * 255.;
                    float_times_255.convertTo(grey_uchar, CV_8UC4);
                    grey_uchar.copyTo(mat_rgba);
                }
                else
                    throw std::runtime_error("unsupported image format");
            }
            return mat_rgba;
        }

        cv::Mat make_alpha_channel_checkerboard_image(const cv::Size& size, int squareSize)
        {
            cv::Mat r(size, CV_8UC3);
            for (int x = 0; x < size.width; x++)
            {
                for (int y = 0; y < size.height; y++)
                {
                    uchar colorValue = ((x / squareSize + y / squareSize) % 2 == 0) ? 102 : 152;
                    r.at<cv::Vec3b>(y, x) = cv::Vec3b(colorValue, colorValue, colorValue);
                }
            }
            return r;
        }


        void draw_transparent_pixel(
            cv::Mat &img_rgba,
            const cv::Point2d &position,
            const cv::Scalar &color,
            double alpha
        )
        {
            assert(img_rgba.type() == CV_8UC4);

            auto fnLerpScalar = [](cv::Scalar c1, cv::Scalar c2, double k)
            {
                auto fnLerp = [](double x1, double x2, double k2) {
                    return x1 + k2 * (x2 - x1);
                };
                cv::Scalar r(
                    fnLerp(c1[0], c2[0], k),
                    fnLerp(c1[1], c2[1], k),
                    fnLerp(c1[2], c2[2], k),
                    fnLerp(c1[3], c2[3], k)
                );
                return r;
            };

            double xFloor = (int)position.x;
            double kx0 = 1. - (position.x - xFloor);
            double kx1 = 1. - kx0;
            double yFloor = (int)position.y;
            double ky0 = 1. - (position.y - yFloor);
            double ky1 = 1. - ky0;

            std::vector<std::pair<cv::Point2d, double>> positionAndKs {
                { cv::Point2d(0., 0.), kx0 * ky0 },
                { cv::Point2d(1., 0.), kx1 * ky0 },
                { cv::Point2d(0., 1.), kx0 * ky1 },
                { cv::Point2d(1., 1.), kx1 * ky1 }
            };

            cv::Rect roi(cv::Point(0, 0), img_rgba.size());
            for (const auto& kv: positionAndKs)
            {
                cv::Point pos;
                {
                    cv::Point2d delta = kv.first;
                    pos = cv::Point((int)(position.x + delta.x), (int)(position.y + delta.y));
                }
                double k = kv.second;

                if (!roi.contains(pos))
                    continue;

                cv::Scalar oldColor = img_rgba.at<cv::Vec4b>(pos.y, pos.x);
                cv::Scalar dstColor = fnLerpScalar(oldColor, color, alpha * k);
                img_rgba.at<cv::Vec4b>(pos.y, pos.x) = dstColor;
            }
        }


        void draw_grid(
            cv::Mat& img_rgba,
            cv::Scalar lineColor,
            double alpha,
            double x_spacing, double y_spacing,
            double x_start, double y_start,
            double x_end, double y_end
            )
        {
            assert(img_rgba.type() == CV_8UC4);

            for (double y = y_start; y < y_end; y+= y_spacing)
                for (double x = 0.; x < x_end; x+= 1.)
                    draw_transparent_pixel(img_rgba, cv::Point2d(x, y), lineColor, alpha);
            for (double x = x_start; x < x_end; x+= x_spacing)
                for (double y = 0.; y < y_end; y+= 1.)
                    draw_transparent_pixel(img_rgba, cv::Point2d(x, y), lineColor, alpha);
        }

    }  // namespace CvDrawingUtils
}  // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/matrix_info_utils.cpp                                        //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/matrix_info_utils.h included by src/immvision/internal/cv/matrix_info_utils.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace MatrixInfoUtils
    {
        std::string _MatTypeName(const cv::Mat& m);
        std::string _MatInfo(const cv::Mat &m);
        std::vector<double> MatValuesAt(const cv::Mat& m, int x, int y);
        std::string MatPixelColorInfo(const cv::Mat & m, int x, int y, char separator = ',', bool add_paren = true);

    } // namespace MatrixInfoUtils

} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/matrix_info_utils.cpp continued                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ifndef CV_16F // for old versions of OpenCV
#define CV_16F 7
#endif

namespace ImmVision
{
    namespace MatrixInfoUtils
    {
        std::string _MatTypeName(const cv::Mat& m)
        {
            std::map<int, std::string> depthNames
                {
                    { CV_8U, "CV_8U" },
                    { CV_8S, "CV_8S" },
                    { CV_16U, "CV_16U" },
                    { CV_16S, "CV_16S" },
                    { CV_32S, "CV_32S"},
                    { CV_32F, "CV_32F"},
                    { CV_64F, "CV_64F"},
                    { CV_16F, "CV_16F"}
                };
            return depthNames.at(m.depth()) + "C" + std::to_string(m.channels());
        }

        std::string _MatInfo(const cv::Mat &m)
        {
            return _MatTypeName(m) + " " + std::to_string(m.cols) + "x" + std::to_string(m.rows);
        }

        std::string JoinStrings(const std::vector<std::string>&v, char separator)
        {
            std::string r;
            for (size_t i = 0; i < v.size(); ++ i)
            {
                r += v[i];
                if (i < v.size() - 1)
                    r += separator;
            }
            return r;
        }

        template<typename _Tp>
        std::vector<double> GrabValuesFromBuffer(const uchar * buffer, int nb)
        {
            std::vector<double> r;
            auto buffer_typed =  reinterpret_cast<const _Tp *>(buffer);
            for (int i = 0; i < nb; ++i)
            {
                r.push_back(static_cast<double>(*buffer_typed));
                ++buffer_typed;
            }
            return r;
        }

        std::vector<double> MatValuesAt(const cv::Mat& m, int x, int y)
        {
            int depth = m.depth();
            int nb_channels = m.channels();
            const uchar * ptr = m.ptr(y, x);
            if (depth == CV_8U)
                return GrabValuesFromBuffer<uchar>(ptr, nb_channels);
            else if (depth == CV_8S)
                return GrabValuesFromBuffer<uchar>(ptr, nb_channels);
            else if (depth == CV_16U)
                return GrabValuesFromBuffer<uint16_t>(ptr, nb_channels);
            else if (depth == CV_16S)
                return GrabValuesFromBuffer<int16_t>(ptr, nb_channels);
#if CV_MAJOR_VERSION >= 4
                else if (depth == CV_16F)
                return GrabValuesFromBuffer<cv::float16_t>(ptr, nb_channels);
#endif
            else if (depth == CV_32S)
                return GrabValuesFromBuffer<int32_t>(ptr, nb_channels);
            else if (depth == CV_32F)
                return GrabValuesFromBuffer<float>(ptr, nb_channels);
            else if (depth == CV_64F)
                return GrabValuesFromBuffer<double>(ptr, nb_channels);
            else
                throw std::runtime_error("MatValuesAt: unhandled depth");
        }

        std::string MatPixelColorInfo(const cv::Mat & m, int x, int y, char separator, bool add_paren)
        {
            if (!cv::Rect(cv::Point(0, 0), m.size()).contains(cv::Point(x, y)))
                return "";
            std::vector<double> values = MatValuesAt(m, x, y);

            auto formatValue = [](double v, int depth) -> std::string
            {
                bool isFloat = false;
                if ((depth == CV_32F) || (depth == CV_64F))
                    isFloat = true;
#if CV_MAJOR_VERSION >= 4
                if (depth == CV_16F)
                    isFloat = true;
#endif
                if (isFloat)
                {
                    char buffer_color[300];
                    snprintf(buffer_color, 300, "%.5G", (double) v);
                    return std::string(buffer_color);
                }
                else
                {
                    char buffer_color[300];
                    snprintf(buffer_color, 300, "%lld", (long long) v);
                    return std::string(buffer_color);
                }
            };

            std::vector<std::string> strs;
            int depth = m.depth();
            for (double v: values)
                strs.push_back(formatValue(v, depth));

            std::string r = JoinStrings(strs, separator);
            if (add_paren)
                r = std::string("(") + r + ")";
            return r;
        }

    } // namespace MatrixInfoUtils

} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/zoom_pan_transform.cpp                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/zoom_pan_transform.h included by src/immvision/internal/cv/zoom_pan_transform.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace ZoomPanTransform
    {
        using MatrixType = cv::Matx33d;

        MatrixType Identity();

        MatrixType ComputeZoomMatrix(const cv::Point2d & zoomCenter, double zoomRatio);
        MatrixType ComputePanMatrix(const cv::Point2d& dragDelta, double currentZoom);
        MatrixType MakeScaleOne(cv::Size imageSize, cv::Size viewportSize);
        MatrixType MakeFullView(cv::Size imageSize, cv::Size viewportSize);
        cv::Matx33d MakeZoomMatrix(const cv::Point2d & zoomCenter, double zoomRatio,const cv::Size displayedImageSize);

        bool IsEqual(const MatrixType & v1, const MatrixType & v2);

        cv::Point2d Apply(const MatrixType& zoomMatrix, const cv::Point2d &p);

        cv::Matx23d ZoomMatrixToM23(const cv::Matx33d &m);

        MatrixType UpdateZoomMatrix_DisplaySizeChanged(
            const MatrixType& oldZoomMatrix,
            const cv::Size& oldDisplaySize, const cv::Size& newDisplaySize);

        cv::Rect VisibleRoi(const MatrixType & zoomMatrix,
                            cv::Size imageDisplaySize,
                            cv::Size originalImageSize
                            );

    } // namespace ZoomPanTransform

    cv::Matx33d MakeZoomPanMatrix(const cv::Point2d & zoomCenter, double zoomRatio, const cv::Size displayedImageSize);

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/cv/zoom_pan_transform.cpp continued                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace ZoomPanTransform
    {
        using MatrixType = cv::Matx33d;

        MatrixType Identity()
        {
            return cv::Matx33d::eye();
        }

        MatrixType ComputeZoomMatrix(const cv::Point2d & zoomCenter, double zoomRatio)
        {
            auto mat = cv::Matx33d::eye();
            mat(0, 0) = zoomRatio;
            mat(1, 1) = zoomRatio;
            mat(0, 2) = zoomCenter.x * (1. - zoomRatio);
            mat(1, 2) = zoomCenter.y * (1. - zoomRatio);
            return mat;
        }

        MatrixType ComputePanMatrix(const cv::Point2d& dragDelta, double currentZoom)
        {
            auto mat = cv::Matx33d::eye();
            mat(0, 2) = (double)dragDelta.x / currentZoom;
            mat(1, 2) = (double)dragDelta.y / currentZoom;
            return mat;
        }

        MatrixType MakeScaleOne(cv::Size imageSize, cv::Size viewportSize)
        {
            MatrixType r = Identity();
            r(0, 2) = (viewportSize.width / 2 - imageSize.width / 2);
            r(1, 2) = (viewportSize.height / 2 - imageSize.height / 2);
            return r;
        }

        cv::Matx23d ZoomMatrixToM23(const cv::Matx33d &m)
        {
            cv::Matx23d r;
            for (int y = 0; y < 2; y++)
                for (int x = 0; x < 3; x++)
                    r(y, x) = m(y, x);
            return r;
        }

        MatrixType MakeFullView(cv::Size imageSize, cv::Size viewportSize)
        {
            assert(imageSize.area() > 0);
            assert(viewportSize.area() >0);

            MatrixType r = Identity();

            double zoom;
            {
                double k_image = (double)imageSize.width / (double)imageSize.height;
                double k_viewport = (double)viewportSize.width / (double)viewportSize.height;
                if (k_image > k_viewport)
                    zoom = (double)viewportSize.width / (double)imageSize.width;
                else
                    zoom = (double)viewportSize.height / (double)imageSize.height;
            }

            r(0, 0) = zoom;
            r(1, 1) = zoom;

            return r;
        }

        bool IsEqual(const MatrixType & v1, const MatrixType & v2)
        {
            for (int j = 0; j < 3; j++)
                for (int i = 0; i < 3; i++)
                    if (fabs(v2(j, i) - v1(j, i)) > 1E-6)
                        return false;
            return true;
        }

        cv::Point2d Apply(const MatrixType& zoomMatrix, const cv::Point2d &p)
        {
            cv::Matx31d pMat(p.x, p.y, 1.);
            cv::Matx31d rMat = zoomMatrix * pMat;
            cv::Point2d r(rMat(0, 0), rMat(1, 0));
            return r;
        }

        MatrixType UpdateZoomMatrix_DisplaySizeChanged(
            const MatrixType& oldZoomMatrix,
            const cv::Size& oldDisplaySize, const cv::Size& newDisplaySize)
        {
            if (oldDisplaySize.area() == 0 || newDisplaySize.area() == 0)
                return oldZoomMatrix;

            MatrixType zoomMatrix;

            auto fnImageCenter = [](const cv::Size s) {
                return cv::Point2d((double)s.width / 2., (double)s.height / 2.);
            };

            double newZoomFactor;
            {
                double oldZoomFactor = oldZoomMatrix(0, 0);
                double kx = (double)newDisplaySize.width / (double)oldDisplaySize.width;
                double ky = (double)newDisplaySize.height / (double)oldDisplaySize.height;
                double k = (kx + ky) / 2.;
                newZoomFactor = oldZoomFactor * k;
            }

            zoomMatrix = MatrixType::eye();
            zoomMatrix(0, 0) = zoomMatrix(1, 1) = newZoomFactor;

            cv::Point2d translation;
            {
                cv::Point2d oldDisplayCenter_Zoomed = fnImageCenter(oldDisplaySize);
                cv::Point2d oldDisplayCenter_Image = ZoomPanTransform::Apply(oldZoomMatrix.inv(), oldDisplayCenter_Zoomed);

                cv::Point2d newDisplayCenter_Zoomed_Wanted = fnImageCenter(newDisplaySize);
                cv::Point2d newDisplayCenter_Zoomed_Now = ZoomPanTransform::Apply(zoomMatrix, oldDisplayCenter_Image);
                translation = newDisplayCenter_Zoomed_Wanted - newDisplayCenter_Zoomed_Now;
            }

            zoomMatrix(0, 2) = translation.x;
            zoomMatrix(1, 2) = translation.y;

            return zoomMatrix;
        }

        cv::Matx33d MakeZoomMatrix(const cv::Point2d & zoomCenter, double zoomRatio,const cv::Size displayedImageSize)
        {
            auto mat = cv::Matx33d::eye();
            mat(0, 0) = zoomRatio;
            mat(1, 1) = zoomRatio;
            double dx = (double)displayedImageSize.width / 2. - zoomRatio * zoomCenter.x;
            double dy = (double)displayedImageSize.height / 2. - zoomRatio * zoomCenter.y;
            mat(0, 2) = dx;
            mat(1, 2) = dy;
            return mat;
        }

        cv::Rect VisibleRoi(const MatrixType & zoomMatrix, cv::Size imageDisplaySize, cv::Size originalImageSize)
        {
            cv::Rect roi;
            {
                cv::Point2d tl = ZoomPanTransform::Apply(zoomMatrix.inv(), cv::Point2d(0., 0.));
                cv::Point tli(MathUtils::RoundInt(tl.x), MathUtils::RoundInt(tl.y));
                tli.x = std::clamp(tli.x, 0, originalImageSize.width - 1);
                tli.y = std::clamp(tli.y, 0, originalImageSize.height - 1);

                cv::Point2d br = ZoomPanTransform::Apply(zoomMatrix.inv(), cv::Point2d(
                    (double)imageDisplaySize.width, (double)imageDisplaySize.height));
                cv::Point bri(MathUtils::RoundInt(br.x), MathUtils::RoundInt(br.y));
                bri.x = std::clamp(bri.x, 0, originalImageSize.width);
                bri.y = std::clamp(bri.y, 0, originalImageSize.height);

                //                bri.x += 1;
//                bri.y += 1;
                roi = cv::Rect(tli, bri);
            }
            return roi;
        }

    } // namespace ZoomPanTransform

    cv::Matx33d MakeZoomPanMatrix(const cv::Point2d & zoomCenter, double zoomRatio, const cv::Size displayedImageSize)
    {
        return ZoomPanTransform::MakeZoomMatrix(zoomCenter, zoomRatio, displayedImageSize);
    }

    cv::Matx33d MakeZoomPanMatrix_ScaleOne(
        cv::Size imageSize,
        const cv::Size displayedImageSize)
    {
        return ZoomPanTransform::MakeScaleOne(imageSize, displayedImageSize);
    }

    cv::Matx33d MakeZoomPanMatrix_FullView(
        cv::Size imageSize,
        const cv::Size displayedImageSize)
    {
        return ZoomPanTransform::MakeFullView(imageSize, displayedImageSize);
    }

}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/image_drawing.cpp                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/image_drawing.h included by src/immvision/internal/drawing/image_drawing.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace ImageDrawing
    {
        cv::Mat DrawWatchedPixels(const cv::Mat& image, const ImageParams& params);

        void DrawGrid(cv::Mat& inOutImageRgba, const ImageParams& params);

        cv::Mat DrawValuesOnZoomedPixels(const cv::Mat& drawingImage, const cv::Mat& valuesImage,
                                         const ImageParams& params, bool drawPixelCoords);

        cv::Mat MakeSchoolPaperBackground(cv::Size s);

        void BlitImageTexture(
            const ImageParams& params,
            const cv::Mat& image,
            cv::Mat& in_out_rgba_image_cache,
            bool shall_refresh_rgba,
            GlTextureCv* outTexture
        );

        bool HasColormapParam(const ImageParams& params);

    } // namespace ImageDrawing

} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/image_drawing.cpp continued                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>


namespace ImmVision
{
    namespace ImageDrawing
    {
        cv::Mat DrawWatchedPixels(const cv::Mat& image, const ImageParams& params)
        {
            cv::Mat r = image.clone();

            std::vector<std::pair<size_t, cv::Point2d>> visiblePixels;
            {
                for (size_t i = 0; i < params.WatchedPixels.size(); ++i)
                {
                    cv::Point w = params.WatchedPixels[i];
                    cv::Point2d p = ZoomPanTransform::Apply(params.ZoomPanMatrix, w);
                    if (cv::Rect(cv::Point(0, 0), params.ImageDisplaySize).contains(p))
                        visiblePixels.push_back({i, p});
                }
            }

            for (const auto& kv : visiblePixels)
            {
                CvDrawingUtils::draw_named_feature(
                    r,         // img
                    kv.second, // position,
                    std::to_string(kv.first),       // name
                    cv::Scalar(255, 255, 255, 255), // color
                    true, // add_cartouche
                    4.,   // size
                    2.5,  // size_hole
                    1     // thickness
                );
            }

            return r;
        }

        void DrawGrid(cv::Mat& inOutImageRgba, const ImageParams& params)
        {
            double x_spacing = (double) params.ZoomPanMatrix(0, 0);
            double y_spacing = (double) params.ZoomPanMatrix(1, 1);

            double x_start, y_start;
            {
                cv::Point2d origin_unzoomed = ZoomPanTransform::Apply(params.ZoomPanMatrix.inv(), cv::Point2d(0., 0.));
                origin_unzoomed = cv::Point2d(std::floor(origin_unzoomed.x) + 0.5, std::floor(origin_unzoomed.y) + 0.5);
                cv::Point2d origin_zoomed = ZoomPanTransform::Apply(params.ZoomPanMatrix, origin_unzoomed);
                x_start = origin_zoomed.x;
                y_start = origin_zoomed.y;
            }
            double x_end = (double)inOutImageRgba.cols - 1.;
            double y_end = (double)inOutImageRgba.rows - 1.;

            auto lineColor = cv::Scalar(255, 255, 0, 255);
            double alpha = 0.3;
            CvDrawingUtils::draw_grid(inOutImageRgba, lineColor, alpha, x_spacing, y_spacing, x_start, y_start, x_end, y_end);
        }

        cv::Mat DrawValuesOnZoomedPixels(const cv::Mat& drawingImage, const cv::Mat& valuesImage,
                                         const ImageParams& params, bool drawPixelCoords)
        {
            assert(drawingImage.type() == CV_8UC4);

            cv::Mat r = drawingImage;
            cv::Point tl, br;
            {
                cv::Point2d tld = ZoomPanTransform::Apply(params.ZoomPanMatrix.inv(), cv::Point2d(0., 0.));
                cv::Point2d brd = ZoomPanTransform::Apply(params.ZoomPanMatrix.inv(),
                                                          cv::Point2d((double)params.ImageDisplaySize.width,
                                                                      (double)params.ImageDisplaySize.height));
                tl = { (int)std::floor(tld.x), (int)std::floor(tld.y) };
                br = { (int)std::ceil(brd.x), (int)std::ceil(brd.y) };
            }

            for (int x = tl.x; x <= br.x; x+= 1)
            {
                for (int y = tl.y; y <= br.y; y+= 1)
                {
                    std::string pixelInfo = MatrixInfoUtils::MatPixelColorInfo(valuesImage, x, y, '\n', false);
                    if (drawPixelCoords)
                        pixelInfo = std::string("x:") + std::to_string(x) + "\n" + "y:" + std::to_string(y) + "\n" + pixelInfo;

                    cv::Point2d position = ZoomPanTransform::Apply(params.ZoomPanMatrix, cv::Point2d((double)x, (double )y));

                    cv::Scalar textColor;
                    {
                        cv::Scalar white(255, 255, 255, 255);
                        cv::Scalar black(0, 0, 0, 255);
                        cv::Vec4b backgroundColor(0, 0, 0, 0);
                        if ( cv::Rect(cv::Point(), drawingImage.size()).contains({(int)position.x, (int)position.y}))
                            backgroundColor = drawingImage.at<cv::Vec4b>((int)position.y, (int)position.x);
                        double luminance = backgroundColor[2] * 0.2126 + backgroundColor[1] * 0.7152 + backgroundColor[0] * 0.0722;
                        if (luminance > 170.)
                            textColor = black;
                        else
                            textColor = white;
                    }
                    CvDrawingUtils::text(
                        r,
                        position,
                        pixelInfo,
                        textColor,
                        true, // center_around_point
                        false, // add_cartouche
                        0.3,  //fontScale
                        1     //int thickness
                    );
                }
            }
            return r;
        };


        cv::Mat MakeSchoolPaperBackground(cv::Size s)
        {
            cv::Mat mat(s, CV_8UC4);

            auto paperColor = cv::Scalar(205, 215, 220, 255);
            auto lineColor = cv::Scalar(199, 196, 184, 255);
            mat = paperColor;
            int quadSize = 17;
            for (int y = 0; y < s.height; y+= quadSize)
            {
                auto linePtr = mat.ptr<cv::Vec4b>(y);
                for (int x = 0; x < s.width; ++x)
                {
                    *linePtr = lineColor;
                    linePtr++;
                }
            }
            for (int y = 0; y < s.height; y++)
            {
                auto linePtr = mat.ptr<cv::Vec4b>(y);
                for (int x = 0; x < s.width; x+=quadSize)
                {
                    *linePtr = lineColor;
                    linePtr += quadSize;
                }
            }
            return mat;
        }

        void BlitImageTexture(
            const ImageParams& params,
            const cv::Mat& image,
            cv::Mat& in_out_rgba_image_cache,
            bool shall_refresh_rgba,
            GlTextureCv* outTexture
        )
        {
            if (image.empty())
                return;

            cv::Mat finalImage = image.clone();

            //
            // Adjustements needed before conversion to rgba
            //
            auto fnSelectChannel = [&finalImage, params]()
            {
                // Selected channels
                if (finalImage.channels() > 1 && (params.SelectedChannel >= 0) && (params.SelectedChannel < finalImage.channels()))
                {
                    std::vector<cv::Mat> channels;
                    cv::split(finalImage, channels);
                    finalImage = channels[(size_t)params.SelectedChannel];
                }

            };
            auto fnAlphaCheckerboard = [&finalImage, params]()
            {
                if ((finalImage.type() == CV_8UC4) && params.ShowAlphaChannelCheckerboard)
                {
                    cv::Mat background = CvDrawingUtils::make_alpha_channel_checkerboard_image(finalImage.size());
                    finalImage = CvDrawingUtils::overlay_alpha_image_precise(background, finalImage, 1.);
                }
            };
            auto fnMakeBackground = [&params]() -> cv::Mat
            {
                if (params.ShowSchoolPaperBackground)
                    return MakeSchoolPaperBackground(params.ImageDisplaySize);
                else
                {
                    cv::Mat m(params.ImageDisplaySize, CV_8UC4);
                    m = cv::Scalar(0, 0, 0, 255);
                    return m;
                }

            };

            //
            // Convert to rgba with adjustments if needed
            //
            if (shall_refresh_rgba)
            {
                if (HasColormapParam(params) && Colormap::CanColormap(image))
                    finalImage = Colormap::ApplyColormap(finalImage, params.ColormapSettings); // returns a rgba image
                else
                {
                    fnSelectChannel();
                    fnAlphaCheckerboard();
                    finalImage = CvDrawingUtils::converted_to_rgba_image(finalImage, params.IsColorOrderBGR);
                }
                in_out_rgba_image_cache = finalImage;
                assert(finalImage.type() == CV_8UC4);
            }
            else
            {
                finalImage = in_out_rgba_image_cache;
                assert(finalImage.type() == CV_8UC4);
                assert(!finalImage.empty());
            }

            //
            // Zoom
            //
            {
                cv::Mat backgroundWithImage = fnMakeBackground();
                cv::warpAffine(finalImage, backgroundWithImage,
                               ZoomPanTransform::ZoomMatrixToM23(params.ZoomPanMatrix),
                               params.ImageDisplaySize,
                               cv::INTER_NEAREST,
                               cv::BorderTypes::BORDER_TRANSPARENT,
                               cv::Scalar(127, 127, 127, 127)
                );
                finalImage = backgroundWithImage;
            }

            //
            // Drawings on final image
            //
            {
                // Draw grid
                double gridMinZoomFactor = 12.;
                double zoomFactor = (double)params.ZoomPanMatrix(0, 0);
                if (params.ShowGrid && zoomFactor >= gridMinZoomFactor)
                    DrawGrid(finalImage, params);

                // Draw Pixel Values
                double drawPixelvaluesMinZoomFactor = (image.depth() == CV_8U) ? 36. : 48.;
                if (params.DrawValuesOnZoomedPixels && zoomFactor > drawPixelvaluesMinZoomFactor)
                {
                    double drawPixelCoordsMinZoomFactor = 60.;
                    bool drawPixelCoords = zoomFactor > drawPixelCoordsMinZoomFactor;
                    finalImage = DrawValuesOnZoomedPixels(finalImage, image, params, drawPixelCoords);
                }

                // Draw Watched Pixels
                if (params.HighlightWatchedPixels && (! params.WatchedPixels.empty()))
                    finalImage = DrawWatchedPixels(finalImage, params);

            }

            //
            // Blit
            //
            outTexture->BlitMat(finalImage, false);
        }

        bool HasColormapParam(const ImageParams &params)
        {
            return (!params.ColormapSettings.Colormap.empty() || !params.ColormapSettings.internal_ColormapHovered.empty());
        }

    } // namespace ImageDrawing

} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/internal_icons.cpp                                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/internal_icons.h included by src/immvision/internal/drawing/internal_icons.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace Icons
    {
        enum class IconType
        {
            ZoomPlus,
            ZoomMinus,
            ZoomScaleOne,
            ZoomFullView,
            AdjustLevels,
        };
        unsigned int GetIcon(IconType iconType);

        bool IconButton(IconType iconType, bool disabled = false);

        void ClearIconsTextureCache();

        void DevelPlaygroundGui();

    } // namespace Icons
} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/internal_icons.cpp continued                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/imgui_imm_gl_image.h included by src/immvision/internal/drawing/internal_icons.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// Wrappers for ImGui::Image, ImGui::ImageButton and ImGui::GetWindowDrawList()->AddImage
//
// They have the same behavior under C++, but under python this is transferred to the python interpreter
// (see gl_provider_python.cpp for their python definition)
//
namespace ImGuiImmGlImage
{
    IMGUI_API void  Image(unsigned int user_texture_id, const ImVec2& size, const ImVec2& uv0 = ImVec2(0, 0), const ImVec2& uv1 = ImVec2(1,1), const ImVec4& tint_col = ImVec4(1,1,1,1), const ImVec4& border_col = ImVec4(0,0,0,0));
    IMGUI_API bool  ImageButton(unsigned int user_texture_id, const ImVec2& size, const ImVec2& uv0 = ImVec2(0, 0),  const ImVec2& uv1 = ImVec2(1,1), int frame_padding = -1, const ImVec4& bg_col = ImVec4(0,0,0,0), const ImVec4& tint_col = ImVec4(1,1,1,1));    // <0 frame_padding uses default frame padding settings. 0 for no padding
    IMGUI_API void  GetWindowDrawList_AddImage(unsigned int user_texture_id, const ImVec2& p_min, const ImVec2& p_max, const ImVec2& uv_min = ImVec2(0, 0), const ImVec2& uv_max = ImVec2(1, 1), ImU32 col = IM_COL32_WHITE);
} // namespace ImGuiImmGlImage

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/drawing/internal_icons.cpp continued                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace Icons
    {
        static cv::Size iconsSizeDraw(200, 200);
        auto ScalePoint = [](cv::Point2d p) {
            return cv::Point2d(p.x * (double) iconsSizeDraw.width, p.y * (double) iconsSizeDraw.height);
        };
        auto ScaleDouble = [](double v) {
            return v * (double) iconsSizeDraw.width;
        };
        auto ScaleInt = [](double v) {
            return (int) (v * (double) iconsSizeDraw.width + 0.5);
        };

        auto PointFromOther = [](cv::Point2d o, double angleDegree, double distance) {
            double m_pi = 3.14159265358979323846;
            double angleRadian = -angleDegree / 180. * m_pi;
            cv::Point2d r(o.x + cos(angleRadian) * distance, o.y + sin(angleRadian) * distance);
            return r;
        };


        cv::Mat MakeMagnifierImage(IconType iconType)
        {
            using namespace ImmVision;
            cv::Mat m(iconsSizeDraw, CV_8UC4);


            // Transparent background
            m = cv::Scalar(0, 0, 0, 0);

            cv::Scalar color(255, 255, 255, 255);
            double radius = 0.3;
            cv::Point2d center(1. - radius * 1.3, radius * 1.2);
            // Draw shadow
            {
                cv::Point2d decal(radius * 0.1, radius * 0.1);
                cv::Scalar color_shadow(127, 127, 127, 255);

                CvDrawingUtils::circle(
                    m, //image,
                    ScalePoint(center + decal),
                    ScaleDouble(radius), //radius
                    color_shadow,
                    ScaleInt(0.08)
                );
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 225., radius * 1.7) + decal),
                    ScalePoint(PointFromOther(center, 225., radius * 1.03) + decal),
                    color_shadow,
                    ScaleInt(0.08)
                );
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 225., radius * 2.3) + decal),
                    ScalePoint(PointFromOther(center, 225., radius * 1.5) + decal),
                    color_shadow,
                    ScaleInt(0.14)
                );
            }
            // Draw magnifier
            {
                CvDrawingUtils::circle(
                    m, //image,
                    ScalePoint(center),
                    ScaleDouble(radius), //radius
                    color,
                    ScaleInt(0.08)
                );
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 225., radius * 1.7)),
                    ScalePoint(PointFromOther(center, 225., radius * 1.03)),
                    color,
                    ScaleInt(0.08)
                );
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 225., radius * 2.3)),
                    ScalePoint(PointFromOther(center, 225., radius * 1.5)),
                    color,
                    ScaleInt(0.14)
                );
            }

            if (iconType == IconType::ZoomPlus)
            {
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 0., radius * 0.6)),
                    ScalePoint(PointFromOther(center, 180., radius * 0.6)),
                    color,
                    ScaleInt(0.06)
                );
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 90., radius * 0.6)),
                    ScalePoint(PointFromOther(center, 270., radius * 0.6)),
                    color,
                    ScaleInt(0.06)
                );
            }
            if (iconType == IconType::ZoomMinus)
            {
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(PointFromOther(center, 0., radius * 0.6)),
                    ScalePoint(PointFromOther(center, 180., radius * 0.6)),
                    color,
                    ScaleInt(0.06)
                );
            }
            if (iconType == IconType::ZoomScaleOne)
            {
                cv::Point2d a = PointFromOther(center, -90., radius * 0.45);
                cv::Point2d b = PointFromOther(center, 90., radius * 0.45);
                a.x += radius * 0.05;
                b.x += radius * 0.05;
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(a),
                    ScalePoint(b),
                    color,
                    ScaleInt(0.06)
                );
                cv::Point2d c(b.x - radius * 0.2, b.y + radius * 0.2);
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(b),
                    ScalePoint(c),
                    color,
                    ScaleInt(0.06)
                );
            }

            return m;
        }


        cv::Mat MakeFullViewImage()
        {
            cv::Mat m(iconsSizeDraw, CV_8UC4);
            m = cv::Scalar(0, 0, 0, 0);

            cv::Scalar color(255, 255, 255, 255);
            double decal = 0.1;
            double length_x = 0.3, length_y = 0.3;
            for (int y = 0; y <= 1; ++y)
            {
                for (int x = 0; x <= 1; ++x)
                {
                    cv::Point2d corner;

                    corner.x = (x == 0) ? decal : 1. - decal;
                    corner.y = (y == 0) ? decal : 1. - decal;
                    double moveX = (x == 0) ? length_x : -length_x;
                    double moveY = (y == 0) ? length_y : -length_y;
                    cv::Point2d pt_x(corner.x + moveX, corner.y);
                    cv::Point2d pt_y(corner.x, corner.y + moveY);
                    int thickness = ScaleInt(0.09);
                    CvDrawingUtils::line(
                        m,
                        ScalePoint(corner),
                        ScalePoint(pt_x),
                        color,
                        thickness
                    );
                    CvDrawingUtils::line(
                        m,
                        ScalePoint(corner),
                        ScalePoint(pt_y),
                        color,
                        thickness
                    );
                }
            }
            return m;
        }

        cv::Mat MakeAdjustLevelsImage()
        {
            cv::Mat m(iconsSizeDraw, CV_8UC4);
            m = cv::Scalar(0, 0, 0, 0);
            cv::Scalar color(255, 255, 255, 255);

            double yMin = 0.15, yMax = 0.8;
            int nbBars = 3;
            for (int bar = 0; bar < nbBars; ++bar)
            {
                double xBar = (double)bar / ((double)(nbBars) + 0.17) + 0.2;
                cv::Point2d a(xBar, yMin);
                cv::Point2d b(xBar, yMax);
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(a),
                    ScalePoint(b),
                    color,
                    ScaleInt(0.08)
                );

                double barWidth = 0.1;
                double yBar = 0.7 - 0.2 * (double)bar;
                cv::Point2d c(a.x - barWidth / 2., yBar);
                cv::Point2d d(a.x + barWidth / 2., yBar);
                CvDrawingUtils::line(
                    m, //image,
                    ScalePoint(c),
                    ScalePoint(d),
                    color,
                    ScaleInt(0.16)
                );
            }

            return m;
        }


        static std::map<IconType, std::unique_ptr<GlTextureCv>> sIconsTextureCache;
        static cv::Size gIconSize(20,  20);

        unsigned int GetIcon(IconType iconType)
        {
            if (sIconsTextureCache.find(iconType) == sIconsTextureCache.end())
            {
                cv::Mat m;
                if (iconType == IconType::ZoomFullView)
                    m = MakeFullViewImage();
                else if (iconType == IconType::AdjustLevels)
                    m = MakeAdjustLevelsImage();
                else
                    m = MakeMagnifierImage(iconType);

                cv::Mat resized = m;
                cv::resize(m, resized, cv::Size(gIconSize.width * 2, gIconSize.height * 2), 0., 0., cv::INTER_AREA);
                auto texture = std::make_unique<GlTextureCv>(resized, true);
                sIconsTextureCache[iconType] = std::move(texture);
            }
            return sIconsTextureCache[iconType]->mImTextureId;
        }

        bool IconButton(IconType iconType, bool disabled)
        {
            ImGui::PushID((int)iconType);
            ImVec2 cursorPos = ImGui::GetCursorScreenPos();
            ImU32 backColorEnabled = ImGui::ColorConvertFloat4ToU32(ImVec4 (1.f, 1.f, 1.f, 1.f));
            ImU32 backColorDisabled = ImGui::ColorConvertFloat4ToU32(ImVec4(1.f, 1.f, 0.9f, 0.5f));
            ImU32 backColor = disabled ? backColorDisabled : backColorEnabled;
            if (disabled)
                ImGuiImm::PushDisabled();

            // Cannot use InvisibleButton, since it does not handle "Repeat"
            std::string spaceLabel = " ";
            while (ImGui::CalcTextSize(spaceLabel.c_str()).x < 14.f)
                spaceLabel += " ";
            bool clicked = ImGui::Button(spaceLabel.c_str());

            ImGuiImmGlImage::GetWindowDrawList_AddImage(
                GetIcon(iconType),
                cursorPos,
                {cursorPos.x + (float)gIconSize.width, cursorPos.y + (float)gIconSize.height},
                ImVec2(0.f, 0.f),
                ImVec2(1.f, 1.f),
                backColor
                );

            if (disabled)
                ImGuiImm::PopDisabled();
            ImGui::PopID();
            return disabled ? false : clicked;
        }


        void DevelPlaygroundGui()
        {
            static cv::Mat mag = MakeMagnifierImage(IconType::ZoomScaleOne);
            static cv::Mat img = MakeAdjustLevelsImage();

            static ImmVision::ImageParams imageParams1;
            imageParams1.ImageDisplaySize = {400, 400};
            ImmVision::Image("test", mag, &imageParams1);

            ImGui::SameLine();

            static ImmVision::ImageParams imageParams2;
            imageParams2.ImageDisplaySize = {400, 400};
            ImmVision::Image("test2", img, &imageParams2);

            ImVec2 iconSize(15.f, 15.f);
            ImGuiImmGlImage::ImageButton(GetIcon(IconType::ZoomScaleOne), iconSize);
            ImGuiImmGlImage::ImageButton(GetIcon(IconType::ZoomPlus), iconSize);
            ImGuiImmGlImage::ImageButton(GetIcon(IconType::ZoomMinus), iconSize);
            ImGuiImmGlImage::ImageButton(GetIcon(IconType::ZoomFullView), iconSize);
            ImGuiImmGlImage::ImageButton(GetIcon(IconType::AdjustLevels), iconSize);
        }

        void ClearIconsTextureCache()
        {
            Icons::sIconsTextureCache.clear();
        }

} // namespace Icons


} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_provider.cpp                                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#ifndef IMMVISION_BUILDING_PYBIND // see gl_provider_python for the pybind version


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_provider.h included by src/immvision/internal/gl/gl_provider.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision_GlProvider
{
    // InitGlProvider must be called after the OpenGl Loader is initialized
    void InitGlProvider();
    // InitGlProvider must be called before the OpenGl Loader is reset
    void ResetGlProvider();

    void Blit_RGBA_Buffer(unsigned char *image_data, int image_width, int image_height, unsigned int textureId);
    unsigned int GenTexture();
    void DeleteTexture(unsigned int texture_id);
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_provider.cpp continued                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision_gl_loader/immvision_gl_loader.h included by src/immvision/internal/gl/gl_provider.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#if defined(IMMVISION_CUSTOM_GL_INCLUDE)
    // See https://stackoverflow.com/questions/40062883/how-to-use-a-macro-in-an-include-directive
    #define STRINGIFY_MACRO(x) STR(x)
    #define STR(x) #x
    #include STRINGIFY_MACRO(IMMVISION_CUSTOM_GL_INCLUDE)
#elif defined(IMMVISION_USE_GLAD)
    #include <glad/glad.h>
#elif defined(IMMVISION_USE_GLES3)
    #if defined(IOS)
        #include <OpenGLES/ES3/gl.h>
        #include <OpenGLES/ES3/glext.h>
    #elif defined(__EMSCRIPTEN__)
        #include <GLES3/gl3.h>
        #include <GLES3/gl2ext.h>
    #else
        #include <GLES3/gl3.h>
        #include <GLES3/gl3ext.h>
    #endif
#elif defined(IMMVISION_USE_GLES2)
    #ifdef IOS
        #include <OpenGLES/ES2/gl.h>
        #include <OpenGLES/ES2/glext.h>
    #else
        #include <GLES2/gl2.h>
        #include <GLES2/gl2ext.h>
    #endif
#else
    #error "immvision_include_opengl: cannot determine GL include path"
#endif

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_provider.cpp continued                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <iostream>

namespace ImmVision_GlProvider
{
    void _AssertOpenGlLoaderWorking()
    {
        size_t glGenTexturesAddress = (size_t)glGenTextures;
        size_t glDeleteTexturesAddress = (size_t)glDeleteTextures;

        if ((glGenTexturesAddress == 0) || (glDeleteTexturesAddress == 0))
        {
            const char* err_msg = "glGenTextures/glDeleteTexturesAddress address not initialized. Is your your OpenGL Loader initialized?";
            std::cerr << err_msg;
            assert(false);
            throw std::runtime_error(err_msg);
        }
    }

    void InitGlProvider()
    {
        // InitGlProvider must be called after the OpenGl Loader is initialized
        _AssertOpenGlLoaderWorking();
    }

    void ResetGlProvider()
    {
        // InitGlProvider must be called before the OpenGl Loader is reset
        _AssertOpenGlLoaderWorking();
        ImmVision::ClearTextureCache();
        ImmVision::Colormap::ClearColormapsTexturesCache();
        ImmVision::Icons::ClearIconsTextureCache();
    }

    void Blit_RGBA_Buffer(unsigned char *image_data, int image_width, int image_height, unsigned int textureId)
    {
        static int counter = 0;
        ++counter;
        std::cout << "Blit_RGBA_Buffer counter=" << counter << "\n";
        glBindTexture(GL_TEXTURE_2D, textureId);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
#if defined(__EMSCRIPTEN__) || defined(IMMVISION_USE_GLES2) || defined(IMMVISION_USE_GLES3)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        // glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);
#endif
        GLenum gl_color_flag_input = GL_RGBA;
        GLenum gl_color_flag_output = GL_RGBA;
        glTexImage2D(GL_TEXTURE_2D, 0, gl_color_flag_input,
                     image_width,
                     image_height, 0, gl_color_flag_output, GL_UNSIGNED_BYTE, image_data);
        glBindTexture(GL_TEXTURE_2D, 0);
    }

    unsigned int GenTexture()
    {
        std::cout << "GenTexture()\n";
        _AssertOpenGlLoaderWorking();
        GLuint textureId_Gl;
        glGenTextures(1, &textureId_Gl);
        return textureId_Gl;
    }

    void DeleteTexture(unsigned int texture_id)
    {
        std::cout << "DeleteTexture()\n";
        _AssertOpenGlLoaderWorking();
        glDeleteTextures(1, &texture_id);
    }
}

#endif // #ifndef IMMVISION_BUILDING_PYBIND


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/gl_texture.cpp                                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////



namespace ImmVision
{
    GlTexture::GlTexture()
    {
        unsigned int textureId_Gl = ImmVision_GlProvider::GenTexture();
        this->mImTextureId = textureId_Gl;
    }

    GlTexture::~GlTexture()
    {
        ImmVision_GlProvider::DeleteTexture(mImTextureId);
    }

    void GlTexture::Draw(const ImVec2& size, const ImVec2& uv0, const ImVec2& uv1, const ImVec4& tint_col, const ImVec4& border_col) const
    {
        ImVec2 size_(size);
        if (size.x == 0.f)
            size_ = this->mImageSize;
        ImGuiImmGlImage::Image(this->mImTextureId, size_, uv0, uv1, tint_col, border_col);
    }

    bool GlTexture::DrawButton(const ImVec2& size, const ImVec2& uv0, const ImVec2& uv1, int frame_padding, const ImVec4& bg_col, const ImVec4& tint_col) const
    {
        ImVec2 size_(size);
        if (size.x == 0.f)
            size_ = this->mImageSize;
        return ImGuiImmGlImage::ImageButton(this->mImTextureId, size_, uv0, uv1, frame_padding, bg_col, tint_col);
    }

    void GlTexture::Draw_DisableDragWindow(const ImVec2 &size) const
    {
        ImVec2 size_(size);
        if (size.x == 0.f)
            size_ = this->mImageSize;

        ImVec2 imageTl = ImGui::GetCursorScreenPos();
        ImVec2 imageBr(imageTl.x + size.x, imageTl.y + size.y);
        std::stringstream id;
        id << "##" << mImTextureId;
        ImGui::InvisibleButton(id.str().c_str(), size);
        ImGuiImmGlImage::GetWindowDrawList_AddImage(mImTextureId, imageTl, imageBr);
    }

    void GlTexture::Blit_RGBA_Buffer(unsigned char *image_data, int image_width, int image_height)
    {
        ImmVision_GlProvider::Blit_RGBA_Buffer(image_data, image_width, image_height, this->mImTextureId);
        mImageSize = ImVec2((float)image_width, (float) image_height);
    }

    //
    // ImageTextureCv
    //
    GlTextureCv::GlTextureCv(const cv::Mat& mat, bool isBgrOrBgra) : GlTextureCv()
    {
        BlitMat(mat, isBgrOrBgra);
    }

    void GlTextureCv::BlitMat(const cv::Mat& mat, bool isBgrOrBgra)
    {
        if (mat.empty())
            return;
        cv::Mat mat_rgba = CvDrawingUtils::converted_to_rgba_image(mat, isBgrOrBgra);

        Blit_RGBA_Buffer(mat_rgba.data, mat_rgba.cols, mat_rgba.rows);
    }
} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/imgui_imm_gl_image.cpp                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImGuiImmGlImage
{
//#define IMMVISION_BUILDING_PYBIND // KK
    static void* UintToTextureID(unsigned int id)
    {
        return (void *)(intptr_t)id;
    }

#ifndef IMMVISION_BUILDING_PYBIND
    void  Image(unsigned int user_texture_id, const ImVec2& size, const ImVec2& uv0, const ImVec2& uv1, const ImVec4& tint_col, const ImVec4& border_col)
    {
        ImGui::Image(UintToTextureID(user_texture_id), size, uv0, uv1, tint_col, border_col);
    }
    bool  ImageButton(unsigned int user_texture_id, const ImVec2& size, const ImVec2& uv0,  const ImVec2& uv1, int frame_padding, const ImVec4& bg_col, const ImVec4& tint_col)
    {
        return ImGui::ImageButton(UintToTextureID(user_texture_id), size, uv0, uv1, frame_padding, bg_col, tint_col);
    }
    void  GetWindowDrawList_AddImage(unsigned int user_texture_id, const ImVec2& p_min, const ImVec2& p_max, const ImVec2& uv_min, const ImVec2& uv_max, ImU32 col)
    {
        ImGui::GetWindowDrawList()->AddImage(UintToTextureID(user_texture_id), p_min, p_max, uv_min, uv_max, col);
    }
#endif
} // namespace ImGuiImmGlImage


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/short_lived_cache.cpp                                        //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/short_lived_cache.h included by src/immvision/internal/gl/short_lived_cache.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////



namespace ImmVision
{
    namespace internal
    {
        double TimerSeconds();

        template<typename Key, typename Value>
        class Cache
        {
        public:
            bool Contains(const Key& k) const
            {
                return mDict.find(k) != mDict.end();
            }

            Value& Get(const Key& k)
            {
                // If you encounter this assert during debugging, it is perhaps due to ShortLiveCache (below)
                // which periodically removes elements that were unused during a given period (5 seconds)
                assert(mDict.find(k) != mDict.end());
                return mDict.at(k);
            }

            void AddKey(const Key& k)
            {
                assert(mDict.find(k) == mDict.end());
                mDict.insert({k, Value()});
            }

            void RemoveKey(const Key& k)
            {
                mDict.erase(k);
            }

            void Clear()
            {
                mDict.clear();
            }

            std::vector<Key> Keys() const
            {
                std::vector<Key> r;
                for (const auto& kv: mDict)
                    r.push_back(kv.first);
                return r;
            }
        private:
            std::map<Key, Value> mDict;
        };


        template<typename Value>
        class ShortLivedValue
        {
        public:
            ShortLivedValue()
            {
                mLastAccessTime = TimerSeconds();
            }
            Value& Get()
            {
                mLastAccessTime = TimerSeconds();
                return mValue;
            }
            const Value& Get() const
            {
                mLastAccessTime = TimerSeconds();
                return mValue;
            }
            double LastAccessTime() const
            {
                return mLastAccessTime;
            }
        private:
            mutable double mLastAccessTime = TimerSeconds();
            Value mValue;
        };


        template<typename Key, typename Value>
        class ShortLivedCache
        {
        public:
            ShortLivedCache(double timeToLive) : mTimeToLiveSeconds(timeToLive) {}
            bool Contains(const Key& k)
            {
                return mCache.Contains(k);
            }
            Value& Get(const Key& k)
            {
                auto& cached = mCache.Get(k);
                // double now = TimerSeconds();
                // printf("now=%.1f Get %p Last Access Time=%.1f Age=%.1f\n", now, k, cached.LastAccessTime(), now - cached.LastAccessTime());
                return cached.Get();
            }
            const Value& Get(const Key& k) const
            {
                return Get(k);
            }
            void AddKey(const Key& k)
            {
                mCache.AddKey(k);
            }
            void RemoveKey(const Key& k)
            {
                mCache.RemoveKey(k);
            }
            std::vector<Key> Keys() const
            {
                return mCache.Keys();
            }

            void ClearOldEntries()
            {
                double now = TimerSeconds();
                std::vector<Key> oldEntries;
                for (const auto& key: Keys())
                    if ((now - mCache.Get(key).LastAccessTime()) > mTimeToLiveSeconds)
                        oldEntries.push_back(key);

                for (auto& key: oldEntries)
                    mCache.RemoveKey(key);
            }

            void Clear()
            {
                mCache.Clear();
            }
        private:
            double mTimeToLiveSeconds = 1.;
            Cache< Key, ShortLivedValue<Value> > mCache;
        };
    } // namespace internal
} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/gl/short_lived_cache.cpp continued                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <chrono>

namespace ImmVision
{
    namespace internal
    {
        double TimerSeconds()
        {
            using chrono_second = std::chrono::duration<double, std::ratio<1>>;
            using chrono_clock = std::chrono::steady_clock;

            static std::chrono::time_point<chrono_clock> startTime = chrono_clock::now();
            double elapsed = std::chrono::duration_cast<chrono_second>(chrono_clock::now() - startTime).count();
            return elapsed;
        }

    } // namespace internal
} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image.cpp                                                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <opencv2/imgcodecs.hpp>


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/portable_file_dialogs.h included by src/immvision/internal/image.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
//  Portable File Dialogs :
//  Thanks to Sam Hocevar <sam@hocevar.net>
//  https://github.com/samhocevar/portable-file-dialogs
//
//
//  Copyright © 2018—2020 Sam Hocevar <sam@hocevar.net>
//
//  This library is free software. It comes without any warranty, to
//  the extent permitted by applicable law. You can redistribute it
//  and/or modify it under the terms of the Do What the Fuck You Want
//  to Public License, Version 2, as published by the WTFPL Task Force.
//  See http://www.wtfpl.net/ for more details.
//


#if _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#   define WIN32_LEAN_AND_MEAN 1
#endif
#include <windows.h>
#include <commdlg.h>
#include <shlobj.h>
#include <shobjidl.h> // IFileDialog
#include <shellapi.h>
#include <strsafe.h>
#include <future>     // std::async

#elif __EMSCRIPTEN__
#include <emscripten.h>

#else
#ifndef _POSIX_C_SOURCE
#   define _POSIX_C_SOURCE 2 // for popen()
#endif
#ifdef __APPLE__
#   ifndef _DARWIN_C_SOURCE
#       define _DARWIN_C_SOURCE
#   endif
#endif
#include <cstdio>     // popen()
#include <cstdlib>    // std::getenv()
#include <fcntl.h>    // fcntl()
#include <unistd.h>   // read(), pipe(), dup2()
#include <csignal>    // ::kill, std::signal
#include <sys/wait.h> // waitpid()
#endif

#include <string>   // std::string
#include <memory>   // std::shared_ptr
#include <iostream> // std::ostream
#include <map>      // std::map
#include <set>      // std::set
#include <regex>    // std::regex
#include <thread>   // std::mutex, std::this_thread
#include <chrono>   // std::chrono

// Versions of mingw64 g++ up to 9.3.0 do not have a complete IFileDialog
#ifndef PFD_HAS_IFILEDIALOG
#   define PFD_HAS_IFILEDIALOG 1
#   if (defined __MINGW64__ || defined __MINGW32__) && defined __GXX_ABI_VERSION
#       if __GXX_ABI_VERSION <= 1013
#           undef PFD_HAS_IFILEDIALOG
#           define PFD_HAS_IFILEDIALOG 0
#       endif
#   endif
#endif

namespace pfd
{

    enum class button
    {
        cancel = -1,
        ok,
        yes,
        no,
        abort,
        retry,
        ignore,
    };

    enum class choice
    {
        ok = 0,
        ok_cancel,
        yes_no,
        yes_no_cancel,
        retry_cancel,
        abort_retry_ignore,
    };

    enum class icon
    {
        info = 0,
        warning,
        error,
        question,
    };

// Additional option flags for various dialog constructors
    enum class opt : uint8_t
    {
        none = 0,
        // For file open, allow multiselect.
        multiselect     = 0x1,
        // For file save, force overwrite and disable the confirmation dialog.
        force_overwrite = 0x2,
        // For folder select, force path to be the provided argument instead
        // of the last opened directory, which is the Microsoft-recommended,
        // user-friendly behaviour.
        force_path      = 0x4,
    };

    inline opt operator |(opt a, opt b) { return opt(uint8_t(a) | uint8_t(b)); }
    inline bool operator &(opt a, opt b) { return bool(uint8_t(a) & uint8_t(b)); }

// The settings class, only exposing to the user a way to set verbose mode
// and to force a rescan of installed desktop helpers (zenity, kdialog…).
    class settings
    {
    public:
        static bool available();

        static void verbose(bool value);
        static void rescan();

    protected:
        explicit settings(bool resync = false);

        bool check_program(std::string const &program);

        inline bool is_osascript() const;
        inline bool is_zenity() const;
        inline bool is_kdialog() const;

        enum class flag
        {
            is_scanned = 0,
            is_verbose,

            has_zenity,
            has_matedialog,
            has_qarma,
            has_kdialog,
            is_vista,

            max_flag,
        };

        // Static array of flags for internal state
        bool const &flags(flag in_flag) const;

        // Non-const getter for the static array of flags
        bool &flags(flag in_flag);
    };

// Internal classes, not to be used by client applications
    namespace internal
    {

// Process wait timeout, in milliseconds
        static int const default_wait_timeout = 20;

        class executor
        {
            friend class dialog;

        public:
            // High level function to get the result of a command
            std::string result(int *exit_code = nullptr);

            // High level function to abort
            bool kill();

#if _WIN32
            void start_func(std::function<std::string(int *)> const &fun);
    static BOOL CALLBACK enum_windows_callback(HWND hwnd, LPARAM lParam);
#elif __EMSCRIPTEN__
            void start(int exit_code);
#else
            void start_process(std::vector<std::string> const &command);
#endif

            ~executor();

        protected:
            bool ready(int timeout = default_wait_timeout);
            void stop();

        private:
            bool m_running = false;
            std::string m_stdout;
            int m_exit_code = -1;
#if _WIN32
            std::future<std::string> m_future;
    std::set<HWND> m_windows;
    std::condition_variable m_cond;
    std::mutex m_mutex;
    DWORD m_tid;
#elif __EMSCRIPTEN__ || __NX__
            // FIXME: do something
#else
            pid_t m_pid = 0;
            int m_fd = -1;
#endif
        };

        class platform
        {
        protected:
#if _WIN32
            // Helper class around LoadLibraryA() and GetProcAddress() with some safety
    class dll
    {
    public:
        dll(std::string const &name);
        ~dll();

        template<typename T> class proc
        {
        public:
            proc(dll const &lib, std::string const &sym)
              : m_proc(reinterpret_cast<T *>(::GetProcAddress(lib.handle, sym.c_str())))
            {}

            operator bool() const { return m_proc != nullptr; }
            operator T *() const { return m_proc; }

        private:
            T *m_proc;
        };

    private:
        HMODULE handle;
    };

    // Helper class around CoInitialize() and CoUnInitialize()
    class ole32_dll : public dll
    {
    public:
        ole32_dll();
        ~ole32_dll();
        bool is_initialized();

    private:
        HRESULT m_state;
    };

    // Helper class around CreateActCtx() and ActivateActCtx()
    class new_style_context
    {
    public:
        new_style_context();
        ~new_style_context();

    private:
        HANDLE create();
        ULONG_PTR m_cookie = 0;
    };
#endif
        };

        class dialog : protected settings, protected platform
        {
        public:
            bool ready(int timeout = default_wait_timeout) const;
            bool kill() const;

        protected:
            explicit dialog();

            std::vector<std::string> desktop_helper() const;
            static std::string buttons_to_name(choice _choice);
            static std::string get_icon_name(icon _icon);

            std::string powershell_quote(std::string const &str) const;
            std::string osascript_quote(std::string const &str) const;
            std::string shell_quote(std::string const &str) const;

            // Keep handle to executing command
            std::shared_ptr<executor> m_async;
        };

        class file_dialog : public dialog
        {
        protected:
            enum type
            {
                open,
                save,
                folder,
            };

            file_dialog(type in_type,
                        std::string const &title,
                        std::string const &default_path = "",
                        std::vector<std::string> const &filters = {},
                        opt options = opt::none);

        protected:
            std::string string_result();
            std::vector<std::string> vector_result();

#if _WIN32
            static int CALLBACK bffcallback(HWND hwnd, UINT uMsg, LPARAM, LPARAM pData);
#if PFD_HAS_IFILEDIALOG
    std::string select_folder_vista(IFileDialog *ifd, bool force_path);
#endif

    std::wstring m_wtitle;
    std::wstring m_wdefault_path;

    std::vector<std::string> m_vector_result;
#endif
        };

    } // namespace internal

//
// The notify widget
//

    class notify : public internal::dialog
    {
    public:
        notify(std::string const &title,
               std::string const &message,
               icon _icon = icon::info);
    };

//
// The message widget
//

    class message : public internal::dialog
    {
    public:
        message(std::string const &title,
                std::string const &text,
                choice _choice = choice::ok_cancel,
                icon _icon = icon::info);

        button result();

    private:
        // Some extra logic to map the exit code to button number
        std::map<int, button> m_mappings;
    };

//
// The open_file, save_file, and open_folder widgets
//

    class open_file : public internal::file_dialog
    {
    public:
        open_file(std::string const &title,
                  std::string const &default_path = "",
                  std::vector<std::string> const &filters = { "All Files", "*" },
                  opt options = opt::none);

#if defined(__has_cpp_attribute)
#if __has_cpp_attribute(deprecated)
        // Backwards compatibility
    [[deprecated("Use pfd::opt::multiselect instead of allow_multiselect")]]
#endif
#endif
        open_file(std::string const &title,
                  std::string const &default_path,
                  std::vector<std::string> const &filters,
                  bool allow_multiselect);

        std::vector<std::string> result();
    };

    class save_file : public internal::file_dialog
    {
    public:
        save_file(std::string const &title,
                  std::string const &default_path = "",
                  std::vector<std::string> const &filters = { "All Files", "*" },
                  opt options = opt::none);

#if defined(__has_cpp_attribute)
#if __has_cpp_attribute(deprecated)
        // Backwards compatibility
    [[deprecated("Use pfd::opt::force_overwrite instead of confirm_overwrite")]]
#endif
#endif
        save_file(std::string const &title,
                  std::string const &default_path,
                  std::vector<std::string> const &filters,
                  bool confirm_overwrite);

        std::string result();
    };

    class select_folder : public internal::file_dialog
    {
    public:
        select_folder(std::string const &title,
                      std::string const &default_path = "",
                      opt options = opt::none);

        std::string result();
    };

//
// Below this are all the method implementations. You may choose to define the
// macro PFD_SKIP_IMPLEMENTATION everywhere before including this header except
// in one place. This may reduce compilation times.
//

#if !defined PFD_SKIP_IMPLEMENTATION

// internal free functions implementations

    namespace internal
    {

#if _WIN32
        static inline std::wstring str2wstr(std::string const &str)
{
    int len = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), nullptr, 0);
    std::wstring ret(len, '\0');
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), (LPWSTR)ret.data(), (int)ret.size());
    return ret;
}

static inline std::string wstr2str(std::wstring const &str)
{
    int len = WideCharToMultiByte(CP_UTF8, 0, str.c_str(), (int)str.size(), nullptr, 0, nullptr, nullptr);
    std::string ret(len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, str.c_str(), (int)str.size(), (LPSTR)ret.data(), (int)ret.size(), nullptr, nullptr);
    return ret;
}

static inline bool is_vista()
{
    OSVERSIONINFOEXW osvi;
    memset(&osvi, 0, sizeof(osvi));
    DWORDLONG const mask = VerSetConditionMask(
            VerSetConditionMask(
                    VerSetConditionMask(
                            0, VER_MAJORVERSION, VER_GREATER_EQUAL),
                    VER_MINORVERSION, VER_GREATER_EQUAL),
            VER_SERVICEPACKMAJOR, VER_GREATER_EQUAL);
    osvi.dwOSVersionInfoSize = sizeof(osvi);
    osvi.dwMajorVersion = HIBYTE(_WIN32_WINNT_VISTA);
    osvi.dwMinorVersion = LOBYTE(_WIN32_WINNT_VISTA);
    osvi.wServicePackMajor = 0;

    return VerifyVersionInfoW(&osvi, VER_MAJORVERSION | VER_MINORVERSION | VER_SERVICEPACKMAJOR, mask) != FALSE;
}
#endif

// This is necessary until C++20 which will have std::string::ends_with() etc.

        static inline bool ends_with(std::string const &str, std::string const &suffix)
        {
            return suffix.size() <= str.size() &&
                   str.compare(str.size() - suffix.size(), suffix.size(), suffix) == 0;
        }

        static inline bool starts_with(std::string const &str, std::string const &prefix)
        {
            return prefix.size() <= str.size() &&
                   str.compare(0, prefix.size(), prefix) == 0;
        }

    } // namespace internal

// settings implementation

    inline settings::settings(bool resync)
    {
        flags(flag::is_scanned) &= !resync;

        if (flags(flag::is_scanned))
            return;

#if _WIN32
        flags(flag::is_vista) = internal::is_vista();
#elif !__APPLE__
        flags(flag::has_zenity) = check_program("zenity");
    flags(flag::has_matedialog) = check_program("matedialog");
    flags(flag::has_qarma) = check_program("qarma");
    flags(flag::has_kdialog) = check_program("kdialog");

    // If multiple helpers are available, try to default to the best one
    if (flags(flag::has_zenity) && flags(flag::has_kdialog))
    {
        auto desktop_name = std::getenv("XDG_SESSION_DESKTOP");
        if (desktop_name && desktop_name == std::string("gnome"))
            flags(flag::has_kdialog) = false;
        else if (desktop_name && desktop_name == std::string("KDE"))
            flags(flag::has_zenity) = false;
    }
#endif

        flags(flag::is_scanned) = true;
    }

    inline bool settings::available()
    {
#if _WIN32
        return true;
#elif __APPLE__
        return true;
#elif __EMSCRIPTEN__
        // FIXME: Return true after implementation is complete.
    return false;
#else
    settings tmp;
    return tmp.flags(flag::has_zenity) ||
           tmp.flags(flag::has_matedialog) ||
           tmp.flags(flag::has_qarma) ||
           tmp.flags(flag::has_kdialog);
#endif
    }

    inline void settings::verbose(bool value)
    {
        settings().flags(flag::is_verbose) = value;
    }

    inline void settings::rescan()
    {
        settings(/* resync = */ true);
    }

// Check whether a program is present using “which”.
    inline bool settings::check_program(std::string const &program)
    {
#if _WIN32
        (void)program;
    return false;
#elif __EMSCRIPTEN__
        (void)program;
    return false;
#else
        int exit_code = -1;
        internal::executor async;
        async.start_process({"/bin/sh", "-c", "which " + program});
        async.result(&exit_code);
        return exit_code == 0;
#endif
    }

    inline bool settings::is_osascript() const
    {
#if __APPLE__
        return true;
#else
        return false;
#endif
    }

    inline bool settings::is_zenity() const
    {
        return flags(flag::has_zenity) ||
               flags(flag::has_matedialog) ||
               flags(flag::has_qarma);
    }

    inline bool settings::is_kdialog() const
    {
        return flags(flag::has_kdialog);
    }

    inline bool const &settings::flags(flag in_flag) const
    {
        static bool flags[size_t(flag::max_flag)];
        return flags[size_t(in_flag)];
    }

    inline bool &settings::flags(flag in_flag)
    {
        return const_cast<bool &>(static_cast<settings const *>(this)->flags(in_flag));
    }

// executor implementation

    inline std::string internal::executor::result(int *exit_code /* = nullptr */)
    {
        stop();
        if (exit_code)
            *exit_code = m_exit_code;
        return m_stdout;
    }

    inline bool internal::executor::kill()
    {
#if _WIN32
        if (m_future.valid())
    {
        // Close all windows that weren’t open when we started the future
        auto previous_windows = m_windows;
        EnumWindows(&enum_windows_callback, (LPARAM)this);
        for (auto hwnd : m_windows)
            if (previous_windows.find(hwnd) == previous_windows.end())
                SendMessage(hwnd, WM_CLOSE, 0, 0);
    }
#elif __EMSCRIPTEN__ || __NX__
        // FIXME: do something
    return false; // cannot kill
#else
        ::kill(m_pid, SIGKILL);
#endif
        stop();
        return true;
    }

#if _WIN32
    inline BOOL CALLBACK internal::executor::enum_windows_callback(HWND hwnd, LPARAM lParam)
{
    auto that = (executor *)lParam;

    DWORD pid;
    auto tid = GetWindowThreadProcessId(hwnd, &pid);
    if (tid == that->m_tid)
        that->m_windows.insert(hwnd);
    return TRUE;
}
#endif

#if _WIN32
    inline void internal::executor::start_func(std::function<std::string(int *)> const &fun)
{
    stop();

    auto trampoline = [fun, this]()
    {
        // Save our thread id so that the caller can cancel us
        m_tid = GetCurrentThreadId();
        EnumWindows(&enum_windows_callback, (LPARAM)this);
        m_cond.notify_all();
        return fun(&m_exit_code);
    };

    std::unique_lock<std::mutex> lock(m_mutex);
    m_future = std::async(std::launch::async, trampoline);
    m_cond.wait(lock);
    m_running = true;
}

#elif __EMSCRIPTEN__
    inline void internal::executor::start(int exit_code)
{
    m_exit_code = exit_code;
}

#else
    inline void internal::executor::start_process(std::vector<std::string> const &command)
    {
        stop();
        m_stdout.clear();
        m_exit_code = -1;

        int in[2], out[2];
        if (pipe(in) != 0 || pipe(out) != 0)
            return;

        m_pid = fork();
        if (m_pid < 0)
            return;

        close(in[m_pid ? 0 : 1]);
        close(out[m_pid ? 1 : 0]);

        if (m_pid == 0)
        {
            dup2(in[0], STDIN_FILENO);
            dup2(out[1], STDOUT_FILENO);

            // Ignore stderr so that it doesn’t pollute the console (e.g. GTK+ errors from zenity)
            int fd = open("/dev/null", O_WRONLY);
            dup2(fd, STDERR_FILENO);
            close(fd);

            std::vector<char *> args;
            std::transform(command.cbegin(), command.cend(), std::back_inserter(args),
                           [](std::string const &s) { return const_cast<char *>(s.c_str()); });
            args.push_back(nullptr); // null-terminate argv[]

            execvp(args[0], args.data());
            exit(1);
        }

        close(in[1]);
        m_fd = out[0];
        auto flags = fcntl(m_fd, F_GETFL);
        fcntl(m_fd, F_SETFL, flags | O_NONBLOCK);

        m_running = true;
    }
#endif

    inline internal::executor::~executor()
    {
        stop();
    }

    inline bool internal::executor::ready(int timeout /* = default_wait_timeout */)
    {
        if (!m_running)
            return true;

#if _WIN32
        if (m_future.valid())
    {
        auto status = m_future.wait_for(std::chrono::milliseconds(timeout));
        if (status != std::future_status::ready)
        {
            // On Windows, we need to run the message pump. If the async
            // thread uses a Windows API dialog, it may be attached to the
            // main thread and waiting for messages that only we can dispatch.
            MSG msg;
            while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE))
            {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }
            return false;
        }

        m_stdout = m_future.get();
    }
#elif __EMSCRIPTEN__ || __NX__
        // FIXME: do something
    (void)timeout;
#else
        char buf[BUFSIZ];
        ssize_t received = read(m_fd, buf, BUFSIZ); // Flawfinder: ignore
        if (received > 0)
        {
            m_stdout += std::string(buf, (size_t)received);
            return false;
        }

        // Reap child process if it is dead. It is possible that the system has already reaped it
        // (this happens when the calling application handles or ignores SIG_CHLD) and results in
        // waitpid() failing with ECHILD. Otherwise we assume the child is running and we sleep for
        // a little while.
        int status;
        pid_t child = waitpid(m_pid, &status, WNOHANG);
        if (child != m_pid && (child >= 0 || errno != ECHILD))
        {
            // FIXME: this happens almost always at first iteration
            std::this_thread::sleep_for(std::chrono::milliseconds(timeout));
            return false;
        }

        close(m_fd);
        m_exit_code = WEXITSTATUS(status);
#endif

        m_running = false;
        return true;
    }

    inline void internal::executor::stop()
    {
        // Loop until the user closes the dialog
        while (!ready())
            ;
    }

// dll implementation

#if _WIN32
    inline internal::platform::dll::dll(std::string const &name)
  : handle(::LoadLibraryA(name.c_str()))
{}

inline internal::platform::dll::~dll()
{
    if (handle)
        ::FreeLibrary(handle);
}
#endif // _WIN32

// ole32_dll implementation

#if _WIN32
    inline internal::platform::ole32_dll::ole32_dll()
    : dll("ole32.dll")
{
    // Use COINIT_MULTITHREADED because COINIT_APARTMENTTHREADED causes crashes.
    // See https://github.com/samhocevar/portable-file-dialogs/issues/51
    auto coinit = proc<HRESULT WINAPI (LPVOID, DWORD)>(*this, "CoInitializeEx");
    m_state = coinit(nullptr, COINIT_MULTITHREADED);
}

inline internal::platform::ole32_dll::~ole32_dll()
{
    if (is_initialized())
        proc<void WINAPI ()>(*this, "CoUninitialize")();
}

inline bool internal::platform::ole32_dll::is_initialized()
{
    return m_state == S_OK || m_state == S_FALSE;
}
#endif

// new_style_context implementation

#if _WIN32
    inline internal::platform::new_style_context::new_style_context()
{
    // Only create one activation context for the whole app lifetime.
    static HANDLE hctx = create();

    if (hctx != INVALID_HANDLE_VALUE)
        ActivateActCtx(hctx, &m_cookie);
}

inline internal::platform::new_style_context::~new_style_context()
{
    DeactivateActCtx(0, m_cookie);
}

inline HANDLE internal::platform::new_style_context::create()
{
    // This “hack” seems to be necessary for this code to work on windows XP.
    // Without it, dialogs do not show and close immediately. GetError()
    // returns 0 so I don’t know what causes this. I was not able to reproduce
    // this behavior on Windows 7 and 10 but just in case, let it be here for
    // those versions too.
    // This hack is not required if other dialogs are used (they load comdlg32
    // automatically), only if message boxes are used.
    dll comdlg32("comdlg32.dll");

    // Using approach as shown here: https://stackoverflow.com/a/10444161
    UINT len = ::GetSystemDirectoryA(nullptr, 0);
    std::string sys_dir(len, '\0');
    ::GetSystemDirectoryA(&sys_dir[0], len);

    ACTCTXA act_ctx =
    {
        // Do not set flag ACTCTX_FLAG_SET_PROCESS_DEFAULT, since it causes a
        // crash with error “default context is already set”.
        sizeof(act_ctx),
        ACTCTX_FLAG_RESOURCE_NAME_VALID | ACTCTX_FLAG_ASSEMBLY_DIRECTORY_VALID,
        "shell32.dll", 0, 0, sys_dir.c_str(), (LPCSTR)124,
    };

    return ::CreateActCtxA(&act_ctx);
}
#endif // _WIN32

// dialog implementation

    inline bool internal::dialog::ready(int timeout /* = default_wait_timeout */) const
    {
        return m_async->ready(timeout);
    }

    inline bool internal::dialog::kill() const
    {
        return m_async->kill();
    }

    inline internal::dialog::dialog()
        : m_async(std::make_shared<executor>())
    {
    }

    inline std::vector<std::string> internal::dialog::desktop_helper() const
    {
#if __APPLE__
        return { "osascript" };
#else
        return { flags(flag::has_zenity) ? "zenity"
           : flags(flag::has_matedialog) ? "matedialog"
           : flags(flag::has_qarma) ? "qarma"
           : flags(flag::has_kdialog) ? "kdialog"
           : "echo" };
#endif
    }

    inline std::string internal::dialog::buttons_to_name(choice _choice)
    {
        switch (_choice)
        {
            case choice::ok_cancel: return "okcancel";
            case choice::yes_no: return "yesno";
            case choice::yes_no_cancel: return "yesnocancel";
            case choice::retry_cancel: return "retrycancel";
            case choice::abort_retry_ignore: return "abortretryignore";
            case choice::ok: default: return "ok";
        }
    }

    inline std::string internal::dialog::get_icon_name(icon _icon)
    {
        switch (_icon)
        {
            case icon::warning: return "warning";
            case icon::error: return "error";
            case icon::question: return "question";
                // Zenity wants "information" but WinForms wants "info"
                case icon::info:  default:
#if _WIN32
                return "info";
#else
                return "information";
#endif
        }
    }

// THis is only used for debugging purposes
    inline std::ostream& operator <<(std::ostream &s, std::vector<std::string> const &v)
    {
        int not_first = 0;
        for (auto &e : v)
            s << (not_first++ ? " " : "") << e;
        return s;
    }

// Properly quote a string for Powershell: replace ' or " with '' or ""
// FIXME: we should probably get rid of newlines!
// FIXME: the \" sequence seems unsafe, too!
// XXX: this is no longer used but I would like to keep it around just in case
    inline std::string internal::dialog::powershell_quote(std::string const &str) const
    {
        return "'" + std::regex_replace(str, std::regex("['\"]"), "$&$&") + "'";
    }

// Properly quote a string for osascript: replace \ or " with \\ or \"
// XXX: this also used to replace ' with \' when popen was used, but it would be
// smarter to do shell_quote(osascript_quote(...)) if this is needed again.
    inline std::string internal::dialog::osascript_quote(std::string const &str) const
    {
        return "\"" + std::regex_replace(str, std::regex("[\\\\\"]"), "\\$&") + "\"";
    }

// Properly quote a string for the shell: just replace ' with '\''
// XXX: this is no longer used but I would like to keep it around just in case
    inline std::string internal::dialog::shell_quote(std::string const &str) const
    {
        return "'" + std::regex_replace(str, std::regex("'"), "'\\''") + "'";
    }

// file_dialog implementation

    inline internal::file_dialog::file_dialog(type in_type,
                                              std::string const &title,
                                              std::string const &default_path /* = "" */,
                                              std::vector<std::string> const &filters /* = {} */,
                                              opt options /* = opt::none */)
    {
#if _WIN32
        std::string filter_list;
    std::regex whitespace("  *");
    for (size_t i = 0; i + 1 < filters.size(); i += 2)
    {
        filter_list += filters[i] + '\0';
        filter_list += std::regex_replace(filters[i + 1], whitespace, ";") + '\0';
    }
    filter_list += '\0';

    m_async->start_func([this, in_type, title, default_path, filter_list,
                         options](int *exit_code) -> std::string
    {
        (void)exit_code;
        m_wtitle = internal::str2wstr(title);
        m_wdefault_path = internal::str2wstr(default_path);
        auto wfilter_list = internal::str2wstr(filter_list);

        // Initialise COM. This is required for the new folder selection window,
        // (see https://github.com/samhocevar/portable-file-dialogs/pull/21)
        // and to avoid random crashes with GetOpenFileNameW() (see
        // https://github.com/samhocevar/portable-file-dialogs/issues/51)
        ole32_dll ole32;

        // Folder selection uses a different method
        if (in_type == type::folder)
        {
#if PFD_HAS_IFILEDIALOG
            if (flags(flag::is_vista))
            {
                // On Vista and higher we should be able to use IFileDialog for folder selection
                IFileDialog *ifd;
                HRESULT hr = dll::proc<HRESULT WINAPI (REFCLSID, LPUNKNOWN, DWORD, REFIID, LPVOID *)>(ole32, "CoCreateInstance")
                                 (CLSID_FileOpenDialog, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&ifd));

                // In case CoCreateInstance fails (which it should not), try legacy approach
                if (SUCCEEDED(hr))
                    return select_folder_vista(ifd, options & opt::force_path);
            }
#endif

            BROWSEINFOW bi;
            memset(&bi, 0, sizeof(bi));

            bi.lpfn = &bffcallback;
            bi.lParam = (LPARAM)this;

            if (flags(flag::is_vista))
            {
                if (ole32.is_initialized())
                    bi.ulFlags |= BIF_NEWDIALOGSTYLE;
                bi.ulFlags |= BIF_EDITBOX;
                bi.ulFlags |= BIF_STATUSTEXT;
            }

            auto *list = SHBrowseForFolderW(&bi);
            std::string ret;
            if (list)
            {
                auto buffer = new wchar_t[MAX_PATH];
                SHGetPathFromIDListW(list, buffer);
                dll::proc<void WINAPI (LPVOID)>(ole32, "CoTaskMemFree")(list);
                ret = internal::wstr2str(buffer);
                delete[] buffer;
            }
            return ret;
        }

        OPENFILENAMEW ofn;
        memset(&ofn, 0, sizeof(ofn));
        ofn.lStructSize = sizeof(OPENFILENAMEW);
        ofn.hwndOwner = GetActiveWindow();

        ofn.lpstrFilter = wfilter_list.c_str();

        auto woutput = std::wstring(MAX_PATH * 256, L'\0');
        ofn.lpstrFile = (LPWSTR)woutput.data();
        ofn.nMaxFile = (DWORD)woutput.size();
        if (!m_wdefault_path.empty())
        {
            // If a directory was provided, use it as the initial directory. If
            // a valid path was provided, use it as the initial file. Otherwise,
            // let the Windows API decide.
            auto path_attr = GetFileAttributesW(m_wdefault_path.c_str());
            if (path_attr != INVALID_FILE_ATTRIBUTES && (path_attr & FILE_ATTRIBUTE_DIRECTORY))
                ofn.lpstrInitialDir = m_wdefault_path.c_str();
            else if (m_wdefault_path.size() <= woutput.size())
                //second argument is size of buffer, not length of string
                StringCchCopyW(ofn.lpstrFile, MAX_PATH*256+1, m_wdefault_path.c_str());
            else
            {
                ofn.lpstrFileTitle = (LPWSTR)m_wdefault_path.data();
                ofn.nMaxFileTitle = (DWORD)m_wdefault_path.size();
            }
        }
        ofn.lpstrTitle = m_wtitle.c_str();
        ofn.Flags = OFN_NOCHANGEDIR | OFN_EXPLORER;

        dll comdlg32("comdlg32.dll");

        // Apply new visual style (required for windows XP)
        new_style_context ctx;

        if (in_type == type::save)
        {
            if (!(options & opt::force_overwrite))
                ofn.Flags |= OFN_OVERWRITEPROMPT;

            dll::proc<BOOL WINAPI (LPOPENFILENAMEW)> get_save_file_name(comdlg32, "GetSaveFileNameW");
            if (get_save_file_name(&ofn) == 0)
                return "";
            return internal::wstr2str(woutput.c_str());
        }
        else
        {
            if (options & opt::multiselect)
                ofn.Flags |= OFN_ALLOWMULTISELECT;
            ofn.Flags |= OFN_PATHMUSTEXIST;

            dll::proc<BOOL WINAPI (LPOPENFILENAMEW)> get_open_file_name(comdlg32, "GetOpenFileNameW");
            if (get_open_file_name(&ofn) == 0)
                return "";
        }

        std::string prefix;
        for (wchar_t const *p = woutput.c_str(); *p; )
        {
            auto filename = internal::wstr2str(p);
            p += wcslen(p);
            // In multiselect mode, we advance p one wchar further and
            // check for another filename. If there is one and the
            // prefix is empty, it means we just read the prefix.
            if ((options & opt::multiselect) && *++p && prefix.empty())
            {
                prefix = filename + "/";
                continue;
            }

            m_vector_result.push_back(prefix + filename);
        }

        return "";
    });
#elif __EMSCRIPTEN__
        // FIXME: do something
    (void)in_type;
    (void)title;
    (void)default_path;
    (void)filters;
    (void)options;
#else
        auto command = desktop_helper();

        if (is_osascript())
        {
            std::string script = "set ret to choose";
            switch (in_type)
            {
                case type::save:
                    script += " file name";
                    break;
                case type::open: default:
                    script += " file";
                    if (options & opt::multiselect)
                        script += " with multiple selections allowed";
                    break;
                case type::folder:
                    script += " folder";
                    break;
            }

            if (default_path.size())
                script += " default location " + osascript_quote(default_path);
            script += " with prompt " + osascript_quote(title);

            if (in_type == type::open)
            {
                // Concatenate all user-provided filter patterns
                std::string patterns;
                for (size_t i = 0; i < filters.size() / 2; ++i)
                    patterns += " " + filters[2 * i + 1];

                // Split the pattern list to check whether "*" is in there; if it
                // is, we have to disable filters because there is no mechanism in
                // OS X for the user to override the filter.
                std::regex sep("\\s+");
                std::string filter_list;
                bool has_filter = true;
                std::sregex_token_iterator iter(patterns.begin(), patterns.end(), sep, -1);
                std::sregex_token_iterator end;
                for ( ; iter != end; ++iter)
                {
                    auto pat = iter->str();
                    if (pat == "*" || pat == "*.*")
                        has_filter = false;
                    else if (internal::starts_with(pat, "*."))
                        filter_list += (filter_list.size() == 0 ? "" : ",") +
                                       osascript_quote(pat.substr(2, pat.size() - 2));
                }
                if (has_filter && filter_list.size() > 0)
                    script += " of type {" + filter_list + "}";
            }

            if (in_type == type::open && (options & opt::multiselect))
            {
                script += "\nset s to \"\"";
                script += "\nrepeat with i in ret";
                script += "\n  set s to s & (POSIX path of i) & \"\\n\"";
                script += "\nend repeat";
                script += "\ncopy s to stdout";
            }
            else
            {
                script += "\nPOSIX path of ret";
            }

            command.push_back("-e");
            command.push_back(script);
        }
        else if (is_zenity())
        {
            command.push_back("--file-selection");
            command.push_back("--filename=" + default_path);
            command.push_back("--title");
            command.push_back(title);
            command.push_back("--separator=\n");

            for (size_t i = 0; i < filters.size() / 2; ++i)
            {
                command.push_back("--file-filter");
                command.push_back(filters[2 * i] + "|" + filters[2 * i + 1]);
            }

            if (in_type == type::save)
                command.push_back("--save");
            if (in_type == type::folder)
                command.push_back("--directory");
            if (!(options & opt::force_overwrite))
                command.push_back("--confirm-overwrite");
            if (options & opt::multiselect)
                command.push_back("--multiple");
        }
        else if (is_kdialog())
        {
            switch (in_type)
            {
                case type::save: command.push_back("--getsavefilename"); break;
                case type::open: command.push_back("--getopenfilename"); break;
                case type::folder: command.push_back("--getexistingdirectory"); break;
            }
            if (options & opt::multiselect)
            {
                command.push_back("--multiple");
                command.push_back("--separate-output");
            }

            command.push_back(default_path);

            std::string filter;
            for (size_t i = 0; i < filters.size() / 2; ++i)
                filter += (i == 0 ? "" : " | ") + filters[2 * i] + "(" + filters[2 * i + 1] + ")";
            command.push_back(filter);

            command.push_back("--title");
            command.push_back(title);
        }

        if (flags(flag::is_verbose))
            std::cerr << "pfd: " << command << std::endl;

        m_async->start_process(command);
#endif
    }

    inline std::string internal::file_dialog::string_result()
    {
#if _WIN32
        return m_async->result();
#else
        auto ret = m_async->result();
        // Strip potential trailing newline (zenity). Also strip trailing slash
        // added by osascript for consistency with other backends.
        while (!ret.empty() && (ret.back() == '\n' || ret.back() == '/'))
            ret.pop_back();
        return ret;
#endif
    }

    inline std::vector<std::string> internal::file_dialog::vector_result()
    {
#if _WIN32
        m_async->result();
    return m_vector_result;
#else
        std::vector<std::string> ret;
        auto result = m_async->result();
        for (;;)
        {
            // Split result along newline characters
            auto i = result.find('\n');
            if (i == 0 || i == std::string::npos)
                break;
            ret.push_back(result.substr(0, i));
            result = result.substr(i + 1, result.size());
        }
        return ret;
#endif
    }

#if _WIN32
    // Use a static function to pass as BFFCALLBACK for legacy folder select
inline int CALLBACK internal::file_dialog::bffcallback(HWND hwnd, UINT uMsg,
                                                       LPARAM, LPARAM pData)
{
    auto inst = (file_dialog *)pData;
    switch (uMsg)
    {
        case BFFM_INITIALIZED:
            SendMessage(hwnd, BFFM_SETSELECTIONW, TRUE, (LPARAM)inst->m_wdefault_path.c_str());
            break;
    }
    return 0;
}

#if PFD_HAS_IFILEDIALOG
inline std::string internal::file_dialog::select_folder_vista(IFileDialog *ifd, bool force_path)
{
    std::string result;

    IShellItem *folder;

    // Load library at runtime so app doesn't link it at load time (which will fail on windows XP)
    dll shell32("shell32.dll");
    dll::proc<HRESULT WINAPI (PCWSTR, IBindCtx*, REFIID, void**)>
        create_item(shell32, "SHCreateItemFromParsingName");

    if (!create_item)
        return "";

    auto hr = create_item(m_wdefault_path.c_str(),
                          nullptr,
                          IID_PPV_ARGS(&folder));

    // Set default folder if found. This only sets the default folder. If
    // Windows has any info about the most recently selected folder, it
    // will display it instead. Generally, calling SetFolder() to set the
    // current directory “is not a good or expected user experience and
    // should therefore be avoided”:
    // https://docs.microsoft.com/windows/win32/api/shobjidl_core/nf-shobjidl_core-ifiledialog-setfolder
    if (SUCCEEDED(hr))
    {
        if (force_path)
            ifd->SetFolder(folder);
        else
            ifd->SetDefaultFolder(folder);
        folder->Release();
    }

    // Set the dialog title and option to select folders
    ifd->SetOptions(FOS_PICKFOLDERS);
    ifd->SetTitle(m_wtitle.c_str());

    hr = ifd->Show(GetActiveWindow());
    if (SUCCEEDED(hr))
    {
        IShellItem* item;
        hr = ifd->GetResult(&item);
        if (SUCCEEDED(hr))
        {
            wchar_t* wselected = nullptr;
            item->GetDisplayName(SIGDN_FILESYSPATH, &wselected);
            item->Release();

            if (wselected)
            {
                result = internal::wstr2str(std::wstring(wselected));
                dll::proc<void WINAPI (LPVOID)>(ole32_dll(), "CoTaskMemFree")(wselected);
            }
        }
    }

    ifd->Release();

    return result;
}
#endif
#endif

// notify implementation

    inline notify::notify(std::string const &title,
                          std::string const &message,
                          icon _icon /* = icon::info */)
    {
        if (_icon == icon::question) // Not supported by notifications
            _icon = icon::info;

#if _WIN32
        // Use a static shared pointer for notify_icon so that we can delete
    // it whenever we need to display a new one, and we can also wait
    // until the program has finished running.
    struct notify_icon_data : public NOTIFYICONDATAW
    {
        ~notify_icon_data() { Shell_NotifyIconW(NIM_DELETE, this); }
    };

    static std::shared_ptr<notify_icon_data> nid;

    // Release the previous notification icon, if any, and allocate a new
    // one. Note that std::make_shared() does value initialization, so there
    // is no need to memset the structure.
    nid = nullptr;
    nid = std::make_shared<notify_icon_data>();

    // For XP support
    nid->cbSize = NOTIFYICONDATAW_V2_SIZE;
    nid->hWnd = nullptr;
    nid->uID = 0;

    // Flag Description:
    // - NIF_ICON    The hIcon member is valid.
    // - NIF_MESSAGE The uCallbackMessage member is valid.
    // - NIF_TIP     The szTip member is valid.
    // - NIF_STATE   The dwState and dwStateMask members are valid.
    // - NIF_INFO    Use a balloon ToolTip instead of a standard ToolTip. The szInfo, uTimeout, szInfoTitle, and dwInfoFlags members are valid.
    // - NIF_GUID    Reserved.
    nid->uFlags = NIF_MESSAGE | NIF_ICON | NIF_INFO;

    // Flag Description
    // - NIIF_ERROR     An error icon.
    // - NIIF_INFO      An information icon.
    // - NIIF_NONE      No icon.
    // - NIIF_WARNING   A warning icon.
    // - NIIF_ICON_MASK Version 6.0. Reserved.
    // - NIIF_NOSOUND   Version 6.0. Do not play the associated sound. Applies only to balloon ToolTips
    switch (_icon)
    {
        case icon::warning: nid->dwInfoFlags = NIIF_WARNING; break;
        case icon::error: nid->dwInfoFlags = NIIF_ERROR; break;
        /* case icon::info: */ default: nid->dwInfoFlags = NIIF_INFO; break;
    }

    ENUMRESNAMEPROC icon_enum_callback = [](HMODULE, LPCTSTR, LPTSTR lpName, LONG_PTR lParam) -> BOOL
    {
        ((NOTIFYICONDATAW *)lParam)->hIcon = ::LoadIcon(GetModuleHandle(nullptr), lpName);
        return false;
    };

    nid->hIcon = ::LoadIcon(nullptr, IDI_APPLICATION);
    ::EnumResourceNames(nullptr, RT_GROUP_ICON, icon_enum_callback, (LONG_PTR)nid.get());

    nid->uTimeout = 5000;

    StringCchCopyW(nid->szInfoTitle, ARRAYSIZE(nid->szInfoTitle), internal::str2wstr(title).c_str());
    StringCchCopyW(nid->szInfo, ARRAYSIZE(nid->szInfo), internal::str2wstr(message).c_str());

    // Display the new icon
    Shell_NotifyIconW(NIM_ADD, nid.get());
#elif __EMSCRIPTEN__
        // FIXME: do something
    (void)title;
    (void)message;
#else
        auto command = desktop_helper();

        if (is_osascript())
        {
            command.push_back("-e");
            command.push_back("display notification " + osascript_quote(message) +
                              " with title " + osascript_quote(title));
        }
        else if (is_zenity())
        {
            command.push_back("--notification");
            command.push_back("--window-icon");
            command.push_back(get_icon_name(_icon));
            command.push_back("--text");
            command.push_back(title + "\n" + message);
        }
        else if (is_kdialog())
        {
            command.push_back("--icon");
            command.push_back(get_icon_name(_icon));
            command.push_back("--title");
            command.push_back(title);
            command.push_back("--passivepopup");
            command.push_back(message);
            command.push_back("5");
        }

        if (flags(flag::is_verbose))
            std::cerr << "pfd: " << command << std::endl;

        m_async->start_process(command);
#endif
    }

// message implementation

    inline message::message(std::string const &title,
                            std::string const &text,
                            choice _choice /* = choice::ok_cancel */,
                            icon _icon /* = icon::info */)
    {
#if _WIN32
        // Use MB_SYSTEMMODAL rather than MB_TOPMOST to ensure the message window is brought
    // to front. See https://github.com/samhocevar/portable-file-dialogs/issues/52
    UINT style = MB_SYSTEMMODAL;
    switch (_icon)
    {
        case icon::warning: style |= MB_ICONWARNING; break;
        case icon::error: style |= MB_ICONERROR; break;
        case icon::question: style |= MB_ICONQUESTION; break;
        /* case icon::info: */ default: style |= MB_ICONINFORMATION; break;
    }

    switch (_choice)
    {
        case choice::ok_cancel: style |= MB_OKCANCEL; break;
        case choice::yes_no: style |= MB_YESNO; break;
        case choice::yes_no_cancel: style |= MB_YESNOCANCEL; break;
        case choice::retry_cancel: style |= MB_RETRYCANCEL; break;
        case choice::abort_retry_ignore: style |= MB_ABORTRETRYIGNORE; break;
        /* case choice::ok: */ default: style |= MB_OK; break;
    }

    m_mappings[IDCANCEL] = button::cancel;
    m_mappings[IDOK] = button::ok;
    m_mappings[IDYES] = button::yes;
    m_mappings[IDNO] = button::no;
    m_mappings[IDABORT] = button::abort;
    m_mappings[IDRETRY] = button::retry;
    m_mappings[IDIGNORE] = button::ignore;

    m_async->start_func([text, title, style](int* exit_code) -> std::string
    {
        auto wtext = internal::str2wstr(text);
        auto wtitle = internal::str2wstr(title);
        // Apply new visual style (required for all Windows versions)
        new_style_context ctx;
        *exit_code = MessageBoxW(GetActiveWindow(), wtext.c_str(), wtitle.c_str(), style);
        return "";
    });

#elif __EMSCRIPTEN__
        std::string full_message;
    switch (_icon)
    {
        case icon::warning: full_message = "⚠️"; break;
        case icon::error: full_message = "⛔"; break;
        case icon::question: full_message = "❓"; break;
        /* case icon::info: */ default: full_message = "ℹ"; break;
    }

    full_message += ' ' + title + "\n\n" + text;

    // This does not really start an async task; it just passes the
    // EM_ASM_INT return value to a fake start() function.
    m_async->start(EM_ASM_INT(
    {
        if ($1)
            return window.confirm(UTF8ToString($0)) ? 0 : -1;
        alert(UTF8ToString($0));
        return 0;
    }, full_message.c_str(), _choice == choice::ok_cancel));
#else
        auto command = desktop_helper();

        if (is_osascript())
        {
            std::string script = "display dialog " + osascript_quote(text) +
                                 " with title " + osascript_quote(title);
            switch (_choice)
            {
                case choice::ok_cancel:
                    script += "buttons {\"OK\", \"Cancel\"}"
                              " default button \"OK\""
                              " cancel button \"Cancel\"";
                    m_mappings[256] = button::cancel;
                    break;
                case choice::yes_no:
                    script += "buttons {\"Yes\", \"No\"}"
                              " default button \"Yes\""
                              " cancel button \"No\"";
                    m_mappings[256] = button::no;
                    break;
                case choice::yes_no_cancel:
                    script += "buttons {\"Yes\", \"No\", \"Cancel\"}"
                              " default button \"Yes\""
                              " cancel button \"Cancel\"";
                    m_mappings[256] = button::cancel;
                    break;
                case choice::retry_cancel:
                    script += "buttons {\"Retry\", \"Cancel\"}"
                              " default button \"Retry\""
                              " cancel button \"Cancel\"";
                    m_mappings[256] = button::cancel;
                    break;
                case choice::abort_retry_ignore:
                    script += "buttons {\"Abort\", \"Retry\", \"Ignore\"}"
                              " default button \"Retry\""
                              " cancel button \"Retry\"";
                    m_mappings[256] = button::cancel;
                    break;
                case choice::ok: default:
                    script += "buttons {\"OK\"}"
                              " default button \"OK\""
                              " cancel button \"OK\"";
                    m_mappings[256] = button::ok;
                    break;
            }
            script += " with icon ";
            switch (_icon)
            {
#define PFD_OSX_ICON(n) "alias ((path to library folder from system domain) as text " \
                "& \"CoreServices:CoreTypes.bundle:Contents:Resources:" n ".icns\")"
                case icon::info: default: script += PFD_OSX_ICON("ToolBarInfo"); break;
                case icon::warning: script += "caution"; break;
                case icon::error: script += "stop"; break;
                case icon::question: script += PFD_OSX_ICON("GenericQuestionMarkIcon"); break;
#undef PFD_OSX_ICON
            }

            command.push_back("-e");
            command.push_back(script);
        }
        else if (is_zenity())
        {
            switch (_choice)
            {
                case choice::ok_cancel:
                    command.insert(command.end(), { "--question", "--cancel-label=Cancel", "--ok-label=OK" }); break;
                case choice::yes_no:
                    // Do not use standard --question because it causes “No” to return -1,
                    // which is inconsistent with the “Yes/No/Cancel” mode below.
                    command.insert(command.end(), { "--question", "--switch", "--extra-button=No", "--extra-button=Yes" }); break;
                case choice::yes_no_cancel:
                    command.insert(command.end(), { "--question", "--switch", "--extra-button=Cancel", "--extra-button=No", "--extra-button=Yes" }); break;
                case choice::retry_cancel:
                    command.insert(command.end(), { "--question", "--switch", "--extra-button=Cancel", "--extra-button=Retry" }); break;
                case choice::abort_retry_ignore:
                    command.insert(command.end(), { "--question", "--switch", "--extra-button=Ignore", "--extra-button=Abort", "--extra-button=Retry" }); break;
                case choice::ok:
                default:
                    switch (_icon)
                    {
                        case icon::error: command.push_back("--error"); break;
                        case icon::warning: command.push_back("--warning"); break;
                        default: command.push_back("--info"); break;
                    }
            }

            command.insert(command.end(), { "--title", title,
                                            "--width=300", "--height=0", // sensible defaults
                                            "--text", text,
                                            "--icon-name=dialog-" + get_icon_name(_icon) });
        }
        else if (is_kdialog())
        {
            if (_choice == choice::ok)
            {
                switch (_icon)
                {
                    case icon::error: command.push_back("--error"); break;
                    case icon::warning: command.push_back("--sorry"); break;
                    default: command.push_back("--msgbox"); break;
                }
            }
            else
            {
                std::string flag = "--";
                if (_icon == icon::warning || _icon == icon::error)
                    flag += "warning";
                flag += "yesno";
                if (_choice == choice::yes_no_cancel)
                    flag += "cancel";
                command.push_back(flag);
                if (_choice == choice::yes_no || _choice == choice::yes_no_cancel)
                {
                    m_mappings[0] = button::yes;
                    m_mappings[256] = button::no;
                }
            }

            command.push_back(text);
            command.push_back("--title");
            command.push_back(title);

            // Must be after the above part
            if (_choice == choice::ok_cancel)
                command.insert(command.end(), { "--yes-label", "OK", "--no-label", "Cancel" });
        }

        if (flags(flag::is_verbose))
            std::cerr << "pfd: " << command << std::endl;

        m_async->start_process(command);
#endif
    }

    inline button message::result()
    {
        int exit_code;
        auto ret = m_async->result(&exit_code);
        // osascript will say "button returned:Cancel\n"
        // and others will just say "Cancel\n"
        if (exit_code < 0 || // this means cancel
            internal::ends_with(ret, "Cancel\n"))
            return button::cancel;
        if (internal::ends_with(ret, "OK\n"))
            return button::ok;
        if (internal::ends_with(ret, "Yes\n"))
            return button::yes;
        if (internal::ends_with(ret, "No\n"))
            return button::no;
        if (internal::ends_with(ret, "Abort\n"))
            return button::abort;
        if (internal::ends_with(ret, "Retry\n"))
            return button::retry;
        if (internal::ends_with(ret, "Ignore\n"))
            return button::ignore;
        if (m_mappings.count(exit_code) != 0)
            return m_mappings[exit_code];
        return exit_code == 0 ? button::ok : button::cancel;
    }

// open_file implementation

    inline open_file::open_file(std::string const &title,
                                std::string const &default_path /* = "" */,
                                std::vector<std::string> const &filters /* = { "All Files", "*" } */,
                                opt options /* = opt::none */)
        : file_dialog(type::open, title, default_path, filters, options)
    {
    }

    inline open_file::open_file(std::string const &title,
                                std::string const &default_path,
                                std::vector<std::string> const &filters,
                                bool allow_multiselect)
        : open_file(title, default_path, filters,
                    (allow_multiselect ? opt::multiselect : opt::none))
    {
    }

    inline std::vector<std::string> open_file::result()
    {
        return vector_result();
    }

// save_file implementation

    inline save_file::save_file(std::string const &title,
                                std::string const &default_path /* = "" */,
                                std::vector<std::string> const &filters /* = { "All Files", "*" } */,
                                opt options /* = opt::none */)
        : file_dialog(type::save, title, default_path, filters, options)
    {
    }

    inline save_file::save_file(std::string const &title,
                                std::string const &default_path,
                                std::vector<std::string> const &filters,
                                bool confirm_overwrite)
        : save_file(title, default_path, filters,
                    (confirm_overwrite ? opt::none : opt::force_overwrite))
    {
    }

    inline std::string save_file::result()
    {
        return string_result();
    }

// select_folder implementation

    inline select_folder::select_folder(std::string const &title,
                                        std::string const &default_path /* = "" */,
                                        opt options /* = opt::none */)
        : file_dialog(type::folder, title, default_path, {}, options)
    {
    }

    inline std::string select_folder::result()
    {
        return string_result();
    }

#endif // PFD_SKIP_IMPLEMENTATION

} // namespace pfd


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image.cpp continued                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/imgui/image_widgets.h included by src/immvision/internal/image.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    namespace ImageWidgets
    {
        cv::Point2d DisplayTexture_TrackMouse(const GlTextureCv& texture, ImVec2 displaySize);
        void ShowImageInfo(const cv::Mat &image, double zoomFactor);
        void ShowPixelColorWidget(const cv::Mat &image, cv::Point pt, const ImageParams& params);

        // If true, the collapsing headers will be synced across instances
        extern bool s_CollapsingHeader_CacheState_Sync;
        bool CollapsingHeader_OptionalCacheState(const char *name, bool forceOpen = false);
    } // namespace ImageWidgets

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image.cpp continued                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image_cache.h included by src/immvision/internal/image.cpp      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace ImageCache
    {
        using KeyType = std::size_t;

        class ImageTextureCache
        {
        public:
            // members
            struct CachedParams
            {
                // This caches are small and will persist during the application lifetime
                ImageParams* ParamsPtr = nullptr;
                ImVec2 LastDragDelta;
                std::vector<char> FilenameEditBuffer = std::vector<char>(1000, '\0');
                bool   IsMouseDragging = false;
                struct ImageParams  PreviousParams;
            };
            struct CachedImages
            {
                // This caches are heavy and will be destroyed
                // if not used (after about 5 seconds)
                cv::Mat     ImageRgbaCache;
                std::unique_ptr<GlTextureCv> GlTexture;
            };


            // returns true if new entry
            bool UpdateCache(const std::string& id_label, const cv::Mat& image, ImageParams* params, bool userRefresh);
            KeyType GetID(const std::string& id_label);
            CachedParams& GetCacheParams(const std::string& id_label);
            CachedImages& GetCacheImages(const std::string& id_label);
            void ClearImagesCache();

        private:
            // Methods
            void UpdateLinkedZooms(const std::string& id_label);
            void UpdateLinkedColormapSettings(const std::string& id_label);
            bool AddEntryIfMissing(KeyType key);


            internal::Cache<KeyType, CachedParams> mCacheParams;
            double mCachedImagesTimeToLive = 5.;
            internal::ShortLivedCache<KeyType, CachedImages> mCacheImages { mCachedImagesTimeToLive };
        };

        extern ImageTextureCache gImageTextureCache;

    } // namespace ImageUtils


} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image.cpp continued                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/panic.h included by src/immvision/internal/image.cpp       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <exception>

namespace ImmVision
{
    void Panic(const std::exception& e);
    void Panic_UnknownCause();
} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image.cpp continued                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#ifndef IMMVISION_VERSION
#define IMMVISION_VERSION "unknown version"
#endif

namespace ImmVision
{
    void ClearTextureCache()
    {
        ImageCache::gImageTextureCache.ClearImagesCache();
        Icons::ClearIconsTextureCache();
    }


    void Image(const std::string& label_id, const cv::Mat& image, ImageParams* params)
    {
        // Note: although this function is long, it is well organized, and it behaves almost like a class
        // with members = (cv::Mat& image, ImageParams* params).
        //
        // - it begins by defining a set a lambdas that display various widgets
        //   for the different zones of the Gui (those lambdas are named fnXXXX)
        //
        // - the core of the function is only a few lines long and begins after the line
        //    "Core of the function below"
        //
        // If your editor is able to collapse the lambda definitions, you will see the structure.

        using CachedParams = ImageCache::ImageTextureCache::CachedParams;
        using CachedImages = ImageCache::ImageTextureCache::CachedImages;

        //
        // Lambda / is Label visible
        //
        auto fnIsLabelVisible = [&label_id]() -> bool {
            if (label_id.empty())
                return false;
            if (label_id.find("##") == 0)
                return false;
            return true;
        };
        //
        // Lambdas / Watched Pixels
        //
        bool wasWatchedPixelAdded = false;
        auto fnWatchedPixels_Add = [&params, &wasWatchedPixelAdded](const cv::Point2d& pixelDouble)
        {
            cv::Point pixel((int)(pixelDouble.x + .5), (int)(pixelDouble.y + .5));
            params->WatchedPixels.push_back(pixel);

            wasWatchedPixelAdded = true;
            if (! params->ShowOptionsInTooltip)
                params->ShowOptionsPanel = true;
        };
        auto fnWatchedPixels_Gui = [&params, &image]()
        {
            ImGui::Text("Double click the image...");

            int idxToRemove = -1;

            if (! params->WatchedPixels.empty())
            {
                ImGui::BeginTable("WatchedPixels", 4, ImGuiTableFlags_SizingFixedFit | ImGuiTableFlags_NoHostExtendX);
                ImGui::TableNextRow(ImGuiTableRowFlags_Headers);
                ImGui::TableNextColumn();
                ImGui::Text("#");
                ImGui::TableNextColumn();
                ImGui::Text("(x,y)");
                ImGui::TableNextColumn();
                ImGui::Text("Color");
                ImGui::TableNextColumn();
                ImGui::Text("%s", "");

                for (size_t i = 0; i < params->WatchedPixels.size(); ++i)
                {
                    cv::Point watchedPixel = params->WatchedPixels[i];
                    ImGui::TableNextRow();

                    // index
                    ImGui::TableNextColumn();
                    ImGui::Text("#%i: ", (int)i);

                    // (x,y)
                    ImGui::TableNextColumn();
                    std::string posStr = std::string("(") + std::to_string(watchedPixel.x) + "," + std::to_string(watchedPixel.y) +")";
                    ImGui::Text("%s", posStr.c_str());

                    // Show Color Cell
                    ImGui::TableNextColumn();
                    ImageWidgets::ShowPixelColorWidget(image, watchedPixel, *params);

                    // Actions
                    ImGui::TableNextColumn();
                    std::string lblRemove = "x##" + std::to_string(i);
                    if (ImGui::SmallButton(lblRemove.c_str()))
                        idxToRemove = (int) i;
                    ImGui::SameLine();
                }
                ImGui::EndTable();
            }
            if (idxToRemove >= 0)
                params->WatchedPixels.erase(params->WatchedPixels.begin() + (std::ptrdiff_t)idxToRemove);

            ImGui::Checkbox("Add Watched Pixel on double click", &params->AddWatchedPixelOnDoubleClick);
            ImGui::Checkbox("Highlight Watched Pixels", &params->HighlightWatchedPixels);
        };

        //
        // Lambdas / Colormap
        //
        auto fnColormap = [&params, &image](float availableGuiWidth)
        {
            cv::Rect roi = ZoomPanTransform::VisibleRoi(params->ZoomPanMatrix, params->ImageDisplaySize, image.size());
            Colormap::GuiShowColormapSettingsData(
                image,
                roi,
                availableGuiWidth,
                &params->ColormapSettings);
        };


        //
        // Lambdas / Options & Adjustments
        //
        auto fnOptionsInnerGui = [&params, &image, &fnWatchedPixels_Gui, &wasWatchedPixelAdded, &fnColormap](
                CachedParams & cacheParams)
        {
            float optionsWidth = 330.f;
            // Group with fixed width, so that Collapsing headers stop at optionsWidth
            ImGuiImm::BeginGroupFixedWidth(optionsWidth);

            // Colormap
            if (Colormap::CanColormap(image) && ImageWidgets::CollapsingHeader_OptionalCacheState("Colormap"))
                fnColormap(optionsWidth);

            // Watched Pixels
            if (ImageWidgets::CollapsingHeader_OptionalCacheState("Watched Pixels", wasWatchedPixelAdded))
                fnWatchedPixels_Gui();

            // Image display options
            if (ImageWidgets::CollapsingHeader_OptionalCacheState("Image Display"))
            {
                if (image.type() == CV_8UC3 || image.type() == CV_8UC4)
                {
                    ImGui::Text("Color Order");
                    ImGui::SameLine();
                    int v = params->IsColorOrderBGR ? 0 : 1;
                    ImGui::RadioButton("RGB", &v, 1);
                    ImGui::SameLine();
                    ImGui::RadioButton("BGR", &v, 0);
                    params->IsColorOrderBGR = (v == 0);
                }
                ImGui::Checkbox("Show school paper background", &params->ShowSchoolPaperBackground);
                if (image.type() == CV_8UC4)
                    ImGui::Checkbox("Show alpha channel checkerboard", &params->ShowAlphaChannelCheckerboard);
                if (image.channels() > 1)
                {
                    ImGui::Text("Channels: ");
                    ImGui::RadioButton("All", &params->SelectedChannel, -1); ImGui::SameLine();
                    for (int channel_id = 0; channel_id < image.channels(); ++channel_id)
                    {
                        ImGui::RadioButton(std::to_string(channel_id).c_str(), &params->SelectedChannel, channel_id);
                        ImGui::SameLine();
                    }
                    ImGui::NewLine();
                }
                {
                    ImGuiImm::BeginGroupPanel("High zoom options");
                    ImGui::Checkbox("Grid", &params->ShowGrid);
                    ImGui::Checkbox("Draw values on pixels", &params->DrawValuesOnZoomedPixels);
                    ImGuiImm::EndGroupPanel();
                }

            }

            // Image display options
            if (ImageWidgets::CollapsingHeader_OptionalCacheState("Options"))
            {
                {
                    ImGuiImm::BeginGroupPanel("Image display options");
                    ImGui::Checkbox("Show image info", &params->ShowImageInfo);
                    ImGui::Checkbox("Show pixel info", &params->ShowPixelInfo);
                    ImGui::Checkbox("Show zoom buttons", &params->ShowZoomButtons);
                    ImGuiImm::EndGroupPanel();
                }

                ImGui::Checkbox("Pan with mouse", &params->PanWithMouse);
                ImGui::Checkbox("Zoom with mouse wheel", &params->ZoomWithMouseWheel);

                ImGui::Separator();
                if (ImGui::Checkbox("Show Options in tooltip window", &params->ShowOptionsInTooltip))
                {
                    if (!params->ShowOptionsInTooltip) // We were in a tooltip when clicking
                        params->ShowOptionsPanel = true;
                }
            }

            // Save Image
            if (ImageWidgets::CollapsingHeader_OptionalCacheState("Save"))
            {
                // Use portable_file_dialogs if available
                if (pfd::settings::available())
                {
                    if (ImGui::Button("Save Image"))
                    {
                        pfd::settings::verbose(true);
                        std::string filename = pfd::save_file("Select a file", ".",
                                                              { "Image Files", "*.png *.jpg *.jpeg *.jpg *.bmp *.gif *.exr",
                                                                "All Files", "*" }).result();
                        if (!filename.empty())
                        {
                            try
                            {
                                cv::imwrite(filename, image);
                            }
                            catch(const cv::Exception& e)
                            {
                                std::string errorMessage = std::string("Could not save image\n") + e.err.c_str();
                                pfd::message("Error", errorMessage, pfd::choice::ok, pfd::icon::error);
                            }
                        }
                    }
                }
                else
                {
                    ImGui::Text("File name");
                    char *filename = cacheParams.FilenameEditBuffer.data();
                    ImGui::SetNextItemWidth(200.f);
                    ImGui::InputText("##filename", filename, 1000);
                    //ImGui::SetNextItemWidth(200.f);
                    ImGui::Text("The image will be saved in the current folder");
                    ImGui::Text("with a format corresponding to the extension");
                    if (ImGui::SmallButton("save"))
                        cv::imwrite(filename, image);
                }
            }

            ImGuiImm::EndGroupFixedWidth();

        };
        auto fnToggleShowOptions = [&params]()
        {
            if (params->ShowOptionsInTooltip)
                ImGui::OpenPopup("Options");
            else
                params->ShowOptionsPanel = !params->ShowOptionsPanel;
        };
        auto fnOptionGui = [&params, &fnOptionsInnerGui](CachedParams & cacheParams)
        {
            if (params->ShowOptionsInTooltip)
            {
                if (ImGui::BeginPopup("Options"))
                {
                    fnOptionsInnerGui(cacheParams);
                    ImGui::EndPopup();
                }
            }
            else if (params->ShowOptionsPanel)
            {
                ImGui::SameLine();
                ImGui::BeginGroup();
                ImGui::Text("Options");
                fnOptionsInnerGui(cacheParams);
                ImGui::EndGroup();
            }
        };

        //
        // Lambdas / Handle Zoom
        //
        // Mouse dragging
        auto fnHandleMouseDragging = [&params](CachedParams & cacheParams)
        {
            ZoomPanTransform::MatrixType& zoomMatrix = params->ZoomPanMatrix;

            int mouseDragButton = 0;
            bool isMouseDraggingInside = ImGui::IsMouseDragging(mouseDragButton) && ImGui::IsItemHovered();
            if (isMouseDraggingInside)
                cacheParams.IsMouseDragging = true;
            if (! ImGui::IsMouseDown(mouseDragButton))
            {
                cacheParams.IsMouseDragging = false;
                cacheParams.LastDragDelta = ImVec2(0.f, 0.f);
            }
            if (cacheParams.IsMouseDragging && params->PanWithMouse )
            {
                ImVec2 dragDelta = ImGui::GetMouseDragDelta(mouseDragButton);
                ImVec2 dragDeltaDelta(dragDelta.x - cacheParams.LastDragDelta.x, dragDelta.y - cacheParams.LastDragDelta.y);
                zoomMatrix = zoomMatrix * ZoomPanTransform::ComputePanMatrix(
                    cv::Point2d((double)dragDeltaDelta.x, (double)dragDeltaDelta.y),
                    zoomMatrix(0, 0));
                cacheParams.LastDragDelta = dragDelta;
            }
        };
        auto fnHandleMouseWheel = [&params](const cv::Point2d& mouseLocation)
        {
            if (!params->ZoomWithMouseWheel)
                return;
            ImGui::SetItemUsingMouseWheel();

            if ((fabs(ImGui::GetIO().MouseWheel) > 0.f) && (ImGui::IsItemHovered()))
            {
                double zoomRatio = (double)ImGui::GetIO().MouseWheel / 4.;
                params->ZoomPanMatrix = params->ZoomPanMatrix * ZoomPanTransform::ComputeZoomMatrix(mouseLocation, exp(zoomRatio));
            }
        };
        auto fnShowZoomButtons = [&params, &image]()
        {
            if (params->ShowZoomButtons)
            {
                ZoomPanTransform::MatrixType& zoomMatrix = params->ZoomPanMatrix;

                cv::Point2d viewportCenter_originalImage = ZoomPanTransform::Apply(
                    zoomMatrix.inv(),
                    cv::Point2d (
                        (double)params->ImageDisplaySize.width / 2.,
                        (double)params->ImageDisplaySize.height / 2.)
                );

                {
                    cv::Point2d zoomCenter = params->WatchedPixels.empty() ?
                                viewportCenter_originalImage
                            :   cv::Point2d(params->WatchedPixels.back());
                    ImGui::PushButtonRepeat(true);
                    if (Icons::IconButton(Icons::IconType::ZoomPlus))
                        zoomMatrix = zoomMatrix * ZoomPanTransform::ComputeZoomMatrix(zoomCenter, 1.1);

                    ImGui::SameLine();

                    if (Icons::IconButton(Icons::IconType::ZoomMinus))
                        zoomMatrix = zoomMatrix * ZoomPanTransform::ComputeZoomMatrix(zoomCenter, 1. / 1.1);

                    ImGui::PopButtonRepeat();
                }
                ImGui::SameLine();
                // Scale1 & Full View Zoom  buttons
                {
                    auto scaleOneZoomInfo = ZoomPanTransform::MakeScaleOne(image.size(), params->ImageDisplaySize);
                    auto fullViewZoomInfo = ZoomPanTransform::MakeFullView(image.size(), params->ImageDisplaySize);
                    if (Icons::IconButton(
                        Icons::IconType::ZoomScaleOne,
                        ZoomPanTransform::IsEqual(zoomMatrix, scaleOneZoomInfo)) // disabled flag
                        )
                        zoomMatrix = scaleOneZoomInfo;

                    ImGui::SameLine();

                    if (Icons::IconButton(
                        Icons::IconType::ZoomFullView,
                        ZoomPanTransform::IsEqual(zoomMatrix, fullViewZoomInfo)) // disabled flag
                        )
                        zoomMatrix = fullViewZoomInfo;
                }
            }

        };
        //
        // Lambda / Show image
        //
        auto fnShowImage = [&params](CachedImages & cacheImages) ->  MouseInformation
        {
            cv::Point2d mouseLocation = ImageWidgets::DisplayTexture_TrackMouse(
                    *cacheImages.GlTexture,
                    ImVec2((float)params->ImageDisplaySize.width, (float)params->ImageDisplaySize.height));

            MouseInformation mouseInfo;
            if (ImGui::IsItemHovered())
            {
                mouseInfo.IsMouseHovering = true;
                mouseInfo.MousePosition = ZoomPanTransform::Apply(params->ZoomPanMatrix.inv(), mouseLocation);
                mouseInfo.MousePosition_Displayed = mouseLocation;
            }
            return mouseInfo;
        };


        //
        // Lambda / Show pixel info
        //
        auto fnShowPixelInfo = [&image, &params](const cv::Point2d& mouseLocation)
        {
            cv::Point mouseLoc =
                mouseLocation.x >= 0. ?
                        cv::Point((int)(mouseLocation.x + 0.5), (int)(mouseLocation.y + 0.5))
                    :   cv::Point(-1, -1)
                    ;
            if (mouseLoc.x >= 0)
            {
                ImGui::Text("(%i,%i)", mouseLoc.x, mouseLoc.y);
                ImGui::SameLine();
            }
            ImageWidgets::ShowPixelColorWidget(image, mouseLoc, *params);
        };

        //
        // Lambda / Show full Gui
        //
        auto fnShowFullGui = [&](CachedParams& cacheParams, CachedImages &cacheImages) -> MouseInformation
        {

            ImGui::BeginGroup();
            // Show image
            auto mouseInfo = fnShowImage(cacheImages);
            // Add Watched Pixel on double click
            if (   params->AddWatchedPixelOnDoubleClick
                && ImGui::IsMouseDoubleClicked(ImGuiMouseButton_Left)
                && ImGui::IsItemHovered())
                fnWatchedPixels_Add(mouseInfo.MousePosition);

            // Handle Mouse
            fnHandleMouseDragging(cacheParams);
            fnHandleMouseWheel(mouseInfo.MousePosition);

            // Zoom+ / Zoom- buttons
            fnShowZoomButtons();
            // adjust button
            if (params->ShowOptionsButton)
            {
                if (!params->ShowZoomButtons)
                    ImGui::NewLine();
                ImGuiImm::SameLineAlignRight(20.f, (float)params->ImageDisplaySize.width);
                if (Icons::IconButton(Icons::IconType::AdjustLevels))
                    fnToggleShowOptions();
            }

            // Show infos
            if (params->ShowImageInfo)
                ImageWidgets::ShowImageInfo(image, params->ZoomPanMatrix(0, 0));
            if (params->ShowPixelInfo)
                fnShowPixelInfo(mouseInfo.MousePosition);
            ImGui::EndGroup();

            // Show Options
            fnOptionGui(cacheParams);

            return mouseInfo;
        };
        auto fnShowFullGui_WithBorder = [&](CachedParams& cacheParams, CachedImages &cacheImages) -> MouseInformation
        {
            // BeginGroupPanel
            bool drawBorder =  fnIsLabelVisible();
            std::string title = label_id + "##title";
            ImGuiImm::BeginGroupPanel_FlagBorder(title.c_str(), drawBorder);
            auto mouseInfo = fnShowFullGui(cacheParams, cacheImages);
            ImGuiImm::EndGroupPanel_FlagBorder();
            return mouseInfo;
        };


        /////////////////////////////////////////////////////////////////////////////////////////
        //
        // Core of the function below (there are only lambdas declarations before)
        //
        /////////////////////////////////////////////////////////////////////////////////////////
        if (image.empty())
        {
            ImGui::TextColored(ImVec4(1.f, 0.f, 0.f, 1.f),
                               "%s -> empty image !!!", label_id.c_str());
            params->MouseInfo = MouseInformation();
            return;
        }

        ImGui::PushID(label_id.c_str());
        try
        {
            bool isNewImage = ImageCache::gImageTextureCache.UpdateCache(label_id, image, params, params->RefreshImage);
            auto &cacheParams = ImageCache::gImageTextureCache.GetCacheParams(label_id);
            auto &cacheImages = ImageCache::gImageTextureCache.GetCacheImages(label_id);
            params->MouseInfo = fnShowFullGui_WithBorder(cacheParams, cacheImages);

            // Handle Colormap
            cv::Rect roi = ZoomPanTransform::VisibleRoi(params->ZoomPanMatrix, params->ImageDisplaySize, image.size());
            if (isNewImage || params->RefreshImage)
                Colormap::InitStatsOnNewImage(image, roi, &params->ColormapSettings);
            if (! ZoomPanTransform::IsEqual(cacheParams.PreviousParams.ZoomPanMatrix, params->ZoomPanMatrix))
                Colormap::UpdateRoiStatsInteractively(image, roi, &params->ColormapSettings);
        }
        catch(std::exception& e)
        {
            Panic(e);
        }
        catch(...)
        {
            Panic_UnknownCause();
        }
        ImGui::PopID();
    }


    cv::Point2d ImageDisplay(
        const std::string& label_id,
        const cv::Mat& mat,
        const cv::Size& imageDisplaySize,
        bool refreshImage,
        bool showOptionsButton,
        bool isBgrOrBgra)
    {
        static std::map<const cv::Mat *, ImageParams> s_Params;
        if (s_Params.find(&mat) == s_Params.end())
        {
            ImageParams params = showOptionsButton ? ImageParams() : FactorImageParamsDisplayOnly();
            s_Params[&mat] = params;
        }

        ImageParams& params = s_Params.at(&mat);
        {
            params.ShowOptionsButton = showOptionsButton;
            params.ImageDisplaySize = imageDisplaySize;
            params.RefreshImage = refreshImage;
            params.IsColorOrderBGR = isBgrOrBgra;
        }

        Image(label_id, mat, &params);
        return params.MouseInfo.MousePosition;
    }


    ImageParams FactorImageParamsDisplayOnly()
    {
        ImageParams imageParams;
        {
            imageParams.ShowOptionsButton = false;
            imageParams.ShowOptionsPanel = false;
            imageParams.ZoomWithMouseWheel = false;
            imageParams.PanWithMouse = false;
            imageParams.ShowPixelInfo = false;
            imageParams.ShowImageInfo = false;
            imageParams.ShowGrid = false;
            imageParams.ShowAlphaChannelCheckerboard = false;
            imageParams.ShowSchoolPaperBackground = false;
            imageParams.ShowZoomButtons = false;
            imageParams.AddWatchedPixelOnDoubleClick = false;
        }
        return imageParams;
    }


    std::string VersionInfo()
    {
        char msg[2000];
        snprintf(msg, 2000, "immvision version %s (%s)", IMMVISION_VERSION, __TIMESTAMP__);
        return msg;
    }

    std::vector<std::string> AvailableColormaps()
    {
        return Colormap::AvailableColormaps();
    }


    cv::Mat GetCachedRgbaImage(const std::string& label_id)
    {
        cv::Mat r = ImageCache::gImageTextureCache.GetCacheImages(label_id).ImageRgbaCache;
        return r;
    }

} // namespace ImmVision


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/image_cache.cpp                                                 //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace ImageCache
    {

        static KeyType hash_str(const std::string& str)
        {
            std::string str2 = str + "mlkyqsdadsfklqqsmax!(((!' "; // I let my cat walk on the keyboard
            const std::hash<std::string> hasher;
            size_t hashResult = hasher(str2);
            return hashResult;
        }

        void InitializeMissingParams(ImageParams* params, const cv::Mat& image)
        {
            if (Colormap::IsNone(params->ColormapSettings))
                params->ColormapSettings = Colormap::ComputeInitialColormapSettings(image);
            if (params->ZoomPanMatrix == cv::Matx33d::eye())
                params->ZoomPanMatrix = ZoomPanTransform::MakeFullView(image.size(), params->ImageDisplaySize);
        }

        bool ShallRefreshRgbaCache(const ImageParams& v1, const ImageParams& v2)
        {
            if (v1.ColormapSettings.Colormap != v2.ColormapSettings.Colormap)
                return true;
            if (v1.ColormapSettings.internal_ColormapHovered != v2.ColormapSettings.internal_ColormapHovered)
                return true;
            if (! Colormap::IsEqual(v1.ColormapSettings, v2.ColormapSettings))
                return true;
            if (v1.SelectedChannel != v2.SelectedChannel)
                return true;
            if (v1.ShowAlphaChannelCheckerboard != v2.ShowAlphaChannelCheckerboard)
                return true;
            if (v1.ShowSchoolPaperBackground != v2.ShowSchoolPaperBackground)
                return true;
            if (v1.IsColorOrderBGR != v2.IsColorOrderBGR)
                return true;
            return false;
        }

        bool ShallRefreshTexture(const ImageParams& v1, const ImageParams& v2)
        {
            if (v1.ColormapSettings.Colormap != v2.ColormapSettings.Colormap)
                return true;
            if (v1.ColormapSettings.internal_ColormapHovered != v2.ColormapSettings.internal_ColormapHovered)
                return true;
            if (v1.ImageDisplaySize != v2.ImageDisplaySize)
                return true;
            if (! ZoomPanTransform::IsEqual(v1.ZoomPanMatrix, v2.ZoomPanMatrix))
                return true;
            if (! Colormap::IsEqual(v1.ColormapSettings, v2.ColormapSettings))
                return true;
            if (v1.ShowGrid != v2.ShowGrid)
                return true;
            if (v1.SelectedChannel != v2.SelectedChannel)
                return true;
            if (v1.ShowSchoolPaperBackground != v2.ShowSchoolPaperBackground)
                return true;
            if (v1.IsColorOrderBGR != v2.IsColorOrderBGR)
                return true;
            if (v1.WatchedPixels.size() != v2.WatchedPixels.size())
                return true;
            if (v1.HighlightWatchedPixels != v2.HighlightWatchedPixels)
                return true;
            if (v1.DrawValuesOnZoomedPixels != v2.DrawValuesOnZoomedPixels)
                return true;
            return false;
        }


        //
        // ImageTextureCache impl below
        //
        bool ImageTextureCache::AddEntryIfMissing(KeyType key)
        {
            bool isNewEntry = false;
            if (! mCacheParams.Contains(key))
            {
                isNewEntry = true;
                mCacheParams.AddKey(key);
            }
            if (! mCacheImages.Contains(key))
            {
                mCacheImages.AddKey(key);
                isNewEntry = true;
                mCacheImages.Get(key).GlTexture = std::make_unique<GlTextureCv>();
            }
            return isNewEntry;
        }


        bool ImageTextureCache::UpdateCache(const std::string& id_label, const cv::Mat& image, ImageParams* params, bool userRefresh)
        {
            // Update cache entries
            auto cacheKey = GetID(id_label);
            bool isNewEntry = AddEntryIfMissing(cacheKey);

            // Get caches
            CachedParams& cachedParams = mCacheParams.Get(cacheKey);
            CachedImages& cachedImage = mCacheImages.Get(cacheKey);
            cachedParams.ParamsPtr = params;
            ImageParams oldParams = cachedParams.PreviousParams;

            // Update current params if needed
            {
                params->ImageDisplaySize = ImGuiImm::ComputeDisplayImageSize(params->ImageDisplaySize, image.size());

                if (isNewEntry)
                    InitializeMissingParams(params, image);

                bool tryAdaptZoomToNewDisplaySize =
                    (oldParams.ImageDisplaySize != params->ImageDisplaySize)
                    &&  !(oldParams.ImageDisplaySize.area() == 0);
                if (tryAdaptZoomToNewDisplaySize)
                {
                    params->ZoomPanMatrix = ZoomPanTransform::UpdateZoomMatrix_DisplaySizeChanged(
                        oldParams.ZoomPanMatrix, oldParams.ImageDisplaySize, params->ImageDisplaySize);
                }
            }

            bool shallRefreshTexture = false;
            bool shallRefreshRgbaCache = false;
            {
                bool fullRefresh =
                    (      userRefresh
                        || isNewEntry
                        || (cachedImage.GlTexture->mImageSize.x == 0.f)
                        || ShallRefreshRgbaCache(oldParams, *params));
                if (fullRefresh)
                {
                    shallRefreshTexture = true;
                    shallRefreshRgbaCache = true;
                }
                if (ShallRefreshTexture(oldParams, *params))
                    shallRefreshTexture = true;
            }

            if (shallRefreshTexture)
            {
                ImageDrawing::BlitImageTexture(
                    *params, image, cachedImage.ImageRgbaCache, shallRefreshRgbaCache, cachedImage.GlTexture.get());
            }

            if (! ZoomPanTransform::IsEqual(oldParams.ZoomPanMatrix, params->ZoomPanMatrix))
                UpdateLinkedZooms(id_label);
            if (! Colormap::IsEqual(oldParams.ColormapSettings, params->ColormapSettings))
                UpdateLinkedColormapSettings(id_label);

            cachedParams.PreviousParams = *params;
            mCacheImages.ClearOldEntries();

            return isNewEntry;
        }

        KeyType ImageTextureCache::GetID(const std::string& id_label)
        {
            return hash_str(id_label);
        }

        ImageTextureCache::CachedParams& ImageTextureCache::GetCacheParams(const std::string& id_label)
        {
            return mCacheParams.Get(GetID(id_label));
        }
        ImageTextureCache::CachedImages& ImageTextureCache::GetCacheImages(const std::string& id_label)
        {
            return mCacheImages.Get(GetID(id_label));
        }

        void ImageTextureCache::ClearImagesCache()
        {
            mCacheImages.Clear();
        }

        void ImageTextureCache::UpdateLinkedZooms(const std::string& id_label)
        {
            auto currentCacheKey = GetID(id_label);
            auto & currentCache = mCacheParams.Get(currentCacheKey);
            std::string zoomKey = currentCache.ParamsPtr->ZoomKey;
            if (zoomKey.empty())
                return;
            ZoomPanTransform::MatrixType newZoom = currentCache.ParamsPtr->ZoomPanMatrix;
            for (auto& otherCacheKey : mCacheParams.Keys())
            {
                CachedParams & otherCache = mCacheParams.Get(otherCacheKey);
                if ((otherCacheKey != currentCacheKey) && (otherCache.ParamsPtr->ZoomKey == zoomKey))
                    otherCache.ParamsPtr->ZoomPanMatrix = newZoom;
            }
        }
        void ImageTextureCache::UpdateLinkedColormapSettings(const std::string& id_label)
        {
            auto currentCacheKey = GetID(id_label);
            auto & currentCache = mCacheParams.Get(currentCacheKey);
            std::string colormapKey = currentCache.ParamsPtr->ColormapKey;
            if (colormapKey.empty())
                return;
            ColormapSettingsData newColorAdjustments = currentCache.ParamsPtr->ColormapSettings;
            for (auto& otherCacheKey : mCacheParams.Keys())
            {
                CachedParams & otherCache = mCacheParams.Get(otherCacheKey);
                if ((otherCacheKey != currentCacheKey) && (otherCache.ParamsPtr->ColormapKey == colormapKey))
                    otherCache.ParamsPtr->ColormapSettings = newColorAdjustments;
            }
        }


    ImageTextureCache gImageTextureCache;
    } // namespace ImageUtils


} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/imgui/image_widgets.cpp                                         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace ImageWidgets
    {
        cv::Point2d DisplayTexture_TrackMouse(const GlTextureCv& texture, ImVec2 displaySize)
        {
            ImVec2 imageTopLeft = ImGui::GetCursorScreenPos();
            texture.Draw_DisableDragWindow(displaySize);
            bool isImageHovered = ImGui::IsItemHovered();
            ImVec2 mouse = ImGui::GetMousePos();
            if (isImageHovered)
                return cv::Point2d((double)(mouse.x - imageTopLeft.x), (double)(mouse.y - imageTopLeft.y));
            else
                return cv::Point2d(-1., -1.);
        }

        void ShowImageInfo(const cv::Mat &image, double zoomFactor)
        {
            std::string info = MatrixInfoUtils::_MatInfo(image);
            ImGui::Text("%s - Zoom:%.3lf", info.c_str(), zoomFactor);
        }


        void ShowPixelColorWidget(
            const cv::Mat &image,
            cv::Point pt,
            const ImageParams& params)
        {
            bool isInImage = cv::Rect(cv::Point(0, 0), image.size()).contains((pt));
            auto UCharToFloat = [](int v) { return (float)((float) v / 255.f); };
            auto Vec3bToImVec4 = [&UCharToFloat, &params](cv::Vec3b v) {
                return params.IsColorOrderBGR ?
                       ImVec4(UCharToFloat(v[2]), UCharToFloat(v[1]), UCharToFloat(v[0]), UCharToFloat(255))
                                              :   ImVec4(UCharToFloat(v[0]), UCharToFloat(v[1]), UCharToFloat(v[2]), UCharToFloat(255));
            };
            auto Vec4bToImVec4 = [&UCharToFloat, &params](cv::Vec4b v) {
                return params.IsColorOrderBGR ?
                       ImVec4(UCharToFloat(v[2]), UCharToFloat(v[1]), UCharToFloat(v[0]), UCharToFloat(v[3]))
                                              :    ImVec4(UCharToFloat(v[0]), UCharToFloat(v[1]), UCharToFloat(v[2]), UCharToFloat(v[3]));
            };

            bool done = false;
            std::string id = std::string("##pixelcolor_") + std::to_string(pt.x) + "," + std::to_string(pt.y);
            if (image.depth() == CV_8U)
            {
                ImGuiColorEditFlags editFlags =
                    ImGuiColorEditFlags_InputRGB | ImGuiColorEditFlags_AlphaPreviewHalf
                    | ImGuiColorEditFlags_DisplayRGB | ImGuiColorEditFlags_Uint8;
                if (!isInImage)
                {
                    // ColorEdit4 introduces a strange line spacing on the next group
                    // which cannot be simulated with ImGui::Dummy
                    // => we add a dummy one (hopefully black on a black background)
                    float dummyColor[4]{0.f, 0.f, 0.f, 255.f};
                    ImGui::SetNextItemWidth(1.f);
                    int colorEditFlags =
                        ImGuiColorEditFlags_NoInputs
                        | ImGuiColorEditFlags_InputRGB
                        | ImGuiColorEditFlags_DisplayRGB;
                    ImGui::ColorEdit4(id.c_str(), dummyColor, colorEditFlags );
                    done = true;
                }
                else if (image.channels() == 3)
                {
                    cv::Vec3b col = image.at<cv::Vec3b>(pt.y, pt.x);
                    ImVec4 colorAsImVec = Vec3bToImVec4(col);
                    ImGui::SetNextItemWidth(150.f);
                    ImGui::ColorEdit3(id.c_str(), (float*)&colorAsImVec, editFlags);
                    done = true;
                }
                else if (image.channels() == 4)
                {
                    cv::Vec4b col = image.at<cv::Vec4b>(pt.y, pt.x);
                    ImVec4 colorAsImVec = Vec4bToImVec4(col);
                    ImGui::SetNextItemWidth(200.f);
                    ImGui::ColorEdit4(id.c_str(), (float*)&colorAsImVec, editFlags);
                    done = true;
                }
            }
            if (! done)
            {
                std::string pixelInfo = MatrixInfoUtils::MatPixelColorInfo(image, pt.x, pt.y);
                ImGui::Text("%s", pixelInfo.c_str());
            }
        }


        // If true, the collapsing headers will be synced across instances
        bool s_CollapsingHeader_CacheState_Sync = false;

        bool CollapsingHeader_OptionalCacheState(const char *name, bool forceOpen)
        {
            static std::map<std::string, bool> collapsingHeadersState;
            bool shallOpen = forceOpen;
            if (s_CollapsingHeader_CacheState_Sync)
            {
                if (collapsingHeadersState.find(name) != collapsingHeadersState.end())
                {
                    bool wasOpenedLastTime = collapsingHeadersState.at(name);
                    if (wasOpenedLastTime)
                        shallOpen = true;
                }
            }
            if (shallOpen)
                ImGui::SetNextItemOpen(shallOpen, ImGuiCond_Always);
            bool opened = ImGui::CollapsingHeader(name);
            collapsingHeadersState[name] = opened;
            return opened;
        };

    } // namespace ImageWidgets

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/imgui/imgui_imm.cpp                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define IMGUI_DEFINE_MATH_OPERATORS

#include <sstream>
#include <stack>

namespace ImGuiImm
{
    template<typename AnyFloat>
    bool SliderAnyFloat(
        const char*label,
        AnyFloat* v,
        AnyFloat v_min,
        AnyFloat v_max,
        float width,
        bool logarithmic,
        int nb_decimals)
    {
        float vf = (float)*v;
        std::string formatString = std::string("%.") + std::to_string(nb_decimals) + "f";
        ImGui::SetNextItemWidth(width);
        ImGuiSliderFlags flags = 0;
        if (logarithmic)
            flags |= ImGuiSliderFlags_Logarithmic;
        bool changed = ImGui::SliderFloat(label, &vf, (float)v_min, (float)v_max, formatString.c_str(), flags);
        if (changed)
            *v = (AnyFloat)vf;
        return changed;
    }

#define EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT(AnyFloat)                       \
    template bool SliderAnyFloat<AnyFloat>(                                     \
    const char*label, AnyFloat* v, AnyFloat v_min, AnyFloat v_max, float width, \
    bool logarithmic, int nb_decimals);

    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT(float);
    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT(double);
    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT(long double);


    template<typename AnyFloat>
    bool SliderAnyFloatLogarithmic(
        const char*label,
        AnyFloat* v,
        AnyFloat v_min,
        AnyFloat v_max,
        float width,
        int nb_decimals)
    {
        return SliderAnyFloat(label, v, v_min, v_max, width, true, nb_decimals);
    }

#define EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT_LOGARITHMIC(AnyFloat)                   \
    template bool SliderAnyFloatLogarithmic<AnyFloat>(                                  \
    const char*label, AnyFloat* v, AnyFloat v_min, AnyFloat v_max, float width,         \
    int nb_decimals);

    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT_LOGARITHMIC(float);
    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT_LOGARITHMIC(double);
    EXPLICIT_INSTANTIATION_SLIDER_ANY_FLOAT_LOGARITHMIC(long double);


    ImVec2 ComputeDisplayImageSize(
        ImVec2 askedImageSize,
        ImVec2 realImageSize
    )
    {
        if ((askedImageSize.x == 0.f) && (askedImageSize.y == 0.f))
            return realImageSize;
        else if ((askedImageSize.x == 0.f) && (realImageSize.y >= 1.f))
            return ImVec2(askedImageSize.y * realImageSize.x / realImageSize.y, askedImageSize.y);
        else if ((askedImageSize.y == 0.f) && (realImageSize.x >= 1.f))
            return ImVec2(askedImageSize.x, askedImageSize.x * realImageSize.y / realImageSize.x);
        else
            return askedImageSize;
    }
    cv::Size ComputeDisplayImageSize(cv::Size askedImageSize, cv::Size realImageSize)
    {
        auto toSize = [](ImVec2 v) { return cv::Size((int)((double)v.x + 0.5), (int)((double)v.y + 0.5)); };
        auto toImVec2 = [](cv::Size v) { return ImVec2((float)v.width, (float)v.height); };
        return toSize( ComputeDisplayImageSize(toImVec2(askedImageSize), toImVec2(realImageSize)) );
    }

    void PushDisabled()
    {
        ImGui::PushItemFlag(ImGuiItemFlags_Disabled, true);
        ImGui::PushStyleVar(ImGuiStyleVar_Alpha, ImGui::GetStyle().Alpha * 0.7f);

    }
    void PopDisabled()
    {
        ImGui::PopStyleVar();
        ImGui::PopItemFlag();
    }

    void SameLineAlignRight(float rightMargin, float alignRegionWidth)
    {
        auto window = ImGui::GetCurrentWindow();
        if (alignRegionWidth < 0.f)
            alignRegionWidth = window->Size.x;

        // Formulas taken from ImGui::ItemSize() code
        float xLineStart = IM_FLOOR(window->Pos.x + window->DC.Indent.x + window->DC.ColumnsOffset.x);
        float y = window->DC.CursorPosPrevLine.y;

        float x = xLineStart + alignRegionWidth - rightMargin;
        ImGui::SetCursorScreenPos({x, y});
    }



    // cf https://github.com/ocornut/imgui/issues/1496#issuecomment-655048353
    static ImVector<ImRect> s_GroupPanelLabelStack;
    void BeginGroupPanel(const char* name, const ImVec2& size)
    {
        ImGui::BeginGroup();

        auto itemSpacing = ImGui::GetStyle().ItemSpacing;
        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(0.0f, 0.0f));
        ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(0.0f, 0.0f));

        auto frameHeight = ImGui::GetFrameHeight();
        ImGui::BeginGroup();

        ImVec2 effectiveSize = size;
        if (size.x < 0.0f)
            effectiveSize.x = ImGui::GetWindowContentRegionWidth();
        else
            effectiveSize.x = size.x;
        ImGui::Dummy(ImVec2(effectiveSize.x, 0.0f));

        ImGui::Dummy(ImVec2(frameHeight * 0.5f, 0.0f));
        ImGui::SameLine(0.0f, 0.0f);
        ImGui::BeginGroup();
        ImGui::Dummy(ImVec2(frameHeight * 0.5f, 0.0f));
        ImGui::SameLine(0.0f, 0.0f);
        if (strlen(name) > 0)
            ImGui::TextUnformatted(name);

        auto labelMin = ImGui::GetItemRectMin();
        auto labelMax = ImGui::GetItemRectMax();
        ImGui::SameLine(0.0f, 0.0f);
        ImGui::Dummy(ImVec2(0.0, frameHeight + itemSpacing.y));
        ImGui::BeginGroup();

        //ImGui::GetWindowDrawList()->AddRect(labelMin, labelMax, IM_COL32(255, 0, 255, 255));

        ImGui::PopStyleVar(2);

#if IMGUI_VERSION_NUM >= 17301
        ImGui::GetCurrentWindow()->ContentRegionRect.Max.x -= frameHeight * 0.5f;
        ImGui::GetCurrentWindow()->WorkRect.Max.x          -= frameHeight * 0.5f;
        ImGui::GetCurrentWindow()->InnerRect.Max.x         -= frameHeight * 0.5f;
#else
        ImGui::GetCurrentWindow()->ContentsRegionRect.Max.x -= frameHeight * 0.5f;
#endif
        ImGui::GetCurrentWindow()->Size.x                   -= frameHeight;

        auto itemWidth = ImGui::CalcItemWidth();
        ImGui::PushItemWidth(ImMax(0.0f, itemWidth - frameHeight));

        s_GroupPanelLabelStack.push_back(ImRect(labelMin, labelMax));
    }

    void EndGroupPanel()
    {
        ImGui::PopItemWidth();

        auto itemSpacing = ImGui::GetStyle().ItemSpacing;

        ImGui::PushStyleVar(ImGuiStyleVar_FramePadding, ImVec2(0.0f, 0.0f));
        ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(0.0f, 0.0f));

        auto frameHeight = ImGui::GetFrameHeight();

        ImGui::EndGroup();

        //ImGui::GetWindowDrawList()->AddRectFilled(ImGui::GetItemRectMin(), ImGui::GetItemRectMax(), IM_COL32(0, 255, 0, 64), 4.0f);

        ImGui::EndGroup();

        ImGui::SameLine(0.0f, 0.0f);
        ImGui::Dummy(ImVec2(frameHeight * 0.5f, 0.0f));
        ImGui::Dummy(ImVec2(0.0, frameHeight - frameHeight * 0.5f - itemSpacing.y));

        ImGui::EndGroup();

        auto itemMin = ImGui::GetItemRectMin();
        auto itemMax = ImGui::GetItemRectMax();
        //ImGui::GetWindowDrawList()->AddRectFilled(itemMin, itemMax, IM_COL32(255, 0, 0, 64), 4.0f);

        auto labelRect = s_GroupPanelLabelStack.back();
        s_GroupPanelLabelStack.pop_back();

        ImVec2 halfFrame = ImVec2(frameHeight * 0.25f * 0.5f, frameHeight * 0.5f);
        ImRect frameRect = ImRect(ImVec2(itemMin.x + halfFrame.x, itemMin.y + halfFrame.y), ImVec2(itemMax.x - halfFrame.x, itemMax.y));
        labelRect.Min.x -= itemSpacing.x;
        labelRect.Max.x += itemSpacing.x;

        for (int i = 0; i < 4; ++i)
        {
            switch (i)
            {
                // left half-plane
                case 0: ImGui::PushClipRect(ImVec2(-FLT_MAX, -FLT_MAX), ImVec2(labelRect.Min.x, FLT_MAX), true); break;
                    // right half-plane
                case 1: ImGui::PushClipRect(ImVec2(labelRect.Max.x, -FLT_MAX), ImVec2(FLT_MAX, FLT_MAX), true); break;
                    // top
                case 2: ImGui::PushClipRect(ImVec2(labelRect.Min.x, -FLT_MAX), ImVec2(labelRect.Max.x, labelRect.Min.y), true); break;
                    // bottom
                case 3: ImGui::PushClipRect(ImVec2(labelRect.Min.x, labelRect.Max.y), ImVec2(labelRect.Max.x, FLT_MAX), true); break;
            }

            ImGui::GetWindowDrawList()->AddRect(
                frameRect.Min, frameRect.Max,
                ImColor(ImGui::GetStyleColorVec4(ImGuiCol_Border)),
                halfFrame.x);

            ImGui::PopClipRect();
        }

        ImGui::PopStyleVar(2);

#if IMGUI_VERSION_NUM >= 17301
        ImGui::GetCurrentWindow()->ContentRegionRect.Max.x += frameHeight * 0.5f;
        ImGui::GetCurrentWindow()->WorkRect.Max.x          += frameHeight * 0.5f;
        ImGui::GetCurrentWindow()->InnerRect.Max.x         += frameHeight * 0.5f;
#else
        ImGui::GetCurrentWindow()->ContentsRegionRect.Max.x += frameHeight * 0.5f;
#endif
        ImGui::GetCurrentWindow()->Size.x                   += frameHeight;

        ImGui::Dummy(ImVec2(0.0f, 0.0f));

        ImGui::EndGroup();
    }


    static std::stack<bool> s_GroupPanel_FlagBorder_DrawBorder;
    static std::stack<std::string> s_GroupPanel_FlagBorder_Names;
    static std::unordered_map<std::string, ImVec2> s_GroupPanel_FlagBorder_Sizes;

    void BeginGroupPanel_FlagBorder(const char* name, bool draw_border, const ImVec2& size)
    {
        std::string name_s(name);
        std::string name_displayed;
        {
            auto pos = name_s.find("##");
            if (pos != std::string::npos)
                name_displayed =  name_s.substr(0, pos);
            else
                name_displayed = name_s;
        }

        ImGui::BeginGroup();
        s_GroupPanel_FlagBorder_DrawBorder.push(draw_border);
        s_GroupPanel_FlagBorder_Names.push(name);
        if (draw_border)
            BeginGroupPanel(name_displayed.c_str(), size);
        else
        {
            ImGui::BeginGroup();
            if (strlen(name) > 0)
                ImGui::Text("%s", name_displayed.c_str());
        }
    }

    void EndGroupPanel_FlagBorder()
    {
        bool drawBorder = s_GroupPanel_FlagBorder_DrawBorder.top();
        s_GroupPanel_FlagBorder_DrawBorder.pop();
        if (drawBorder)
            EndGroupPanel();
        else
            ImGui::EndGroup();

        ImGui::EndGroup();

        // Store size
        {
            std::string name = s_GroupPanel_FlagBorder_Names.top();
            s_GroupPanel_FlagBorder_Names.pop();
            s_GroupPanel_FlagBorder_Sizes[name] = ImGui::GetItemRectSize();
        }
    }

    ImVec2 GroupPanel_FlagBorder_LastKnownSize(const char* name)
    {
        if (s_GroupPanel_FlagBorder_Sizes.find(name) == s_GroupPanel_FlagBorder_Sizes.end())
            return ImVec2(3.f, 3.f);
        else
            return s_GroupPanel_FlagBorder_Sizes.at(name);
    }

    std::stack<ImRect> s_OldWorkRects;
    void BeginGroupFixedWidth(float width)
    {
        ImGui::BeginGroup();
        ImGui::Dummy(ImVec2(width, 1.f));
        ImRect oldWorkRect = ImGui::GetCurrentWindow()->WorkRect;
        {
            ImRect newRect = oldWorkRect;
            newRect.Max.x = ImGui::GetCursorScreenPos().x + width - ImGui::GetStyle().ItemSpacing.x;
            ImGui::GetCurrentWindow()->WorkRect = newRect;
            s_OldWorkRects.push(oldWorkRect);
        }
    }

    void EndGroupFixedWidth()
    {
        ImGui::EndGroup();
        assert(!s_OldWorkRects.empty());
        ImRect oldWorkRect = s_OldWorkRects.top();
        s_OldWorkRects.pop();
        ImGui::GetCurrentWindow()->WorkRect = oldWorkRect;
    }

    // Draw a fixed width Separator
    // useful when ImGui::Separator() overflows to the right
    void SeparatorFixedWidth(float width)
    {
        ImVec2 a = ImGui::GetCursorScreenPos();
        a.y += 4.f;
        ImVec2 b = a;
        b.x += width;
        auto col = ImGui::GetStyle().Colors[ImGuiCol_Separator];
        ImGui::GetWindowDrawList()->AddLine(a, b, ImGui::GetColorU32(col), 1.f);
        ImGui::NewLine();
    }

    void Theme_Debug()
    {
        ImGuiStyle &style = ImGui::GetStyle();
        style.Colors[ImGuiCol_Text] = ImVec4(0.90f, 0.90f, 0.90f, 1.00f);
        style.Colors[ImGuiCol_TextDisabled] = ImVec4(0.60f, 0.60f, 0.60f, 1.00f);
        style.Colors[ImGuiCol_WindowBg] = ImVec4(0.21f, 0.25f, 0.21f, 0.70f);
        style.Colors[ImGuiCol_PopupBg] = ImVec4(0.05f, 0.05f, 0.10f, 0.90f);
        style.Colors[ImGuiCol_Border] = ImVec4(0.70f, 0.70f, 0.70f, 0.40f);
        style.Colors[ImGuiCol_BorderShadow] = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        style.Colors[ImGuiCol_FrameBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.30f);
        style.Colors[ImGuiCol_FrameBgHovered] = ImVec4(0.90f, 0.80f, 0.80f, 0.40f);
        style.Colors[ImGuiCol_FrameBgActive] = ImVec4(0.65f, 0.90f, 0.70f, 0.45f);
        style.Colors[ImGuiCol_TitleBg] = ImVec4(0.27f, 0.54f, 0.28f, 0.83f);
        style.Colors[ImGuiCol_TitleBgCollapsed] = ImVec4(0.40f, 0.80f, 0.43f, 0.20f);
        style.Colors[ImGuiCol_TitleBgActive] = ImVec4(0.32f, 0.63f, 0.33f, 0.87f);
        style.Colors[ImGuiCol_MenuBarBg] = ImVec4(0.40f, 0.55f, 0.45f, 0.80f);
        style.Colors[ImGuiCol_ScrollbarBg] = ImVec4(0.20f, 0.25f, 0.30f, 0.60f);
        style.Colors[ImGuiCol_ScrollbarGrab] = ImVec4(0.40f, 0.80f, 0.53f, 0.30f);
        style.Colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.40f, 0.80f, 0.48f, 0.40f);
        style.Colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(0.50f, 0.80f, 0.54f, 0.40f);
        style.Colors[ImGuiCol_CheckMark] = ImVec4(0.90f, 0.90f, 0.90f, 0.50f);
        style.Colors[ImGuiCol_SliderGrab] = ImVec4(1.00f, 1.00f, 1.00f, 0.30f);
        style.Colors[ImGuiCol_SliderGrabActive] = ImVec4(0.80f, 0.50f, 0.50f, 1.00f);
        style.Colors[ImGuiCol_Button] = ImVec4(0.40f, 0.67f, 0.47f, 0.60f);
        style.Colors[ImGuiCol_ButtonHovered] = ImVec4(0.40f, 0.50f, 0.67f, 1.00f);
        style.Colors[ImGuiCol_ButtonActive] = ImVec4(0.05f, 0.20f, 0.51f, 1.00f);
        style.Colors[ImGuiCol_Header] = ImVec4(0.38f, 0.76f, 0.17f, 0.45f);
        style.Colors[ImGuiCol_HeaderHovered] = ImVec4(0.45f, 0.90f, 0.47f, 0.80f);
        style.Colors[ImGuiCol_HeaderActive] = ImVec4(0.55f, 0.87f, 0.53f, 0.80f);
        style.Colors[ImGuiCol_Separator] = ImVec4(0.50f, 0.50f, 0.50f, 1.00f);
        style.Colors[ImGuiCol_SeparatorHovered] = ImVec4(0.60f, 0.60f, 0.70f, 1.00f);
        style.Colors[ImGuiCol_SeparatorActive] = ImVec4(0.70f, 0.70f, 0.90f, 1.00f);
        style.Colors[ImGuiCol_ResizeGrip] = ImVec4(1.00f, 1.00f, 1.00f, 0.30f);
        style.Colors[ImGuiCol_ResizeGripHovered] = ImVec4(1.00f, 1.00f, 1.00f, 0.60f);
        style.Colors[ImGuiCol_ResizeGripActive] = ImVec4(1.00f, 1.00f, 1.00f, 0.90f);
        style.Colors[ImGuiCol_PlotLines] = ImVec4(1.00f, 1.00f, 1.00f, 1.00f);
        style.Colors[ImGuiCol_PlotLinesHovered] = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogram] = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogramHovered] = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_TextSelectedBg] = ImVec4(0.00f, 0.00f, 1.00f, 0.35f);
    }


    // Theme CorporateGrey: https://github.com/ocornut/imgui/issues/707#issuecomment-468798935
    void Theme_CorporateGrey()
    {
        ImGuiStyle & style = ImGui::GetStyle();
        ImVec4 * colors = style.Colors;

        /// 0 = FLAT APPEARENCE
        /// 1 = MORE "3D" LOOK
        int is3D = 0;

        colors[ImGuiCol_Text]                   = ImVec4(1.00f, 1.00f, 1.00f, 1.00f);
        colors[ImGuiCol_TextDisabled]           = ImVec4(0.40f, 0.40f, 0.40f, 1.00f);
        colors[ImGuiCol_ChildBg]                = ImVec4(0.25f, 0.25f, 0.25f, 1.00f);
        colors[ImGuiCol_WindowBg]               = ImVec4(0.25f, 0.25f, 0.25f, 1.00f);
        colors[ImGuiCol_PopupBg]                = ImVec4(0.25f, 0.25f, 0.25f, 1.00f);
        colors[ImGuiCol_Border]                 = ImVec4(0.12f, 0.12f, 0.12f, 0.71f);
        colors[ImGuiCol_BorderShadow]           = ImVec4(1.00f, 1.00f, 1.00f, 0.06f);
        colors[ImGuiCol_FrameBg]                = ImVec4(0.42f, 0.42f, 0.42f, 0.54f);
        colors[ImGuiCol_FrameBgHovered]         = ImVec4(0.42f, 0.42f, 0.42f, 0.40f);
        colors[ImGuiCol_FrameBgActive]          = ImVec4(0.56f, 0.56f, 0.56f, 0.67f);
        colors[ImGuiCol_TitleBg]                = ImVec4(0.19f, 0.19f, 0.19f, 1.00f);
        colors[ImGuiCol_TitleBgActive]          = ImVec4(0.22f, 0.22f, 0.22f, 1.00f);
        colors[ImGuiCol_TitleBgCollapsed]       = ImVec4(0.17f, 0.17f, 0.17f, 0.90f);
        colors[ImGuiCol_MenuBarBg]              = ImVec4(0.335f, 0.335f, 0.335f, 1.000f);
        colors[ImGuiCol_ScrollbarBg]            = ImVec4(0.24f, 0.24f, 0.24f, 0.53f);
        colors[ImGuiCol_ScrollbarGrab]          = ImVec4(0.41f, 0.41f, 0.41f, 1.00f);
        colors[ImGuiCol_ScrollbarGrabHovered]   = ImVec4(0.52f, 0.52f, 0.52f, 1.00f);
        colors[ImGuiCol_ScrollbarGrabActive]    = ImVec4(0.76f, 0.76f, 0.76f, 1.00f);
        colors[ImGuiCol_CheckMark]              = ImVec4(0.65f, 0.65f, 0.65f, 1.00f);
        colors[ImGuiCol_SliderGrab]             = ImVec4(0.52f, 0.52f, 0.52f, 1.00f);
        colors[ImGuiCol_SliderGrabActive]       = ImVec4(0.64f, 0.64f, 0.64f, 1.00f);
        colors[ImGuiCol_Button]                 = ImVec4(0.54f, 0.54f, 0.54f, 0.35f);
        colors[ImGuiCol_ButtonHovered]          = ImVec4(0.52f, 0.52f, 0.52f, 0.59f);
        colors[ImGuiCol_ButtonActive]           = ImVec4(0.76f, 0.76f, 0.76f, 1.00f);
        colors[ImGuiCol_Header]                 = ImVec4(0.38f, 0.38f, 0.38f, 1.00f);
        colors[ImGuiCol_HeaderHovered]          = ImVec4(0.47f, 0.47f, 0.47f, 1.00f);
        colors[ImGuiCol_HeaderActive]           = ImVec4(0.76f, 0.76f, 0.76f, 0.77f);
        colors[ImGuiCol_Separator]              = ImVec4(0.000f, 0.000f, 0.000f, 0.137f);
        colors[ImGuiCol_SeparatorHovered]       = ImVec4(0.700f, 0.671f, 0.600f, 0.290f);
        colors[ImGuiCol_SeparatorActive]        = ImVec4(0.702f, 0.671f, 0.600f, 0.674f);
        colors[ImGuiCol_ResizeGrip]             = ImVec4(0.26f, 0.59f, 0.98f, 0.25f);
        colors[ImGuiCol_ResizeGripHovered]      = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        colors[ImGuiCol_ResizeGripActive]       = ImVec4(0.26f, 0.59f, 0.98f, 0.95f);
        colors[ImGuiCol_PlotLines]              = ImVec4(0.61f, 0.61f, 0.61f, 1.00f);
        colors[ImGuiCol_PlotLinesHovered]       = ImVec4(1.00f, 0.43f, 0.35f, 1.00f);
        colors[ImGuiCol_PlotHistogram]          = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotHistogramHovered]   = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
        colors[ImGuiCol_TextSelectedBg]         = ImVec4(0.73f, 0.73f, 0.73f, 0.35f);
        colors[ImGuiCol_ModalWindowDimBg]       = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);
        colors[ImGuiCol_DragDropTarget]         = ImVec4(1.00f, 1.00f, 0.00f, 0.90f);
        colors[ImGuiCol_NavHighlight]           = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        colors[ImGuiCol_NavWindowingHighlight]  = ImVec4(1.00f, 1.00f, 1.00f, 0.70f);
        colors[ImGuiCol_NavWindowingDimBg]      = ImVec4(0.80f, 0.80f, 0.80f, 0.20f);

        style.PopupRounding = 3;

        style.WindowPadding = ImVec2(4, 4);
        style.FramePadding  = ImVec2(6, 4);
        style.ItemSpacing   = ImVec2(6, 2);

        style.ScrollbarSize = 18;

        style.WindowBorderSize = 1;
        style.ChildBorderSize  = 1;
        style.PopupBorderSize  = 1;
        style.FrameBorderSize  = (float)is3D;

        style.WindowRounding    = 3;
        style.ChildRounding     = 3;
        style.FrameRounding     = 3;
        style.ScrollbarRounding = 2;
        style.GrabRounding      = 3;

#ifdef IMGUI_HAS_DOCK
        style.TabBorderSize = (float)is3D;
        style.TabRounding   = 3;

        colors[ImGuiCol_DockingEmptyBg]     = ImVec4(0.38f, 0.38f, 0.38f, 1.00f);
        colors[ImGuiCol_Tab]                = ImVec4(0.25f, 0.25f, 0.25f, 1.00f);
        colors[ImGuiCol_TabHovered]         = ImVec4(0.40f, 0.40f, 0.40f, 1.00f);
        colors[ImGuiCol_TabActive]          = ImVec4(0.33f, 0.33f, 0.33f, 1.00f);
        colors[ImGuiCol_TabUnfocused]       = ImVec4(0.25f, 0.25f, 0.25f, 1.00f);
        colors[ImGuiCol_TabUnfocusedActive] = ImVec4(0.33f, 0.33f, 0.33f, 1.00f);
        colors[ImGuiCol_DockingPreview]     = ImVec4(0.85f, 0.85f, 0.85f, 0.28f);

        if (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_ViewportsEnable)
        {
            style.WindowRounding = 0.0f;
            style.Colors[ImGuiCol_WindowBg].w = 1.0f;
        }
#endif
    }

    void Theme_Dark()
    {
        //ImGui::GetIO().Fonts->AddFontFromFileTTF("../data/Fonts/Ruda-Bold.ttf", 15.0f, &config);
        ImGui::GetStyle().FrameRounding = 4.0f;
        ImGui::GetStyle().GrabRounding = 4.0f;

        ImVec4* colors = ImGui::GetStyle().Colors;
        colors[ImGuiCol_Text] = ImVec4(0.95f, 0.96f, 0.98f, 1.00f);
        colors[ImGuiCol_TextDisabled] = ImVec4(0.36f, 0.42f, 0.47f, 1.00f);
        colors[ImGuiCol_WindowBg] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
        colors[ImGuiCol_ChildBg] = ImVec4(0.15f, 0.18f, 0.22f, 1.00f);
        colors[ImGuiCol_PopupBg] = ImVec4(0.08f, 0.08f, 0.08f, 0.94f);
        colors[ImGuiCol_Border] = ImVec4(0.08f, 0.10f, 0.12f, 1.00f);
        colors[ImGuiCol_BorderShadow] = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        colors[ImGuiCol_FrameBg] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
        colors[ImGuiCol_FrameBgHovered] = ImVec4(0.12f, 0.20f, 0.28f, 1.00f);
        colors[ImGuiCol_FrameBgActive] = ImVec4(0.09f, 0.12f, 0.14f, 1.00f);
        colors[ImGuiCol_TitleBg] = ImVec4(0.09f, 0.12f, 0.14f, 0.65f);
        colors[ImGuiCol_TitleBgActive] = ImVec4(0.08f, 0.10f, 0.12f, 1.00f);
        colors[ImGuiCol_TitleBgCollapsed] = ImVec4(0.00f, 0.00f, 0.00f, 0.51f);
        colors[ImGuiCol_MenuBarBg] = ImVec4(0.15f, 0.18f, 0.22f, 1.00f);
        colors[ImGuiCol_ScrollbarBg] = ImVec4(0.02f, 0.02f, 0.02f, 0.39f);
        colors[ImGuiCol_ScrollbarGrab] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
        colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.18f, 0.22f, 0.25f, 1.00f);
        colors[ImGuiCol_ScrollbarGrabActive] = ImVec4(0.09f, 0.21f, 0.31f, 1.00f);
        colors[ImGuiCol_CheckMark] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
        colors[ImGuiCol_SliderGrab] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
        colors[ImGuiCol_SliderGrabActive] = ImVec4(0.37f, 0.61f, 1.00f, 1.00f);
        colors[ImGuiCol_Button] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
        colors[ImGuiCol_ButtonHovered] = ImVec4(0.28f, 0.56f, 1.00f, 1.00f);
        colors[ImGuiCol_ButtonActive] = ImVec4(0.06f, 0.53f, 0.98f, 1.00f);
        colors[ImGuiCol_Header] = ImVec4(0.20f, 0.25f, 0.29f, 0.55f);
        colors[ImGuiCol_HeaderHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
        colors[ImGuiCol_HeaderActive] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        colors[ImGuiCol_Separator] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
        colors[ImGuiCol_SeparatorHovered] = ImVec4(0.10f, 0.40f, 0.75f, 0.78f);
        colors[ImGuiCol_SeparatorActive] = ImVec4(0.10f, 0.40f, 0.75f, 1.00f);
        colors[ImGuiCol_ResizeGrip] = ImVec4(0.26f, 0.59f, 0.98f, 0.25f);
        colors[ImGuiCol_ResizeGripHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        colors[ImGuiCol_ResizeGripActive] = ImVec4(0.26f, 0.59f, 0.98f, 0.95f);
        colors[ImGuiCol_Tab] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
        colors[ImGuiCol_TabHovered] = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
        colors[ImGuiCol_TabActive] = ImVec4(0.20f, 0.25f, 0.29f, 1.00f);
        colors[ImGuiCol_TabUnfocused] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
        colors[ImGuiCol_TabUnfocusedActive] = ImVec4(0.11f, 0.15f, 0.17f, 1.00f);
        colors[ImGuiCol_PlotLines] = ImVec4(0.61f, 0.61f, 0.61f, 1.00f);
        colors[ImGuiCol_PlotLinesHovered] = ImVec4(1.00f, 0.43f, 0.35f, 1.00f);
        colors[ImGuiCol_PlotHistogram] = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotHistogramHovered] = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
        colors[ImGuiCol_TextSelectedBg] = ImVec4(0.26f, 0.59f, 0.98f, 0.35f);
        colors[ImGuiCol_DragDropTarget] = ImVec4(1.00f, 1.00f, 0.00f, 0.90f);
        colors[ImGuiCol_NavHighlight] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        colors[ImGuiCol_NavWindowingHighlight] = ImVec4(1.00f, 1.00f, 1.00f, 0.70f);
        colors[ImGuiCol_NavWindowingDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.20f);
        colors[ImGuiCol_ModalWindowDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);

    }

    void Theme_EmbraceTheDarkness()
    {
        ImVec4* colors = ImGui::GetStyle().Colors;
        colors[ImGuiCol_Text]                   = ImVec4(1.00f, 1.00f, 1.00f, 1.00f);
        colors[ImGuiCol_TextDisabled]           = ImVec4(0.50f, 0.50f, 0.50f, 1.00f);
        colors[ImGuiCol_WindowBg]               = ImVec4(0.10f, 0.10f, 0.10f, 1.00f);
        colors[ImGuiCol_ChildBg]                = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        colors[ImGuiCol_PopupBg]                = ImVec4(0.19f, 0.19f, 0.19f, 0.92f);
        colors[ImGuiCol_Border]                 = ImVec4(0.19f, 0.19f, 0.19f, 0.29f);
        colors[ImGuiCol_BorderShadow]           = ImVec4(0.00f, 0.00f, 0.00f, 0.24f);
        colors[ImGuiCol_FrameBg]                = ImVec4(0.05f, 0.05f, 0.05f, 0.54f);
        colors[ImGuiCol_FrameBgHovered]         = ImVec4(0.19f, 0.19f, 0.19f, 0.54f);
        colors[ImGuiCol_FrameBgActive]          = ImVec4(0.20f, 0.22f, 0.23f, 1.00f);
        colors[ImGuiCol_TitleBg]                = ImVec4(0.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_TitleBgActive]          = ImVec4(0.06f, 0.06f, 0.06f, 1.00f);
        colors[ImGuiCol_TitleBgCollapsed]       = ImVec4(0.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_MenuBarBg]              = ImVec4(0.14f, 0.14f, 0.14f, 1.00f);
        colors[ImGuiCol_ScrollbarBg]            = ImVec4(0.05f, 0.05f, 0.05f, 0.54f);
        colors[ImGuiCol_ScrollbarGrab]          = ImVec4(0.34f, 0.34f, 0.34f, 0.54f);
        colors[ImGuiCol_ScrollbarGrabHovered]   = ImVec4(0.40f, 0.40f, 0.40f, 0.54f);
        colors[ImGuiCol_ScrollbarGrabActive]    = ImVec4(0.56f, 0.56f, 0.56f, 0.54f);
        colors[ImGuiCol_CheckMark]              = ImVec4(0.33f, 0.67f, 0.86f, 1.00f);
        colors[ImGuiCol_SliderGrab]             = ImVec4(0.34f, 0.34f, 0.34f, 0.54f);
        colors[ImGuiCol_SliderGrabActive]       = ImVec4(0.56f, 0.56f, 0.56f, 0.54f);
        colors[ImGuiCol_Button]                 = ImVec4(0.05f, 0.05f, 0.05f, 0.54f);
        colors[ImGuiCol_ButtonHovered]          = ImVec4(0.19f, 0.19f, 0.19f, 0.54f);
        colors[ImGuiCol_ButtonActive]           = ImVec4(0.20f, 0.22f, 0.23f, 1.00f);
        colors[ImGuiCol_Header]                 = ImVec4(0.00f, 0.00f, 0.00f, 0.52f);
        colors[ImGuiCol_HeaderHovered]          = ImVec4(0.00f, 0.00f, 0.00f, 0.36f);
        colors[ImGuiCol_HeaderActive]           = ImVec4(0.20f, 0.22f, 0.23f, 0.33f);
        colors[ImGuiCol_Separator]              = ImVec4(0.28f, 0.28f, 0.28f, 0.29f);
        colors[ImGuiCol_SeparatorHovered]       = ImVec4(0.44f, 0.44f, 0.44f, 0.29f);
        colors[ImGuiCol_SeparatorActive]        = ImVec4(0.40f, 0.44f, 0.47f, 1.00f);
        colors[ImGuiCol_ResizeGrip]             = ImVec4(0.28f, 0.28f, 0.28f, 0.29f);
        colors[ImGuiCol_ResizeGripHovered]      = ImVec4(0.44f, 0.44f, 0.44f, 0.29f);
        colors[ImGuiCol_ResizeGripActive]       = ImVec4(0.40f, 0.44f, 0.47f, 1.00f);
        colors[ImGuiCol_Tab]                    = ImVec4(0.00f, 0.00f, 0.00f, 0.52f);
        colors[ImGuiCol_TabHovered]             = ImVec4(0.14f, 0.14f, 0.14f, 1.00f);
        colors[ImGuiCol_TabActive]              = ImVec4(0.20f, 0.20f, 0.20f, 0.36f);
        colors[ImGuiCol_TabUnfocused]           = ImVec4(0.00f, 0.00f, 0.00f, 0.52f);
        colors[ImGuiCol_TabUnfocusedActive]     = ImVec4(0.14f, 0.14f, 0.14f, 1.00f);
        colors[ImGuiCol_DockingPreview]         = ImVec4(0.33f, 0.67f, 0.86f, 1.00f);
        colors[ImGuiCol_DockingEmptyBg]         = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotLines]              = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotLinesHovered]       = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotHistogram]          = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_PlotHistogramHovered]   = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_TableHeaderBg]          = ImVec4(0.00f, 0.00f, 0.00f, 0.52f);
        colors[ImGuiCol_TableBorderStrong]      = ImVec4(0.00f, 0.00f, 0.00f, 0.52f);
        colors[ImGuiCol_TableBorderLight]       = ImVec4(0.28f, 0.28f, 0.28f, 0.29f);
        colors[ImGuiCol_TableRowBg]             = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        colors[ImGuiCol_TableRowBgAlt]          = ImVec4(1.00f, 1.00f, 1.00f, 0.06f);
        colors[ImGuiCol_TextSelectedBg]         = ImVec4(0.20f, 0.22f, 0.23f, 1.00f);
        colors[ImGuiCol_DragDropTarget]         = ImVec4(0.33f, 0.67f, 0.86f, 1.00f);
        colors[ImGuiCol_NavHighlight]           = ImVec4(1.00f, 0.00f, 0.00f, 1.00f);
        colors[ImGuiCol_NavWindowingHighlight]  = ImVec4(1.00f, 0.00f, 0.00f, 0.70f);
        colors[ImGuiCol_NavWindowingDimBg]      = ImVec4(1.00f, 0.00f, 0.00f, 0.20f);
        colors[ImGuiCol_ModalWindowDimBg]       = ImVec4(1.00f, 0.00f, 0.00f, 0.35f);

        ImGuiStyle& style = ImGui::GetStyle();
        style.WindowPadding                     = ImVec2(8.00f, 8.00f);
        style.FramePadding                      = ImVec2(5.00f, 2.00f);
        style.CellPadding                       = ImVec2(6.00f, 6.00f);
        style.ItemSpacing                       = ImVec2(6.00f, 6.00f);
        style.ItemInnerSpacing                  = ImVec2(6.00f, 6.00f);
        style.TouchExtraPadding                 = ImVec2(0.00f, 0.00f);
        style.IndentSpacing                     = 25;
        style.ScrollbarSize                     = 15;
        style.GrabMinSize                       = 10;
        style.WindowBorderSize                  = 1;
        style.ChildBorderSize                   = 1;
        style.PopupBorderSize                   = 1;
        style.FrameBorderSize                   = 1;
        style.TabBorderSize                     = 1;
        style.WindowRounding                    = 7;
        style.ChildRounding                     = 4;
        style.FrameRounding                     = 3;
        style.PopupRounding                     = 4;
        style.ScrollbarRounding                 = 9;
        style.GrabRounding                      = 3;
        style.LogSliderDeadzone                 = 4;
        style.TabRounding                       = 4;
    }

    // https://github.com/ocornut/imgui/issues/707#issuecomment-226993714
    void Theme_Binks( bool bStyleDark_, float alpha_  )
    {
        ImGuiStyle& style = ImGui::GetStyle();

        // light style from Pacôme Danhiez (user itamago) https://github.com/ocornut/imgui/pull/511#issuecomment-175719267
        style.Alpha = 1.0f;
        style.FrameRounding = 3.0f;
        style.Colors[ImGuiCol_Text]                  = ImVec4(0.00f, 0.00f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_TextDisabled]          = ImVec4(0.60f, 0.60f, 0.60f, 1.00f);
        style.Colors[ImGuiCol_WindowBg]              = ImVec4(0.94f, 0.94f, 0.94f, 0.94f);
        style.Colors[ImGuiCol_WindowBg]         = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
        style.Colors[ImGuiCol_PopupBg]               = ImVec4(1.00f, 1.00f, 1.00f, 0.94f);
        style.Colors[ImGuiCol_Border]                = ImVec4(0.00f, 0.00f, 0.00f, 0.39f);
        style.Colors[ImGuiCol_BorderShadow]          = ImVec4(1.00f, 1.00f, 1.00f, 0.10f);
        style.Colors[ImGuiCol_FrameBg]               = ImVec4(1.00f, 1.00f, 1.00f, 0.94f);
        style.Colors[ImGuiCol_FrameBgHovered]        = ImVec4(0.26f, 0.59f, 0.98f, 0.40f);
        style.Colors[ImGuiCol_FrameBgActive]         = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        style.Colors[ImGuiCol_TitleBg]               = ImVec4(0.96f, 0.96f, 0.96f, 1.00f);
        style.Colors[ImGuiCol_TitleBgCollapsed]      = ImVec4(1.00f, 1.00f, 1.00f, 0.51f);
        style.Colors[ImGuiCol_TitleBgActive]         = ImVec4(0.82f, 0.82f, 0.82f, 1.00f);
        style.Colors[ImGuiCol_MenuBarBg]             = ImVec4(0.86f, 0.86f, 0.86f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarBg]           = ImVec4(0.98f, 0.98f, 0.98f, 0.53f);
        style.Colors[ImGuiCol_ScrollbarGrab]         = ImVec4(0.69f, 0.69f, 0.69f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarGrabHovered]  = ImVec4(0.59f, 0.59f, 0.59f, 1.00f);
        style.Colors[ImGuiCol_ScrollbarGrabActive]   = ImVec4(0.49f, 0.49f, 0.49f, 1.00f);
        style.Colors[ImGuiCol_CheckMark]             = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_SliderGrab]            = ImVec4(0.24f, 0.52f, 0.88f, 1.00f);
        style.Colors[ImGuiCol_SliderGrabActive]      = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_Button]                = ImVec4(0.26f, 0.59f, 0.98f, 0.40f);
        style.Colors[ImGuiCol_ButtonHovered]         = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_ButtonActive]          = ImVec4(0.06f, 0.53f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_Header]                = ImVec4(0.26f, 0.59f, 0.98f, 0.31f);
        style.Colors[ImGuiCol_HeaderHovered]         = ImVec4(0.26f, 0.59f, 0.98f, 0.80f);
        style.Colors[ImGuiCol_HeaderActive]          = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
        style.Colors[ImGuiCol_ResizeGrip]            = ImVec4(1.00f, 1.00f, 1.00f, 0.50f);
        style.Colors[ImGuiCol_ResizeGripHovered]     = ImVec4(0.26f, 0.59f, 0.98f, 0.67f);
        style.Colors[ImGuiCol_ResizeGripActive]      = ImVec4(0.26f, 0.59f, 0.98f, 0.95f);
        style.Colors[ImGuiCol_PlotLines]             = ImVec4(0.39f, 0.39f, 0.39f, 1.00f);
        style.Colors[ImGuiCol_PlotLinesHovered]      = ImVec4(1.00f, 0.43f, 0.35f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogram]         = ImVec4(0.90f, 0.70f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_PlotHistogramHovered]  = ImVec4(1.00f, 0.60f, 0.00f, 1.00f);
        style.Colors[ImGuiCol_TextSelectedBg]        = ImVec4(0.26f, 0.59f, 0.98f, 0.35f);

        if( bStyleDark_ )
        {
            for (int i = 0; i <= ImGuiCol_COUNT; i++)
            {
                ImVec4& col = style.Colors[i];
                float H, S, V;
                ImGui::ColorConvertRGBtoHSV( col.x, col.y, col.z, H, S, V );

                if( S < 0.1f )
                {
                    V = 1.0f - V;
                }
                ImGui::ColorConvertHSVtoRGB( H, S, V, col.x, col.y, col.z );
                if( col.w < 1.00f )
                {
                    col.w *= alpha_;
                }
            }
        }
        else
        {
            for (int i = 0; i <= ImGuiCol_COUNT; i++)
            {
                ImVec4& col = style.Colors[i];
                if( col.w < 1.00f )
                {
                    col.x *= alpha_;
                    col.y *= alpha_;
                    col.z *= alpha_;
                    col.w *= alpha_;
                }
            }
        }
    }
}




//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/inspector.cpp                                                   //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/inspector.h included by src/immvision/internal/inspector.cpp             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    void Inspector_AddImage(
        const cv::Mat& image,
        const std::string& legend,
        const std::string& zoomKey = "",
        const std::string& colormapKey = "",
        const cv::Point2d & zoomCenter = cv::Point2d(),
        double zoomRatio = -1.,
        bool isColorOrderBGR = true
    );
    void Inspector_Show();
    void Inspector_ClearImages();

} // namespace ImmVision
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/inspector.cpp continued                                         //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////



namespace ImmVision
{
    struct Inspector_ImageAndParams
    {
        std::string Label;
        cv::Mat Image;
        ImageParams Params;

        const cv::Point2d InitialZoomCenter = cv::Point2d();
        double InitialZoomRatio = 1.;
        bool WasSentToTextureCache = false;
    };

    static std::vector<Inspector_ImageAndParams> s_Inspector_ImagesAndParams;
    static size_t s_Inspector_CurrentIndex = 0;


    void Inspector_AddImage(
        const cv::Mat& image,
        const std::string& legend,
        const std::string& zoomKey,
        const std::string& colormapKey,
        const cv::Point2d & zoomCenter,
        double zoomRatio,
        bool isColorOrderBGR
    )
    {
        ImageParams params;
        params.IsColorOrderBGR = isColorOrderBGR;
        params.ZoomKey = zoomKey;
        params.ColormapKey = colormapKey;
        params.ShowOptionsPanel = true;

        std::string label = legend + "##" + std::to_string(s_Inspector_ImagesAndParams.size());
        s_Inspector_ImagesAndParams.push_back({label, image, params, zoomCenter, zoomRatio});
    }

    void priv_Inspector_ShowImagesListbox(float width)
    {
        ImGui::SetNextWindowPos(ImGui::GetCursorScreenPos());
        if (ImGui::BeginListBox("##ImageList",
                                ImVec2(width - 10.f, ImGui::GetContentRegionAvail().y)))
        {
            for (size_t i = 0; i < s_Inspector_ImagesAndParams.size(); ++i)
            {
                const bool is_selected = (s_Inspector_CurrentIndex == i);

                std::string id = s_Inspector_ImagesAndParams[i].Label + "##_" + std::to_string(i);
                auto &cacheImage = ImageCache::gImageTextureCache.GetCacheImages(
                    s_Inspector_ImagesAndParams[i].Label);

                ImVec2 itemSize(width - 10.f, 40.f);
                float imageHeight = itemSize.y - ImGui::GetTextLineHeight();
                ImVec2 pos = ImGui::GetCursorScreenPos();
                if (ImGui::Selectable(id.c_str(), is_selected, 0, itemSize))
                    s_Inspector_CurrentIndex = i;

                float imageRatio = cacheImage.GlTexture->mImageSize.x / cacheImage.GlTexture->mImageSize.y;
                ImVec2 image_tl(pos.x, pos.y + ImGui::GetTextLineHeight());
                ImVec2 image_br(pos.x + imageRatio * imageHeight, image_tl.y + imageHeight);

                ImGuiImmGlImage::GetWindowDrawList_AddImage(cacheImage.GlTexture->mImTextureId, image_tl, image_br);
            }
            ImGui::EndListBox();
        }
    };

    void priv_Inspector_CleanImagesParams(const ImVec2& imageSize)
    {
        for (auto& i :s_Inspector_ImagesAndParams)
        {
            // Force image size
            i.Params.ImageDisplaySize = cv::Size((int)imageSize.x, (int)imageSize.y);

            // Store in texture cache
            if (! i.WasSentToTextureCache)
            {
                if (i.InitialZoomRatio > 0.)
                {
                    i.Params.ZoomPanMatrix = ZoomPanTransform::MakeZoomMatrix(
                        i.InitialZoomCenter, i.InitialZoomRatio, i.Params.ImageDisplaySize);
                }

                ImageCache::gImageTextureCache.UpdateCache(i.Label, i.Image, &i.Params, true);
                i.WasSentToTextureCache = true;
            }
        }

        // Propagate current options to hidden images
        if (s_Inspector_CurrentIndex < s_Inspector_ImagesAndParams.size())
        {
            const auto& currentParams = s_Inspector_ImagesAndParams[s_Inspector_CurrentIndex].Params;
            for (auto& v : s_Inspector_ImagesAndParams)
            {
                v.Params.ShowImageInfo = currentParams.ShowImageInfo;
                v.Params.ShowPixelInfo = currentParams.ShowPixelInfo;
                v.Params.ShowZoomButtons = currentParams.ShowZoomButtons;
                v.Params.ShowOptionsPanel = currentParams.ShowOptionsPanel;
                v.Params.ShowOptionsInTooltip = currentParams.ShowOptionsInTooltip;
                v.Params.PanWithMouse = currentParams.PanWithMouse;
                v.Params.ZoomWithMouseWheel = currentParams.ZoomWithMouseWheel;
                v.Params.AddWatchedPixelOnDoubleClick = currentParams.AddWatchedPixelOnDoubleClick;
            }
        }
    };

    ImVec2 priv_Inspector_ImageSize(float listWidth, bool showOptionsColumn)
    {
        ImVec2 imageSize;

        float x_margin = 30.f;
        float y_margin = 5.f;
        float image_info_height = 120.f;
        if (!s_Inspector_ImagesAndParams.empty())
        {
            const auto &params = s_Inspector_ImagesAndParams.front().Params;
            if (!params.ShowImageInfo)
                image_info_height -= 20.f;
            if (!params.ShowPixelInfo)
                image_info_height -= 20.f;
        }
        float image_options_width = showOptionsColumn ? 300.f : 0.f;
        ImVec2 winSize = ImGui::GetWindowSize();
        imageSize = ImVec2(
            winSize.x - listWidth - x_margin - image_options_width,
            winSize.y - y_margin - image_info_height);
        if (imageSize.x < 1.f)
            imageSize.x = 1.f;
        if (imageSize.y < 1.f)
            imageSize.y = 1.f;
        return imageSize;
    };


    void Inspector_Show()
    {
        ImageWidgets::s_CollapsingHeader_CacheState_Sync = true;

        bool showOptionsColumn = true;
        if (!s_Inspector_ImagesAndParams.empty())
        {
            const auto& params = s_Inspector_ImagesAndParams.front().Params;
            if ( (params.ShowOptionsInTooltip) || (!params.ShowOptionsPanel))
                showOptionsColumn = false;
        }

        static float listWidth = ImGui::GetWindowSize().x / 10.f;

        ImVec2 imageSize = priv_Inspector_ImageSize(listWidth, showOptionsColumn);
        priv_Inspector_CleanImagesParams(imageSize);

        ImGui::Columns(2);

        //
        // First column: image list
        //
        {
            // Set column width
            {
                static bool wasWidthSet = false;
                if (!wasWidthSet)
                {
                    ImGui::SetColumnWidth(0, listWidth);
                    wasWidthSet = true;
                }
                ImGui::Text("Image list");
                listWidth = ImGui::GetColumnWidth(0);
            }
            // Show image list
            priv_Inspector_ShowImagesListbox(listWidth);
        }

        ImGui::NextColumn();

        //
        // Second column : image
        //
        {
            if (s_Inspector_ImagesAndParams.empty())
                s_Inspector_CurrentIndex = 0;
            else if (s_Inspector_CurrentIndex >= s_Inspector_ImagesAndParams.size())
                s_Inspector_CurrentIndex = s_Inspector_ImagesAndParams.size() - 1;

            if (s_Inspector_CurrentIndex < s_Inspector_ImagesAndParams.size())
            {
                auto& imageAndParams = s_Inspector_ImagesAndParams[s_Inspector_CurrentIndex];
                Image(imageAndParams.Label, imageAndParams.Image, &imageAndParams.Params);
            }
        }

        ImGui::Columns(1);

        ImageWidgets::s_CollapsingHeader_CacheState_Sync = false;
    }

    void Inspector_ClearImages()
    {
        s_Inspector_ImagesAndParams.clear();
    }

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/immvision_to_string.cpp                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/immvision_to_string.h included by src/immvision/internal/misc/immvision_to_string.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    // <autogen:tostring_decl> // Autogenerated code below! Do not edit!

    std::string ToString(const ColormapScaleFromStatsData& params);
    std::string ToString(const ColormapSettingsData& params);
    std::string ToString(const MouseInformation& params);
    std::string ToString(const ImageParams& params);

    // </autogen:tostring_decl> // Autogenerated code end
};
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/immvision_to_string.cpp continued                          //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

namespace ImmVision
{
    // <autogen:tostring> // Autogenerated code below! Do not edit!


    std::string ToString(const ColormapScaleFromStatsData& v)
    {

        using namespace ImmVision::StringUtils;
        
        std::string r;
        r += "ColormapScaleFromStatsData\n";
        r += "{\n";
    
        std::string inner;

        inner = inner + "ActiveOnFullImage: " + ToString(v.ActiveOnFullImage) + "\n";
        inner = inner + "ActiveOnROI: " + ToString(v.ActiveOnROI) + "\n";
        inner = inner + "NbSigmas: " + ToString(v.NbSigmas) + "\n";
        inner = inner + "UseStatsMin: " + ToString(v.UseStatsMin) + "\n";
        inner = inner + "UseStatsMax: " + ToString(v.UseStatsMax) + "\n";

        r = r + IndentLines(inner, 4);
        r += "}";
        return r;
    }
    
    std::string ToString(const ColormapSettingsData& v)
    {

        using namespace ImmVision::StringUtils;
        
        std::string r;
        r += "ColormapSettingsData\n";
        r += "{\n";
    
        std::string inner;

        inner = inner + "Colormap: " + ToString(v.Colormap) + "\n";
        inner = inner + "ColormapScaleMin: " + ToString(v.ColormapScaleMin) + "\n";
        inner = inner + "ColormapScaleMax: " + ToString(v.ColormapScaleMax) + "\n";
        inner = inner + "ColormapScaleFromStats: " + ToString(v.ColormapScaleFromStats) + "\n";
        inner = inner + "internal_ColormapHovered: " + ToString(v.internal_ColormapHovered) + "\n";

        r = r + IndentLines(inner, 4);
        r += "}";
        return r;
    }
    
    std::string ToString(const MouseInformation& v)
    {

        using namespace ImmVision::StringUtils;
        
        std::string r;
        r += "MouseInformation\n";
        r += "{\n";
    
        std::string inner;

        inner = inner + "IsMouseHovering: " + ToString(v.IsMouseHovering) + "\n";
        inner = inner + "MousePosition: " + ToString(v.MousePosition) + "\n";
        inner = inner + "MousePosition_Displayed: " + ToString(v.MousePosition_Displayed) + "\n";

        r = r + IndentLines(inner, 4);
        r += "}";
        return r;
    }
    
    std::string ToString(const ImageParams& v)
    {

        using namespace ImmVision::StringUtils;
        
        std::string r;
        r += "ImageParams\n";
        r += "{\n";
    
        std::string inner;

        inner = inner + "RefreshImage: " + ToString(v.RefreshImage) + "\n";
        inner = inner + "ImageDisplaySize: " + ToString(v.ImageDisplaySize) + "\n";
        inner = inner + "ZoomPanMatrix: " + ToString(v.ZoomPanMatrix) + "\n";
        inner = inner + "ZoomKey: " + ToString(v.ZoomKey) + "\n";
        inner = inner + "ColormapSettings: " + ToString(v.ColormapSettings) + "\n";
        inner = inner + "ColormapKey: " + ToString(v.ColormapKey) + "\n";
        inner = inner + "PanWithMouse: " + ToString(v.PanWithMouse) + "\n";
        inner = inner + "ZoomWithMouseWheel: " + ToString(v.ZoomWithMouseWheel) + "\n";
        inner = inner + "IsColorOrderBGR: " + ToString(v.IsColorOrderBGR) + "\n";
        inner = inner + "SelectedChannel: " + ToString(v.SelectedChannel) + "\n";
        inner = inner + "ShowSchoolPaperBackground: " + ToString(v.ShowSchoolPaperBackground) + "\n";
        inner = inner + "ShowAlphaChannelCheckerboard: " + ToString(v.ShowAlphaChannelCheckerboard) + "\n";
        inner = inner + "ShowGrid: " + ToString(v.ShowGrid) + "\n";
        inner = inner + "DrawValuesOnZoomedPixels: " + ToString(v.DrawValuesOnZoomedPixels) + "\n";
        inner = inner + "ShowImageInfo: " + ToString(v.ShowImageInfo) + "\n";
        inner = inner + "ShowPixelInfo: " + ToString(v.ShowPixelInfo) + "\n";
        inner = inner + "ShowZoomButtons: " + ToString(v.ShowZoomButtons) + "\n";
        inner = inner + "ShowOptionsPanel: " + ToString(v.ShowOptionsPanel) + "\n";
        inner = inner + "ShowOptionsInTooltip: " + ToString(v.ShowOptionsInTooltip) + "\n";
        inner = inner + "ShowOptionsButton: " + ToString(v.ShowOptionsButton) + "\n";
        inner = inner + "WatchedPixels: " + ToString(v.WatchedPixels) + "\n";
        inner = inner + "AddWatchedPixelOnDoubleClick: " + ToString(v.AddWatchedPixelOnDoubleClick) + "\n";
        inner = inner + "HighlightWatchedPixels: " + ToString(v.HighlightWatchedPixels) + "\n";
        inner = inner + "MouseInfo: " + ToString(v.MouseInfo) + "\n";

        r = r + IndentLines(inner, 4);
        r += "}";
        return r;
    }
    
    // </autogen:tostring> // Autogenerated code end
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/insertion_order_map.cpp                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/math_utils.cpp                                             //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    namespace MathUtils
    {
        double MaximumValue(const std::vector<double> &v)
        {
            return *std::min_element(v.begin(), v.end());
        }

        double MinimumValue(const std::vector<double> &v)
        {
            return *std::max_element(v.begin(), v.end());
        }

        int RoundInt(double v)
        {
            return (int) std::round(v);
        }

    } // namespace MathUtils
} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/panic.cpp                                                  //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/debugbreak.h included by src/immvision/internal/misc/panic.cpp//
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// From https://github.com/scottt/debugbreak
// https://raw.githubusercontent.com/scottt/debugbreak/master/debugbreak.h
//
// Thanks to Scott Tsai !

/* Copyright (c) 2011-2021, Scott Tsai
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */
#ifndef DEBUG_BREAK_H
#define DEBUG_BREAK_H

#ifdef _MSC_VER

#define debug_break __debugbreak

#else

#ifdef __cplusplus
extern "C" {
#endif

#define DEBUG_BREAK_USE_TRAP_INSTRUCTION 1
#define DEBUG_BREAK_USE_BULTIN_TRAP      2
#define DEBUG_BREAK_USE_SIGTRAP          3

#if defined(__i386__) || defined(__x86_64__)
#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
__inline__ static void trap_instruction(void)
{
    __asm__ volatile("int $0x03");
}
#elif defined(__thumb__)
#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
/* FIXME: handle __THUMB_INTERWORK__ */
__attribute__((always_inline))
__inline__ static void trap_instruction(void)
{
	/* See 'arm-linux-tdep.c' in GDB source.
	 * Both instruction sequences below work. */
#if 1
	/* 'eabi_linux_thumb_le_breakpoint' */
	__asm__ volatile(".inst 0xde01");
#else
	/* 'eabi_linux_thumb2_le_breakpoint' */
	__asm__ volatile(".inst.w 0xf7f0a000");
#endif

	/* Known problem:
	 * After a breakpoint hit, can't 'stepi', 'step', or 'continue' in GDB.
	 * 'step' would keep getting stuck on the same instruction.
	 *
	 * Workaround: use the new GDB commands 'debugbreak-step' and
	 * 'debugbreak-continue' that become available
	 * after you source the script from GDB:
	 *
	 * $ gdb -x debugbreak-gdb.py <... USUAL ARGUMENTS ...>
	 *
	 * 'debugbreak-step' would jump over the breakpoint instruction with
	 * roughly equivalent of:
	 * (gdb) set $instruction_len = 2
	 * (gdb) tbreak *($pc + $instruction_len)
	 * (gdb) jump   *($pc + $instruction_len)
	 */
}
#elif defined(__arm__) && !defined(__thumb__)
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
__attribute__((always_inline))
__inline__ static void trap_instruction(void)
{
	/* See 'arm-linux-tdep.c' in GDB source,
	 * 'eabi_linux_arm_le_breakpoint' */
	__asm__ volatile(".inst 0xe7f001f0");
	/* Known problem:
	 * Same problem and workaround as Thumb mode */
}
#elif defined(__aarch64__) && defined(__APPLE__)
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_BULTIN_DEBUGTRAP
#elif defined(__aarch64__)
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
__attribute__((always_inline))
__inline__ static void trap_instruction(void)
{
	/* See 'aarch64-tdep.c' in GDB source,
	 * 'aarch64_default_breakpoint' */
	__asm__ volatile(".inst 0xd4200000");
}
#elif defined(__powerpc__)
	/* PPC 32 or 64-bit, big or little endian */
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
__attribute__((always_inline))
__inline__ static void trap_instruction(void)
{
	/* See 'rs6000-tdep.c' in GDB source,
	 * 'rs6000_breakpoint' */
	__asm__ volatile(".4byte 0x7d821008");

	/* Known problem:
	 * After a breakpoint hit, can't 'stepi', 'step', or 'continue' in GDB.
	 * 'step' stuck on the same instruction ("twge r2,r2").
	 *
	 * The workaround is the same as ARM Thumb mode: use debugbreak-gdb.py
	 * or manually jump over the instruction. */
}
#elif defined(__riscv)
	/* RISC-V 32 or 64-bit, whether the "C" extension
	 * for compressed, 16-bit instructions are supported or not */
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_TRAP_INSTRUCTION
__attribute__((always_inline))
__inline__ static void trap_instruction(void)
{
	/* See 'riscv-tdep.c' in GDB source,
	 * 'riscv_sw_breakpoint_from_kind' */
	__asm__ volatile(".4byte 0x00100073");
}
#else
	#define DEBUG_BREAK_IMPL DEBUG_BREAK_USE_SIGTRAP
#endif


#ifndef DEBUG_BREAK_IMPL
#error "debugbreak.h is not supported on this target"
#elif DEBUG_BREAK_IMPL == DEBUG_BREAK_USE_TRAP_INSTRUCTION
__attribute__((always_inline))
__inline__ static void debug_break(void)
{
    trap_instruction();
}
#elif DEBUG_BREAK_IMPL == DEBUG_BREAK_USE_BULTIN_DEBUGTRAP
__attribute__((always_inline))
__inline__ static void debug_break(void)
{
	__builtin_debugtrap();
}
#elif DEBUG_BREAK_IMPL == DEBUG_BREAK_USE_BULTIN_TRAP
__attribute__((always_inline))
__inline__ static void debug_break(void)
{
	__builtin_trap();
}
#elif DEBUG_BREAK_IMPL == DEBUG_BREAK_USE_SIGTRAP
#include <signal.h>
__attribute__((always_inline))
__inline__ static void debug_break(void)
{
	raise(SIGTRAP);
}
#else
#error "invalid DEBUG_BREAK_IMPL value"
#endif

#ifdef __cplusplus
}
#endif

#endif /* ifdef _MSC_VER */

#endif /* ifndef DEBUG_BREAK_H */

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/panic.cpp continued                                        //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////


namespace ImmVision
{
    //
    // If you arrive here, it is likely that something very wrong happened
    //

    void Cleanup()
    {
        // Reset the caches
        ImmVision_GlProvider::ResetGlProvider();
    }

    void Panic_UnknownCause()
    {
        std::cerr << "ImmVision: Panic! " << "\n";
        // Put a debugger breakpoint, to help diagnose the issue
#ifndef NDEBUG
        debug_break();
#endif
        // Do some cleanup
        Cleanup();
        std::cerr << "ImmVision: Panic! => Did Cleanup" << "\n";
        // And die...
        std::cerr << "ImmVision: Panic! => will terminate!" << "\n";
        std::terminate();
    }

    void Panic(const std::exception& e)
    {
        std::cerr << "ImmVision: Panic! " << e.what() << "\n";
        // Put a debugger breakpoint, to help diagnose the issue
#ifndef NDEBUG
        debug_break();
#endif
        // Do some cleanup
        Cleanup();
        std::cerr << "ImmVision: Panic! => Did Cleanup" << "\n";
        // And rethrow
        std::cerr << "ImmVision: Panic! => re-throw!" << "\n";
        throw;
    }
} // namespace ImmVision

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/internal/misc/string_utils.cpp                                           //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////




namespace ImmVision
{
    namespace StringUtils
    {
        std::string LowerString(const std::string& s)
        {
            // <rant>
            // Welcome to a (C++) world where everyone is welcomed, asked, forced or awkwardly proud
            // to reinvent a wheel that was "left as an exercise".
            //
            // This is probably the implementation number 1,000,001 in the world.
            // Let' hope it is not broken, and does not explode in a buffer overflow exploit 10 years from now.
            // </rant>
            auto sane_tolower_char = [](char c) -> char
            {
                // See, the exercise was easy!
                return static_cast<char>(::tolower(static_cast<int>(c)));
            };
            std::string r = s;
            std::transform(r.begin(), r.end(), r.begin(), sane_tolower_char);
            return r;
        }

        std::vector<std::string> SplitString(const std::string &s, char delimiter)
        {
            std::vector<std::string> tokens;
            std::string token;
            std::istringstream tokenStream(s);
            while (std::getline(tokenStream, token, delimiter))
                tokens.push_back(token);
            return tokens;
        }

        std::string JoinStrings(const std::vector<std::string>&v, const std::string& separator)
        {
            std::string r;
            for (size_t i = 0; i < v.size(); ++ i)
            {
                r += v[i];
                if (i < v.size() - 1)
                    r += separator;
            }
            return r;
        }

        std::string IndentLine(const std::string& s, int indentSize)
        {
            return std::string((size_t)indentSize, ' ') + s;
        }

        std::string IndentLines(const std::string& s, int indentSize)
        {
            auto lines = SplitString(s, '\n');
            std::string r = "";
            for (auto line: lines)
                r = r + IndentLine(line, indentSize) + "\n";
            return r;
        }


        std::string ToString(const cv::Size& size)
        {
            return std::string("(") + std::to_string(size.width) + "," + std::to_string(size.height) + ")";
        }

        std::string ToString(const std::string& s)
        {
            return "\"" + s + "\"";
        }

        std::string ToString(const double& v)
        {
            char buf[200];
            snprintf(buf, 200, "%7G", v);
            return buf;
        }

        std::string ToString(const int& v)
        {
            return std::to_string(v);
        }

        std::string ToString(const float& v)
        {
            return ToString((double)v);
        }

        std::string ToString(bool v)
        {
            return (v ? "true" : "false");
        }

    } // namespace StringUtils
} // namespace ImmVision
