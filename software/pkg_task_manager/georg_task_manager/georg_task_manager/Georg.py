from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from std_msgs.msg import Bool
from pib_gestures_action.action import PibGesturesInterface
from datatypes.srv import PlayAudioFromSpeech
from datatypes.srv import StartModel    #Object Detection Models
from datatypes.srv import StopModel     #Object Detection Models
from georg_nav_msgs.action import Navigate, DriveRoute
from std_msgs.msg import String as StringMsg
from .interface import RobotState
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

        self.speak_service_client = node.create_client(
            PlayAudioFromSpeech,
            "/play_audio_from_speech"
        )

        self.audio_say_pub = node.create_publisher(
            StringMsg,
            "audio/say",
            10
        )

        # Navigate

        self.navigate_room_action_client = ActionClient(
            node,
            Navigate,
            "nav/navigate_room_x"
        )

        self.navigate_object_action_client = ActionClient(
            node,
            Navigate,
            "nav/navigate_object_x"
        )

        # Drive 

        self.drive_route_action_client = ActionClient(
            node,
            DriveRoute,
            "nav/drive_route"
        )

        # Vision 
        self.StartModel = node.create_client(
            StartModel,
            "/start_model" 
        )

        self.StopModel = node.create_client(
            StopModel,
            "/stop_model" 
        )
        
        # Odometrie
        self.odom_sub = node.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )
        
        # Gestures
        self.greet_action_client = ActionClient(
            node,
            PibGesturesInterface,
            "pib_gestures_interface"
        )



    def odom_callback(self, msg: Odometry):
        self.state.current_position = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
        )

        self.state.current_orientation = msg.pose.pose.orientation
