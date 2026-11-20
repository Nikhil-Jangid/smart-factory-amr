"""M6 localization on the saved M5 map (DEC-056, DEC-060, Task A).

Starts four nodes on simulation time and nothing else:
  map_server         (nav2_map_server) serves the map file on /map (latched: transient-local QoS): the ROS-correct
                     map (DEC-055) for RViz and, from M7, Nav2
  map_server_amcl    (nav2_map_server) serves the AMCL-convention copy (origin + half a cell) on /map_amcl
                     (DEC-062, TS-045: Nav2 AMCL reads the origin as the centre of cell 0, ROS as its corner)
  amcl               (nav2_amcl) estimates the robot's pose on /map_amcl from /scan and the odometry TF;
                     publishes TF map -> odom, /amcl_pose (with covariance) and /particle_cloud
  lifecycle_manager  (nav2_lifecycle_manager) configures and activates both map servers, then amcl (autostart)
It runs beside the simulation, which it does not start or change (sim.launch.py is unchanged, DEC-060):
  terminal 1: ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf
  terminal 2: ros2 launch amr_bringup localization.launch.py
  terminal 3: rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/localization.rviz --ros-args -p use_sim_time:=true
SLAM (slam.launch.py) must not run at the same time: both would publish map -> odom.

M6 Task D option (DEC-057): ekf:=true also starts the robot_localization EKF (config/ekf.yaml), which fuses
the wheel-odometry velocities with the IMU yaw rate and publishes TF odom -> base_footprint and /odometry/filtered.
The simulation must then run with the fusion controllers file, which differs only by enable_odom_tf: false:
  terminal 1: ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf \
                controllers_file:=$(ros2 pkg prefix amr_bringup)/share/amr_bringup/config/controllers_ekf.yaml
  terminal 2: ros2 launch amr_bringup localization.launch.py ekf:=true
Default ekf:=false: unchanged Task A behaviour (the controller publishes odom -> base_footprint).

Nav2 nodes are lifecycle nodes: they start "unconfigured" and do nothing until a manager moves them through
configure and activate. The order matters: AMCL needs the map when it activates, so map_server comes first.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('amr_bringup')
    map_file = LaunchConfiguration('map')
    amcl_map_file = LaunchConfiguration('amcl_map')
    params_file = LaunchConfiguration('amcl_params_file')
    sim_time = {'use_sim_time': True}
    return LaunchDescription([
        DeclareLaunchArgument(
            'map', default_value=PathJoinSubstitution([share, 'maps', 'mapping_arena.yaml']),
            description='Map YAML to localize on (default: the M5 reference map, DEC-055 origin)'),
        DeclareLaunchArgument(
            'amcl_map', default_value=PathJoinSubstitution([share, 'maps', 'mapping_arena_amcl.yaml']),
            description='AMCL-convention copy of the map, served on /map_amcl (DEC-062)'),
        DeclareLaunchArgument(
            'amcl_params_file', default_value=PathJoinSubstitution([share, 'config', 'amcl.yaml']),
            description='AMCL parameter file (default: the M6 file, DEC-056)'),
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'yaml_filename': map_file}, sim_time]),
        Node(package='nav2_map_server', executable='map_server', name='map_server_amcl', output='screen',
             parameters=[{'yaml_filename': amcl_map_file, 'topic_name': 'map_amcl'}, sim_time]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
             parameters=[params_file, sim_time]),
        DeclareLaunchArgument(
            'ekf', default_value='false',
            description='true: also start the robot_localization EKF (odometry + IMU yaw rate, DEC-057); requires '
                        'sim.launch.py controllers_file:=.../controllers_ekf.yaml'),
        Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node', output='screen',
             parameters=[PathJoinSubstitution([share, 'config', 'ekf.yaml']), sim_time],
             condition=IfCondition(LaunchConfiguration('ekf'))),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_localization',
             output='screen',
             parameters=[{'node_names': ['map_server', 'map_server_amcl', 'amcl'], 'autostart': True}, sim_time]),
    ])
