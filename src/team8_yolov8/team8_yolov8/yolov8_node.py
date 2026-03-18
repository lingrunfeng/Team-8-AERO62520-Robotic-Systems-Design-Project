#!/usr/bin/env python3
import json

import rclpy
from cv_bridge import CvBridge
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String


class Yolov8Node(Node):
    def __init__(self):
        super().__init__('yolov8_node')
        self.bridge = CvBridge()
        self.latest_image = None
        self.pred_pub = self.create_publisher(Image, '/yolo/prediction/image', 10)
        self.item_pub = self.create_publisher(String, '/yolo/prediction/item_dict', 10)
        self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self._image_cb,
            qos_profile_sensor_data,
        )
        self.create_timer(0.2, self._publish_placeholder)

    def _image_cb(self, msg):
        self.latest_image = msg

    def _publish_placeholder(self):
        if self.latest_image is not None:
            self.pred_pub.publish(self.latest_image)
        payload = {
            'item_0': {
                'class': 'object',
                'conf': 0.5,
                'center_2d': [320.0, 240.0],
                'bbox': [280.0, 200.0, 360.0, 280.0],
                'has_mask': False,
            }
        }
        self.item_pub.publish(String(data=json.dumps(payload)))


def main(args=None):
    rclpy.init(args=args)
    node = Yolov8Node()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
