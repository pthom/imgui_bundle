
####################################################
# add_simple_external_library : will add a target
# when its folder structure is simple
####################################################
function(add_simple_external_library target_name target_subdir)
    add_library(${target_name} STATIC)
    target_link_libraries(${target_name} PUBLIC imgui)
    set(target_source_dir ${CMAKE_CURRENT_LIST_DIR}/external/${target_subdir})
    target_include_directories(${target_name} PUBLIC ${target_source_dir}/..)

    target_link_libraries(imgui_bundle PUBLIC ${target_name})
endfunction()

function(add_simple_external_library_with_sources target_name target_subdir)
    add_simple_external_library(${target_name} ${target_subdir})
    set(target_source_dir ${CMAKE_CURRENT_LIST_DIR}/external/${target_subdir})
    file(GLOB target_sources ${target_source_dir}/*.cpp ${target_source_dir}/*.h)
    target_sources(${target_name}  PRIVATE ${target_sources})
endfunction()
