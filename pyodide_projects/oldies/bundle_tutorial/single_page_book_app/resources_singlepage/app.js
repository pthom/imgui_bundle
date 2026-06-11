import {initializePyodideHelper} from "./pyodide_helper.js";
import {registerPageSectionEvents} from "./page_sections";
import Split from 'split.js';
import {initializeNavigation} from "./navig.js";

function _triggerWindowResizeToForceImGuiSizeRefresh() {
    // Important:
    // When the canvas size is updated, we need to trigger a window resize event
    // to force ImGui to recompute its size
    if (typeof window.dispatchEvent === "function") {
        window.dispatchEvent(new Event("resize"));
    }
}

function _createSplitBetweenContentAndImGuiCanvas()
{
    Split(['#doc-layout-container', '#imgui-canvas-div'], {
        sizes: [60, 40],
        minSize: 0,
        gutterSize: 14,
        cursor: 'col-resize',
        onDrag: () => {
            _triggerWindowResizeToForceImGuiSizeRefresh();
        }
    });
}

function _registerToggleTocBtnEvents()
{
    const toggleTocBtn = document.getElementById("toggle-toc-btn");
    const tocSidebar = document.getElementById("toc-sidebar");

    toggleTocBtn.addEventListener("click", () => {
        tocSidebar.classList.toggle("hidden");
    });
}

function _registerDarkModeEvents()
{
    const darkModeBtn = document.getElementById("toggle-dark-mode");

    const moonSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
     viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
     class="lucide lucide-moon-icon">
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
</svg>
`;

    const sunSvg = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
     viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
     class="lucide lucide-sun-icon">
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2m0 16v2m10-10h-2M4 12H2
             m15.364-6.364l-1.414 1.414
             M6.05 17.95l-1.414 1.414
             m12.728 0l-1.414-1.414
             M6.05 6.05L4.636 4.636" />
</svg>
`;
    function isDarkMode()
    {
        return document.body.classList.contains("dark-mode");
    }

    // Sets Dark Mode, stores the value in localStorage, and updates the button icon
    function setDarkMode(isDark)
    {
        if (isDark)
            document.body.classList.add("dark-mode");
        else
            document.body.classList.remove("dark-mode");

        localStorage.setItem("dark-mode", isDark.toString());

        // Update button icon
        darkModeBtn.innerHTML = isDark ? moonSvg : sunSvg;
    }

    // Reload dark mode option at startup (default is dark mode)
    function darkMode_reloadOptionAtStartup()
    {
        const stored_value = localStorage.getItem("dark-mode");
        if (stored_value === "true")
            setDarkMode(true);
        else if (stored_value === "false")
            setDarkMode(false);
        else
            // if not set, the default is dark mode
            setDarkMode(true);
    }

    function _toggleDarkMode()
    {
        const isDark = isDarkMode();
        setDarkMode(!isDark);
    }

    darkMode_reloadOptionAtStartup();
    darkModeBtn.addEventListener("click", _toggleDarkMode);
}


async function initializeAll() {

    _registerDarkModeEvents();
    registerPageSectionEvents();
    _registerToggleTocBtnEvents();
    _createSplitBetweenContentAndImGuiCanvas();

    await initializeNavigation();

    // Initialize Pyodide environment
    await initializePyodideHelper();
}

document.addEventListener("DOMContentLoaded", initializeAll);
