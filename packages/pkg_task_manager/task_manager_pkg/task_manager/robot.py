from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from std_msgs.msg import Bool
from georg_gesture_msgs.action import PibGesturesInterface, PibPose
from georg_sim_msgs.action import ResetSim
from georg_speech_msgs.action import Listen, Say
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String as StringMsg
from .state import RobotState
from nav_msgs.msg import Odometry

class Georg:

    def __init__(self, node: Node):

        self.node = node

        self.state = RobotState()

        self.taskmanager_current_task_pub = (
            node.create_publisher(
                String,
                "task/current_task",
                10
            )
        )

        # Voice

        self.listen_action_client = ActionClient(
            node,
            Listen,
            "audio/listen"
        )

        # speak (pkg_pib_bridge -> pib-backend /play_audio_from_speech, or the mocks)
        self.say_action_client = ActionClient(
            node,
            Say,
            "speech/say"
        )

        # simulator reset (profile sim, pkg_sim)
        self.reset_sim_action_client = ActionClient(
            node,
            ResetSim,
            "sim/reset"
        )

        # named pib poses (pkg_pib_model fake motors in sim)
        self.pib_pose_action_client = ActionClient(
            node,
            PibPose,
            "pib/pose"
        )

        self.greet_action_client = ActionClient(
            node,
            PibGesturesInterface,
            "pib_gestures_interface"
        )

        # Navigation: Nav2 (pkg_nav2) plans and drives (tasks/nav2_go.py)
        self.nav2_action_client = ActionClient(node, NavigateToPose, "navigate_to_pose")

        # # Vision (Placeholder)

        # self.search_guest_pub = (
        #     node.create_publisher(
        #         Bool,
        #         "vision/search_guest",
        #         10
        #     )
        # )

        # self.search_seat_pub = (
        #     node.create_publisher(
        #         Bool,
        #         "vision/search_seat",
        #         10
        #     )
        # )

        self.odom_sub = node.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )
        



        self.audio_say_pub = node.create_publisher(
            StringMsg,
            "audio/say",
            10
        )

    def odom_callback(self, msg: Odometry):
        self.state.current_position = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
        )

        self.state.current_orientation = msg.pose.pose.orientation
