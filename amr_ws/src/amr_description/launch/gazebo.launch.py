"""M1 Gazebo Harmonic spawn of the AMR model in an empty world (TEST-M1-06, TEST-M1-07).

robot_state_publisher expands the Xacro model and publishes /robot_description;
ros_gz_sim `create` reads that topic and spawns the entity `amr` into the stock `empty`
world, which starts running immediately (-r). No /clock bridge, controllers, sensors or
damping: the wheel joints stay unactuated (frames_and_tf.md §4), as M1 requires.

The default spawn pose puts base_footprint (the ground point under the axle) on the
ground plane, so the wheels and caster start tangent to it (CALC-M1-04).

Gazebo is started with `gz sim` directly rather than through ros_gz_sim's gz_sim.launch.py:
that file runs gz through a shell, which does not forward SIGINT, so stopping the launch
left `gz sim server`/`gui` running (TS-009).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, Shutdown
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

SPAWN_POSE = ('x', 'y', 'z', 'roll', 'pitch', 'yaw')


def generate_launch_description():
    xacro_file = PathJoinSubstitution([FindPackageShare('amr_description'), 'urdf', 'amr.urdf.xacro'])
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    pose_args = [
        DeclareLaunchArgument(name, default_value='0.0',
                              description=f'Spawn pose of base_footprint in the world: {name} (m or rad)')
        for name in SPAWN_POSE
    ]

    # Stock empty world (gz-sim8 worlds/empty.sdf), started running (-r). No shell, so
    # SIGINT reaches gz and it stops its server and GUI; closing Gazebo ends the launch.
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', 'empty.sdf'],
        output='screen',
        on_exit=Shutdown(),
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-world', 'empty',
            '-topic', 'robot_description',
            '-name', 'amr',
            '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'), '-z', LaunchConfiguration('z'),
            '-R', LaunchConfiguration('roll'), '-P', LaunchConfiguration('pitch'), '-Y', LaunchConfiguration('yaw'),
        ],
        output='screen',
    )

    return LaunchDescription(pose_args + [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
        gazebo,
        spawn,
    ])
