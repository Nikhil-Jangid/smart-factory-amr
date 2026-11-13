cmake_minimum_required(VERSION 3.8)
project(amr_gazebo_plugins)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(gz_sim_vendor REQUIRED)
find_package(gz-sim REQUIRED)
find_package(gz_plugin_vendor REQUIRED)
find_package(gz-plugin REQUIRED COMPONENTS register)
find_package(gz_transport_vendor REQUIRED)
find_package(gz-transport REQUIRED)
find_package(gz_msgs_vendor REQUIRED)
find_package(gz-msgs REQUIRED)

# Gazebo-independent core of the DEC-038 IMU decimation (unit-tested, TEST-M3-13).
add_library(imu_block_averager STATIC src/imu_block_averager.cpp)
target_compile_features(imu_block_averager PUBLIC cxx_std_17)
set_target_properties(imu_block_averager PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_include_directories(imu_block_averager PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

# Gazebo Sim 8 system plugin (DEC-038): gz /imu_raw (1 kHz) -> gz /imu (100 Hz block mean).
# Loaded by the file name amr_imu_decimator_system from GZ_SIM_SYSTEM_PLUGIN_PATH (environment hook below).
add_library(amr_imu_decimator_system SHARED src/imu_decimator.cpp)
target_compile_features(amr_imu_decimator_system PUBLIC cxx_std_17)
target_link_libraries(amr_imu_decimator_system
  imu_block_averager
  gz-sim::core
  gz-plugin::register
  gz-transport::core
  gz-msgs::core)
install(TARGETS amr_imu_decimator_system LIBRARY DESTINATION lib)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/${PROJECT_NAME}.dsv.in")

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_imu_block_averager test/test_imu_block_averager.cpp)
  target_link_libraries(test_imu_block_averager imu_block_averager)
endif()

ament_package()
