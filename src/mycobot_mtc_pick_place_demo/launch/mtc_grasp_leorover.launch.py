#!/usr/bin/env python3
"""
MTC Grasp Demo for LeoRover + MyCobot
Adapted from mycobot_mtc_pick_place_demo for LeoRover environment
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from launch.actions import OpaqueFunction


def generate_launch_description():
    # Package names
    pkg_bme_nav = 'team8_navigation'
    pkg_moveit_config = 'mycobot_moveit_config'
    pkg_mtc_demo = 'mycobot_mtc_pick_place_demo'
    
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Gazebo world file'
    )
    
    # 1. Start Gazebo + Robot (uses existing spawn_robot.launch.py)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare(pkg_bme_nav),
                'launch',
                'spawn_robot.launch.py'
            ])
        ]),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )
    
    # 2. MoveIt Configuration
    def configure_moveit_mtc(context):
        robot_name_str = 'mycobot_280'
        pkg_share_moveit_config = FindPackageShare(pkg_moveit_config).find(pkg_moveit_config)
        pkg_share_bme_nav = FindPackageShare(pkg_bme_nav).find(pkg_bme_nav)
        config_path = os.path.join(pkg_share_moveit_config, 'config', robot_name_str)
        
        # Config file paths
        joint_limits_file = os.path.join(config_path, 'joint_limits.yaml')
        kinematics_file = os.path.join(config_path, 'kinematics.yaml')
        moveit_controllers_file = os.path.join(config_path, 'moveit_controllers.yaml')  
        srdf_model = os.path.join(config_path, f'{robot_name_str}.srdf')
        pilz_limits = os.path.join(config_path, 'pilz_cartesian_limits.yaml')
        urdf_file = os.path.join(pkg_share_bme_nav, 'urdf', 'leo_sim.urdf.xacro')
        
        # Build MoveIt config with LeoRover-compatible files
        moveit_config = (
            MoveItConfigsBuilder(robot_name_str, package_name=pkg_moveit_config)
            .robot_description(file_path=urdf_file)
            .robot_description_semantic(file_path=os.path.join(config_path, 'leorover_mycobot.srdf'))
            .joint_limits(file_path=os.path.join(config_path, 'leorover_joint_limits.yaml'))
            .robot_description_kinematics(file_path=kinematics_file)
            .trajectory_execution(file_path=os.path.join(config_path, 'leorover_controllers.yaml'))
            .planning_pipelines(
                pipelines=["ompl", "pilz_industrial_motion_planner"],
                default_planning_pipeline="ompl"
            )
            .planning_scene_monitor(
                publish_robot_description=True,
                publish_robot_description_semantic=True,
                publish_planning_scene=True,
            )
            .pilz_cartesian_limits(file_path=pilz_limits)
            .to_moveit_configs()
        )
        
        # Move Group Node
        move_group_node = Node(
            package='moveit_ros_move_group',
            executable='move_group',
            output='screen',
            parameters=[
                moveit_config.to_dict(),
                {'use_sim_time': True}
            ],
        )
        
        # RViz Node
        rviz_config_file = PathJoinSubstitution([
            FindPackageShare(pkg_mtc_demo),
            'rviz',
            'mtc_demos.rviz'
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
        
        # MTC Grasp Pose Node
        mtc_params = {
            'execute': True,
            'object_type': "cylinder",
            'object_dimensions': [0.1, 0.0125],  # [height, radius]
            
            # Robot configuration
            'arm_group_name': "arm",
            'gripper_group_name': "gripper",
            'gripper_frame': "mycobot_link6_flange",
            'gripper_open_pose': "open",
            'gripper_close_pose': "half_closed",
            'arm_home_pose': "ready",
            'world_frame': "base_link",
            
           # Motion parameters
            'approach_object_min_dist': 0.005,
            'approach_object_max_dist': 0.20,
            'lift_object_min_dist': 0.01,
            'lift_object_max_dist': 0.20,
            
            # Grasp frame transform (lift grasp point above object center)
            'grasp_frame_transform_x': 0.0,
            'grasp_frame_transform_y': 0.0,
            'grasp_frame_transform_z': 0.08,  # Lift by 8cm to grasp from above
            
            # Top grasp orientation (gripper pointing down)
            'top_grasp_orientation': [1.0, 0.0, 0.0, 0.0],  # x, y, z, w
        }
        
        mtc_node = Node(
            package=pkg_mtc_demo,
            executable='mtc_grasp_pose_node',
            output='screen',
            parameters=[
                moveit_config.to_dict(),
                {'use_sim_time': True},
                mtc_params
            ],
        )
        
        return [move_group_node, rviz_node, mtc_node]
    
    moveit_setup = OpaqueFunction(function=configure_moveit_mtc)
    
    # Delay MoveIt to let Gazebo start first
    moveit_delayed = TimerAction(
        period=10.0,
        actions=[moveit_setup]
    )
    
    # Launch description
    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(world_arg)
    ld.add_action(gazebo_launch)
    ld.add_action(moveit_delayed)
    
    return ld
