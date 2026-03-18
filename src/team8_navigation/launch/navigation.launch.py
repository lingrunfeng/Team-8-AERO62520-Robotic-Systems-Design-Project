import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_team8_navigation = get_package_share_directory('team8_navigation')

    gazebo_models_path, ignore_last_dir = os.path.split(pkg_team8_navigation)
    os.environ["GZ_SIM_RESOURCE_PATH"] += os.pathsep + gazebo_models_path

    rviz_launch_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Open RViz'
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config', default_value='navigation.rviz',
        description='RViz config file'
    )

    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='True',
        description='Flag to enable use_sim_time'
    )

    # Path to the Slam Toolbox launch file
    nav2_localization_launch_path = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'launch',
        'localization_launch.py'
    )

    nav2_navigation_launch_path = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'launch',
        'navigation_launch.py'
    )

    localization_params_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'amcl_localization.yaml'
    )

    navigation_params_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'navigation.yaml'
    )

    map_file_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(get_package_share_directory('team8_navigation'), 'maps', 'exploration_map.yaml'),
        description='Full path to map file to load'
    )

    # Launch rviz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([pkg_team8_navigation, 'rviz', LaunchConfiguration('rviz_config')]),
                   '--ros-args', '--log-level', 'warn'],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    log_level_arg = DeclareLaunchArgument(
        'log_level', default_value='warn',
        description='Log level for Nav2 nodes'
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_localization_launch_path),
        launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': localization_params_path,
                'map': LaunchConfiguration('map'),
                'log_level': LaunchConfiguration('log_level')
        }.items()
    )

    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_navigation_launch_path),
        launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': navigation_params_path,
                'log_level': LaunchConfiguration('log_level')
        }.items()
    )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(log_level_arg)
    launchDescriptionObject.add_action(rviz_launch_arg)
    launchDescriptionObject.add_action(rviz_config_arg)
    launchDescriptionObject.add_action(sim_time_arg)
    launchDescriptionObject.add_action(rviz_node)
    launchDescriptionObject.add_action(map_file_arg)
    launchDescriptionObject.add_action(localization_launch)
    launchDescriptionObject.add_action(navigation_launch)

    return launchDescriptionObject
