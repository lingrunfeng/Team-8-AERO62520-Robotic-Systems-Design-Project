import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
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

    # SLAM backend selection: 'cartographer' or 'slam_toolbox' (default: slam_toolbox)
    slam_backend_arg = DeclareLaunchArgument(
        'slam_backend', default_value='slam_toolbox',
        description='SLAM backend to use: cartographer or slam_toolbox'
    )

    nav2_navigation_launch_path = os.path.join(
        get_package_share_directory('nav2_bringup'),
        'launch',
        'navigation_launch.py'
    )

    navigation_params_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'navigation.yaml'
    )

    # SLAM Toolbox config (backup)
    slam_toolbox_params_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'slam_toolbox_mapping.yaml'
    )

    # Cartographer config
    cartographer_config_dir = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config'
    )

    # Launch rviz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([pkg_team8_navigation, 'rviz', LaunchConfiguration('rviz_config')])],
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    # ==================== SLAM Toolbox (backup) ====================
    slam_toolbox_launch_path = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch_path),
        launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'slam_params_file': slam_toolbox_params_path,
        }.items(),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_backend'), "' == 'slam_toolbox'"]))
    )

    # ==================== Cartographer (default) ====================
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', 'cartographer.lua'
        ],
        remappings=[
            ('scan', '/scan'),
            ('odom', '/odom'),
            ('imu', '/imu'),  # 添加 IMU 话题 remap
        ],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_backend'), "' == 'cartographer'"]))
    )

    # Cartographer occupancy grid node (publishes /map)
    cartographer_occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'resolution': 0.05},
            {'publish_period_sec': 0.3}  # 加快发布频率
        ],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_backend'), "' == 'cartographer'"]))
    )

    # ==================== Navigation ====================
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_navigation_launch_path),
        launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': navigation_params_path,
        }.items()
    )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(rviz_launch_arg)
    launchDescriptionObject.add_action(rviz_config_arg)
    launchDescriptionObject.add_action(sim_time_arg)
    launchDescriptionObject.add_action(slam_backend_arg)
    launchDescriptionObject.add_action(rviz_node)
    
    # SLAM backends (conditional)
    launchDescriptionObject.add_action(slam_toolbox_launch)
    launchDescriptionObject.add_action(cartographer_node)
    launchDescriptionObject.add_action(cartographer_occupancy_grid_node)
    
    launchDescriptionObject.add_action(navigation_launch)

    return launchDescriptionObject
