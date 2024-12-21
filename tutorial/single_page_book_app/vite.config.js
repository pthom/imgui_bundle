import { defineConfig } from "vite";

export default {
    root: './', // Set the root folder (e.g., your project folder)
    build: {
        outDir: 'dist', // Output directory
    },
    resolve: {
        alias: {
            "@codemirror/state": require.resolve("@codemirror/state"),
        },
    }
};

