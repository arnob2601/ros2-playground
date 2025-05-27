import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package share directory
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_race_track = get_package_share_directory('race_track')

    # Path to your robot's SDF file
    # IMPORTANT: Change 'your_robot_model_folder_name' and 'your_robot.sdf'
    # to your actual robot model folder and SDF file name.
    # Assumes your robot model is in race_track/models/my_bot/model.sdf
    robot_sdf_path = os.path.join(pkg_race_track, 'models', 'my_bot', 'model.sdf')
    # If your robot SDF is located elsewhere, provide the absolute path or adjust accordingly.
    # Example if it's in a globally installed package:
    # robot_sdf_path = os.path.join(get_package_share_directory('name_of_robot_pkg'), 'models', 'robot_name', 'model.sdf')


    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file_name = 'track.sdf'
    world_path = os.path.join(pkg_race_track, 'worlds', world_file_name)

    # Gazebo server
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_path, 'verbose': 'true'}.items()
    )

    # Gazebo client
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # Spawn Robot Entity
    # IMPORTANT: Change 'my_robot' to the desired name for your robot in simulation
    # Ensure your robot SDF model file is correctly specified in robot_sdf_path
    spawn_robot_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'my_robot', # Name of the robot in Gazebo
            '-file', robot_sdf_path,
            '-x', '0.0',        # Initial X position
            '-y', '-2.0',       # Initial Y position (e.g. on the track)
            '-z', '0.1',        # Initial Z position
            '-Y', '1.5707'      # Initial Yaw orientation (optional, radians)
        ],
        output='screen'
    )

    # Keyboard teleoperation node
    teleop_twist_keyboard_cmd = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',  # Launches in a new terminal window
        remappings=[('/cmd_vel', '/your_robot_diff_drive_controller/cmd_vel_unstamped')] # Or just '/cmd_vel'
        # IMPORTANT: Check your robot's differential drive plugin configuration.
        # It might subscribe to /cmd_vel or a namespaced topic like /diff_drive_controller/cmd_vel
        # or /your_robot_name/cmd_vel. Adjust the remapping accordingly.
        # If your robot's plugin subscribes to '/cmd_vel' directly, you can remove the remapping or use:
        # remappings=[('/cmd_vel', '/cmd_vel')]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        gzserver_cmd,
        gzclient_cmd,
        spawn_robot_cmd,
        teleop_twist_keyboard_cmd
    ])