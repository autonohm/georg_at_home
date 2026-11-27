'''
core functionality of go rest:

Both arms are moved down in resting position simultaniously
'''

from pib_gestures.config import gestures
from pib_gestures.utils import pib_control
from pib_sdk.control import *

from pathlib import Path

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')
    
def go_rest(
    pib_mode
):

    logger.info("started, getting arm joint rotation angles")
    q_gesture_arm = gestures.arm_gesture_joint_angles["go_rest"][pib_mode]
    
    # using objects from pib sdk
    arm_joints_left = left_arm # left hand from sdk.control
    arm_joints_right = right_arm # right_hand from sdk.control
    
    logger.info("publishing joint angles") 
    # move joints 
    pib_control.move_joints(arm_joints_left, q_gesture_arm)
    pib_control.move_joints(arm_joints_right, q_gesture_arm)

    logger.info("finished\n\n ")
    
    return 0
