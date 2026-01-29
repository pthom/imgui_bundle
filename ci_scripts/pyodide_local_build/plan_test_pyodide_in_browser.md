# Test in a browser for pyodide (local build) + imgui-bundle

# Infos

## Urls for Pyodide release and pyodide.js

When we know which release of Pyodide to target (below it 0.29.3) we can
know:

1. The URL to download the pyodide release containing the base pyodide.js and
  pyodide.wasm + all wheels for that release (including an older wheel for imgui-bundle because it was added to the pyodide-recipes)
  The url is 
  https://github.com/pyodide/pyodide/releases/download/0.29.3/pyodide-0.29.3.tar.bz2
 
(we may want to compute it dynamically from the version number which would be stored in a variable somewhere)

2. The URL to load pyodide.js from a CDN for that release, which is:
   https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js

## Example web page
Read
ci_scripts/old_docker_pyodide/test_pyodide.html

## Goals
We want to test 
- a page that uses pyodide from a local folder: for that we need to download the pyodide release tarball, extract it to a local folder (e.g. pyodide_official_0.29.3/ + a symlink pyodide_official_latest/ pointing to it)
- a page that uses pyodide from the CDN and loads imgui-bundle from a local folder
- a page that uses pyodide from the CDN and loads imgui-bundle from the CDN

We need to serve the files with a local web server that supports CORS.
See ci_scripts/old_docker_pyodide/serve_test.py

We will be working in the folder ci_scripts/pyodide_local_build/

