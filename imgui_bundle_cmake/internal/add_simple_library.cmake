set(IMGUIBUNDLE_EXTERNAL_PATH ${IMGUI_BUNDLE_PATH}/external CACHE STRING "" FORCE)


####################################################
# add_simple_external_library : will add a target
# when its folder structure is simple
####################################################
function(add_simple_external_library lib_target_name lib_folder)
    add_library(${lib_target_name} STATIC)
    target_link_libraries(${lib_target_name} PUBLIC imgui)

    set(lib_parent_folder ${IMGUIBUNDLE_EXTERNAL_PATH}/${lib_folder})
    target_include_directories(${lib_target_name} PUBLIC $<BUILD_INTERFACE:${lib_parent_folder}>)
    target_link_libraries(imgui_bundle INTERFACE ${lib_target_name})

    if(IMGUI_BUNDLE_INSTALL_CPP)
        ibd_add_installable_dependency(${lib_target_name})
    endif()
endfunction()

function(add_simple_external_library_with_sources lib_target_name lib_folder)
    add_simple_external_library(${lib_target_name} ${lib_folder})
    set(lib_parent_folder ${IMGUIBUNDLE_EXTERNAL_PATH}/${lib_folder})

    set(lib_inner_folder ${IMGUIBUNDLE_EXTERNAL_PATH}/${lib_folder}/${lib_folder})
    file(GLOB lib_sources ${lib_inner_folder}/*.cpp ${lib_inner_folder}/*.h)

    target_sources(${lib_target_name} PRIVATE ${lib_sources})
    hello_imgui_msvc_target_group_sources(${lib_target_name})

    if(IMGUI_BUNDLE_INSTALL_CPP)
        file(GLOB lib_headers ${lib_inner_folder}/*.h)
        install(FILES ${lib_headers} DESTINATION include/${lib_folder})
    endif()
endfunction()


function(add_additional_sources_to_external_library lib_target_name lib_folder additional_sources_folder)
    set(lib_additional_folder ${IMGUIBUNDLE_EXTERNAL_PATH}/${lib_folder}/${additional_sources_folder})
    file(GLOB lib_additional_sources ${lib_additional_folder}/*.cpp ${lib_additional_folder}/*.h)
    target_sources(${lib_target_name} PRIVATE ${lib_additional_sources})
endfunction()
