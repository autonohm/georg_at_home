# maps

Map files for the pib robot "Georg". Each `.yaml` file describes one environment: the occupancy layout (walls, obstacles, boundary) and named points of interest (objects such as a door or a seat). The navigation servers read these files, and the Task Manager refers to them by path or name.

Currently included:

| File | Content |
|---|---|
| `Nav_Test.yaml` | Test arena (about 10 m × 9.5 m) with walls, a door, and a seat |

Maps are created with the map editor and exported as YAML. Do not edit the coordinates by hand unless you know what you are changing.

## File format

```yaml
map:
  resolution: 0.05          # cell size in m (informational, the server uses its own cell_size_m)
  origin:                   # bottom-left corner of the map in the map frame, [x, y] in m
  - -0.355
  - -3.387
  width_px: 200
  height_px: 189
  width_m: 10.0             # used to size the grid if no boundary polygon exists
  height_m: 9.45

objects:                    # named points of interest
  Door:
    type: door
    frame: map
    position: [0.264, 0.105]   # [x, y] in m, map frame
  Seat:
    type: seat
    frame: map
    position: [6.134, 0.093]

polygons:                   # geometry used for the occupancy grid
- name: Wall1
  type: obstacle            # see "Polygon types" below
  frame: map
  color: red
  points:                   # list of [x, y] vertices in m, map frame
  - [0.139, 2.083]
  - ...
```

### Polygon types

The rasterizer (`packages/pkg_navigation/navigate_server_pkg/navigate_server/grid_rasterizer.py`) handles the `type` field as follows:

| `type` | Effect on the grid |
|---|---|
| `boundary` | Defines the map extent. Everything outside this polygon is blocked. Only one boundary should exist. |
| `obstacle` | The area inside the polygon is filled solid (blocked). |
| anything else (e.g. a thin wall) | Only the edges of the polygon are blocked, one cell thick. |

If no `boundary` polygon exists, the extent is taken from `width_m` / `height_m` and `origin`. If those are missing too, the extent is the bounding box of all features plus 0.5 m padding.

### Objects

Each entry under `objects:` is looked up by its key. The Task Manager uses the key as the name in `NavigateObject`:

```python
NavigateObject("Seat", "/root/georg_maps/Nav_Test.yaml")
```

Only `position` is used (`[x, y]`). `type` and `frame` are informational.

## Using a map

### In the Docker image

This folder lives in `pkg_slam` as a debug fallback; the real map is built by SLAM. `pkg_navigation` and `pkg_task_manager` mount it read-only at `/root/georg_maps` (see their `docker-compose.yaml`). Missions reference maps with that absolute path.

### On a development machine

Copy the folder to a location of your choice and point the navigation server at it with its parameters:

```bash
ros2 run navigate_server navigate_action_server --ros-args \
  -p map_dir:=/home/<user>/georg_maps \
  -p default_map_name:=Nav_Test.yaml
```

Or set the environment variables `GEORG_MAP_DIR` and `GEORG_DEFAULT_MAP` before starting the node.

Map names passed in a goal can be a file name (resolved against `map_dir`) or an absolute path.

## Adding a new map

1. Export the map from the map editor as YAML, or write one following the format above.
2. Make sure there is exactly one `boundary` polygon, or set `width_m` and `height_m`.
3. Give every point of interest a unique key under `objects:`. The key is the name that missions use.
4. Check the result in a test run before a demo: plan a route with the Navigate action (see [pkg_navigation](../../pkg_navigation/README.md)) between the points you need.
5. Commit the file to this folder and reference it from the mission with its path.

## Known issues

- **Default map directory.** `DEFAULT_MAP_DIR` in `navigate_action_server.py` is `os.path.expanduser("root/georg_maps")`, which is a relative path. Set `GEORG_MAP_DIR` or the `map_dir` parameter explicitly.
- **Hard-coded paths in missions.** Missions use absolute paths such as `/root/georg_maps/Nav_Test.yaml` and `/home/giu/georg_maps/...`. Those work only on the machines that have these folders. Consider a single configurable map directory.
- **Only `Nav_Test.yaml` exists.** The Task Manager mission names `Seat` and `Door`, which are defined in this file only.
