"""M2 simulation of the AMR under ros2_control in Gazebo Harmonic (TEST-M2-03 to -10).

Starts Gazebo (stock empty world, 1 kHz physics), robot_state_publisher with the model expanded
with use_ros2_control:=true (DEC-023), the /clock bridge, the spawn, the command-freshness guard
(/cmd_vel -> /diff_drive_controller/cmd_vel, DEC-029), and then the controller spawners in order:
joint_state_broadcaster, then diff_drive_controller. Every ROS node runs on simulation time.
Command publishers use /cmd_vel (geometry_msgs/TwistStamped, simulation-time stamps, DEC-026); only
the guard publishes to the controller input.

Gazebo is started with `gz sim` directly, as in amr_description/launch/gazebo.launch.py, so SIGINT
reaches it and no server is left running (TS-009). headless:=true runs the server only (-s).

M3 options (DEC-034). The defaults reproduce the M2 launch exactly: `gz sim -r [-s] empty.sdf`,
world name `empty`, and the model expanded with use_sensors:=false (byte-identical to M2, TEST-M3-02).
  sensors:=true  expands the model with use_sensors:=true (LiDAR and IMU, amr.sensors.xacro) and starts
                 the /scan and /imu bridge (config/sensor_bridge.yaml). Headless, Gazebo then also gets
                 --headless-rendering, which gpu_lidar needs without a display (feasibility gate G1).
  world:=<file>  the Gazebo world. A bare file name found in this package's worlds/ directory (e.g.
                 sensor_test.sdf) is resolved there; anything else is passed to gz sim unchanged
                 (default: the stock empty.sdf). The spawn uses the <world name> read from the file.
M4 option: controllers_file:=<path> loads another ros2_control parameter file. It exists for the
TEST-M4-09 test-only calibration overrides (DEC-043); the default is the package's config/controllers.yaml.
M7 option (DEC-075; screen recordings only): gui_config:=<file> starts the Gazebo GUI with that layout
(`gz sim --gui-config`). A bare name is resolved in this package's config/ directory, e.g.
gui_config:=gazebo_gui_capture.config (no side panels, 960 x 1000 px). Default empty: the command is unchanged
(`gz sim -r [-s] <world>`) and Gazebo loads the user's own GUI layout. Ignored with headless:=true.
M3 sensor tests: ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf
Keyboard control (TEST-M2-09), in a second terminal:
  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
    -p stamped:=true -p frame_id:=base_footprint -p use_sim_time:=true -r cmd_vel:=/cmd_vel
"""
import os
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler,
                            SetLaunchConfiguration, Shutdown)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

SPAWN_POSE = ('x', 'y', 'z', 'roll', 'pitch', 'yaw')


def is_true(context, name):
    return LaunchConfiguration(name).perform(context).lower() in ('true', '1')


def resolve_world(context):
    """Return (path passed to gz sim, world name for the spawn)."""
    world = LaunchConfiguration('world').perform(context)
    packaged = os.path.join(get_package_share_directory('amr_bringup'), 'worlds', world)
    if not os.path.isabs(world) and os.path.isfile(packaged):
        world = packaged
    if os.path.isfile(world):
        name = ET.parse(world).getroot().find('world').get('name')
    else:  # a world resolved by gz sim itself, e.g. the stock empty.sdf (world name 'empty')
        name = os.path.splitext(os.path.basename(world))[0]
    return world, name


def gazebo_process(context):
    world, world_name = resolve_world(context)
    cmd = ['gz', 'sim', '-r']
    if is_true(context, 'headless'):
        cmd.append('-s')
        if is_true(context, 'sensors'):
            cmd.append('--headless-rendering')
    gui_config = LaunchConfiguration('gui_config').perform(context)
    if gui_config and not is_true(context, 'headless'):  # DEC-075: recordings only; default leaves cmd unchanged
        packaged = os.path.join(get_package_share_directory('amr_bringup'), 'config', gui_config)
        cmd += ['--gui-config', packaged if os.path.isfile(packaged) else gui_config]
    cmd.append(world)
    return [SetLaunchConfiguration('world_name', world_name),
            ExecuteProcess(cmd=cmd, output='screen', on_exit=Shutdown())]


