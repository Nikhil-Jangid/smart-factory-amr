"""LOWOBS investigation launch (throwaway; copy of the FEAS-M3 gate launch). Mirrors amr_bringup/launch/sim.launch.py, with the prototype
sensors-on URDF, the gate world, headless rendering (-s --headless-rendering), and /scan + /imu bridges."""
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, Shutdown
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

URDF = os.environ['GATE_URDF']; WORLD = os.environ['GATE_WORLD']
HEADLESS = os.environ.get('GATE_HEADLESS', 'render')  # 'render' = -s --headless-rendering


def generate_launch_description():
    desc = open(URDF).read()
    cmd = ['gz', 'sim', '-r']
    if HEADLESS == 'render':
        cmd += ['-s', '--headless-rendering']
    cmd.append(WORLD)
    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': desc, 'use_sim_time': True}], output='screen')
    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                             '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                             '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU'] + [a for a in os.environ.get('GATE_BRIDGE_EXTRA', '').split() if a],
                  parameters=[{'use_sim_time': True}], output='screen')
    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-world', 'lowobs', '-topic', 'robot_description', '-name', 'amr'], output='screen')
    jsb = Node(package='controller_manager', executable='spawner',
               arguments=['joint_state_broadcaster', '--controller-manager-timeout', '60'], output='screen')
    ddc = Node(package='controller_manager', executable='spawner',
               arguments=['diff_drive_controller', '--controller-manager-timeout', '60'], output='screen')
    return LaunchDescription([
        rsp, bridge, ExecuteProcess(cmd=cmd, output='screen', on_exit=Shutdown()), spawn,
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[jsb])),
        RegisterEventHandler(OnProcessExit(target_action=jsb, on_exit=[ddc])),
    ])
