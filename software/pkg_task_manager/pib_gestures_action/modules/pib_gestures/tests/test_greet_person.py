from pib_gestures.core import greet_person
from pib_gestures.config import gestures

import sys

if __name__ == "__main__":
    pib_side = gestures.pib_side['none']
    pib_gesture = gestures.pib_gesture['wave']
    
    camera_vector_x = -1000.0
    camera_vector_y = 0.0
    camera_vector_z = 0.0
    
    greet_person(camera_vector_x, camera_vector_y, camera_vector_z, pib_side, pib_gesture)
