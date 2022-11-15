// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/immvision.h                                                              //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/image.h included by src/immvision/immvision.h                            //
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
//                       src/immvision/immvision.h continued                                                    //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       src/immvision/inspector.h included by src/immvision/immvision.h                        //
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