

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
