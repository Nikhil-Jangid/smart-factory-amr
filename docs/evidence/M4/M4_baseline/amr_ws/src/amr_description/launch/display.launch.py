"""M1 RViz display of the AMR model (TEST-M1-04, TEST-M1-05).

Starts robot_state_publisher with the expanded Xacro model, joint_state_publisher_gui
(sliders for the two continuous wheel joints), and RViz2 with rviz/display.rviz.
No simulation, controllers or sensors: those belong to later steps and milestones.
"""
from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('amr_description')
    xacro_file = PathJoinSubstitution([pkg_share, 'urdf', 'amr.urdf.xacro'])
    rviz_config = PathJoinSubstitution([pkg_share, 'rviz', 'display.rviz'])

    # value_type=str stops launch from trying to parse the URDF text as YAML.
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
        ),
    ])
