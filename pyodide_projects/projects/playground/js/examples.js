// js/examples.js

// The welcome: the explorer's intro module, served from demos_python (its entry in examples.json)
// ==============================================================================================
const WELCOME_FILENAME = 'demo_imgui_bundle_intro.py';
const WELCOME_SOURCE = 'demos_python';

// load the initial example code
async function initial_example_code() {
    try {
        const response = await fetch(`${WELCOME_SOURCE}/${WELCOME_FILENAME}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const content = await response.text();
        return content; // Return the fetched code
    } catch (error) {
        console.error('Error loading initial code:', error);
        return `# Fallback initial code\nprint("Failed to load initial code.")`;
    }
}

// Before the welcome runs: the files it reads (welcome.md, resources.md) in Pyodide's file system, and the editor
// folded (its 1500 lines are not what the visitor came for; the "Code" rail unfolds it)
async function prepareWelcome() {
    if (examplesMetadata.length === 0) examplesMetadata = await fetchExampleMetadata();
    const welcome = examplesMetadata.find(e => e.filename === WELCOME_FILENAME);
    if (welcome) await installBundleFiles(welcome.bundle_files, welcome.source);
    if (!narrowScreen.matches) setCodeFolded(true);
}

// A demo meant to be hacked (the Start here category): a hint, once, that the code at the left is the point
let hackHintShown = false;
function showHackHint(example) {
    if (hackHintShown || !example || example.category !== 'Start here' || example.filename === WELCOME_FILENAME) return;
    hackHintShown = true;
    const hint = document.createElement('div');
    hint.id = 'hack-hint';
    hint.textContent = narrowScreen.matches ? 'Try it: open the Code, edit it, then Run'
                                            : 'Try it: edit the code at the left, then click Run';
    document.getElementById('canvas-container').appendChild(hint);
    setTimeout(() => hint.classList.add('fading'), 6000);
    hint.addEventListener('transitionend', () => hint.remove(), {once: true});
}

// Check URL for ?demo=filename parameter
function getDemoFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('demo');
}

// Run this function on page load
document.addEventListener('DOMContentLoaded', async () => {
    // The welcome hides its code from the start, while Pyodide loads (a ?demo= link shows the demo's code)
    if (!getDemoFromUrl() && !narrowScreen.matches) {
        setCodeFolded(true);
        document.querySelector('#loading-banner .loading-hint').hidden = true;  // "browse the code on the left"
    }
    const initialCode = await initial_example_code();
    editor.setValue(initialCode);
    setLoadedCode(initialCode);
    setEditorLabel('Welcome to Dear ImGui Bundle');
});


// Populate the example selector
// ==============================

// Function to fetch example metadata from JSON
async function fetchExampleMetadata() {
    try {
        const response = await fetch('examples/examples.json');
        const data = await response.json();
        examplesCategories = data.categories || [];
        examplesSources = data.sources || {};
        return data.examples;
    } catch (error) {
        console.error('Error fetching example metadata:', error);
        displayError('Failed to fetch example metadata. See console for details.');
        return [];
    }
}

// Track which packages have already been installed
const installedPackages = new Set();

// Per-package expected install time on a typical 4G connection (ms).
// Used only to tune the asymptotic smoothProgress animation; actual
// install time can be longer or shorter — phase.complete() snaps the
// bar when micropip.install resolves.
const PACKAGE_EXPECTED_MS = {
    'opencv-python': 8000,  // ~11 MB
    'fiatlight':     3000,
};
const PACKAGE_EXPECTED_MS_DEFAULT = 4000;

