#!/usr/bin/env python3
"""
Simple MoveIt Demo for LeoRover + MyCobot
Just MoveIt Move Group + RViz, no MTC
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    # Package names
    pkg_bme_nav = 'team8_navigation'
    pkg_moveit_config = 'mycobot_moveit_config'
    
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )
    
    # 1. Start Gazebo + Robot
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
    
    # 2. Start MoveIt
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(pkg_moveit_config),
                'launch',
                'move_group.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )
    
    # Delay MoveIt to let Gazebo start first
    moveit_delayed = TimerAction(
        period=8.0,
        actions=[moveit_launch]
    )
    
    # Launch description
    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(gazebo_launch)
    ld.add_action(moveit_delayed)
    
    return ld
