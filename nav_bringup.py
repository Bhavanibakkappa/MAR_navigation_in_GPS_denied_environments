# Member 3 Master Command
# Run this to start Path Planning and the Map together
ros2 launch nav2_bringup bringup_launch.py \
    use_sim_time:=True \
    map:=/home/pes2ug23cs125/MAR_navigation_in_GPS_denied_environments/my_indoor_map.yaml \
    params_file:=/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml
    
    
1. Summary of Commands You Executed
You can provide this list to your team to show that the navigation environment is ready:

Step 1: Simulation Setup (Connecting Bhuvi's world to ROS 2):
gazebo --verbose -s libgazebo_ros_factory.so indoor.world

Step 2: Robot Identity (Telling the system it's a TurtleBot3):
ros2 run robot_state_publisher robot_state_publisher --ros-args -p use_sim_time:=true -p robot_description:="$(ros2 run xacro xacro /opt/ros/humble/share/turtlebot3_description/urdf/turtlebot3_burger.urdf)"

Step 3: Spawning (Dropping the robot into the walls):
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity turtlebot3_burger -x 0 -y 0 -z 0.1

Step 4: Path Planning Brain (Nav2):
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True

Step 5: Map Integration (Loading kShirin's map):
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=/home/pes2ug23cs125/MAR_navigation_in_GPS_denied_environments/my_indoor_map.yaml -p use_sim_time:=true

Step 6: Visualization:
ros2 run rviz2 rviz2
