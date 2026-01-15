# Application Settings

ImGui applications usually store settings such as window positions, opened windows (etc.), in a file "imgui.ini".
HelloImGui and ImmApp extend this functionality by storing additional settings such as application layouts, status bar settings, and user-defined custom settings.

## Settings location

By default, the settings are stored in a ini file whose named is derived from the window title (i.e. `runnerParams.appWindowParams.windowTitle`).
This is convenient when developing, but not so much when deploying the app.

You can finely define where they are stored by filling `runnerParams.iniFolderType` and `runnerParams.iniFilename`.

**runnerParams.iniFolderType**

Choose between: `CurrentFolder`, `AppUserConfigFolder`, `AppExecutableFolder`, `HomeFolder`, `TempFolder` and `DocumentsFolder`.

:::{note}
AppUserConfigFolder corresponds to `...\[Username]\AppData\Roaming` under Windows, `~/.config` under Linux, `~/Library/Application Support` under macOS or iOS
:::

**runnerParams.iniFilename**

This will be the name of the ini file in which the settings will be stored. It can include a subfolder, in which case it will be created under the folder defined by runnerParams.iniFolderType.

:::{note}
if left empty, the name of the ini file will be derived from appWindowParams.windowTitle.
:::


## Settings content

The settings file contains, standard ImGui settings (window position, size, etc.), as well as additional settings defined by HelloImGui:

* Application status: app window location, opened windows, status bar settings, etc. See members named remember_xxx in the [parameters doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/doc_params.md) for a complete list.
* Settings for each application layout (see [video](https://www.youtube.com/watch?v=XKxmz__F4ow) for an example)

## Store custom settings

You may store additional user settings in the application settings. This is provided as a convenience only, and it is not intended to store large quantities of text data. See [related doc](https://github.com/pthom/hello_imgui/blob/master/src/hello_imgui/doc_api.md#store-user-settings-in-the-ini-file) for more details.
