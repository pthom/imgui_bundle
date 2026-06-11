#!/usr/bin/python3
"""
A simple web server for emscripten when running in multithread mode:
it adds the HTTP headers Cross Origin Opener Policy (COOP) and Cross Origin Embedder Policy (COEP)

See: https://emscripten.org/docs/porting/pthreads.html
Inspired by https://gist.github.com/Faless/1e228325ced0662aee59dc92fa69efd7

Also serves pre-compressed .gz files transparently: if index.wasm.gz exists and the
browser sends Accept-Encoding: gzip, it is served with Content-Encoding: gzip.
Pre-compress with: gzip -k index.wasm index.data index.js
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import os
import argparse


COI_PREFIX = ''  # set by main(); empty string = apply site-wide
GZIP_SUFFIX = ''  # set by main(); e.g. '.data' to serve *.data with Content-Encoding: gzip


class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        if not COI_PREFIX or self.path.startswith(COI_PREFIX):
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        if GZIP_SUFFIX and self.path.endswith(GZIP_SUFFIX):
            self.send_header('Content-Encoding', 'gzip')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        # Serve a pre-compressed .gz file if available and the client accepts gzip
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding and not self.path.endswith('.gz'):
            fs_path = self.translate_path(self.path)
            gz_path = fs_path + '.gz'
            if os.path.isfile(gz_path) and os.path.getmtime(gz_path) >= os.path.getmtime(fs_path):
                try:
                    with open(gz_path, 'rb') as f:
                        content = f.read()
                    ctype = self.guess_type(self.path)
                    self.send_response(200)
                    self.send_header('Content-Type', ctype)
                    self.send_header('Content-Encoding', 'gzip')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception:
                    pass  # fall through to normal handling
        super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int)
    parser.add_argument('-r', '--root', default='', type=str)
    parser.add_argument('--coi-prefix', default='', type=str,
                        help='Only set COOP/COEP on URLs under this prefix (e.g. /explorer/). Empty = site-wide.')
    parser.add_argument('--gzip-suffix', default='', type=str,
                        help='Serve files whose URL ends with this suffix with Content-Encoding: gzip. '
                             'Use when files are already gzipped on disk (e.g. --gzip-suffix=.data).')
    args = parser.parse_args()
    if args.root:
        os.chdir(args.root)
    globals()['COI_PREFIX'] = args.coi_prefix
    globals()['GZIP_SUFFIX'] = args.gzip_suffix
    print(f"http://localhost:{args.port}/")
    test(CORSRequestHandler, HTTPServer, port=args.port)
