'''
move joints function
to move joint(s), joint name or group name is required
target angle is required
more detailed description on pibrocks github / pib-sdk / branch-978

examples:
pib.move("elbow left", +60.0)
pib.move(left_arm, 0.0)
'''

###from pib_sdk.kinematics import fk, ik
###from pib_sdk.control import *

import logging
logger = logging.getLogger(__name__)

# Control client
###pib = Write()

def set_up_pib():
    logger.debug("setting up pib")
    # Motor settings
    pib.set(All, default = True)
    pib.set(All, acceleration = 1000)
    logger.debug("setting up pib complete")
    
def move_joints(joints, angles):
    pib.move(joints, *angles)
    logger.debug("moving joints: " + str(joints) + " with angles: " + str(angles))
    
    
    
