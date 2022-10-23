set(CMAKE_CXX_STANDARD 20)
#message(FATAL_ERROR "PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE}" )
add_executable(pybind_native_debug_bundle pybind_native_debug.cpp)
#target_include_directories(pybind_native_debug PRIVATE ${CMAKE_CURRENT_LIST_DIR}/../example/external/pybind11/include)

find_package(pybind11 CONFIG REQUIRED)
target_link_libraries(pybind_native_debug_bundle PRIVATE pybind11::embed)
#target_include_directories(pybind_native_debug PRIVATE ${pybind11_INCLUDE_DIRS})
