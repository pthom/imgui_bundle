#!/usr/bin/env python3
"""
Simple HTTP server with CORS headers for testing Pyodide locally.

This server adds the required Cross-Origin headers for SharedArrayBuffer
support, which is needed by some Pyodide/emscripten features.

Usage:
    python serve_test.py [-p PORT]

Example:
    python serve_test.py -p 8000
    Then open http://localhost:8000/test_pyodide.html
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import argparse


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for Pyodide compatibility."""

    def end_headers(self):
        # Required for SharedArrayBuffer support
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        # Allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(
        description='HTTP server with CORS headers for Pyodide testing'
    )
    parser.add_argument(
        '-p', '--port',
        default=8000,
        type=int,
        help='Port to serve on (default: 8000)'
    )
    args = parser.parse_args()

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    print(f"URL: http://localhost:{args.port}/")
    print(f"Test page: http://localhost:{args.port}/test_pyodide.html")
    print("\nPress Ctrl+C to stop\n")

    server = HTTPServer(('', args.port), CORSRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == '__main__':
    main()

