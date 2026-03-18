# mycobot_280_real_3dof

Real-robot-only MoveIt config for constrained 3-DOF arm operation.

## Goals
- Keep simulation config untouched.
- Reduce IK failures by using `position_only_ik` for `arm_3dof`.
- Keep this config opt-in via dedicated real launch files.

## Notes
- `arm_3dof` uses the first three arm joints.
- Joints 4-6 are marked as passive in this SRDF profile.
- Real MTC launch maps `eef_name=gripper_3dof` and uses `gripper_frame=mycobot_link4`.
