-- Cartographer configuration for Leorover with RGBD camera
-- Optimized for stable mapping with reduced map jumping

include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "imu_frame",  -- 修复：URDF 中定义的是 imu_frame
  published_frame = "odom",
  odom_frame = "odom",
  provide_odom_frame = false,
  publish_frame_projected_to_2d = true,
  use_odometry = true,
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,
  lookup_transform_timeout_sec = 2.0,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio = 1.,
  odometry_sampling_ratio = 1.,
  fixed_frame_pose_sampling_ratio = 1.,
  imu_sampling_ratio = 1.,
  landmarks_sampling_ratio = 1.,
}

-- ============================================================
-- 2D Trajectory Builder Settings - Optimized for stability
-- ============================================================
MAP_BUILDER.use_trajectory_builder_2d = true
MAP_BUILDER.num_background_threads = 4

-- Laser scan settings
TRAJECTORY_BUILDER_2D.min_range = 0.12
TRAJECTORY_BUILDER_2D.max_range = 12.0
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 3.0
TRAJECTORY_BUILDER_2D.use_imu_data = true  -- 重新开启 IMU 支持

-- Accumulate more scans for stability
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 2

-- Motion filter - be more selective about when to add nodes
TRAJECTORY_BUILDER_2D.motion_filter.max_time_seconds = 0.5
TRAJECTORY_BUILDER_2D.motion_filter.max_distance_meters = 0.15
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(2.0)

-- Real time correlative scan matcher - reduce search window for stability
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.linear_search_window = 0.1
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.angular_search_window = math.rad(25.)  -- 扩大搜索窗口
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.translation_delta_cost_weight = 1e-1
TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.rotation_delta_cost_weight = 1e-2      -- 降低旋转惩罚

-- ============================================================
-- Ceres scan matcher - 滑移转向专用设置
-- 增加雷达权重，降低里程计权重，让激光雷达说了算
-- ============================================================
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.occupied_space_weight = 20.   -- 增加雷达权重（从10到20）
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 10.       -- 降低平移权重
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 1.           -- 大幅降低旋转权重（从40到1）

-- Submap settings
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 80
TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution = 0.05

-- ============================================================
-- Pose Graph Optimization - Reduce loop closure sensitivity
-- ============================================================

-- Optimize less frequently to reduce map jumping
POSE_GRAPH.optimize_every_n_nodes = 150

-- Constraint builder - be more strict about loop closures
POSE_GRAPH.constraint_builder.min_score = 0.65
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.7
POSE_GRAPH.constraint_builder.sampling_ratio = 0.2
POSE_GRAPH.constraint_builder.loop_closure_translation_weight = 1e3
POSE_GRAPH.constraint_builder.loop_closure_rotation_weight = 1e4

-- Fast correlative scan matcher for loop closure
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.linear_search_window = 5.
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.angular_search_window = math.rad(20.)
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.branch_and_bound_depth = 7

-- Ceres scan matcher for constraint refinement
POSE_GRAPH.constraint_builder.ceres_scan_matcher.occupied_space_weight = 20.
POSE_GRAPH.constraint_builder.ceres_scan_matcher.translation_weight = 10.
POSE_GRAPH.constraint_builder.ceres_scan_matcher.rotation_weight = 1.

-- ============================================================
-- Optimization problem - 滑移转向机器人防滑配置 (IMU版)
-- 有了 IMU，我们可以再次降低对里程计旋转的信任，依靠 IMU 和雷达
-- ============================================================
POSE_GRAPH.optimization_problem.odometry_translation_weight = 1e5
POSE_GRAPH.optimization_problem.odometry_rotation_weight = 1e2      -- 有 IMU 了，再次降低里程计权重 (防滑移)
POSE_GRAPH.optimization_problem.local_slam_pose_translation_weight = 1e5
POSE_GRAPH.optimization_problem.local_slam_pose_rotation_weight = 1e6

-- Global sampling and search settings
POSE_GRAPH.global_sampling_ratio = 0.001
POSE_GRAPH.global_constraint_search_after_n_seconds = 30.

return options
