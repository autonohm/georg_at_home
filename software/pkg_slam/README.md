# slam

Simultaneous localisaton and mapping + lidar interface

Nodes:
- [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox) - SLAM implementation
- [rf2o_laser_odometry](https://github.com/MAPIRlab/rf2o_laser_odometry) - LiDAR odometrie
- [sick_scan_xd](https://github.com/SICKAG/sick_scan_xd/tree/3.8.0) - Daten aus LiDAR holen (unsere TIM571 verlieren support nach v3.8.0)
- [laser_scan_merger](https://github.com/BruceChanJianLe/laser_scan_merger.git) - 2 laser scans zu einem mergen

```mermaid
flowchart LR

/georg/lidar1/sick_scan[ /georg/lidar1/sick_scan ]:::node
/georg/lidar2/sick_scan[ /georg/lidar2/sick_scan ]:::node
/georg/CLaserOdometry2DNode[ /georg/CLaserOdometry2DNode ]:::node
/georg/laser_scan_merger_node[ /georg/laser_scan_merger_node ]:::node
/georg/slam_toolbox[ /georg/slam_toolbox ]:::node
/georg/laser_scan_merger_node[ /georg/laser_scan_merger_node ]:::node
/georg/slam_toolbox[ /georg/slam_toolbox ]:::node
/georg/merged_scan([ /georg/merged_scan<br>sensor_msgs/msg/LaserScan ]):::topic
/georg/odom/lidar([ /georg/odom/lidar<br>nav_msgs/msg/Odometry ]):::topic
/georg/lidar1/scan([ /georg/lidar1/scan<br>sensor_msgs/msg/LaserScan ]):::topic
/georg/lidar2/scan([ /georg/lidar2/scan<br>sensor_msgs/msg/LaserScan ]):::topic
/map([ /map<br>nav_msgs/msg/OccupancyGrid ]):::topic
/georg/pose([ /georg/pose<br>geometry_msgs/msg/PoseWithCovarianceStamped ]):::bugged
/georg/slam_toolbox/graph_visualization([ /georg/slam_toolbox/graph_visualization<br>visualization_msgs/msg/MarkerArray ]):::bugged
/georg/slam_toolbox/scan_visualization([ /georg/slam_toolbox/scan_visualization<br>sensor_msgs/msg/LaserScan ]):::bugged
/georg/slam_toolbox/update([ /georg/slam_toolbox/update<br>visualization_msgs/msg/InteractiveMarkerUpdate ]):::bugged
/map_metadata([ /map_metadata<br>nav_msgs/msg/MapMetaData ]):::bugged


/georg/lidar1/sick_scan --> /georg/lidar1/scan
/georg/lidar2/sick_scan --> /georg/lidar2/scan
/georg/merged_scan --> /georg/CLaserOdometry2DNode
/georg/lidar1/scan --> /georg/laser_scan_merger_node
/georg/lidar2/scan --> /georg/laser_scan_merger_node
/georg/merged_scan --> /georg/slam_toolbox
/map --> /georg/slam_toolbox
/georg/CLaserOdometry2DNode --> /georg/odom/lidar
/georg/laser_scan_merger_node --> /georg/merged_scan
/georg/slam_toolbox --> /map
/georg/slam_toolbox --> /georg/pose
/georg/slam_toolbox --> /georg/slam_toolbox/graph_visualization
/georg/slam_toolbox --> /georg/slam_toolbox/scan_visualization
/georg/slam_toolbox --> /georg/slam_toolbox/update
/georg/slam_toolbox --> /map_metadata


classDef node opacity:0.9,fill:#2A0,stroke:#391,stroke-width:4px,color:#fff
classDef action opacity:0.9,fill:#66A,stroke:#225,stroke-width:2px,color:#fff
classDef service opacity:0.9,fill:#3B8062,stroke:#3B6062,stroke-width:2px,color:#fff
classDef topic opacity:0.9,fill:#852,stroke:#CCC,stroke-width:2px,color:#fff
classDef main opacity:0.9,fill:#059,stroke:#09F,stroke-width:4px,color:#fff
classDef bugged opacity:0.9,fill:#933,stroke:#800,stroke-width:2px,color:#fff

```


> [!TIP]
> Visualize slam with `rviz2 -d georg_slam.rviz`
