#include <geometry_msgs/msg/pose_stamped.hpp>
#include <rclcpp/rclcpp.hpp>

class MtcGraspPoseNode : public rclcpp::Node
{
public:
  MtcGraspPoseNode() : Node("mtc_grasp_pose_node")
  {
    sub_ = create_subscription<geometry_msgs::msg::PoseStamped>(
      "/object_pose", 10,
      [this](const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        count_++;
        last_pose_ = *msg;
        RCLCPP_INFO(
          get_logger(),
          "placeholder grasp node received pose #%zu at [%.3f, %.3f, %.3f]",
          count_,
          last_pose_.pose.position.x,
          last_pose_.pose.position.y,
          last_pose_.pose.position.z);
      });
  }

private:
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_;
  geometry_msgs::msg::PoseStamped last_pose_;
  std::size_t count_{0};
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MtcGraspPoseNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
