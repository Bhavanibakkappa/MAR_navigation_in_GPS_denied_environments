# 🤖 MAR Navigation in GPS-Denied Environments

> Autonomous mobile robot navigation in indoor GPS-denied environments using ROS 2 Humble, TurtleBot3, SLAM, and Nav2.

---

## 👥 Team Members

| Member | Name | SRN | Role |
|--------|------|-----|------|
| Member 1 | Bhuvi Prashanth | PES2UG23CS130 | Simulation Environment Setup |
| Member 2 | Kshirin Shetty | PES2UG23CS289 | Mapping & Localization (SLAM) |
| Member 3 | Bhavani | PES2UG23CS125 | Path Planning & Navigation |
| Member 4 | Lakshita Negi | PES2UG23CS301 | Interface & Error Handling |

---

## 📌 Project Overview

This project implements a complete autonomous navigation pipeline for a mobile robot operating in a GPS-denied indoor environment. The system uses:

- **Gazebo** for physics simulation
- **TurtleBot3 Burger** as the robot platform
- **SLAM Toolbox** for mapping
- **AMCL** for localization
- **Nav2** for path planning and obstacle avoidance
- **RViz2** for visualization
- A custom **Control Interface** for operator interaction and safety

---

## 🏗️ System Architecture

```
Gazebo Simulation (indoor.world)
           ↓
  Robot State Publisher (TF frames)
           ↓
     Map Server (/map)
           ↓
  AMCL Localization (map → odom)
           ↓
  Nav2 Path Planner + Controller
           ↓
  Control Interface 
     ↙         ↘
Goal Setting   Emergency Stop
Position Track  Sensor Watchdog
```

---

## ⚙️ Requirements

- Ubuntu 22.04
- ROS 2 Humble
- TurtleBot3 packages
- Python 3.10+

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
  ros-humble-rviz2 \
  ros-humble-teleop-twist-keyboard
```

Add to `~/.bashrc`:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```

---

## 📁 Repository Structure

```
MAR_navigation_in_GPS_denied_environments-main/
├── indoor.world              # Gazebo simulation world 
├── my_indoor_map.pgm         # Occupancy grid map 
├── my_indoor_map.yaml        # Map metadata
├── nav_bringup.py            # Navigation launch helper 
├── control_interface.py      # Control interface node 
└── README.md
```

---

## 🚀 Running the Project

> ⚠️ **Before starting:** Update the map path in `my_indoor_map.yaml` to match your username:
> ```yaml
> image: /home/YOUR_USERNAME/Downloads/MAR_navigation_in_GPS_denied_environments-main/my_indoor_map.pgm
> ```

Open a **separate terminal** for each step. Wait for each to fully start before proceeding.

---

### Terminal 1 — Gazebo Simulation

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

> ⏳ Wait ~30 seconds for Gazebo to fully load before proceeding.
> 💡 If Gazebo GUI freezes, kill it with `pkill -f gzclient` — the simulation continues headless.

---

### Terminal 2 — Navigation + Localization (Nav2 + AMCL)

```bash
source /opt/ros/humble/setup.bash
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=True \
  map:=/home/YOUR_USERNAME/Downloads/MAR_navigation_in_GPS_denied_environments-main/my_indoor_map.yaml \
  params_file:=/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml
```

> ⏳ Wait until you see AMCL and planner nodes initialize.

---

### Terminal 3 — RViz Visualization

```bash
source /opt/ros/humble/setup.bash
ros2 run rviz2 rviz2
```

**Configure RViz:**
1. Global Options → Fixed Frame → `map`
2. Add → `Map` → Topic: `/map` → Durability Policy: `Transient Local`
3. Add → `RobotModel` → Topic: `/robot_description`
4. Add → `LaserScan` → Topic: `/scan`
5. Add → `Path` → Topic: `/plan`

---

### Terminal 4 — Set Initial Robot Pose

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{
  header: {frame_id: 'map'},
  pose: {
    pose: {
      position: {x: -2.0, y: -0.5, z: 0.0},
      orientation: {w: 1.0}
    },
    covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0, 0.0, 0.06]
  }
}"
```

> Also click **2D Pose Estimate** in RViz and click on the robot's location to confirm.

---

### Terminal 5 — Control Interface 
```bash
source /opt/ros/humble/setup.bash
python3 ~/Downloads/MAR_navigation_in_GPS_denied_environments-main/control_interface.py
```

---

## 🖥️ Control Interface — Commands

| Command | Description |
|---------|-------------|
| `g` | Set navigation goal (enter X, Y coordinates) |
| `s` | Trigger emergency stop |
| `r` | Reset after emergency stop |
| `q` | Quit the interface |

---

## 🛡️Interface & Error Handling

The control interface (`control_interface.py`) implements the following:

### Goal Setting
- Sends navigation goals to Nav2 via `/goal_pose`
- Validates coordinates — rejects goals outside `±3.0m` boundary
- Blocks new goals when emergency stop is active

### Emergency Stop
- Manual stop via `s` command
- Cancels the active Nav2 goal by sending a goal to the robot's current position
- Publishes zero velocity to `/cmd_vel` to immediately halt motion
- Automatic stop triggers if an obstacle is detected within **0.2m**

### Collision Detection
- Subscribes to `/scan` (LiDAR)
- Filters invalid readings and finds minimum obstacle distance
- Auto-triggers emergency stop on proximity breach

### Sensor Watchdog
- Background timer runs every 3 seconds
- Detects if `/scan` or `/odom` topics stop publishing
- Logs critical error if sensor data is lost for more than 3 seconds

### Real-Time Position Tracking
- Subscribes to `/odom`
- Continuously displays robot X, Y position
- Position used by emergency stop to cancel goals accurately

---

## 🐛 Known Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Gazebo GUI freezes | High resource usage in VM | Kill `gzclient`, keep `gzserver` running |
| `Frame [map] does not exist` | AMCL not initialized | Set initial pose via Terminal 4 or RViz |
| `/odom` and `/scan` missing | Wrong URDF loaded | Use `turtlebot3_gazebo` URDF with plugins |
| Robot moves in wrong direction | Localization offset | Re-run initial pose command |
| Emergency stop not working | Nav2 overrides velocity | Interface cancels goal + publishes zero vel |

---

## 💡 Key Learnings

- TF tree consistency (`map → odom → base_link`) is critical for Nav2 to function
- `bringup_launch.py` must be used instead of `navigation_launch.py` to include AMCL
- Nav2 overrides direct `/cmd_vel` commands — goals must be cancelled to stop the robot
- Gazebo GUI is separate from `gzserver` — simulation works headless
- AMCL requires an initial pose estimate before it can publish the `map` frame

---

## 🔮 Future Improvements

- Graphical user interface (GUI) for the control interface
- Dynamic obstacle avoidance with real-time replanning
- SLAM-based live map building instead of static map
- Multi-robot coordination
- Deployment on a physical TurtleBot3 hardware

---
