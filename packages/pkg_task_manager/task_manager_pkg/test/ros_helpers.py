"""Shared helpers for the ROS integration tests (P2 mocks, P3 simulation).

Import only after checking that ROS is available (see the test modules).
"""

import os
import random
import signal
import subprocess
import tempfile
import threading
import time

from georg_task_manager_msgs.msg import MissionStatus
from georg_task_manager_msgs.srv import CancelMission, ListMissions, StartMission
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

# robot namespace as in main: none ('' -> /task_manager/start)
NS = ''
NS_ARG = NS or '/'  # value for -r __ns:=
FINAL = {MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.ABORTED}
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def _spawn(args, log_path, env, cwd=None):
    log = open(log_path, 'w')
    return subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env,
                            start_new_session=True, cwd=cwd)


def _stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


class Client:
    """Test-side ROS node: service clients and the latest status."""

    def __init__(self):
        self.node = rclpy.create_node('task_manager_test')
        qos = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                         reliability=ReliabilityPolicy.RELIABLE)
        self.statuses = []
        self._lock = threading.Lock()
        self.node.create_subscription(MissionStatus, f'{NS}/task_manager/status',
                                      self._on_status, qos)
        self.start_cli = self.node.create_client(StartMission, f'{NS}/task_manager/start')
        self.cancel_cli = self.node.create_client(CancelMission, f'{NS}/task_manager/cancel')
        self.list_cli = self.node.create_client(ListMissions, f'{NS}/task_manager/list_missions')
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)
        self._thread = threading.Thread(target=self.executor.spin, daemon=True)
        self._thread.start()

    def _on_status(self, msg):
        with self._lock:
            self.statuses.append(msg)

    def last(self):
        with self._lock:
            return self.statuses[-1] if self.statuses else None

    def call(self, client, request, timeout=15.0):
        assert client.wait_for_service(timeout_sec=timeout), 'service not available'
        future = client.call_async(request)
        end = time.monotonic() + timeout
        while not future.done():
            assert time.monotonic() < end, 'service call timed out'
            time.sleep(0.02)
        return future.result()

    def start(self, mission_id='mock_test'):
        return self.call(self.start_cli, StartMission.Request(mission_id=mission_id))

    def cancel(self):
        return self.call(self.cancel_cli, CancelMission.Request())

    def wait_for(self, predicate, timeout=30.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            msg = self.last()
            if msg is not None and predicate(msg):
                return msg
            time.sleep(0.05)
        raise AssertionError(f'timeout, last status: {self.last()}')

    def wait_final(self, app_id, timeout=30.0):
        return self.wait_for(lambda m: m.burr_app_id == app_id and m.state in FINAL, timeout)

    def close(self):
        self.executor.shutdown()
        self.node.destroy_node()


def make_env(profile):
    """Environment for the processes under test: own ROS domain, maps, Burr dir, profile."""
    tmp = tempfile.mkdtemp(prefix=f'georg_{profile}_test_')
    e = dict(os.environ,
             ROS_DOMAIN_ID=str(random.randint(60, 100)),
             GEORG_MAP_DIR=os.path.join(REPO, 'pkg_slam', 'maps'),
             GEORG_DEFAULT_MAP='Nav_Test.yaml',
             GEORG_BURR_STORAGE_DIR=os.path.join(tmp, 'burr'),
             GEORG_PROFILE=profile,
             PYTHONUNBUFFERED='1',
             RCUTILS_LOGGING_BUFFERED_STREAM='0')
    os.environ['ROS_DOMAIN_ID'] = e['ROS_DOMAIN_ID']
    e['TMP'] = tmp
    return e


def start_bridge(env):
    return _spawn(['ros2', 'run', 'task_manager', 'task_manager',
                   '--ros-args', '-r', f'__ns:={NS_ARG}'],
                  os.path.join(env['TMP'], 'bridge.log'), env)


def start_client():
    rclpy.init()
    c = Client()
    c.wait_for(lambda m: True, timeout=20)   # first status from the node
    return c


def stop_client(c):
    c.close()
    rclpy.shutdown()


class Mocks:
    def __init__(self, env):
        self.env = env
        self.proc = None
        self.log = ''

    def run(self, scenario):
        self.stop()
        self.log = os.path.join(self.env['TMP'], f'mock_{scenario}.log')
        self.proc = _spawn(['ros2', 'run', 'task_manager', 'mock_packages',
                            '--scenario', scenario, '--ros-args', '-r', f'__ns:={NS_ARG}'],
                           self.log, self.env)
        end = time.monotonic() + 20
        while 'mock packages ready' not in open(self.log).read():
            assert time.monotonic() < end, open(self.log).read()
            time.sleep(0.1)
        time.sleep(1.0)   # let discovery settle

    def text(self):
        return open(self.log).read()

    def wait_text(self, needle, count=1, timeout=5.0):
        """Wait until ``needle`` appears ``count`` times in the mock log (logs are async)."""
        end = time.monotonic() + timeout
        while self.text().count(needle) < count:
            assert time.monotonic() < end, f'{needle!r} x{count} not in mock log:\n{self.text()}'
            time.sleep(0.05)
        return self.text().count(needle)

    def stop(self):
        if self.proc is not None:
            _stop(self.proc)
            self.proc = None
            time.sleep(0.5)


class FakeLLMServer:
    """OpenAI-compatible HTTP endpoint with scripted answers (P6 integration tests).

    ``answers``: list of dicts/str, one per chat request; ``offline`` makes it unreachable.
    """

    def __init__(self):
        import http.server
        import json as _json

        server = self
        self.answers = []
        self.requests = []
        self.offline = False

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _send(self, code, body):
                data = _json.dumps(body).encode()
                self.send_response(code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if server.offline:
                    self._send(503, {'error': 'offline'})
                else:
                    self._send(200, {'data': [{'id': 'fake'}]})

            def do_POST(self):
                length = int(self.headers.get('Content-Length', 0))
                server.requests.append(_json.loads(self.rfile.read(length)))
                answer = server.answers.pop(0) if server.answers else {
                    'decision': 'abort', 'steps': [], 'reason': 'script empty'}
                content = answer if isinstance(answer, str) else _json.dumps(answer)
                self._send(200, {'choices': [{'message': {'role': 'assistant',
                                                          'content': content}}]})

        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = f'http://127.0.0.1:{self.httpd.server_address[1]}'
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
