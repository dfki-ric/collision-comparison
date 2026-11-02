cmake_minimum_required(VERSION 3.9.4)

project(collision-comparison VERSION 1.0.0)
set_property(GLOBAL PROPERTY CXX_STANDARD 20)

SET(BUILD_PYTHON_INTERFACE OFF)

# Optimizations for all C++ code built here (benchmark, HPP-FCL, Bullet): instructions of the host CPU, fast math,
# link-time optimization, and direct calls within the shared library of HPP-FCL
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native -ffast-math -flto=auto -fno-semantic-interposition")

add_executable(compare
        main.cpp
        jolt.cpp
        fcl.cpp
        fcl_original.cpp
        mujoco.cpp
        bullet.cpp
        utility.cpp
        collider.cpp
        libccd.cpp
        openGJK.cpp
        openGJK_impl.cpp
        support_mappings.cpp
)

include_directories(/usr/include/assimp)

# Json
include_directories(${CMAKE_SOURCE_DIR}/../json/include)

# Benchmark
include_directories(${CMAKE_SOURCE_DIR}/../nanobench/src/include)

# GLM
include_directories(${CMAKE_SOURCE_DIR}/../glm)

# Jolt
include_directories(${CMAKE_SOURCE_DIR}/../JoltPhysics)

target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../JoltPhysics/Build/Linux_Distribution/libJolt.a)

# FCL
find_package (Eigen3 REQUIRED NO_MODULE)
target_link_libraries (compare Eigen3::Eigen)

add_subdirectory(${CMAKE_SOURCE_DIR}/../hpp-fcl ${CMAKE_BINARY_DIR}/hpp-fcl)
include_directories(${CMAKE_SOURCE_DIR}/../hpp-fcl/include)
include_directories(${CMAKE_BINARY_DIR}/hpp-fcl/include)
target_link_libraries(compare ${CMAKE_BINARY_DIR}/hpp-fcl/src/libhpp-fcl.so)

# Bullet3 in double precision, like the other libraries (the benchmark must use the same precision as the library)
set(USE_DOUBLE_PRECISION ON CACHE BOOL "Use double precision" FORCE)
add_subdirectory(${CMAKE_SOURCE_DIR}/../bullet3 ${CMAKE_BINARY_DIR}/bullet)
target_compile_definitions(compare PRIVATE BT_USE_DOUBLE_PRECISION)
include_directories(${CMAKE_SOURCE_DIR}/../bullet3/src)

add_library(libbullet3collsion STATIC IMPORTED)
set_target_properties(libbullet3collsion PROPERTIES IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/bullet/src/Bullet3Collision/libBullet3Collision.a)
set_target_properties(libbullet3collsion PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbullet3collsion)

add_library(libbulletcollsion STATIC IMPORTED)
set_target_properties(libbulletcollsion PROPERTIES IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/bullet/src/BulletCollision/libBulletCollision.a)
set_target_properties(libbulletcollsion PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbulletcollsion)

add_library(libbulletlinearmath STATIC IMPORTED)
set_target_properties(libbulletlinearmath PROPERTIES IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/bullet/src/LinearMath/libLinearMath.a)
set_target_properties(libbulletlinearmath PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /usr/include)
target_link_libraries(compare libbulletlinearmath)

# libccd
include_directories(${CMAKE_SOURCE_DIR}/../libccd/build/src/)
include_directories(${CMAKE_SOURCE_DIR}/../libccd/src)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../libccd/build/src/libccd.a)

# FCL (the original, with its own GJK), static library built by scripts/repo_setup.sh (it cannot be built together
# with HPP-FCL: both define the target "uninstall")
include_directories(${CMAKE_SOURCE_DIR}/../fcl/include)
include_directories(${CMAKE_SOURCE_DIR}/../fcl/build/include)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../fcl/build/lib/libfcl.a)

# MuJoCo (built by scripts/repo_setup.sh as shared library: it contains its own libccd). Its GJK is not part of the
# public API, so the internal headers in src/ are needed as well.
include_directories(${CMAKE_SOURCE_DIR}/../mujoco/include)
include_directories(${CMAKE_SOURCE_DIR}/../mujoco/src)
target_link_libraries(compare ${CMAKE_SOURCE_DIR}/../mujoco/build/lib/libmujoco.so)


install(TARGETS compare DESTINATION bin)
