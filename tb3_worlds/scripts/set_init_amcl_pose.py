#!/usr/bin/env python3

"""
Script that sets the initial pose for AMCL.
"""
import time
import rclpy
import transforms3d
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped


class InitPosePublisher(Node):
    def __init__(self):
        super().__init__("init_pose_publisher")

        self.declare_parameter("x", value=0.6)
        self.declare_parameter("y", value=0.6)
        self.declare_parameter("theta", value=0.0)
        self.declare_parameter("cov", value=0.5**2)

        self.publisher = self.create_publisher(
            PoseWithCovarianceStamped, "/initialpose", 10
        )
        while self.publisher.get_subscription_count() == 0:
            self.get_logger().info("Waiting for AMCL Initial pose subscriber")
            time.sleep(1.0)

        self.timer = self.create_timer(0.3, self.timer_callback)

    def timer_callback(self):
        x = self.get_parameter("x").value
        y = self.get_parameter("y").value
        theta = self.get_parameter("theta").value
        cov = self.get_parameter("cov").value
        self.get_logger().info(
            f"Setting initial AMCL pose to [x: {x}, y: {y}, theta: {theta}] ..."
        )
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        quat = transforms3d.euler.euler2quat(0, 0, theta)
        msg.pose.pose.orientation.w = quat[0]
        msg.pose.pose.orientation.x = quat[1]
        msg.pose.pose.orientation.y = quat[2]
        msg.pose.pose.orientation.z = quat[3]
        msg.pose.covariance = [
            cov,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,  # Pos X
            0.0,
            cov,
            0.0,
            0.0,
            0.0,
            0.0,  # Pos Y
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,  # Pos Z
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,  # Rot X
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,  # Rot Y
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            cov,  # Rot Z
        ]
        self.publisher.publish(msg)


if __name__ == "__main__":
    # Start ROS node and action client
    rclpy.init()
    # Send initial pose to AMCL node
    pub = InitPosePublisher()

    # Run for predefined number of cycles
    number_of_cycles = 3
    cycle_count = 0
    while rclpy.ok() and cycle_count < number_of_cycles:
        rclpy.spin_once(pub)
        cycle_count += 1

    pub.destroy_node()
    rclpy.shutdown()
