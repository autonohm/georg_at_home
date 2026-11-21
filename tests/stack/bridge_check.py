"""Bridge to pib-backend seen from the stack: head camera arrives, speech/say, audio/listen.

    docker cp tests/stack/bridge_check.py georg-task_manager-1:/tmp/ \\
      && docker exec georg-task_manager-1 bash -c "source /ws/install/setup.bash && python3 /tmp/bridge_check.py"

Needs GEORG_WITH_PIB_BACKEND=1 ./projectctl.bash up sim and pib-backend running.
Warning: speech/say makes pib-backend speak (sound on the machine running pib-backend).
"""
import os
import threading
import time

from georg_speech_msgs.action import Listen, Say
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage

rclpy.init()
n = Node('bridge_check')
frames = []
n.create_subscription(CompressedImage, '/oak/rgb/image_raw/compressed',
                      lambda m: frames.append((time.monotonic(), len(m.data), m.format)),
                      qos_profile_sensor_data)
say = ActionClient(n, Say, 'speech/say')
listen = ActionClient(n, Listen, 'audio/listen')
threading.Thread(target=rclpy.spin, args=(n,), daemon=True).start()


def run(client, goal, timeout):
    if not client.wait_for_server(timeout_sec=10):
        return 'server not available'
    gh = client.send_goal_async(goal)
    end = time.monotonic() + timeout
    while not gh.done() and time.monotonic() < end:
        time.sleep(0.05)
    res = gh.result().get_result_async()
    while not res.done() and time.monotonic() < end:
        time.sleep(0.05)
    return res.result().result if res.done() else 'timeout'


time.sleep(6)
if frames:
    span = frames[-1][0] - frames[0][0]
    print(f'camera: {len(frames)} frames in {span:.1f} s ({len(frames) / max(span, 1e-3):.1f} Hz), '
          f'{frames[-1][1] / 1000:.0f} kB, format {frames[-1][2]}', flush=True)
else:
    print('camera: no frames', flush=True)
g = Say.Goal()
g.text = 'Test.'
t0 = time.monotonic()
print(f'say: {run(say, g, 40)} ({time.monotonic() - t0:.1f} s)', flush=True)
g = Listen.Goal()
g.mode, g.timeout_sec = Listen.Goal.MODE_SPEECH, 3.0
t0 = time.monotonic()
print(f'listen (nobody speaks, 3 s): {run(listen, g, 15)} ({time.monotonic() - t0:.1f} s)',
      flush=True)
os._exit(0)
