#include "image_with_gui.h"


namespace VisualProg
{

    std::vector<cv::Mat> SplitChannels(const Image& image)
    {
        assert(image.channels() > 1);
        std::vector<cv::Mat> r;
        cv::split(image, r);
        return r;
    }

}