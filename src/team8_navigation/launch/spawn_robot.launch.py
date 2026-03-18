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
        'rviz_config', default_value='rviz.rviz',
        description='RViz config file'
    )

    world_arg = DeclareLaunchArgument(
        'world', default_value='empty.sdf',
        description='Name of the Gazebo world file to load'
    )

    model_arg = DeclareLaunchArgument(
        'model', default_value='leo_sim.urdf.xacro',
        description='Name of the URDF description to load'
    )

    x_arg = DeclareLaunchArgument(
        'x', default_value='2.5',
        description='x coordinate of spawned robot'
    )

    y_arg = DeclareLaunchArgument(
        'y', default_value='1.5',
        description='y coordinate of spawned robot'
    )

    yaw_arg = DeclareLaunchArgument(
        'yaw', default_value='-1.5707',
        description='yaw angle of spawned robot'
    )

    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='True',
        description='Flag to enable use_sim_time'
    )

    # Define the path to your URDF or Xacro file
    urdf_file_path = PathJoinSubstitution([
        pkg_team8_navigation,  # Replace with your package name
        "urdf",
        LaunchConfiguration('model')  # Replace with your URDF or Xacro file
    ])

    gz_bridge_params_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'gz_bridge.yaml'
    )

    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_team8_navigation, 'launch', 'world.launch.py'),
        ),
        launch_arguments={
        'world': LaunchConfiguration('world'),
        }.items()
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

    # Spawn the URDF model using the `/world/<world_name>/create` service
    spawn_urdf_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "leo_rover",
            "-topic", "robot_description",
            "-x", LaunchConfiguration('x'), "-y", LaunchConfiguration('y'), "-z", "0.5", "-Y", LaunchConfiguration('yaw')  # Initial spawn position
        ],
        output="screen",
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    # Node to bridge /cmd_vel and /odom
    gz_bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args', '-p',
            f'config_file:={gz_bridge_params_path}'
        ],
        output="screen",
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    # Node to bridge /cmd_vel and /odom
    gz_image_bridge_node = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=[
            "/camera/image",
            "/rgbd_camera/image",
        ],
        output="screen",
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time'),
             'camera.image.compressed.jpeg_quality': 75},
        ],
    )

    # Relay node to republish camera_info to /camera_info
    relay_camera_info_node = Node(
        package='topic_tools',
        executable='relay',
        name='relay_camera_info',
        output='screen',
        arguments=['camera/camera_info', 'camera/image/camera_info'],
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': Command(['xacro', ' ', urdf_file_path]),
             'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ]
    )

    trajectory_node = Node(
        package='team8_trajectory_server',
        executable='team8_trajectory_server',
        name='team8_trajectory_server',
        parameters=[{
            'reference_frame_id': 'odom',  # Start with odom, will be changed to map when SLAM starts
            'robot_frame_id': 'base_link',
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            os.path.join(pkg_team8_navigation, 'config', 'ekf.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
             ]
    )

    # Path to controller config
    controller_config_path = os.path.join(
        get_package_share_directory('team8_navigation'),
        'config',
        'mycobot_controllers.yaml'
    )
    
    # Controller spawner for joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager',
                  '--param-file', controller_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    # Controller spawner for arm_controller
    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller', '--controller-manager', '/controller_manager',
                  '--param-file', controller_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    # Controller spawner for gripper_action_controller
    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_action_controller', '--controller-manager', '/controller_manager',
                  '--param-file', controller_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    # Arm hold pose node - keeps arm in fixed upright position
    # To use coordinate control mode instead, comment this out and uncomment the next node
    arm_hold_pose_node = Node(
        package='team8_navigation',
        executable='arm_hold_pose.py',
        name='arm_hold_pose',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    # Arm coordinate controller node - for grasp testing
    # Uncomment this when testing coordinate-based grasping
    # arm_coordinate_controller_node = Node(
    #     package='team8_navigation',
    #     executable='arm_coordinate_controller.py',
    #     name='arm_coordinate_controller',
    #     output='screen',
    #     parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    # )

    launchDescriptionObject = LaunchDescription()

    #launchDescriptionObject.add_action(rviz_launch_arg)
    #launchDescriptionObject.add_action(rviz_config_arg)
    launchDescriptionObject.add_action(world_arg)
    launchDescriptionObject.add_action(model_arg)
    launchDescriptionObject.add_action(x_arg)
    launchDescriptionObject.add_action(y_arg)
    launchDescriptionObject.add_action(yaw_arg)
    launchDescriptionObject.add_action(sim_time_arg)
    launchDescriptionObject.add_action(world_launch)
    #launchDescriptionObject.add_action(rviz_node)
    launchDescriptionObject.add_action(spawn_urdf_node)
    launchDescriptionObject.add_action(gz_bridge_node)
    launchDescriptionObject.add_action(gz_image_bridge_node)
    launchDescriptionObject.add_action(relay_camera_info_node)
    launchDescriptionObject.add_action(robot_state_publisher_node)
    launchDescriptionObject.add_action(trajectory_node)
    launchDescriptionObject.add_action(ekf_node)
    launchDescriptionObject.add_action(joint_state_broadcaster_spawner)
    launchDescriptionObject.add_action(arm_controller_spawner)
    launchDescriptionObject.add_action(gripper_controller_spawner)
    # launchDescriptionObject.add_action(arm_hold_pose_node)  # Disabled for MTC compatibility
    # Uncomment next line when testing coordinate control:
    # launchDescriptionObject.add_action(arm_coordinate_controller_node)

    return launchDescriptionObject
