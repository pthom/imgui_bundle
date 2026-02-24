#!/usr/bin/env bash
# This script deploys the manual to github pages at https://pthom.github.io/imgui_manual_online/
set -euo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_DIR=$SCRIPT_DIR/..
cd "$REPO_DIR"

REMOTE_URL=https://github.com/pthom/imgui_manual_online.git
CHECKOUT_DIR=external/imgui_manual/imgui_manual_online
WEBSITE=$CHECKOUT_DIR/website

# Clone the repo if not already present
if [ ! -d "$CHECKOUT_DIR/.git" ]; then
    echo "Cloning $REMOTE_URL into $CHECKOUT_DIR..."
    git clone "$REMOTE_URL" "$CHECKOUT_DIR"
fi

# Clear website dir (keep .nojekyll)
find "$WEBSITE" -mindepth 1 ! -name '.nojekyll' -delete 2>/dev/null || true

# Copy build output to website root (no .gz files — GitHub Pages CDN handles compression)
rsync -a --exclude='*.gz' build_manual_ems/bin/ "$WEBSITE"/
# Copy favicon (generated outside bin/ by CMake)
cp build_manual_ems/external/imgui_manual/imgui_manual/imgui_manual_favicon.png "$WEBSITE"/
# Ensure .nojekyll exists
touch "$WEBSITE/.nojekyll"

# Redirect from old URL: manual/imgui_manual.html -> root
mkdir -p "$WEBSITE/manual"
cat > "$WEBSITE/manual/imgui_manual.html" << 'REDIRECT_EOF'
<!DOCTYPE html>
<html><head>
<meta http-equiv="refresh" content="0; url=../">
<link rel="canonical" href="https://pthom.github.io/imgui_manual_online/">
</head><body>
<p>Redirecting to <a href="../">the manual</a>...</p>
</body></html>
REDIRECT_EOF

### Commit and push
cd "$CHECKOUT_DIR"
git add -A
git commit -m "Update manual ($(date +%Y-%m-%d))"
git push
echo "Pushed to imgui_manual_online. GitHub Pages will deploy to https://pthom.github.io/imgui_manual_online/"
echo "Verify compression: curl -sI -H 'Accept-Encoding: gzip' https://pthom.github.io/imgui_manual_online/index.wasm | grep -i content-encoding"
echo "Should be online soon at "
echo "    https://pthom.github.io/imgui_manual_online/"
echo "    (check deploy actions at:    https://github.com/pthom/imgui_manual_online/actions )"
