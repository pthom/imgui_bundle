# Example: packaging a Python application for macOS with pyinstaller

This example shows how to package a Python application for macOS with pyinstaller.

## Requirements
```bash
pip install pyinstaller
```

## Build app
```bash
pyinstaller bundle_macos_demo.spec
```
The app is then located in the `dist` folder.


## Notes

### Assets folder
The function below will change the assets folder if we detect that we are inside a macOS bundle.

```python
def set_assets_folder_if_macos_bundle():
    import os
    this_dir = str(os.path.dirname(os.path.realpath(__file__)))
    if this_dir.endswith("Contents/Frameworks"):
        assets_folder = this_dir + "/../Resources/assets"
        hello_imgui.set_assets_folder(assets_folder)
        print(f"Changed assets folder to: {assets_folder}")
```

### Spec

The spec file contains the following lines that define the app name, icon and bundle identifier, as well as the assets folder to embed.

```python
a = Analysis(
    ['bundle_macos_demo.py'],
    ...
    datas=[("assets", "assets")],               # Embed assets
    ...
    )

...
...

app = BUNDLE(
    coll,
    name='bundle_macos_demo.app',               # define app name
    icon="logo_imgui_bundle.icns",              # define app icon
    bundle_identifier="bundle_macos_demo",      # define bundle identifier
)
```
