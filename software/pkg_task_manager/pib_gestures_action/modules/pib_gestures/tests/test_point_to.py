from pib_gestures.core import point_to
from pib_gestures.config import gestures

import sys

if __name__ == "__main__":
    pib_side = gestures.pib_side['right']
    pib_gesture = gestures.pib_gesture['none']
    pib_hand = gestures.pib_hand['index_finger']
    
    camera_vector_x = -1000.0
    camera_vector_y = 0.0
    camera_vector_z = 500.0
    
    point_to(camera_vector_x, camera_vector_y, camera_vector_z, pib_side, pib_gesture, pib_hand)