// Function to install extra packages required by an example
async function installExamplePackages(packages) {
    if (!packages || packages.length === 0) return;
    if (!pyodide) {
        console.error('Pyodide not loaded yet');
        return;
    }
    const toInstall = packages.filter(pkg => !installedPackages.has(pkg));
    if (toInstall.length === 0) return;

    const micropip = pyodide.pyimport("micropip");
    showLoadingModal();
    const total = toInstall.length;
    for (let i = 0; i < total; i++) {
        const pkg = toInstall[i];
        const startPct = (i / total) * 95;
        const endPct   = ((i + 1) / total) * 95;
        const expectedMs = PACKAGE_EXPECTED_MS[pkg] ?? PACKAGE_EXPECTED_MS_DEFAULT;
        const phase = smoothProgress(startPct, endPct, expectedMs,
            (pct) => updateProgress(pct, `Installing ${pkg}…`));
        await micropip.install(pkg);
        phase.complete();
        installedPackages.add(pkg);
        console.log(`${pkg} installed.`);
    }
    updateProgress(100, 'Ready');
    await new Promise(resolve => setTimeout(resolve, 300));
    hideLoadingModal();
}

// Download bundled folders (e.g. fiat_settings) into the Pyodide virtual filesystem. A folder is relative to the
// example's source folder, and lands under /home/pyodide at the same relative path; a folder outside it (e.g.
// ../demos_assets, for the immapp demos) lands under its own name (/home/pyodide/demos_assets). Its manifest.json lists
// its files, in subfolders too (ci_scripts/playground_examples_docs.py); they are written as bytes (fonts, images...).
async function installBundleFolders(bundleFolders, source) {
    if (!bundleFolders || bundleFolders.length === 0 || !pyodide) return;
    for (const folder of bundleFolders) {
        const url = `${source || 'examples'}/${folder}`;
        const manifestResp = await fetch(`${url}/manifest.json`);
        if (!manifestResp.ok) {
            console.warn(`No manifest.json found for bundle folder ${folder}`);
            continue;
        }
        const files = await manifestResp.json();
        const targetDir = `/home/pyodide/${folder.replace(/^(\.\.\/)+/, '')}`;
        for (const file of files) {
            const resp = await fetch(`${url}/${file}`);
            if (!resp.ok) continue;
            const path = `${targetDir}/${file}`;
            pyodide.FS.mkdirTree(path.substring(0, path.lastIndexOf('/')));
            pyodide.FS.writeFile(path, new Uint8Array(await resp.arrayBuffer()));
        }
        console.log(`Installed bundle folder: ${folder} (${files.length} files)`);
    }
}

// A few files from a big folder (examples.json "bundle_files": paths from the example's source folder), written
// into Pyodide's file system at the same place as a bundle folder's files (/home/pyodide/<path without ../>)
async function installBundleFiles(bundleFiles, source) {
    if (!bundleFiles || bundleFiles.length === 0 || !pyodide) return;
    for (const file of bundleFiles) {
        const resp = await fetch(`${source || 'examples'}/${file}`);
        if (!resp.ok) {
            console.warn(`Bundle file not found: ${file}`);
            continue;
        }
        const path = `/home/pyodide/${file.replace(/^(\.\.\/)+/, '')}`;
        pyodide.FS.mkdirTree(path.substring(0, path.lastIndexOf('/')));
        pyodide.FS.writeFile(path, new Uint8Array(await resp.arrayBuffer()));
    }
}

// Function to load example content (and install packages + bundle folders if needed).
// source: the served folder of the example's file (examples.json "source"; e.g. demos_immapp), examples by default
async function loadExample(filename, packages, label, bundleFolders, source, bundleFiles) {
    try {
        await installExamplePackages(packages);
        await installBundleFolders(bundleFolders, source);
        await installBundleFiles(bundleFiles, source);
        const response = await fetch(`${source || 'examples'}/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const content = await response.text();
        editor.setValue(content);
        setLoadedCode(content);
        loadedExampleFilename = filename;
        if (label) setEditorLabel(label);
        clearError(); // Clear previous errors when loading a new example
    } catch (error) {
        console.error('Error loading example:', error);
        displayError('Failed to load the example. Please try again.');
    }
}

// Store example metadata so we can look up packages later
let examplesMetadata = [];
let examplesCategories = [];  // [{name, about}], in the order of the menu
let examplesSources = {};  // {source: its folder, relative to the examples folder}: where a demo's file is in the repository
let examplesDocs = {};  // {filename: {title, text}}: examples_docs.json, see ci_scripts/playground_examples_docs.py

// The example loaded in the editor (null for the landing page): runEditorPythonCode() runs it at its own path
let loadedExampleFilename = null;

// The gallery: the launcher's twin in HTML (demo_immapp_launcher.py). An overlay under the header: the category chips
// (a click scrolls to the category), the library filter and the search box, then the categories with their cards
// (picture, tags, title, summary; the whole text as a tooltip). A card loads and runs its demo.

// Markdown as plain text: links keep their text, emphasis and code marks go
function plainText(markdown) {
    return markdown.replace(/\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/[*`]/g, '').replace(/\s+/g, ' ').trim();
}

