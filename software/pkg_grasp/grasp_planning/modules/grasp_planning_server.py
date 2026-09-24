#!/usr/bin/env python3
import os
import sys
import time
import json
import signal
import subprocess

import rclpy
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from std_msgs.msg import String, Float32
from geometry_msgs.msg import Point

from grasp_planning.action import GraspPlanning


class GraspPlannerServer(Node):

    def __init__(self):
        super().__init__('GraspPlannerServer')
        self._callback_group = ReentrantCallbackGroup()
        self._action_server = ActionServer(
            self, GraspPlanning, 'grasp_planning',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._callback_group,
        )
        self._goal_running = False

    def goal_callback(self, goal_request):
        if not goal_request.goal_content == 'goal_content':
            return GoalResponse.REJECT
        if self._goal_running:
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT  # without this, is_cancel_requested never fires

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        self._goal_running = True

        feedback_msg = GraspPlanning.Feedback()
        feedback_msg.feedback_content = 'feedback_content'
        goal_handle.publish_feedback(feedback_msg)

        goal = goal_handle.request

        DRO_GYM_DIR = '/home/athome/DRO-Gym'
        CONDA_SH = '/home/athome/miniconda3/etc/profile.d/conda.sh'

        start_time = time.time()
        hand_override = f"dataset.robot_names=['{goal.which_hand}']"
        object_override = f"dataset.debug_object_names=['contactdb+{goal.object_name}']"
        handoff_path = os.path.join(DRO_GYM_DIR, 'grasp_candidates_latest.json')
        parser_script = os.path.join(DRO_GYM_DIR, 'grasp_output_parser.py')

        shell_cmd = (
            f'source {CONDA_SH} && conda activate dro && '
            f'export LD_LIBRARY_PATH="/home/athome/miniconda3/envs/dro/lib:$LD_LIBRARY_PATH" && '
            f'python {goal.script_path} {hand_override} {object_override} && '
            f'python {parser_script} '
            f'--robot_name {goal.which_hand} '
            f'--dro_gym_dir {DRO_GYM_DIR} '
            f'--output {handoff_path} '
            f'--since {start_time}'
        )
        cmd = ['bash', '-c', shell_cmd]

        dro_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, cwd=DRO_GYM_DIR,
            start_new_session=True,  # own process group, so we can kill the whole tree
        )


        feedback_msg = GraspPlanning.Feedback()
        for line in dro_process.stdout:
            if goal_handle.is_cancel_requested:
                os.killpg(os.getpgid(dro_process.pid), signal.SIGTERM)
                try:
                    dro_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(dro_process.pid), signal.SIGKILL)
                    dro_process.wait()
                self._goal_running = False
                result = GraspPlanning.Result()
                result.result_content = 'cancelled'
                goal_handle.canceled()
                return result

            feedback_msg.feedback_content = line.strip()
            goal_handle.publish_feedback(feedback_msg)

        dro_process.wait()
        self._goal_running = False
        result = GraspPlanning.Result()

        #cuRobo starten
        # VENV_PATH = 'home/athome/curobo/.venv/bin/python'
        # cuRobo_skript_path = 'curobo.curobo.examples.getting_started.motion_planning'

        # shell_cmd = (
        #     f'source {VENV_PATH} && '
        #     f'python -m {cuRobo_skript_path} && '
        # )
        # cmd = ['bash', '-c', shell_cmd]

        # cuRobo_process = subprocess.Popen(
        #     cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        #     text=True, bufsize=1, cwd=DRO_GYM_DIR,
        #     start_new_session=True,  # own process group, so we can kill the whole tree
        # )

        # feedback_msg = GraspPlanning.Feedback()
        # for line in cuRobo_process.stdout:
        #     if goal_handle.is_cancel_requested:
        #         os.killpg(os.getpgid(cuRobo_process.pid), signal.SIGTERM)
        #         try:
        #             cuRobo_process.wait(timeout=5)
        #         except subprocess.TimeoutExpired:
        #             os.killpg(os.getpgid(cuRobo_process.pid), signal.SIGKILL)
        #             cuRobo_process.wait()
        #         self._goal_running = False
        #         result = GraspPlanning.Result()
        #         result.result_content = 'cancelled'
        #         goal_handle.canceled()
        #         return result

        #     feedback_msg.feedback_content = line.strip()
        #     goal_handle.publish_feedback(feedback_msg)

        # cuRobo_process.wait()
        # self._goal_running = False
        # result = GraspPlanning.Result()

        # if process.returncode == 0:
        #     with open(handoff_path) as f:
        #         grasp_data = json.load(f)
        #     result.result_content = (
        #         f"success: {grasp_data['num_candidates']} grasp candidates "
        #         f"written to {handoff_path}"
        #     )
        #     goal_handle.succeed()
        # else:
        #     result.result_content = f'script exited with code {process.returncode}'
        #     goal_handle.abort()

        return result


def main(args=None):
    rclpy.init(args=args)
    node = GraspPlannerServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()