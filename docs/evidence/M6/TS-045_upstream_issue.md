<!-- TS-045 upstream report, posted 2026-11-20 as https://github.com/ros-navigation/navigation2/issues/6833 (exact text below; title on the first line). -->

# [nav2_amcl] Map origin is treated as the centre of cell 0, not its corner: half-cell (resolution/2) bias in the pose estimate

## Bug report

**Required Info:**

- Operating System:
  - Ubuntu 24.04
- Computer:
  - x86_64 desktop (12 threads)
- ROS2 Version:
  - Jazzy, apt binaries
- Version or commit hash:
  - ros-jazzy-nav2-amcl 1.3.14-1noble.20261105.140844. The same code is on `main` today (checked 2026-11-20).
- DDS implementation:
  - Fast DDS (rmw_fastrtps_cpp 8.4.5, the default)

#### Steps to reproduce issue

You can see this by reading the code. `nav_msgs/MapMetaData` defines `origin` as the pose of cell (0,0): its lower-left **corner**. So in ROS, the centre of cell `i` is at `origin.x + (i + 0.5) * resolution`. `nav2_costmap_2d` follows this (`Costmap2D::mapToWorld`: `wx = origin_x_ + (mx + 0.5) * resolution_`).

`nav2_amcl` does not:

```cpp
// nav2_amcl/src/amcl_node.cpp, AmclNode::convertMap
map->origin_x = map_msg.info.origin.position.x + (map->size_x / 2) * map->scale;
map->origin_y = map_msg.info.origin.position.y + (map->size_y / 2) * map->scale;

// nav2_amcl/include/nav2_amcl/map/map.hpp
#define MAP_WXGX(map, i) (map->origin_x + ((i) - map->size_x / 2) * map->scale)
#define MAP_GXWX(map, x) (floor((x - map->origin_x) / map->scale + 0.5) + map->size_x / 2)
```

Substituting the first into the second gives `MAP_WXGX(i) = info.origin.x + i * scale`. AMCL places the centre of cell `i` where ROS places its corner. `MAP_GXWX` rounds (`floor(... + 0.5)`) and so agrees with that convention. Every occupied cell, and therefore the likelihood field, sits half a cell too low in x and in y. Because the scan is matched against that field, the pose estimate is biased by the same amount.

Measured reproduction (simulation, Gazebo Harmonic):
1. Use a map whose `origin` is correct under the ROS corner convention (resolution 0.05 m). We checked it against the simulated world geometry: the walls fit with a best-fit offset of (0.000, 0.000) m.
2. Run `nav2_amcl` (`likelihood_field`, 2D LiDAR) with exact simulated odometry. Drive a fixed route with 11 stops.
3. At each stop, compare `map -> base_footprint` with the simulator's ground-truth pose.
4. Repeat with the same map, with only `origin` moved by `+resolution/2` in x and y.

#### Expected behavior

With exact odometry and a correct map, the pose error has no constant offset.

#### Actual behavior

- **Original map:** the error settles on a nearly constant vector of about (−0.022, −0.032) m, 37–41 mm at the stops after the filter converges, with heading error < 0.1°. The prediction for 0.05 m cells is (−0.025, −0.025) m.
- **Origin moved by +0.025 m:** the constant offset disappears. The maximum error over the 11 stops falls from 41.0 mm to 11.2 mm, the AMCL parameters being the same.

#### Reproduction instructions

As above. A unit-level check: give `convertMap` a map whose only occupied cell is `(i, j)`. Compare `MAP_WXGX(map, i)` with `info.origin.x + (i + 0.5) * info.resolution`. They differ by `resolution / 2`.

#### Additional information

**Possible fix.** Adding half a cell in `convertMap` makes both macros follow the ROS convention:

```cpp
map->origin_x = map_msg.info.origin.position.x + (map->size_x / 2 + 0.5) * map->scale;
map->origin_y = map_msg.info.origin.position.y + (map->size_y / 2 + 0.5) * map->scale;
```

With this, `MAP_WXGX(i) = info.origin.x + (i + 0.5) * scale` (the cell centre), and `MAP_GXWX(x) = floor((x - info.origin.x) / scale)` (the containing cell), which is the same as `Costmap2D::worldToMap`. The same `origin_x`/`origin_y` are used where AMCL publishes or reads map positions, for example the free-space list used for uniform pose generation. Those uses would then also match the ROS convention.

**Compatibility.** SLAM Toolbox (2.8.5, `vis_utils::toNavMap`) appears to make the opposite error. Karto's grid offset is the centre of cell 0 (`CoordinateConverter::WorldToGrid` rounds), and it is copied unchanged into `OccupancyGrid.info.origin`. Maps saved from SLAM Toolbox are therefore half a cell off for every corner-convention consumer: costmaps, RViz. For AMCL the two errors cancel. So AMCL users with unmodified SLAM Toolbox maps currently get correct results, and a change to AMCL alone would shift them by half a cell. You may want to coordinate it with SLAM Toolbox or document it in the migration notes. I can open the matching SLAM Toolbox issue if that helps.

**Workaround in use.** We give AMCL its own copy of the map, with `origin` moved by `+resolution/2`, on a separate topic (`map_topic`). Every other consumer keeps the correct map.

I'm happy to open a PR with the fix and a unit test if you agree with the approach.

