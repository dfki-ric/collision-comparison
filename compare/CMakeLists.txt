cmake_minimum_required(VERSION 2.8)

project(collision-comparison)

add_executable(compare main.cpp jolt.cpp)


# Jolt
add_subdirectory(${CMAKE_SOURCE_DIR}/../JoltPhysics/Build ${CMAKE_SOURCE_DIR}/build/Jolt)
include_directories(${CMAKE_SOURCE_DIR}/../JoltPhysics)

add_library(libjolt STATIC IMPORTED)
set_target_properties(libjolt PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/build/Jolt/libJolt.a)
set_target_properties(libjolt PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)

target_link_libraries(compare libjolt)



install(TARGETS compare DESTINATION bin)

