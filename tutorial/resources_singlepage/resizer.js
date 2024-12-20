let isResizing = false;
let startX = 0;
let startContentWidth = 0;

function _onResizerMouseDown(e)
{
    const layout = document.querySelector('.layout-container');
    isResizing = true;
    startX = e.clientX;
    // Get current width of content area (second column)
    // We assume something like: [TOC:200px] [content:auto] [handle:5px] [code:33%]
    // We'll convert the content column to a fixed width during resizing
    const computedStyle = window.getComputedStyle(layout);
    const columns = computedStyle.getPropertyValue('grid-template-columns').split(' ');
    // columns[1] is the content area width
    startContentWidth = parseFloat(columns[1]);
    // If it's 'auto', we might need to set a default width or measure #content-area’s offsetWidth
    if (isNaN(startContentWidth)) {
        const contentArea = document.getElementById('content-area');
        startContentWidth = contentArea.offsetWidth;
    }
    document.body.style.userSelect = 'none'; // Prevent text selection
}

function _onResizerMouseMove(e)
{
    const layout = document.querySelector('.layout-container');

    if (!isResizing) return;
    const dx = e.clientX - startX;
    const newContentWidth = startContentWidth + dx;
    if (newContentWidth > 100) { // A minimum width for content area
        layout.style.gridTemplateColumns = `200px ${newContentWidth}px 5px auto`;
    }
}

function _onResizerMouseUp()
{
    isResizing = false;
    document.body.style.userSelect = 'auto';
}

export function initResizer()
{
    const resizer = document.getElementById('resizer');
    resizer.addEventListener('mousedown', _onResizerMouseDown);
    document.addEventListener('mousemove', _onResizerMouseMove);
    document.addEventListener('mouseup', _onResizerMouseUp);
}
