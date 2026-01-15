# Assets folder
(for python)

hello_imgui and immapp applications rely on the presence of an `assets/` folder.

**This folder stores:**

* Default fonts used by the markdown renderer (if the markdown addon is used).
* All the resources (images, fonts, etc.) used by the application. Feel free to add any resources there!

**Assets folder location**

Place the assets folder in the same folder as the script.

**If needed, change the assets folder location:**

Call `hello_imgui.set_assets_folder()` at startup.

**Typical layout of the assets folder**

```
assets/
    +-- fonts/
    |    +-- DroidSans.ttf            # Default fonts used by HelloImGui to
    |    +-- fontawesome-webfont.ttf  # improve text rendering (esp. on High DPI)
    |    |                            # if absent, a default LowRes font is used.
    |    |
    |    +-- Roboto/                  # Optional: fonts for markdown
    |         +-- LICENSE.txt
    |         +-- Roboto-Bold.ttf
    |         +-- Roboto-BoldItalic.ttf
    |         +-- Roboto-Regular.ttf
    |         +-- Roboto-RegularItalic.ttf
    |         +-- Inconsolata-Medium.ttf
    +-- images/
         +-- markdown_broken_image.png  # Optional: used for markdown
         +-- world.png                  # Add anything in the assets folder!
```

Note: in C++, the assets folder also contains an `app_settings` folder, which contains application settings and app icons for different platforms. This is not needed / not available in Python applications.

**Where to find the default assets**

You can [download the default assets as a zip file](https://traineq.org/ImGuiBundle/assets.zip).

Look at the folder [imgui_bundle/bindings/imgui_bundle/assets](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/assets) to see its content.
