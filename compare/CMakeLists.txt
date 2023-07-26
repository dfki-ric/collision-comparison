cmake_minimum_required(VERSION 3.0)

project(collision-comparison VERSION 1.0.0)
set_property(GLOBAL PROPERTY CXX_STANDARD 20)

add_executable(compare 
  main.cpp 
  jolt.cpp 
  fcl.cpp 
  bullet.cpp
  utility.cpp collider.h collider.cpp)

include_directories(/usr/include/assimp)

# Json
include_directories(${CMAKE_SOURCE_DIR}/include/json/include)


# Benchmark
include_directories(${CMAKE_SOURCE_DIR}/include/nanobench/src/include)


# Jolt
include_directories(${CMAKE_SOURCE_DIR}/../JoltPhysics)

#add_library(libjolt STATIC IMPORTED)
#IF(CMAKE_BUILD_TYPE MATCHES DEBUG)
#    set_target_properties(libjolt PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../JoltPhysics/Build/Linux_Debug/libJolt.a)
#else()
#    set_target_properties(libjolt PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../JoltPhysics/Build/Linux_Distribution/libJolt.a)
#endif()
#set_target_properties(libjolt PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
#target_link_libraries(compare libjolt)

target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../JoltPhysics/Build/Linux_Debug/libJolt.a)



# FCL
find_package (Eigen3 3.3 REQUIRED NO_MODULE)
target_link_libraries (compare Eigen3::Eigen)

include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/include)

#add_library(libfcl STATIC IMPORTED)
#IF(CMAKE_BUILD_TYPE MATCHES DEBUG)
#    include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/build/include)
#    set_target_properties(libfcl PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../hpp-fcl/build/src/libhpp-fcl.so)
#else()
#    include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/build_release/include)
#    set_target_properties(libfcl PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../hpp-fcl/build_release/src/libhpp-fcl.so)
#endif()
#set_target_properties(libfcl PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
#target_link_libraries(compare libfcl)

include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/build_release/include)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../hpp-fcl/build_release/src/libhpp-fcl.so)


# Bullet3
include_directories(${CMAKE_SOURCE_DIR}/../bullet3/src)

target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3Common/libBullet3Common.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3Collision/libBullet3Collision.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3Dynamics/libBullet3Dynamics.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3Geometry/libBullet3Geometry.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3OpenCL/libBullet3OpenCL_clew.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/Bullet3Serialize/Bullet2FileLoader/libBullet2FileLoader.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/BulletCollision/libBulletCollision.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/BulletDynamics/libBulletDynamics.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/BulletInverseDynamics/libBulletInverseDynamics.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/BulletSoftBody/libBulletSoftBody.a)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../bullet3/build/src/LinearMath/libLinearMath.a)

# libccd
include_directories(${CMAKE_SOURCE_DIR}/../libccd/src)
add_library(libccd STATIC IMPORTED)
set_target_properties(libccd PROPERTIES IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/../libccd/buid/src/libccd.so)
set_target_properties(libccd PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)


install(TARGETS compare DESTINATION bin)

