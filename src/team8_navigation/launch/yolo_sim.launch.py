"""
YOLO Detection Launch File for Simulation

This launch file starts the YOLOv8 detection node for use with the LeoRover
simulation camera. It remaps the input topic to the Gazebo RGBD camera.

Usage:
  ros2 launch team8_navigation yolo_sim.launch.py

View results:
  rqt_image_view → select topic: /yolo/prediction/image
"""

import os
import torch
torch_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# Allow an external model path to be injected without hard-coding a personal workspace.
MODEL_PATH = os.environ.get('TEAM8_YOLO_MODEL', 'yolov11_seg.pt')


def generate_launch_description():
    
    # Declare launch argument for model selection
    model_arg = DeclareLaunchArgument(
        'model',
        default_value=MODEL_PATH,
        description='Path to YOLO model file'
    )
    
    model_path = LaunchConfiguration('model')
    
    print(f"[YOLO Sim Launch] Using model: {MODEL_PATH}")
    print(f"[YOLO Sim Launch] Device: {torch_device}")
    print(f"[YOLO Sim Launch] Subscribing to: /rgbd_camera/image")
    print(f"[YOLO Sim Launch] Publishing to: /yolo/prediction/image")
    
    # YOLOv8 node with topic remapping for simulation camera
    yolov8_node = Node(
        package='team8_yolov8',
        executable='yolov8_node',
        name='yolov8_sim_node',
        output='screen',
        parameters=[
            {'device': f'{torch_device}'},
            {'model': model_path},
            {'use_openvino': False},
            {'threshold': 0.25},
            {'enable_yolo': True},
        ],
        remappings=[
            # Remap from RealSense topic to Gazebo RGBD camera topic
            ('/camera/camera/color/image_raw', '/rgbd_camera/image'),
        ],
    )
    
    return LaunchDescription([
        model_arg,
        yolov8_node,
    ])
