set(IMGUI_BUNDLE_CMAKE_PATH ${CMAKE_CURRENT_LIST_DIR} CACHE STRING "" FORCE)



###################################################################################################
# Store installable dependencies
###################################################################################################
function(ibd_add_installable_dependency dependency_name)
    set(IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES ${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES} ${dependency_name} CACHE INTERNAL "" FORCE)
    message(STATUS "Added installable dependency ${dependency_name}, IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES=${IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES}")
endfunction()

function(ibd_reset_installable_dependencies)
    set(IMGUI_BUNDLE_INSTALLABLE_DEPENDENCIES "" CACHE INTERNAL "" FORCE)
endfunction()

###################################################################################################
# Misc
###################################################################################################

# make imgui_bundle_add_app available
function(ibd_include_imgui_bundle_add_app)
    list(APPEND CMAKE_MODULE_PATH "${IMGUI_BUNDLE_CMAKE_PATH}")
    include(imgui_bundle_add_app)
endfunction()
