"""M7 navigation with Nav2 on the saved M5 map (DEC-066, Task A).

Starts six nodes on simulation time and nothing else:
  planner_server       global planner (NavFn, DEC-068) on the global costmap (static layer from /map, DEC-062)
  controller_server    local controller (Regulated Pure Pursuit, DEC-067) on the local costmap; publishes cmd_vel_nav
  behavior_server      recovery behaviors: wait only (DEC-071)
  bt_navigator         runs the behavior trees (behavior_trees/, DEC-071) and offers the NavigateToPose and
                       NavigateThroughPoses actions
  velocity_smoother    limits cmd_vel_nav to the DEC-025 values and publishes it on /cmd_vel (DEC-070)
  lifecycle_manager_navigation  configures and activates the five servers in order (autostart)
Command path (DEC-070, DEC-029): controller_server and behavior_server -> cmd_vel_nav -> velocity_smoother ->
/cmd_vel (geometry_msgs/TwistStamped, simulation-time stamps) -> cmd_vel_guard (sim.launch.py) ->
/diff_drive_controller/cmd_vel. The velocity smoother is the only node that publishes /cmd_vel.
It runs beside the simulation and the M6 localization, which it does not start or change:
  terminal 1: ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf
  terminal 2: ros2 launch amr_bringup localization.launch.py
  terminal 3: ros2 launch amr_bringup navigation.launch.py
  terminal 4: rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/navigation.rviz --ros-args -p use_sim_time:=true
Start it after localization is active: the costmaps need the map and the map -> odom transform.
Goals: the "Nav2 Goal" tool in RViz, or the NavigateToPose action (/navigate_to_pose).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('amr_bringup')
    params_file = LaunchConfiguration('nav2_params_file')
    sim_time = {'use_sim_time': True}
    # The servers that publish velocity commands publish on cmd_vel_nav; only the smoother reaches /cmd_vel.
    to_smoother = [('cmd_vel', 'cmd_vel_nav')]
    servers = ['planner_server', 'controller_server', 'behavior_server', 'bt_navigator', 'velocity_smoother']
    return LaunchDescription([
        DeclareLaunchArgument(
            'nav2_params_file', default_value=PathJoinSubstitution([share, 'config', 'nav2.yaml']),
            description='Nav2 parameter file (default: the M7 file, DEC-066)'),
        Node(package='nav2_planner', executable='planner_server', name='planner_server', output='screen',
             parameters=[params_file, sim_time]),
        Node(package='nav2_controller', executable='controller_server', name='controller_server', output='screen',
             parameters=[params_file, sim_time], remappings=to_smoother),
        Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server', output='screen',
             parameters=[params_file, sim_time], remappings=to_smoother),
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator', output='screen',
             parameters=[params_file, sim_time, {
                 'default_nav_to_pose_bt_xml': PathJoinSubstitution(
                     [share, 'behavior_trees', 'navigate_to_pose.xml']),
                 'default_nav_through_poses_bt_xml': PathJoinSubstitution(
                     [share, 'behavior_trees', 'navigate_through_poses.xml'])}]),
        Node(package='nav2_velocity_smoother', executable='velocity_smoother', name='velocity_smoother',
             output='screen', parameters=[params_file, sim_time],
             remappings=[('cmd_vel', 'cmd_vel_nav'), ('cmd_vel_smoothed', '/cmd_vel')]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_navigation',
             output='screen', parameters=[{'node_names': servers, 'autostart': True}, sim_time]),
    ])
