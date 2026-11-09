#pragma once

namespace ImmApp
{
    // A platform specific utility to open an url in a browser
    void BrowseToUrl(const char *url);
    // For an item (a button) that opens an url: call it right after the item, each frame, with the item's own click.
    // In a browser, the page opens the url from the click's own handler, in a new tab (a click seen by Dear ImGui
    // comes too late for Safari to allow one); elsewhere, the click opens it with BrowseToUrl().
    //     if (ImGui::Button("GitHub")) {}  // or: bool clicked = ImGui::Button("GitHub");
    //     ImmApp::BrowseToUrlOnItemClick(clicked, url);
    void BrowseToUrlOnItemClick(bool clicked, const char* url);
}
