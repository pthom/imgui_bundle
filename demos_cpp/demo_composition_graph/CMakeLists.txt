add_demo_cpp(demo_compose_add demo_compose_add.main.cpp)

if (IMGUI_BUNDLE_WITH_IMMVISION)
    add_demo_cpp(demo_compose_image demo_compose_image.main.cpp)
endif()
