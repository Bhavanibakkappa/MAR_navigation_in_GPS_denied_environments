#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from action_msgs.msg import GoalStatusArray
from lifecycle_msgs.srv import ChangeState
import threading
import time

class ControlInterface(Node):
    def __init__(self):
        super().__init__('control_interface')

        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.emergency_stopped = False
        self.last_scan_time = time.time()
        self.last_odom_time = time.time()
        self.robot_x = 0.0
        self.robot_y = 0.0

        self.create_timer(3.0, self.sensor_watchdog)
        self.get_logger().info('✅ Control Interface Node Started')

    def scan_callback(self, msg):
        self.last_scan_time = time.time()
        valid_ranges = [r for r in msg.ranges if r > 0.1 and r < msg.range_max]
        if not valid_ranges:
            self.get_logger().error('❌ SENSOR ERROR: LiDAR returning no valid data!')
            return
        min_dist = min(valid_ranges)
        if min_dist < 0.2 and not self.emergency_stopped:
            self.get_logger().warn(f'⚠️  COLLISION WARNING! Obstacle at {min_dist:.2f}m')
            self.emergency_stop(auto=True)

    def odom_callback(self, msg):
        self.last_odom_time = time.time()
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.get_logger().info(
            f'📍 Position: x={self.robot_x:.2f}, y={self.robot_y:.2f}',
            throttle_duration_sec=2.0
        )

    def sensor_watchdog(self):
        now = time.time()
        if now - self.last_scan_time > 3.0:
            self.get_logger().error('❌ SENSOR ERROR: LiDAR data lost!')
        if now - self.last_odom_time > 3.0:
            self.get_logger().error('❌ SENSOR ERROR: Odometry lost!')

    def send_goal(self, x, y):
        if self.emergency_stopped:
            print('❌ Cannot send goal — press [r] to reset emergency stop first.')
            return
        if abs(x) > 3.0 or abs(y) > 3.0:
            print(f'❌ INVALID GOAL: ({x}, {y}) is outside map boundaries!')
            return
        msg = PoseStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.orientation.w = 1.0
        self.goal_pub.publish(msg)
        self.get_logger().info(f'🎯 Goal sent: ({x}, {y})')

    def emergency_stop(self, auto=False):
        self.emergency_stopped = True
        # Send a new goal to current position to cancel Nav2 movement
        cancel_msg = PoseStamped()
        cancel_msg.header.frame_id = 'map'
        cancel_msg.header.stamp = self.get_clock().now().to_msg()
        cancel_msg.pose.position.x = self.robot_x
        cancel_msg.pose.position.y = self.robot_y
        cancel_msg.pose.orientation.w = 1.0
        self.goal_pub.publish(cancel_msg)
        # Also hammer cmd_vel with zeros
        stop = Twist()
        for _ in range(10):
            self.cmd_vel_pub.publish(stop)
        if auto:
            self.get_logger().warn('🚨 AUTO EMERGENCY STOP — obstacle too close!')
        else:
            self.get_logger().warn('🚨 MANUAL EMERGENCY STOP TRIGGERED')

    def reset(self):
        self.emergency_stopped = False
        print('✅ Emergency stop reset. Ready for new goals.')

def main():
    rclpy.init()
    node = ControlInterface()
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    print('\n=== MAR Robot Control Interface (Member 4) ===')
    print('[g] Set Goal   [s] Emergency Stop   [r] Reset   [q] Quit\n')

    while rclpy.ok():
        cmd = input('Command: ').strip().lower()
        if cmd == 'g':
            try:
                x = float(input('  Goal X: '))
                y = float(input('  Goal Y: '))
                node.send_goal(x, y)
            except ValueError:
                print('❌ Invalid input — enter numbers only.')
        elif cmd == 's':
            node.emergency_stop()
        elif cmd == 'r':
            node.reset()
        elif cmd == 'q':
            break
        else:
            print('❓ Unknown command. Use g / s / r / q')

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()