#!/usr/bin/env python3
"""
MoveIt + LeoRover integrated demo
Uses corrected SRDF with mycobot_ prefix
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    # Packages
    pkg_bme_nav = 'team8_navigation'
    pkg_moveit_config = 'mycobot_moveit_config'
    
    # Arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )
    
    # 1. Gazebo + LeoRover
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(pkg_bme_nav),
                'launch',
                'spawn_robot.launch.py'
            ])
        ]),
        launch_arguments={
            'world': 'empty.sdf',
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )
    
    # 2. MoveIt with LeoRover SRDF
    robot_name_str = 'mycobot_280'
    pkg_share_moveit_config = FindPackageShare(pkg_moveit_config).find(pkg_moveit_config)
    pkg_share_bme_nav = FindPackageShare(pkg_bme_nav).find(pkg_bme_nav)
    config_path = os.path.join(pkg_share_moveit_config, 'config', robot_name_str)
    
    # Use LeoRover-compatible SRDF and controllers
    srdf_model = os.path.join(config_path, 'leorover_mycobot.srdf')
    urdf_file = os.path.join(pkg_share_bme_nav, 'urdf', 'leo_sim.urdf.xacro')
    controllers_file = os.path.join(config_path, 'leorover_controllers.yaml')
    
    moveit_config = (
        MoveItConfigsBuilder(robot_name_str, package_name=pkg_moveit_config)
        .robot_description(file_path=urdf_file)
        .robot_description_semantic(file_path=srdf_model)
        .joint_limits(file_path=os.path.join(config_path, 'leorover_joint_limits.yaml'))
        .robot_description_kinematics(file_path=os.path.join(config_path, 'kinematics.yaml'))
        .trajectory_execution(file_path=controllers_file)
        .planning_pipelines(
            pipelines=["ompl", "pilz_industrial_motion_planner"],
            default_planning_pipeline="ompl"
        )
        .planning_scene_monitor(
            publish_robot_description=True,
            publish_robot_description_semantic=True,
            publish_planning_scene=True,
        )
        .pilz_cartesian_limits(file_path=os.path.join(config_path, 'pilz_cartesian_limits.yaml'))
        .to_moveit_configs()
    )
    
    # Move Group
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            moveit_config.to_dict(),
            {'use_sim_time': True}
        ],
    )
    
    # RViz
    rviz_config_file = PathJoinSubstitution([
        FindPackageShare(pkg_moveit_config),
        'rviz',
        'moveit.rviz'
    ])
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[
            moveit_config.to_dict(),
            {'use_sim_time': True}
        ],
    )
    
    # Delay MoveIt
    moveit_delayed = TimerAction(
        period=10.0,
        actions=[move_group_node, rviz_node]
    )
    
    # Launch description
    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(gazebo_launch)
    ld.add_action(moveit_delayed)
    
    return ld
