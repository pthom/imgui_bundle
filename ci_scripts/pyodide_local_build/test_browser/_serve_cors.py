#!/usr/bin/env python3
"""
HTTP server with CORS headers for testing Pyodide + imgui-bundle locally.

This server adds the required Cross-Origin headers for SharedArrayBuffer
support, which is needed by Pyodide/emscripten for threading and memory features.

Usage:
    ./serve_tests.py [--port PORT]

Example:
    ./serve_tests.py --port 8000
    Then open:
      - http://localhost:8000/
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import argparse
import sys


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for Pyodide compatibility."""

    def end_headers(self):
        # Required for SharedArrayBuffer support (used by Pyodide threading)
        # See: https://pyodide.org/en/stable/usage/quickstart.html#serving-pyodide
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')

        # Allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

        # Cache control for development
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')

        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to add color and better formatting."""
        # Color codes
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        # Determine color based on status code
        status = str(args[1]) if len(args) > 1 else ''
        if status.startswith('2'):
            color = GREEN
        elif status.startswith('3'):
            color = YELLOW
        else:
            color = RESET

        sys.stderr.write(f"{color}[{self.log_date_time_string()}] {format % args}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description='HTTP server with CORS headers for Pyodide testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Pages:
  test_local_pyodide.html            - Uses local Pyodide distribution
  test_cdn_pyodide_local_wheel.html  - Uses CDN Pyodide + local wheel
  test_cdn_all.html                  - Uses CDN for everything (future)
"""
    )
    parser.add_argument(
        '-p', '--port',
        default=8000,
        type=int,
        help='Port to serve on (default: 8000)'
    )
    args = parser.parse_args()

    # Change to the test_browser directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    print("=" * 70)
    print("  Pyodide Test Server")
    print("=" * 70)
    print(f"\n  📡 Server: http://localhost:{args.port}/")
    print(f"\n  Press Ctrl+C to stop")
    print("=" * 70)
    print()

    server = HTTPServer(('', args.port), CORSRequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