function element(tag, className, text) {
    const e = document.createElement(tag);
    e.className = className;
    if (text) e.textContent = text;
    return e;
}

// What an example may need from the browser ("needs" in examples.json), and whether this browser has it
const BROWSER_NEEDS = {
    jspi: {
        has: 'Suspending' in WebAssembly,
        text: 'WebAssembly stack switching (JSPI): Chrome 137, Firefox 153, Safari 27',
    },
};

function unmetNeeds(example) {
    return (example.needs || []).map((n) => BROWSER_NEEDS[n]).filter((need) => need && !need.has);
}

function makeCard(example, category) {
    const doc = examplesDocs[example.filename] || {};
    const unmet = unmetNeeds(example);
    const card = element('div', 'gallery-card' + (unmet.length ? ' unavailable' : ''));
    card.dataset.filename = example.filename;
    card.dataset.category = category.name;
    // What the search looks into: the label, the description, the category, the libraries
    card.dataset.search = [example.label, doc.title, doc.text, category.name, ...(doc.uses || [])]
        .join(' ').toLowerCase();
    card.dataset.uses = JSON.stringify(doc.uses || []);
    card.title = plainText(doc.text || '');
    if (unmet.length) card.title = 'Not in this browser. Needs ' + unmet.map((need) => need.text).join('; ');
    card.tabIndex = unmet.length ? -1 : 0;
    card.setAttribute('role', 'button');
    if (unmet.length) card.setAttribute('aria-disabled', 'true');
    // Its picture, from the website resources (made by ci_scripts/playground_screenshots.py)
    const picture = element('div', 'gallery-picture');
    const img = document.createElement('img');
    img.alt = '';
    img.loading = 'lazy';
    img.onerror = () => { img.remove(); picture.classList.add('gallery-no-picture'); };  // no picture yet
    img.src = '../resources/playground/' + example.filename.split('/').pop().replace(/\.py$/, '.jpg');
    const tags = element('span', 'gallery-tags');
    tags.appendChild(element('span', 'gallery-tag python', 'Python'));
    if (doc.cpp) tags.appendChild(element('span', 'gallery-tag cpp', 'C++'));
    if (example.where === 'browser') tags.appendChild(element('span', 'gallery-tag browser', 'Browser only'));
    if (example.where === 'desktop') tags.appendChild(element('span', 'gallery-tag desktop', 'Desktop only'));
    if (unmet.length) tags.appendChild(element('span', 'gallery-tag unavailable', 'Not in this browser'));
    picture.append(img, tags);
    // A card this browser cannot run says what it needs in place of its summary (a tooltip would not show on a phone)
    const summary = unmet.length ? 'Needs ' + unmet.map((need) => need.text).join('; ') : plainText(doc.summary || '');
    card.append(picture, element('div', 'gallery-title', example.label), element('div', 'gallery-summary', summary));
    if (unmet.length) return card;  // greyed, not clickable
    card.addEventListener('click', async () => {
        closeGallery();
        await loadDemoByFilename(example.filename);
    });
    card.addEventListener('keydown', (event) => { if (event.key === 'Enter') card.click(); });
    return card;
}

