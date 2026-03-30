#!/usr/bin/env python3
"""Serve Python demos for Pyodide testing.

Usage:
    python serve.py [--port PORT] [--no-cors]
    # or: just pyodide_demo_runner

Then open:
    http://localhost:PORT/
        -> listing of available .py demos (with fuzzy search)
    http://localhost:PORT/?file=sandbox/sandbox_markdown_download_images.py
        -> runs that file in Pyodide
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEMOS_DIR = os.path.join(THIS_DIR, "demos")  # symlink to demos_python


class PyodideRunnerHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS headers and a /list_demos endpoint."""

    def __init__(self, *args, cors=True, **kwargs):
        self._cors = cors
        super().__init__(*args, **kwargs)

    def end_headers(self):
        if self._cors:
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/list_demos':
            self._serve_demo_listing()
        else:
            super().do_GET()

    def _serve_demo_listing(self):
        """Return JSON listing of .py files under demos/."""
        demos = []
        for root, dirs, files in os.walk(DEMOS_DIR):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(('.', '__'))]
            for f in sorted(files):
                if f.endswith('.py') and not f.startswith('__'):
                    rel = os.path.relpath(os.path.join(root, f), DEMOS_DIR)
                    demos.append(rel)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(demos).encode())


def make_handler_class(cors):
    """Create a handler class with the cors flag baked in."""
    class Handler(PyodideRunnerHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, cors=cors, **kwargs)
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Pyodide demo runner server')
    parser.add_argument('-p', '--port', default=6789, type=int, help='Port (default: 6789)')
    parser.add_argument('--no-cors', action='store_true', help='Disable CORS headers')
    args = parser.parse_args()

    # Serve from this directory (pyodide_demo_runner/)
    os.chdir(THIS_DIR)

    print("=" * 60)
    print("  Pyodide Demo Runner")
    print("=" * 60)
    print(f"\n  Server: http://localhost:{args.port}/")
    print(f"  CORS:   {'disabled' if args.no_cors else 'enabled'}")
    print(f"  Root:   {THIS_DIR}")
    print(f"  Demos:  {DEMOS_DIR}")
    print(f"\n  Press Ctrl+C to stop")
    print("=" * 60)

    server = HTTPServer(('', args.port), make_handler_class(not args.no_cors))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == '__main__':
    main()
