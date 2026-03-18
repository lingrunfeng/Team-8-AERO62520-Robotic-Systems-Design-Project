#!/usr/bin/env python3
import json
import math
import time

import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray


class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        self.marker_pub = self.create_publisher(MarkerArray, '/patrol_markers', 10)
        self.tasks = self._load_tasks()
        self.current_index = 0
        self.create_timer(2.0, self._tick)
        self.get_logger().info(f'patrol tasks loaded: {len(self.tasks)}')

    def _load_tasks(self):
        task_path = (
            get_package_share_directory('team8_navigation')
            + '/maps/exploration_map_tasks.json'
        )
        try:
            with open(task_path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except Exception as exc:
            self.get_logger().warn(f'failed to load patrol tasks: {exc}')
            return []

        simplified = []
        for index, item in enumerate(data):
            obs = item.get('obs_pos', {})
            simplified.append(
                {
                    'id': item.get('id', index),
                    'x': float(obs.get('x', 0.0)),
                    'y': float(obs.get('y', 0.0)),
                    'yaw': float(obs.get('yaw', 0.0)),
                }
            )
        return simplified

    def _tick(self):
        self._publish_markers()
        if not self.tasks:
            return
        task = self.tasks[self.current_index]
        dist = math.hypot(task['x'], task['y'])
        self.get_logger().info(
            f"patrol placeholder -> target {task['id']} at "
            f"({task['x']:.2f}, {task['y']:.2f}), range={dist:.2f}"
        )
        self.current_index = (self.current_index + 1) % len(self.tasks)

    def _publish_markers(self):
        markers = MarkerArray()
        now = self.get_clock().now().to_msg()
        for index, task in enumerate(self.tasks):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = now
            marker.ns = 'tasks'
            marker.id = index
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = task['x']
            marker.pose.position.y = task['y']
            marker.pose.position.z = 0.1
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.15
            marker.scale.y = 0.15
            marker.scale.z = 0.15
            marker.color.a = 0.85
            marker.color.g = 1.0 if index == self.current_index else 0.3
            marker.color.b = 0.8 if index != self.current_index else 0.0
            markers.markers.append(marker)
        self.marker_pub.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
