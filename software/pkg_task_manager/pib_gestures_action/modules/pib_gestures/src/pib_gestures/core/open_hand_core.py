'''
core functionality of open hand:

all fingers and the thumb are opened simultaneously
thumb opposition is also stretched
'''

from pib_gestures.config import gestures
from pib_gestures.utils import pib_control
from pib_sdk.control import *

from pathlib import Path

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')
    
def open_hand(pib_side):

    logger.info("started, getting hand joint rotation angles")
    q_gesture_hand = gestures.hand_gesture_joint_angles['open_hand']
    
    # using objects from pib sdk
    if pib_side == gestures.pib_side['left']:
        hand_joints = left_hand # left hand from sdk.control
    if pib_side == gestures.pib_side['right']:
        hand_joints = right_hand # right_hand from sdk.control
    
    logger.info("publishing joint angles") 
    # move joints 
    pib_control.move_joints(hand_joints, q_gesture_hand)
    
    logger.info("finished\n\n ")
 
    return 0