def generate_launch_description():
    xacro_file = PathJoinSubstitution([FindPackageShare('amr_description'), 'urdf', 'amr.urdf.xacro'])
    controllers_file = LaunchConfiguration('controllers_file')
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' use_ros2_control:=true controllers_file:=', controllers_file,
                 ' use_sensors:=', LaunchConfiguration('sensors')]),
        value_type=str)
    sensor_bridge_file = PathJoinSubstitution([FindPackageShare('amr_bringup'), 'config', 'sensor_bridge.yaml'])

    args = [DeclareLaunchArgument('headless', default_value='false',
                                  description='true: Gazebo server only, no GUI (scripted tests)'),
            DeclareLaunchArgument('sensors', default_value='false',
                                  description='true: LiDAR and IMU in the model, /scan and /imu bridged (M3)'),
            DeclareLaunchArgument('world', default_value='empty.sdf',
                                  description='Gazebo world: a file in amr_bringup/worlds (e.g. sensor_test.sdf), '
                                              'a path, or a world gz sim resolves (default: stock empty.sdf)'),
            DeclareLaunchArgument('controllers_file',
                                  default_value=PathJoinSubstitution(
                                      [FindPackageShare('amr_bringup'), 'config', 'controllers.yaml']),
                                  description='ros2_control parameter file (default: this package\'s '
                                              'config/controllers.yaml). M4 test-only overrides (TEST-M4-09) only')]
    args += [DeclareLaunchArgument('gui_config', default_value='',
                                   description='Gazebo GUI layout file for screen recordings (DEC-075): a file in '
                                               'amr_bringup/config (e.g. gazebo_gui_capture.config) or a path; '
                                               'default empty = the user\'s own layout, command unchanged')]
    args += [
        DeclareLaunchArgument(name, default_value='0.0',
                              description=f'Spawn pose of base_footprint in the world: {name} (m or rad)')
        for name in SPAWN_POSE
    ]

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    # Gazebo -> ROS sensor topics (DEC-034); only with sensors:=true.
    sensor_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='sensor_bridge',
        parameters=[{'config_file': sensor_bridge_file, 'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('sensors')),
        output='screen',
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', LaunchConfiguration('world_name'),
            '-topic', 'robot_description',
            '-name', 'amr',
            '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'), '-z', LaunchConfiguration('z'),
            '-R', LaunchConfiguration('roll'), '-P', LaunchConfiguration('pitch'), '-Y', LaunchConfiguration('yaw'),
        ],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager-timeout', '60'],
        output='screen',
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager-timeout', '60'],
        output='screen',
    )

    # Rejects commands whose stamp is not within cmd_vel_timeout of simulation time (stale, future,
    # zero, or before the clock is valid) and clamps forwarded stamps to arrival time (TS-015).
    cmd_vel_guard = Node(
        package='amr_bringup',
        executable='cmd_vel_guard',
        parameters=[controllers_file],
        remappings=[('cmd_vel_in', '/cmd_vel'), ('cmd_vel_out', '/diff_drive_controller/cmd_vel')],
        output='screen',
    )

    return LaunchDescription(args + [
        robot_state_publisher,
        clock_bridge,
        sensor_bridge,
        cmd_vel_guard,
        OpaqueFunction(function=gazebo_process),  # also sets world_name, used by the spawn below
        spawn,
        # The plugin creates controller_manager when the model is spawned; then activate
        # the broadcaster first and the drive controller second.
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[joint_state_broadcaster_spawner])),
        RegisterEventHandler(OnProcessExit(target_action=joint_state_broadcaster_spawner,
                                           on_exit=[diff_drive_spawner])),
    ])
