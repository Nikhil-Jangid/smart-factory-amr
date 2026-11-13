cmake_minimum_required(VERSION 3.8)
project(amr_description)

find_package(ament_cmake REQUIRED)

# Data-only package (DEC-017): install the robot model, launch files, and RViz
# configuration into share/amr_description. The .gitkeep placeholders only keep
# the empty directories in Git and are not installed.
install(
  DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
  PATTERN ".gitkeep" EXCLUDE
)

ament_package()
