"""Strip a recording down to raw sensor data for MCAP replay (plan P5).

Rules from the plan for MCAP replay with live SLAM:
- only raw sensors: SLAM output (/map, /map_metadata, slam_toolbox topics) is dropped
- the transform map -> odom is removed from /tf (SLAM publishes it again live)
- one source per topic: topics of the task manager and of the mocks are dropped too,
  they run live during the replay

    python3 mcap_raw_only.py <input.mcap or bag dir> <output dir> [--keep /topic ...]

Needs rosbag2_py (ROS 2 Jazzy) with the MCAP storage plugin.
"""

import argparse
import os
import sys

from rclpy.serialization import deserialize_message, serialize_message
import rosbag2_py
from tf2_msgs.msg import TFMessage

# robot namespace: EDU_ROBOT_NAMESPACE (default none, as in main)
_NS_NAME = os.environ.get('EDU_ROBOT_NAMESPACE', '').strip('/')
NS = f'/{_NS_NAME}' if _NS_NAME else ''
DEFAULT_KEEP = ['/tf', '/tf_static'] + [f'{NS}/{t}' for t in (
    'merged_scan', 'scan', 'odom', 'lidar1/scan', 'lidar2/scan', 'odom/wheel', 'imu')] + [
    # what the robot saw and did with its arms (head camera, detections of the camera,
    # pib joint states) - shown in Lichtblick during the replay
    '/oak/rgb/image_raw/compressed', '/joint_states', '/detections/face_detection_yunet_160x120',
    '/detections/yolov6n_coco_640x640', '/detections/hand_tracking']
DROP_FRAMES = {'map'}


def _drop_map_transforms(data: bytes):
    msg = deserialize_message(data, TFMessage)
    keep = [t for t in msg.transforms
            if t.header.frame_id.lstrip('/') not in DROP_FRAMES
            and t.child_frame_id.lstrip('/') not in DROP_FRAMES]
    if len(keep) == len(msg.transforms):
        return data
    if not keep:
        return None
    msg.transforms = keep
    return serialize_message(msg)


def filter_bag(src: str, dst: str, keep=None) -> dict:
    """Copy ``src`` to ``dst`` with raw sensor topics only. Returns counts per topic."""
    keep = set(keep or DEFAULT_KEEP)
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=src, storage_id='mcap'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=dst, storage_id='mcap'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))
    counts = {}
    for i, topic in enumerate(reader.get_all_topics_and_types()):
        if topic.name in keep:
            writer.create_topic(rosbag2_py.TopicMetadata(
                i, topic.name, topic.type, topic.serialization_format,
                topic.offered_qos_profiles))
            counts[topic.name] = 0
    while reader.has_next():
        name, data, stamp = reader.read_next()
        if name not in counts:
            continue
        if name == '/tf':
            data = _drop_map_transforms(data)
            if data is None:
                continue
        writer.write(name, data, stamp)
        counts[name] += 1
    del writer
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('src')
    parser.add_argument('dst')
    parser.add_argument('--keep', nargs='*', help='topics to keep (default: raw sensors)')
    args = parser.parse_args(argv)
    for name, n in sorted(filter_bag(args.src, args.dst, args.keep).items()):
        print(f'{n:7d}  {name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
