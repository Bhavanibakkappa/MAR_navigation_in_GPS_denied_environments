# MAR Navigation in GPS-Denied Environments

## Project Overview

This project implements an autonomous mobile robot navigation system in a GPS-denied indoor environment using ROS 2 (Humble) and TurtleBot3.

The system integrates simulation, mapping, localization, path planning, and a control interface with safety and error handling.

---

## Team Members

* Bhuvi Prashanth – PES2UG23CS130
* Bhavani – PES2UG23CS125
* Lakshita Negi – PES2UG23CS301
* Kshirin Shetty – PES2UG23CS289

---

## System Architecture

```
Gazebo (Simulation)
        ↓
Robot State Publisher (TF)
        ↓
Map Server (/map)
        ↓
AMCL (map → odom)
        ↓
Nav2 (Planning + Control)
        ↓
Control Interface (User Interaction)
```

---

## Requirements

* Ubuntu 22.04
* ROS 2 Humble
* TurtleBot3 packages

### Install Dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-rviz2
```

---

## Important Configuration

Update the map file path before running:

```bash
nano ~/Downloads/MAR_navigation_in_GPS_denied_environments-main/my_indoor_map.yaml
```

Ensure:

```yaml
image: /home/lakshita/Downloads/MAR_navigation_in_GPS_denied_environments-main/my_indoor_map.pgm
```

---

## Running the Project

### Terminal 1 — Launch Gazebo with Indoor Environment

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger

gzserver --verbose -s libgazebo_ros_factory.so \
/to/your/path/indoor.world
```

### Terminal 2 — Robot State Publisher

```bash
source /opt/ros/humble/setup.bash

ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p use_sim_time:=true \
  -p robot_description:="$(cat /opt/ros/humble/share/turtlebot3_gazebo/urdf/turtlebot3_burger.urdf)"
```

---

### Terminal 3 — Spawn Robot

```bash
source /opt/ros/humble/setup.bash

ros2 run gazebo_ros spawn_entity.py \
  -topic robot_description \
  -entity turtlebot3_burger \
  -x 0.5 -y -1.0 -z 0.1
```

---

### Terminal 4 — Navigation + Localization (Nav2 + AMCL)

```bash
source /opt/ros/humble/setup.bash

ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=True \
  map:=/home/lakshita/Downloads/MAR_navigation_in_GPS_denied_environments-main/my_indoor_map.yaml \
  params_file:=/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml
```

---

### Terminal 5 — RViz

```bash
source /opt/ros/humble/setup.bash
ros2 run rviz2 rviz2
```

#### RViz Configuration

* Fixed Frame → `map`
* Add Displays:

  * Map → `/map`
  * RobotModel → `/robot_description`
  * LaserScan → `/scan`
  * Path → `/plan`

---

### Initialize Robot Pose

In RViz:

* Use **2D Pose Estimate**
* Click on robot location and set orientation

---

### Send Navigation Goal

In RViz:

* Use **2D Goal Pose**
* Select a destination on the map

---

## Control Interface (Interface & Error Handling)

### Run Interface

```bash
source /opt/ros/humble/setup.bash
python3 ~/Downloads/MAR_navigation_in_GPS_denied_environments-main/control_interface.py
```

---

## Features Implemented

### Navigation Control

* Send goal coordinates to robot

### Emergency Stop

* Manual trigger via command
* Automatic trigger based on obstacle proximity

### Collision Detection

* Uses LiDAR data to detect nearby obstacles

### Sensor Monitoring

* Detects loss of LiDAR or odometry data

### Invalid Input Handling

* Prevents goals outside valid boundaries

### Real-Time Feedback

* Displays robot position continuously

---

## Interface Commands

| Command | Description                 |
| ------- | --------------------------- |
| g       | Set goal (X, Y coordinates) |
| s       | Emergency stop              |
| r       | Reset system                |
| q       | Quit interface              |

---

## Challenges and Solutions

### Gazebo Performance Issues

* Issue: GUI freezing in virtualized environments
* Solution: Use headless mode (`gzserver`) instead of full GUI

### Missing Sensor Topics

* Issue: `/odom` and `/scan` not available
* Solution: Use TurtleBot3 Gazebo URDF with required plugins

### Map Not Displaying

* Issue: Incorrect file path or inactive node
* Solution: Correct YAML path and ensure map server is active

### TF Errors (Missing Frames)

* Issue: Missing `map → odom → base_link` chain
* Solution: Use `bringup_launch.py` which includes AMCL

### Robot Not Moving

* Issue: Localization not initialized
* Solution: Set initial pose using RViz

---

## Key Learnings

* Importance of TF tree consistency in ROS 2
* Role of AMCL in localization
* Difference between partial and full Nav2 launch configurations
* Handling system-level and sensor-level failures

---

## Future Improvements

* Graphical user interface for control
* Dynamic obstacle avoidance
* Multi-robot coordination
* Deployment on physical robot

---

## Conclusion

The project demonstrates a complete autonomous navigation pipeline in a GPS-denied indoor environment, integrating simulation, localization, planning, and safety mechanisms within ROS 2.

---
