#pragma once
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES

#include "imgui_md_wrapper.h"

namespace ImGuiMd {
    // Async download callback for C++ desktop using libcurl.
    // Returns Downloading on first call for a URL, Ready/Failed once done.
    // Thread-safe: downloads run in background threads.
    MarkdownDownloadResult DesktopDownloadData(const std::string& url);

    // Clear all pending/completed downloads. Call on DeInitializeMarkdown.
    void ClearDesktopDownloads();
}

#endif
