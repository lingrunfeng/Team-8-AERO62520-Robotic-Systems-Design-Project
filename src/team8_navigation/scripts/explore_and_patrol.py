#!/usr/bin/env python3
import os
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Empty


class ExploreAndPatrolNode(Node):
    def __init__(self):
        super().__init__('explore_and_patrol')
        self.phase = 'explore'
        self.phase_start = time.time()
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Empty, '/stop_exploration_topic', self._stop_exploration, 10)
        self.create_timer(1.0, self._tick)
        self.map_prefix = os.environ.get('TEAM8_MAP_PREFIX', '~/team8_phase1_maps/my_exploration_map')
        self.get_logger().info('simplified explore/patrol pipeline ready')

    def _stop_exploration(self, _msg):
        self.phase = 'patrol'
        self.phase_start = time.time()
        self.cmd_pub.publish(Twist())
        self.get_logger().info('exploration stop signal received')

    def _tick(self):
        elapsed = time.time() - self.phase_start
        if self.phase == 'explore':
            self.get_logger().info(f'exploration placeholder active ({elapsed:.0f}s)')
            return
        self.get_logger().info(f'patrol placeholder active ({elapsed:.0f}s)')


def main(args=None):
    rclpy.init(args=args)
    node = ExploreAndPatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
