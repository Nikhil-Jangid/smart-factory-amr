cmake_minimum_required(VERSION 3.8)
project(amr_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

# Command-freshness guard between /cmd_vel and the drive controller (DEC-029, TS-015).
add_executable(cmd_vel_guard src/cmd_vel_guard.cpp)
target_compile_features(cmd_vel_guard PUBLIC cxx_std_17)
ament_target_dependencies(cmd_vel_guard rclcpp geometry_msgs)
install(TARGETS cmd_vel_guard DESTINATION lib/${PROJECT_NAME})

# Controller and sensor-bridge configuration, launch files (DEC-023), the M3 RViz view (TEST-M3-10, DEC-035) and the
# M3 test world (DEC-034).
install(
  DIRECTORY config launch rviz worlds
  DESTINATION share/${PROJECT_NAME}
  PATTERN ".gitkeep" EXCLUDE
)

ament_package()
