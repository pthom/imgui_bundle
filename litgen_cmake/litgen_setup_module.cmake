function(litgen_setup_module
    # Parameters explanation, with an example: let's say we want to build binding for a C++ library named "foolib",
    bound_library               #  name of the C++ for which we build bindings ("foolib")
    python_native_module_name   #  name of the native python module that provides bindings (for example "_foolib")
    python_module_name          #  name of the standard python module that will import the native module (for example "foolib")
)
    target_link_libraries(${python_native_module_name} PRIVATE ${bound_library})

    # Set python_native_module_name install path to "." (required by skbuild)
    install(TARGETS ${python_native_module_name} DESTINATION .)

    # Copy the python module to the project dir post build (for editable mode)
    set(bindings_module_folder ${PROJECT_SOURCE_DIR}/bindings/${python_module_name})
    set(python_native_module_editable_location ${bindings_module_folder}/$<TARGET_FILE_NAME:${python_native_module_name}>)
    add_custom_target(
        ${python_module_name}_deploy_editable
        ALL
        COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${python_native_module_name}> ${python_native_module_editable_location}
        DEPENDS ${python_native_module_name}
    )
endfunction()