async function buildGallery() {
    examplesMetadata = await fetchExampleMetadata();
    try {
        examplesDocs = await (await fetch('examples/examples_docs.json')).json();
    } catch (error) {
        console.warn('No examples_docs.json: the gallery shows no descriptions', error);
    }
    const body = document.getElementById('gallery-body');
    const chips = document.getElementById('gallery-chips');
    body.innerHTML = '';
    chips.innerHTML = '';
    let count = 0;
    for (const category of examplesCategories) {
        // The gallery shows the demos of the category, except the hidden ones: those that run in the browser, then
        // the desktop-only ones (a card shows their code, their picture and a notice)
        const ofCategory = examplesMetadata.filter((e) => !e.hidden && e.category === category.name);
        const shown = [...ofCategory.filter((e) => e.where !== 'desktop'),
                       ...ofCategory.filter((e) => e.where === 'desktop')];
        if (!shown.length) continue;
        const section = element('section', 'gallery-category');
        section.dataset.category = category.name;
        section.append(element('h2', 'gallery-category-title', category.name),
                       element('div', 'gallery-category-about', category.about));
        if (category.tip) section.appendChild(element('div', 'gallery-category-about', category.tip));
        const grid = element('div', 'gallery-grid');
        for (const example of shown) grid.appendChild(makeCard(example, category));
        section.appendChild(grid);
        body.appendChild(section);
        const chip = element('button', 'gallery-chip');
        chip.dataset.category = category.name;
        chip.addEventListener('click', () => section.scrollIntoView({behavior: 'smooth', block: 'start'}));
        chips.appendChild(chip);
        count += shown.length;
    }
    document.getElementById('examples-button').innerHTML = `Demos<span class="examples-count"> (${count})</span>`;  // the count is hidden on a phone
    chips.addEventListener('scroll', markChipsOverflow);
    window.addEventListener('resize', markChipsOverflow);
    markChipsOverflow();
    const noMatch = element('div', '', 'No demo matches.');
    noMatch.id = 'gallery-no-match';
    noMatch.hidden = true;
    body.appendChild(noMatch);
    fillLibraries();
    filterGallery();
}

// The library select: the libraries the demos use, with counts, the most used first
function fillLibraries() {
    const counts = new Map();
    for (const card of document.querySelectorAll('.gallery-card'))
        for (const library of JSON.parse(card.dataset.uses)) counts.set(library, (counts.get(library) || 0) + 1);
    const select = document.getElementById('gallery-library');
    select.innerHTML = '';
    select.append(new Option('Library', ''));
    for (const [name, count] of [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])))
        select.append(new Option(`${name} (${count})`, name));
}

// The gallery keeps the demos that use the library picked and have every word of the search; the chips count them
function filterGallery() {
    const words = document.getElementById('gallery-search').value.toLowerCase().split(/\s+/).filter(Boolean);
    const library = document.getElementById('gallery-library').value;
    const shown = new Map();
    for (const card of document.querySelectorAll('.gallery-card')) {
        card.hidden = (library && !JSON.parse(card.dataset.uses).includes(library))
            || !words.every((word) => card.dataset.search.includes(word));
        if (!card.hidden) shown.set(card.dataset.category, (shown.get(card.dataset.category) || 0) + 1);
    }
    for (const section of document.querySelectorAll('.gallery-category'))
        section.hidden = !shown.has(section.dataset.category);
    for (const chip of document.querySelectorAll('.gallery-chip')) {
        const n = shown.get(chip.dataset.category) || 0;
        chip.textContent = `${chip.dataset.category} (${n})`;
        chip.hidden = n === 0;
    }
    document.getElementById('gallery-no-match').hidden = shown.size > 0;
    document.getElementById('gallery-clear').hidden = !words.length && !library;
    markCategoryInView();
}

function clearGalleryFilters() {
    document.getElementById('gallery-search').value = '';
    document.getElementById('gallery-library').value = '';
    filterGallery();
}

