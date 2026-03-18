#include <memory>

#include <moveit_msgs/msg/planning_scene_world.hpp>
#include <mycobot_interfaces/srv/get_planning_scene.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>

class GetPlanningSceneServer : public rclcpp::Node
{
public:
  GetPlanningSceneServer() : Node("get_planning_scene_server")
  {
    service_ = create_service<mycobot_interfaces::srv::GetPlanningScene>(
      "/get_planning_scene_mycobot",
      [this](
        const std::shared_ptr<mycobot_interfaces::srv::GetPlanningScene::Request> request,
        std::shared_ptr<mycobot_interfaces::srv::GetPlanningScene::Response> response) {
        (void)request;
        response->scene_world = moveit_msgs::msg::PlanningSceneWorld();
        response->full_cloud = sensor_msgs::msg::PointCloud2();
        response->rgb_image = sensor_msgs::msg::Image();
        response->target_object_id = "placeholder_target";
        response->support_surface_id = "placeholder_support";
        response->success = false;
        RCLCPP_INFO(get_logger(), "placeholder planning scene service invoked");
      });
  }

private:
  rclcpp::Service<mycobot_interfaces::srv::GetPlanningScene>::SharedPtr service_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<GetPlanningSceneServer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
