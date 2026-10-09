// The page's settings, kept in the browser and applied to each demo: a theme and a font size.
// The page turns light with a light theme (styles.css, html.light). The demos get them from py/playground_settings.py,
// after their setup: a demo with a theme of its own ("own_theme" in examples.json) keeps it until the user picks one.

const DARK_THEME = 'DarculaDarker';   // Hello ImGui's default
const LIGHT_THEME = 'WhiteIsWhite';
// Hello ImGui's themes: name, then the colors of their swatch (window, button, accent, text), and whether they are light
const THEMES = [
    ['ImGuiColorsClassic', '#000000', '#59669c', '#e5e5e5', '#e5e5e5', false],
    ['ImGuiColorsDark', '#0f0f0f', '#4296fa', '#4296fa', '#ffffff', false],
    ['ImGuiColorsLight', '#f0f0f0', '#4296fa', '#4296fa', '#000000', true],
    ['MaterialFlat', '#2c313c', '#5a6971', '#4f9fee', '#d4d8e0', false],
    ['PhotoshopStyle', '#2d2d2d', '#ffffff', '#ffffff', '#ffffff', false],
    ['GrayVariations', '#f2f2f2', '#dbdbdb', '#191919', '#191919', true],
    ['GrayVariations_Darker', '#d1d1d1', '#f9f9f9', '#1c1c1c', '#191919', true],
    ['MicrosoftStyle', '#f2f2f2', '#dbdbdb', '#191919', '#191919', true],
    ['Cherry', '#21232b', '#cd74c2', '#b036a1', '#decddc', false],
    ['Darcula', '#3c3f41', '#555a5c', '#e5e5e5', '#bbbbbb', false],
    ['DarculaDarker', '#232426', '#53565a', '#e1e1e1', '#e0e0e0', false],
    ['LightRounded', '#f5f3f3', '#4296f9', '#4296f9', '#000000', true],
    ['SoDark_AccentBlue', '#1a1a1a', '#4d4d4d', '#54b4db', '#ffffff', false],
    ['SoDark_AccentYellow', '#1a1a1a', '#4d4d4d', '#dbd854', '#ffffff', false],
    ['SoDark_AccentRed', '#1a1a1a', '#4d4d4d', '#db5454', '#ffffff', false],
    ['BlackIsBlack', '#000000', '#686868', '#72f5ff', '#ffffff', false],
    ['WhiteIsWhite', '#ffffff', '#cecece', '#181818', '#191919', true],
];
const FONT_SCALES = [0.75, 0.85, 1.0, 1.15, 1.3, 1.5, 1.75, 2.0];  // the steps of the font size buttons
const CODE_FONT_SIZE_PX = 13;  // the code editor's font size at the scale 1

// The browser's storage may be unavailable (a private window): the settings then last for the page
function readSetting(key, fallback) {
    try { return localStorage.getItem('playground.' + key) ?? fallback; } catch (e) { return fallback; }
}
function writeSetting(key, value) {
    try { localStorage.setItem('playground.' + key, value); } catch (e) { /* kept for the page only */ }
}

let currentTheme = readSetting('theme', '');  // '' until the user picks one: each demo keeps its own
let currentFontScale = parseFloat(readSetting('fontScale', '1')) || 1.0;
let pySettings = null;  // py/playground_settings.py, once Pyodide is ready

function isLightTheme(name) {
    const theme = THEMES.find(t => t[0] === name);
    return !!theme && theme[5];
}

// The page follows the theme: light or dark; the switches show which one is on
function showTheme() {
    document.documentElement.classList.toggle('light', isLightTheme(currentTheme));
    const kind = currentTheme === LIGHT_THEME ? 'light' : (!currentTheme || currentTheme === DARK_THEME ? 'dark' : 'more');
    for (const button of document.querySelectorAll('.theme-switch button'))
        button.classList.toggle('active', button.dataset.theme === kind);
    for (const item of document.querySelectorAll('.theme-menu-item'))
        item.classList.toggle('active', item.dataset.theme === (currentTheme || DARK_THEME));
}

function setTheme(name) {
    currentTheme = name;
    writeSetting('theme', name);
    showTheme();
    if (pySettings) pySettings.set_theme(name);
}

// The code editor follows the font size too
function showFontScale() {
    if (typeof editor !== 'undefined') {
        editor.getWrapperElement().style.fontSize = Math.round(CODE_FONT_SIZE_PX * currentFontScale) + 'px';
        editor.refresh();
    }
    for (const button of document.querySelectorAll('.font-size button'))
        button.disabled = button.dataset.step === '-1' ? currentFontScale <= FONT_SCALES[0]
                                                       : currentFontScale >= FONT_SCALES.at(-1);
}

