// Part of ImGui Bundle - MIT License - Copyright (c) 2022-2026 Pascal Thomet - https://github.com/pthom/imgui_bundle
// The welcome of the explorer: see demo_imgui_bundle_intro.cpp
#pragma once
#include <functional>
#include <string>

// What the page that shows the welcome provides: the explorer changes its state. Without it (the welcome alone), the
// page shows no button and no link to the demos.
struct WelcomeHost
{
    int nbDemos = 0;
    std::function<void()> browse;  // opens the catalog of demos
    std::function<void(const std::string&)> openDemo;  // opens one demo of the catalog, by its filename in examples.json
};

// The welcome without its title and links row (the explorer draws its own header above it): the tagline and the
// button to the prose, the carousel of mini demos, the button to the demos and the manuals
void WelcomeGui(const WelcomeHost& host);

// The main links row: the site, the repository, the documentation, the playground, Discord (none on a phone)
void RenderLinksRow();

// The whole page: the title, the links row, the welcome
void gui_demo_imgui_bundle_intro();
