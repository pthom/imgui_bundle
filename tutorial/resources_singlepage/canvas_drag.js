const canvasWindow = document.getElementById("canvas-window");
const titleBar = document.getElementById("canvas-title-bar");
const maximizeBtn = document.getElementById("maximize-btn");

let isDragging = false;
let startX, startY, initialX, initialY;

export function registerCanvasDragEvents() {
    titleBar.addEventListener("mousedown", (e) => {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        const rect = canvasWindow.getBoundingClientRect();
        initialX = rect.left;
        initialY = rect.top;
        document.body.style.userSelect = "none"; // Prevent text selection
    });

    document.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        canvasWindow.style.left = `${initialX + dx}px`;
        canvasWindow.style.top = `${initialY + dy}px`;
    });

    document.addEventListener("mouseup", () => {
        isDragging = false;
        document.body.style.userSelect = ""; // Restore text selection
    });

// Maximize Button
    maximizeBtn.addEventListener("click", () => {
        if (canvasWindow.classList.contains("maximized")) {
            canvasWindow.style.width = "20%";
            canvasWindow.style.height = "20%";
            canvasWindow.style.bottom = "1rem";
            canvasWindow.style.right = "1rem";
            canvasWindow.classList.remove("maximized");
        } else {
            canvasWindow.style.width = "100%";
            canvasWindow.style.height = "100%";
            canvasWindow.style.top = "0";
            canvasWindow.style.left = "0";
            canvasWindow.classList.add("maximized");
        }
    });
}