// The chip of the category in view, as the launcher's: the last one whose title has passed the top (or the last
// one, at the end: the last categories cannot reach the top)
function markCategoryInView() {
    const body = document.getElementById('gallery-body');
    const sections = [...document.querySelectorAll('.gallery-category:not([hidden])')];
    if (!sections.length) return;
    const top = body.getBoundingClientRect().top;
    const atTheEnd = body.scrollTop + body.clientHeight >= body.scrollHeight - 1;
    let current = sections[0];
    for (const section of sections)
        if (section.getBoundingClientRect().top <= top + 3 * parseFloat(getComputedStyle(body).fontSize))
            current = section;
    if (atTheEnd) current = sections[sections.length - 1];
    for (const chip of document.querySelectorAll('.gallery-chip')) {
        const inView = chip.dataset.category === current.dataset.category;
        if (inView && !chip.classList.contains('in-view')) {
            // On a phone the chips are one row that scrolls sideways: the chip in view is brought to the middle
            const strip = chip.parentElement;
            if (strip.scrollWidth > strip.clientWidth)
                strip.scrollTo({left: chip.offsetLeft - (strip.clientWidth - chip.offsetWidth) / 2, behavior: 'smooth'});
        }
        chip.classList.toggle('in-view', inView);
    }
}

// On a phone the chips are one row that scrolls sideways (styles.css): the bar shows a hint at the end that has more
function markChipsOverflow() {
    const chips = document.getElementById('gallery-chips');
    const bar = document.getElementById('gallery-bar');
    bar.classList.toggle('chips-more-left', chips.scrollLeft > 1);
    bar.classList.toggle('chips-more-right', chips.scrollLeft + chips.clientWidth < chips.scrollWidth - 1);
}

// Highlights the demo loaded in the editor
function markCurrentExample(filename) {
    for (const card of document.querySelectorAll('.gallery-card'))
        card.classList.toggle('current', card.dataset.filename === filename);
}

// The cards in view are dealt one after another, from the top left (a CSS animation per card, delayed by its rank)
function dealCards() {
    const bodyRect = document.getElementById('gallery-body').getBoundingClientRect();
    let rank = 0;
    for (const card of document.querySelectorAll('.gallery-card:not([hidden])')) {
        const rect = card.getBoundingClientRect();
        if (rect.bottom < bodyRect.top || rect.top > bodyRect.bottom || rank >= 24) continue;
        card.style.setProperty('--rank', rank);
        card.style.setProperty('--spin', `${((rank * 7) % 5 - 2) * 9}deg`);  // its own, settled on landing
        card.classList.add('dealt');
        card.addEventListener('animationend', () => card.classList.remove('dealt'), {once: true});
        rank++;
    }
}

function openGallery() {
    const gallery = document.getElementById('gallery');
    gallery.style.top = document.getElementById('header').getBoundingClientRect().bottom + 'px';  // under the header
    const wasHidden = gallery.hidden;
    gallery.hidden = false;
    requestAnimationFrame(() => gallery.classList.add('open'));  // a frame later: the transition needs a start state
    document.getElementById('examples-button').setAttribute('aria-expanded', 'true');
    const current = document.querySelector('.gallery-card.current');
    if (current) current.scrollIntoView({block: 'center'});
    markCategoryInView();
    if (wasHidden) dealCards();
    // Not on a touch screen, where the keyboard would cover the gallery (a phone held sideways is wider than 768 px)
    if (!window.matchMedia('(pointer: coarse)').matches) document.getElementById('gallery-search').focus();
}

function closeGallery() {
    const gallery = document.getElementById('gallery');
    gallery.classList.remove('open');
    setTimeout(() => { if (!gallery.classList.contains('open')) gallery.hidden = true; }, 200);  // after its fade
    document.getElementById('examples-button').setAttribute('aria-expanded', 'false');
}

// The interactive manuals have their own "Demo | Code" switch, for the code of their demo. On a phone, the playground's
// switch hides while their demo shows (styles.css): one switch on screen. It comes back with the code pane (an error).
function markOwnCodeSwitch(example) {
    const own = !!example && example.category === 'Interactive manuals';
    document.body.classList.toggle('own-code-switch', own);
    if (own && narrowScreen.matches) setPane('demo');
}

