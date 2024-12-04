###################################################################################################
# Specific build options for conda
###################################################################################################

function(ibd_conda_set_build_options_if_needed)
    if (DEFINED ENV{CONDA_BUILD})
        # With conda, we can rely on finding system libraries (from conda packages)
        set(IMGUI_BUNDLE_PYTHON_USE_SYSTEM_LIBS ON CACHE BOOL "" FORCE)
    endif()
endfunction()
