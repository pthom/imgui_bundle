# Part of ImGui Bundle - MIT License - Copyright (c) 2022-2024 Pascal Thomet - https://github.com/pthom/imgui_bundle
set(himgui_cmake_path ${CMAKE_CURRENT_LIST_DIR}/../external/hello_imgui/hello_imgui/hello_imgui_cmake)
set(HELLOIMGUI_CMAKE_PATH ${himgui_cmake_path} CACHE STRING "HELLOIMGUI_CMAKE_PATH" FORCE)
include(${himgui_cmake_path}/hello_imgui_add_app.cmake)
include(${himgui_cmake_path}/msvc/msvc_target_group.cmake)

#
# imgui_bundle_add_app is a helper function, similar to cmake's "add_executable"
#
# Usage:
#     imgui_bundle_add_app(app_name file1.cpp file2.cpp ...)
# Or:
#     imgui_bundle_add_app(app_name file1.cpp file2.cpp ... ASSETS_LOCATION "path/to/assets")
# (By default, ASSETS_LOCATION is "assets", which means that the assets will be searched in the "assets" folder,
# relative to the location of the CMakeLists.txt file)
#
# Features:
#     * It will automatically link the target to the required libraries (imgui_bundle, OpenGl, glad, etc)
#     * It will embed the assets (for desktop, mobile, and emscripten apps)
#     * It will perform additional customization (app icon and name on mobile platforms, etc)
function(imgui_bundle_add_app)
    set(args ${ARGN})
    list(GET args 0 app_name)

    hello_imgui_add_app(${args})
    target_link_libraries(${app_name} PRIVATE imgui_bundle)

	if (IMMVISION_OPENCV_WORLD_DLL AND WIN32)
		hello_imgui_get_real_output_directory(${app_name} real_output_directory)
		foreach(dll_file ${IMMVISION_OPENCV_WORLD_DLL})
			file(COPY ${dll_file} DESTINATION ${real_output_directory})
		endforeach()
	endif()

	# if (MSVC)
	# 	hello_imgui_msvc_target_group_sources(${app_name})
	# endif()
endfunction()
