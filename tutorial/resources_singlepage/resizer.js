let isResizing = false;
let startX = 0;
let startContentWidth = 0;

function _onResizerMouseDown(e) {
    const layout = document.querySelector('.layout-container');
    isResizing = true;
    startX = e.clientX;

    // Get current grid-template-columns as an array
    const computedStyle = window.getComputedStyle(layout);
    const columns = computedStyle.getPropertyValue('grid-template-columns').split(' ');

    // Parse and store the current width of the content area (2nd column)
    startContentWidth = parseFloat(columns[1]);
    // Fallback: Measure content area if parsing fails
    if (isNaN(startContentWidth)) {
        const contentArea = document.getElementById('content-area');
        startContentWidth = contentArea.offsetWidth;
    }

    document.body.style.userSelect = 'none'; // Prevent text selection
}

function _onResizerMouseMove(e) {
    if (!isResizing) return;

    const layout = document.querySelector('.layout-container');
    const dx = e.clientX - startX;
    const minWidth = 200; // Minimum width for the content area
    const maxWidth = layout.offsetWidth - 300; // Prevent overlapping code panel

    // Calculate and constrain the new content area width
    const newContentWidth = Math.min(Math.max(startContentWidth + dx, minWidth), maxWidth);

    // Lock TOC width to 200px and update the content/code panel widths
    layout.style.gridTemplateColumns = `200px ${newContentWidth}px 5px auto`;
}
function _onResizerMouseUp()
{
    isResizing = false;
    document.body.style.userSelect = 'auto';
}

function _initializeGridTemplateColumns() {
    const layout = document.querySelector('.layout-container');
    // Set the initial grid layout with TOC width locked at 200px
    layout.style.gridTemplateColumns = '200px auto 5px 33%';
}

export function initResizer()
{
    _initializeGridTemplateColumns();
    const resizer = document.getElementById('resizer');
    resizer.addEventListener('mousedown', _onResizerMouseDown);
    document.addEventListener('mousemove', _onResizerMouseMove);
    document.addEventListener('mouseup', _onResizerMouseUp);
}