function stepFontScale(direction) {
    const index = FONT_SCALES.findIndex(s => Math.abs(s - currentFontScale) < 0.01);
    const next = FONT_SCALES[Math.max(0, Math.min(FONT_SCALES.length - 1, (index < 0 ? 2 : index) + direction))];
    currentFontScale = next;
    writeSetting('fontScale', String(next));
    showFontScale();
    if (pySettings) pySettings.set_font_scale(next);
    // The value, for a moment, under the buttons
    for (const toast of document.querySelectorAll('.font-size-toast')) {
        toast.textContent = `Text ${Math.round(next * 100)}%`;
        toast.classList.add('visible');
    }
    clearTimeout(stepFontScale.timer);
    stepFontScale.timer = setTimeout(() => {
        for (const toast of document.querySelectorAll('.font-size-toast')) toast.classList.remove('visible');
    }, 1200);
}

// The menu of all the themes ("..."): a swatch and a name each, the current one marked
function buildThemeMenu() {
    const menu = document.createElement('div');
    menu.className = 'theme-menu';
    for (const [name, bg, button, accent, text] of THEMES) {
        const item = document.createElement('button');
        item.className = 'theme-menu-item';
        item.dataset.theme = name;
        const swatch = document.createElement('span');
        swatch.className = 'theme-swatch';
        swatch.style.background = bg;
        swatch.style.color = text;
        swatch.innerHTML = `<i style="background:${button}"></i><i style="background:${accent}"></i>Aa`;
        item.appendChild(swatch);
        item.appendChild(document.createTextNode(name.replace(/_/g, ' ')));
        menu.appendChild(item);
    }
    return menu;
}

// A theme switch: the header's (desktop), or the one in the (i) note (phone)
function wireThemeSwitch(container) {
    for (const button of container.querySelectorAll('button')) {
        if (button.dataset.theme === 'dark') button.addEventListener('click', () => setTheme(DARK_THEME));
        if (button.dataset.theme === 'light') button.addEventListener('click', () => setTheme(LIGHT_THEME));
        if (button.dataset.theme === 'more') {
            const menu = buildThemeMenu();
            const popup = tippy(button, {
                content: menu,
                trigger: 'click',
                interactive: true,
                appendTo: () => document.body,
                placement: 'bottom-end',
                theme: 'light-border',
                maxWidth: 260,
            });
            for (const item of menu.querySelectorAll('.theme-menu-item'))
                item.addEventListener('click', () => { setTheme(item.dataset.theme); popup.hide(); });
        }
    }
    showTheme();
}

document.addEventListener('DOMContentLoaded', () => {
    wireThemeSwitch(document.getElementById('theme-switch'));
    // On a phone, the header has no room for the switch: a button beside the (i) shows it in a bubble
    const bubble = document.getElementById('theme-bubble-content').content.firstElementChild.cloneNode(true);
    wireThemeSwitch(bubble.querySelector('.theme-switch'));
    const [bubbleTip] = tippy('#theme-button', {
        content: bubble,
        trigger: 'click',
        interactive: true,
        appendTo: () => document.body,
        placement: 'bottom',
        theme: 'light-border',
    });
    // The moon or the sun picked: the bubble closes ("..." keeps it, under its list)
    bubble.addEventListener('click', (e) => {
        if (e.target.closest('button[data-theme="dark"], button[data-theme="light"]')) bubbleTip.hide();
    });
    for (const button of document.querySelectorAll('.font-size button'))
        button.addEventListener('click', () => stepFontScale(parseInt(button.dataset.step)));
    showFontScale();
});
showTheme();  // at once, before the first paint of the page's colors

// Once Pyodide is ready: the module that applies the settings to the demos
async function loadPlaygroundSettings() {
    try {
        const code = await (await fetch('py/playground_settings.py')).text();
        pyodide.FS.writeFile('/home/pyodide/playground_settings.py', code);
        pySettings = pyodide.pyimport('playground_settings');
        pySettings.configure(currentTheme, currentFontScale);
    } catch (e) {  // an older wheel, without the hook: the page's colors follow, the demos keep their own
        console.warn('playground_settings not loaded:', e);
        pySettings = null;
    }
}

// Before a demo runs: does it set a theme of its own?
function settingsBeforeDemo(example) {
    if (pySettings) pySettings.next_demo(!!(example && example.own_theme));
}

// A theme picked inside the running demo (py/playground_settings.py): the page follows it at once
function onDemoThemeChanged(name) {
    currentTheme = name;
    writeSetting('theme', name);
    showTheme();
}

// Before a demo stops: a theme picked inside it (the themes demo, a menu) becomes the page's
function settingsBeforeStop() {
    if (!pySettings) return;
    const picked = pySettings.theme_picked_in_demo();
    if (picked) {
        currentTheme = picked;
        writeSetting('theme', picked);
        pySettings.configure(currentTheme, currentFontScale);
        showTheme();
    }
}
