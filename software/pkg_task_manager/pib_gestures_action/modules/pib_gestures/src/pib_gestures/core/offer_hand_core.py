'''
core functionality of offer hand:

The arm is moved in front with the grasping side up
'''

from pib_gestures.config import gestures
from pib_gestures.utils import pib_control
from pib_sdk.control import *

from pathlib import Path

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')
    
def offer_hand(
    pib_side,
    pib_mode
):

    logger.info("started, getting arm joint rotation angles")
    q_gesture_arm = gestures.arm_gesture_joint_angles["offer_hand"][pib_mode]
    
    # using objects from pib sdk
    if pib_side == gestures.pib_side['left']:
        arm_joints = left_arm # left hand from sdk.control
    if pib_side == gestures.pib_side['right']:
        arm_joints = right_arm # right_hand from sdk.contr
    
    logger.info("publishing joint angles") 
    # move joints 
    pib_control.move_joints(arm_joints, q_gesture_arm)
    
    logger.info("finished\n\n ")
    
    return 0
