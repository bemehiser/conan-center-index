cmake_minimum_required(VERSION 3.8.1)
project(cmake_wrapper LANGUAGES C)

if (APPLE)
    find_library(CORE_FOUNDATION_LIB CoreFoundation)
    if (NOT CORE_FOUNDATION_LIB)
        message(FATAL_ERROR "Core Foundation not found")
    endif ()

    set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY "libc++")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
    set(PLATFORM_DEP_LIBS -pthread pthread -lz ${CORE_FOUNDATION_LIB})

    add_definitions(-DCMAKE_FIND_FRAMEWORK=LAST)
endif ()

include(conanbuildinfo.cmake)
conan_basic_setup()

#set(CMAKE_CXX_STANDARD 11)
if (CMAKE_CXX_STANDARD LESS 11)
    message(ERROR "azure-storage-cpp requires C++11")
endif()

add_subdirectory(source_subfolder/Microsoft.WindowsAzure.Storage)
