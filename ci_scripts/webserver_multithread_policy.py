#!/usr/bin/python3
"""
A simple web server for emscripten when running in multithread mode:
it adds the HTTP headers Cross Origin Opener Policy (COOP) and Cross Origin Embedder Policy (COEP)

See: https://emscripten.org/docs/porting/pthreads.html
Inspired by https://gist.github.com/Faless/1e228325ced0662aee59dc92fa69efd7
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import os
import argparse


class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int)
    parser.add_argument('-r', '--root', default='', type=str)
    args = parser.parse_args()
    if args.root:
        os.chdir(args.root)
    test(CORSRequestHandler, HTTPServer, port=args.port)
