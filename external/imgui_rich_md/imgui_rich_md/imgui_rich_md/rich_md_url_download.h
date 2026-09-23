#pragma once
#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES

#include "rich_md.h"

namespace RichMd {
    // Async download callback for C++ desktop using libcurl.
    // Returns Downloading on first call for a URL, Ready/Failed once done.
    // Thread-safe: downloads run in background threads.
    MarkdownDownloadResult DesktopDownloadData(const std::string& url);

    // Clear all pending/completed downloads. Call on DeInitializeMarkdown.
    void ClearDesktopDownloads();
}

#endif
