# Assets folder
(for C++)

HelloImGui and ImmApp applications rely on the presence of an `assets/` folder.

**This folder stores:**

* Default fonts used by the markdown renderer (if the markdown addon is used).
* All the resources (images, fonts, etc.) used by the application. Feel free to add any resources there!

**Assets folder location**

The assets folder should be placed in the same folder as the CMakeLists.txt for the application (the one calling imgui_bundle_add_app)

**Typical layout of the assets folder**

```
assets/
    +-- app_settings/                # Application settings
    |    +-- icon.png                # This will be the app icon, it should be square
    |    |                           # and at least 256x256. It will  be converted
    |    |                           # to the right format, for each platform (except Android)
    |    +-- apple/
    |    |         +-- Info.plist    # macOS and iOS app settings
    |    |                           # (or Info.ios.plist + Info.macos.plist)
    |    |
    |    +-- android/                # Android app settings: files here will be deployed
    |    |   |-- AndroidManifest.xml # Optional manifest
    |    |   +-- res/
    |    |       +-- mipmap-xxxhdpi/ # Optional icons for different resolutions
    |    |           +-- ...         # Use Android Studio to generate them:
    |    |                           # right click on res/ => New > Image Asset
    |    +-- emscripten/
    |      |-- shell.emscripten.html # Emscripten shell file
    |      |                         #   (this file will be cmake "configured"
    |      |                         #    to add the name and favicon)
    |      +-- custom.js             # Any custom file here will be deployed
    |                                #   in the emscripten build folder

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

**If needed, change the assets folder location:**

Call `HelloImGui::SetAssetsFolder()` at startup. Or specify its location in CMake via `imgui_bundle_add_app(app_name file.cpp ASSETS_LOCATION "path/to/assets")`.


**Where to find the default assets**

You can [download the default assets as a zip file](https://traineq.org/ImGuiBundle/assets.zip).

Look at the folder [imgui_bundle/bindings/imgui_bundle/assets](https://github.com/pthom/imgui_bundle/tree/main/bindings/imgui_bundle/assets) to see its content.
