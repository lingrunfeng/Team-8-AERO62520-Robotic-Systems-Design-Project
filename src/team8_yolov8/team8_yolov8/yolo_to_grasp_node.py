#!/usr/bin/env python3
import json
import select
import sys
import threading

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import String


class YoloToGraspNode(Node):
    def __init__(self):
        super().__init__('yolo_to_grasp_node')
        self.latest_items = {}
        self.pose_pub = self.create_publisher(PoseStamped, '/object_pose', 10)
        self.create_subscription(String, '/yolo/prediction/item_dict', self._items_cb, 10)
        self.create_timer(1.0, self._print_status)
        self.running = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()

    def _items_cb(self, msg):
        try:
            self.latest_items = json.loads(msg.data)
        except Exception:
            self.latest_items = {}

    def _print_status(self):
        self.get_logger().info(f'grasp bridge placeholder detections: {len(self.latest_items)}')

    def _input_loop(self):
        while self.running:
            try:
                if sys.stdin in select.select([sys.stdin], [], [], 0.5)[0]:
                    text = sys.stdin.readline().strip().lower()
                    if text == 'g':
                        self._publish_placeholder_pose()
                    elif text == 'q':
                        self.running = False
                        break
            except Exception:
                pass

    def _publish_placeholder_pose(self):
        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = 0.25
        pose.pose.position.y = 0.0
        pose.pose.position.z = 0.12
        pose.pose.orientation.w = 1.0
        self.pose_pub.publish(pose)
        self.get_logger().info('published simplified grasp pose')


def main(args=None):
    rclpy.init(args=args)
    node = YoloToGraspNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
