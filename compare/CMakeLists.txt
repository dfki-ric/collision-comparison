cmake_minimum_required(VERSION 2.8)

project(collision-comparison)


add_executable(compare 
  main.cpp 
  jolt.cpp 
  fcl.cpp 
  bullet.cpp
  utility.cpp collider.h collider.cpp)


# Json
include_directories(${CMAKE_SOURCE_DIR}/include/json/include)


# Jolt
add_subdirectory(${CMAKE_SOURCE_DIR}/../JoltPhysics/Build ${CMAKE_SOURCE_DIR}/build/Jolt)
include_directories(${CMAKE_SOURCE_DIR}/../JoltPhysics)

add_library(libjolt STATIC IMPORTED)
set_target_properties(libjolt PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/build/Jolt/libJolt.a)
set_target_properties(libjolt PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)

target_link_libraries(compare libjolt)


# FCL
find_package (Eigen3 3.3 REQUIRED NO_MODULE)
target_link_libraries (compare Eigen3::Eigen)

add_subdirectory(${CMAKE_SOURCE_DIR}/../hpp-fcl/ ${CMAKE_SOURCE_DIR}/build/fcl)
include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/include)
include_directories(${CMAKE_SOURCE_DIR}/build/fcl/include)

link_directories(${CMAKE_SOURCE_DIR}/build/fcl/)

target_link_libraries(compare ${CMAKE_SOURCE_DIR}/build/fcl/src/libhpp-fcl.so)


# Bullet3
add_subdirectory(${CMAKE_SOURCE_DIR}/../bullet3 ${CMAKE_SOURCE_DIR}/build/bullet)
set_property(DIRECTORY "${CMAKE_SOURCE_DIR}/../bullet3" APPEND
  PROPERTY COMPILE_DEFINITIONS "-DUSE_DOUBLE_PRECISION=ON -DBT_USE_EGL=ON -DCMAKE_BUILD_TYPE=Release")
include_directories(${CMAKE_SOURCE_DIR}/../bullet3/src)

add_library(libbullet3collsion STATIC IMPORTED)
set_target_properties(libbullet3collsion PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/build/bullet/src/Bullet3Collision/libBullet3Collision.a)
set_target_properties(libbullet3collsion PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbullet3collsion)

add_library(libbulletcollsion STATIC IMPORTED)
set_target_properties(libbulletcollsion PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/build/bullet/src/BulletCollision/libBulletCollision.a)
set_target_properties(libbulletcollsion PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbulletcollsion)

add_library(libbulletlinearmath STATIC IMPORTED)
set_target_properties(libbulletlinearmath PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/build/bullet/src/LinearMath/libLinearMath.a)
set_target_properties(libbulletlinearmath PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbulletlinearmath)

install(TARGETS compare DESTINATION bin)

