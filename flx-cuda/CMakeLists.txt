# CMakeLists.txt
# flx-cuda: GPU-accelerated priority scheduler
# Build with: mkdir build && cd build && cmake .. && make
# Requires: CUDA toolkit (nvcc), CMake 3.13+
#
# Author: SuperInstance
# License: MIT

cmake_minimum_required(VERSION 3.13)
project(flx-cuda CXX C)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 14)

# Find CUDA
find_package(CUDA REQUIRED)

# flx-cuda library (the GPU scheduler)
add_library(flx_cuda STATIC src/flx_cuda.cu)
target_include_directories(flx_cuda PUBLIC src)
target_link_libraries(flx_cuda PUBLIC ${CUDA_LIBRARIES})

# Test executable
enable_testing()
add_executable(test_flx_cuda tests/test_flx_cuda.cpp)
target_link_libraries(test_flx_cuda PRIVATE flx_cuda)

# Run tests with ctest
add_test(NAME flx_cuda_tests COMMAND test_flx_cuda)
