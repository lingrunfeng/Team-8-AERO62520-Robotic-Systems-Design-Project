cmake_minimum_required(VERSION 3.8)
project(mycobot_mtc_pick_place_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(mycobot_interfaces REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

add_executable(get_planning_scene_server src/get_planning_scene_server.cpp)
ament_target_dependencies(get_planning_scene_server
  moveit_msgs
  mycobot_interfaces
  rclcpp
  sensor_msgs
)

add_executable(mtc_grasp_pose_node src/mtc_grasp_pose_node.cpp)
ament_target_dependencies(mtc_grasp_pose_node
  geometry_msgs
  rclcpp
)

install(TARGETS
  get_planning_scene_server
  mtc_grasp_pose_node
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/send_object_pose.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  config
  launch
  rviz
  scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
