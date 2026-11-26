'''
core functionality of locate object function:

transformation of camera vector into vector from center to object by DH matrices
'''

from pib_gestures.utils import transform

from pathlib import Path

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')
    
def locate_object(object_vector_camera):

    logger.info("started, calculating center vector")
    
    # calculate vector from center to object, considering head joint angles
    object_vector_center = transform.calculate_object_vector_center(object_vector_camera)   
    logger.info("finished\n\n ")
    
    return object_vector_center.x, object_vector_center.y, object_vector_center.z
