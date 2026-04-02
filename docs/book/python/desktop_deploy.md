# Desktop Deployment

This page covers packaging Python applications built with Dear ImGui Bundle as standalone desktop executables.

For this, you will need to use a packaging tool like **[PyInstaller](https://pyinstaller.org/)** to create an executable from your Python code. Other tools like [cx_Freeze](https://cx-freeze.readthedocs.io/) or [Nuitka](https://nuitka.net/) can also work.

They will allow you to distribute your application without requiring users to install Python or dependencies. They will also allow you to set an app icon, which is important for a polished user experience.

Using those packaging tools is known to work, but we do not provide official support for them.

## Icons: Window Icon vs App Icon

There are two different types of icons:

- **Window icon**: The icon shown in the window title bar and taskbar while the app is running. Works on Windows and Linux; on macOS, the window icon comes from the app bundle icon.
- **App icon**: The icon of the executable file itself (shown in file explorers, app launchers, etc.). Requires a packaging tool like PyInstaller.

### Window Icon (Windows/Linux)

Place your icon at `assets/app_settings/icon.png` and make sure the assets folder is set correctly:

```python
from imgui_bundle import hello_imgui, immapp
import os

def main():
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    hello_imgui.set_assets_folder(assets_path)  # or hello_imgui.add_assets_search_path    
    immapp.run(gui, window_title="My App")
```

**Icon requirements:**
- Square, PNG format
- At least 256x256 pixels (512x512 recommended)
- Located at `<assets_folder>/app_settings/icon.png`

This sets the **window icon** on Windows and Linux. On macOS, window icons are the same as the app icon (see below).

### App Icon (packaged applications)

In Python, you will need a packaging tool like **PyInstaller** to set the app icon when creating standalone executables.


## Packaging with PyInstaller

It is best to refer to the [PyInstaller](https://pyinstaller.org/) documentation for details, but here are some key points:

### Example with macOS

A complete macOS example is available in the repository: [demo_packaging/macos](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/demos_python/demo_packaging/macos)

### For windows

For windows, you could create a spec file like this:

```
# yourapp.spec
a = Analysis(
['your_app.py'],
datas=[("assets", "assets")],  # Include assets folder
# ... other settings
)

exe = EXE(
pyz,
a.scripts,
# ... other settings
icon='path/to/your_icon.ico',  # <-- Set app icon here (Windows uses . ico)
)
```

Then build with:

```bash
pip install pyinstaller
pyinstaller yourapp.spec
```

## Packaging with Nuitka

Instructions inspired @neudinger's article at 
https://neudinger.medium.com/the-modern-c-python-gui-stack-from-native-binary-to-webassembly-cc235bf3fb3b

Nuitka is a Python compiler that can create standalone executables. It can be used to package Dear ImGui Bundle applications as well.

The following command compiles `your_app.py` into a standalone executable, including the assets from Dear ImGui Bundle:

```
export imgui_bundle_asset_path=`python -c "import imgui_bundle, os; print(os.path.join(os.path.dirname(imgui_bundle.__file__), 'assets'))"`

python -m nuitka \
    --standalone \
    --include-package=imgui_bundle \
    --include-package-data=imgui_bundle \
    --include-module=importlib.util \
    --include-data-dir=${imgui_bundle_asset_path}=imgui_bundle/assets \
    --noinclude-pytest-mode=nofollow \
    --enable-plugin=no-qt \
    -o your_app_compiled \
    your_app.py
```

*Note: Nuitka provides an option "--onefile" to create a single executable, but this will slow the startup time. It is recommended to use the default "standalone" mode, which creates a folder with the executable and dependencies, for better performance.*

Do read Nuitka's documentation for more details and options: https://nuitka.net/doc/user-manual.html
