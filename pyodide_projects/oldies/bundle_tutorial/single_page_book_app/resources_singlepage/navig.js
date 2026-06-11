import { initTOC } from "./toc_loader.js";
import { tocRoot } from "./toc_loader.js";
import { loadPage } from "./page_loader.js";


const currentPage = "";

async function _onBack()
{
    const page = _getPageFromUrl();
    if (page !== currentPage) {
        await navigate(page);
    }
}

function _getPageFromUrl()
{
    const url = new URL(window.location.href);

    const defaultPage = tocRoot().file;
    if (url.searchParams.get("doc") === null) {
        return defaultPage;
    }
    return url.searchParams.get("doc");
}

// Trigger navigation programmatically
export async function navigate(pageName) {
    const url = new URL(window.location.href);
    url.searchParams.set("doc", pageName);
    history.pushState({ page: pageName }, "", url);

    await loadPage(pageName + ".md");
}

export async function initializeNavigation()
{
    await initTOC();

    window.addEventListener("popstate", (_event) => {
        _onBack();
    });

    const page = _getPageFromUrl();
    if (page !== currentPage) {
        await navigate(page);
    }
}
