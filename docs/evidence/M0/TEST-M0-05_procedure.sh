#!/usr/bin/env bash
# TEST-M0-05: read-only environment inventory. Each command is echoed with its exit status.
run() { echo "\$ $*"; bash -c "$*"; echo "[exit=$?]"; echo; }
echo "TEST-M0-05 environment inventory"; echo "date: $(date -Iseconds)"; echo "repo HEAD: $(git -C ~/Projects/smart-factory-amr rev-parse HEAD)"; echo
run "lsb_release -ds"
run "uname -r"
run "echo ROS_DISTRO=\$ROS_DISTRO RMW_IMPLEMENTATION=\${RMW_IMPLEMENTATION:-unset} ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-unset} ROS_AUTOMATIC_DISCOVERY_RANGE=\${ROS_AUTOMATIC_DISCOVERY_RANGE:-unset}"
run "ls -d /opt/ros/*"
run "gz sim --version | head -1"
run "python3 --version"
run "cmake --version | head -1"
run "dpkg-query -W -f='\${Package} \${Version} \${db:Status-Abbrev}\n' python3-colcon-common-extensions graphviz ros-jazzy-demo-nodes-cpp ros-jazzy-rviz2 ros-jazzy-ros-gz ros-jazzy-ros-gz-bridge ros-jazzy-ros-gz-sim ros-jazzy-xacro ros-jazzy-urdf ros-jazzy-robot-state-publisher ros-jazzy-joint-state-publisher ros-jazzy-joint-state-publisher-gui ros-jazzy-sdformat-urdf ros-jazzy-tf2-ros ros-jazzy-tf2-tools ros-jazzy-launch-ros ros-jazzy-rmw-fastrtps-cpp ros-jazzy-ros2-control ros-jazzy-ros2-controllers ros-jazzy-diff-drive-controller ros-jazzy-gz-ros2-control ros-jazzy-teleop-twist-keyboard ros-jazzy-slam-toolbox ros-jazzy-navigation2 ros-jazzy-nav2-bringup"
run "command -v check_urdf urdf_to_graphviz gz ros2"
