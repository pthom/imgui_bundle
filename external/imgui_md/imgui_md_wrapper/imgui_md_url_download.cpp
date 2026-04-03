// URL image download for imgui_md using libcurl.
// Async: each URL is downloaded in a background thread.
// The callback returns Downloading until the thread completes.

#include "imgui_md_url_download.h"

#ifdef IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES

#include <curl/curl.h>
#include <string>
#include <vector>
#include <map>
#include <mutex>
#include <thread>
#include <atomic>
#include <cstdint>
#include <climits>

namespace ImGuiMd {

    static constexpr int kMaxConcurrentDownloads = 10;
    static constexpr size_t kMaxFileSize = 20 * 1024 * 1024; // 20 MB

    struct DownloadState {
        MarkdownDownloadStatus status = MarkdownDownloadStatus::Downloading;
        std::vector<uint8_t> data;
        std::string errorMessage;
    };

    static std::mutex gMutex;
    static std::map<std::string, DownloadState> gDownloads;
    static std::atomic<int> gActiveDownloads{0};
    // Flag to prevent detached threads from writing after cleanup
    static std::atomic<bool> gShuttingDown{false};

    // curl write callback: append received data to a vector, enforce size cap
    static size_t WriteCallback(const void* contents, size_t size, size_t nmemb, void* userp)
    {
        // Overflow check
        if (nmemb != 0 && size > SIZE_MAX / nmemb)
            return 0;
        size_t totalSize = size * nmemb;

        auto* buf = static_cast<std::vector<uint8_t>*>(userp);

        // Enforce max file size (covers chunked transfers where Content-Length is absent)
        if (buf->size() + totalSize > kMaxFileSize)
            return 0; // Returning 0 aborts the transfer

        auto* bytes = static_cast<const uint8_t*>(contents);
        buf->insert(buf->end(), bytes, bytes + totalSize);
        return totalSize;
    }

    static void DownloadThread(const std::string url) // copy, not ref (thread outlives caller)
    {
        std::vector<uint8_t> buffer;
        std::string error;
        bool success = false;

        CURL* curl = curl_easy_init();
        if (curl)
        {
            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &buffer);
            curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
            curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
            curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 5L);
            curl_easy_setopt(curl, CURLOPT_USERAGENT, "imgui_bundle_md/1.0");
            // Restrict to http/https only (prevent file://, ftp://, gopher:// etc.)
            curl_easy_setopt(curl, CURLOPT_PROTOCOLS_STR, "https,http");
            // Explicit TLS verification
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
            curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 2L);

            CURLcode res = curl_easy_perform(curl);
            if (res == CURLE_OK)
            {
                long http_code = 0;
                curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
                if (http_code == 200)
                    success = true;
                else
                    error = "HTTP " + std::to_string(http_code);
            }
            else
            {
                error = curl_easy_strerror(res);
            }
            curl_easy_cleanup(curl);
        }
        else
        {
            error = "curl_easy_init failed";
        }

        {
            std::lock_guard<std::mutex> lock(gMutex);
            if (!gShuttingDown)
            {
                auto& state = gDownloads[url];
                if (success)
                {
                    state.data = std::move(buffer);
                    state.status = MarkdownDownloadStatus::Ready;
                }
                else
                {
                    state.errorMessage = error;
                    state.status = MarkdownDownloadStatus::Failed;
                }
            }
        }
        --gActiveDownloads;
    }


    MarkdownDownloadResult DesktopDownloadData(const std::string& url)
    {
        MarkdownDownloadResult result;

        std::lock_guard<std::mutex> lock(gMutex);
        auto it = gDownloads.find(url);
        if (it != gDownloads.end())
        {
            auto& state = it->second;
            result.status = state.status;
            if (state.status == MarkdownDownloadStatus::Ready)
            {
                result.data = state.data;
            }
            else if (state.status == MarkdownDownloadStatus::Failed)
            {
                result.errorMessage = state.errorMessage;
            }
            return result;
        }

        // Limit concurrent downloads
        if (gActiveDownloads >= kMaxConcurrentDownloads)
        {
            result.status = MarkdownDownloadStatus::Downloading;
            return result; // Will retry next frame (not yet in map)
        }

        // First call for this URL: start background download
        gDownloads[url] = DownloadState{MarkdownDownloadStatus::Downloading, {}, ""};
        ++gActiveDownloads;
        std::thread(DownloadThread, url).detach();

        result.status = MarkdownDownloadStatus::Downloading;
        return result;
    }


    void ClearDesktopDownloads()
    {
        gShuttingDown = true;
        std::lock_guard<std::mutex> lock(gMutex);
        gDownloads.clear();
        gShuttingDown = false;
    }

} // namespace ImGuiMd

#endif // IMGUI_RICHMD_WITH_DOWNLOAD_IMAGES
