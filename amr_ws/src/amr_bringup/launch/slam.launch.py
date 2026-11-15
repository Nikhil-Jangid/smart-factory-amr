"""M5 online SLAM (DEC-048, DEC-050, Task A).

Starts only SLAM Toolbox (online async mapping) with this package's config/slam_toolbox.yaml, on simulation time.
It runs beside the simulation, which it does not start or change (sim.launch.py is unchanged, DEC-050):
  terminal 1: ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf
  terminal 2: ros2 launch amr_bringup slam.launch.py
  terminal 3: rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/mapping.rviz --ros-args -p use_sim_time:=true

It includes the installed slam_toolbox online_async_launch.py rather than copying it: that file starts
async_slam_toolbox_node as a lifecycle node and drives it through configure and activate (autostart), which is
how SLAM Toolbox 2.8 expects to be started. Inputs: /scan and TF odom -> base_footprint -> laser_frame.
Outputs: /map (nav_msgs/OccupancyGrid), TF map -> odom, /slam_toolbox/graph_visualization (pose graph markers).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = LaunchConfiguration('slam_params_file')
    return LaunchDescription([
        DeclareLaunchArgument(
            'slam_params_file',
            default_value=PathJoinSubstitution([FindPackageShare('amr_bringup'), 'config', 'slam_toolbox.yaml']),
            description='SLAM Toolbox parameter file (default: the M5 file, DEC-048)'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py'])),
            launch_arguments={'slam_params_file': params_file, 'use_sim_time': 'true'}.items()),
    ])