// Load a demo by filename (works for both visible and hidden demos)
async function loadDemoByFilename(filename, updateHistory = true) {
    // Look up in metadata (includes hidden demos)
    const example = examplesMetadata.find(e => e.filename === filename);
    const packages = example ? example.packages : undefined;
    const label = example ? example.label : filename;
    const bundleFolders = example ? example.bundle_folders : undefined;
    const bundleFiles = example ? example.bundle_files : undefined;
    const source = example ? example.source : undefined;
    markOwnCodeSwitch(example);
    // The welcome and the manuals hide the code (a manual shows its own); the other demos show it, to be edited
    const hidesCode = filename === WELCOME_FILENAME || (!!example && example.category === 'Interactive manuals');
    if (!narrowScreen.matches) setCodeFolded(hidesCode);
    await loadExample(filename, packages, label, bundleFolders, source, bundleFiles);
    markCurrentExample(filename);
    showHackHint(example);
    // Update browser URL and history
    if (updateHistory) {
        const url = new URL(window.location);
        url.searchParams.set('demo', filename);
        history.pushState({demo: filename}, '', url);
    }
    if (example && example.where === 'desktop') {  // its code is shown, its picture and a notice: it does not run here
        await stopRunningDemo();
        showDesktopPanel(example);
        return;
    }
    await runEditorPythonCode();
}

// The GitHub page of a demo's file (its folder in the repository comes from "sources" in examples.json)
function githubUrl(source, filename) {
    const parts = [];
    const path = 'bindings/imgui_bundle/demos_python/playground/examples/'
        + (examplesSources[source || 'examples'] || '.') + '/' + filename;
    for (const part of path.split('/')) {
        if (part === '..') parts.pop(); else if (part && part !== '.') parts.push(part);
    }
    return 'https://github.com/pthom/imgui_bundle/blob/main/' + parts.join('/');
}

// Check ?demo= URL parameter and load the specified demo after Pyodide is ready
async function loadDemoFromUrlIfNeeded() {
    const demoFile = getDemoFromUrl();
    if (demoFile) {
        // Wait for metadata to be available
        if (examplesMetadata.length === 0) {
            examplesMetadata = await fetchExampleMetadata();
        }
        await loadDemoByFilename(demoFile);
    }
}

// Initialize the examples menu on page load
document.addEventListener('DOMContentLoaded', () => {
    buildGallery().then(() => markCurrentExample(getDemoFromUrl() || WELCOME_FILENAME));

    const gallery = document.getElementById('gallery');
    document.getElementById('examples-button').addEventListener('click', () => {
        if (gallery.hidden || !gallery.classList.contains('open')) openGallery(); else closeGallery();
    });
    document.getElementById('gallery-close').addEventListener('click', closeGallery);
    document.getElementById('gallery-clear').addEventListener('click', clearGalleryFilters);
    const search = document.getElementById('gallery-search');
    const library = document.getElementById('gallery-library');
    search.addEventListener('input', filterGallery);
    library.addEventListener('change', filterGallery);
    document.getElementById('gallery-body').addEventListener('scroll', markCategoryInView);
    window.addEventListener('resize', () => {  // the header's height changes
        if (!gallery.hidden)
            gallery.style.top = document.getElementById('header').getBoundingClientRect().bottom + 'px';
    });
    // Escape (listened in the capture phase: the canvas may stop the events)
    document.addEventListener('keydown', (event) => {
        if (gallery.hidden || event.key !== 'Escape') return;
        if (search.value || library.value) {  // a first Escape clears the filters, a second closes
            clearGalleryFilters();
        } else {
            closeGallery();
        }
    }, true);

    // Handle browser back/forward buttons
    window.addEventListener('popstate', async (event) => {
        if (event.state && event.state.demo) {
            await loadDemoByFilename(event.state.demo, false);
        } else {
            // Back to the root URL (no ?demo=): restore the landing page
            const initialCode = await initial_example_code();
            editor.setValue(initialCode);
            setLoadedCode(initialCode);
            loadedExampleFilename = null;
            markOwnCodeSwitch(null);
            setEditorLabel('Welcome to Dear ImGui Bundle');
            clearError();
            markCurrentExample(WELCOME_FILENAME);
            await prepareWelcome();
            await runEditorPythonCode();
        }
    });
});
