'''
pointing function for pib
pib can point to an object with left or right arm
with different gestures

pointing gesture represents straight arm or bent arm

straight arm: arm rotations and elbow form a straight arm,
pointing orientation only by shoulder vertical and horizontal joints

bent_arm: shoulder vertical and horizontal move arm downwards
pointing orientation only by upper arm rotation and elbow

pib hand represents index finger or open hand
open hand used for more polite gesture or closer objects

vector from center to object is required
pointing vector is calculated by DH matrices 
'''

from core.point_to_core import point_to as point_to_core
from geometry import Object_Vector
from config import gestures

import argparse



def point_to(
    x_value,
    y_value,
    z_value,
    pib_side = "none",
    pib_mode = "none",
    pib_hand = "none"
):
    """pib points towards an object at the given coordinates"""

    if pib_side not in gestures.pib_side.keys():
        raise ValueError(f"Invalid pib_side <{pib_side}>")

    if pib_mode not in gestures.pib_gesture_modes['point_to'].keys():
        raise ValueError(f"Invalid pib_mode <{pib_mode}> for pib_gesture <point_to>")

    if pib_hand not in gestures.pib_hand.keys():
        raise ValueError(f"Invalid pib_hand <{pib_hand}>")

    object_vector_center = Object_Vector.create_object_vector(
        "vector from center to object",
        (float(x_value), float(y_value), float(z_value)),
    )
    
    return point_to_core(object_vector_center, pib_side, pib_mode, pib_hand)
    
    
    
def main():
    parser = argparse.ArgumentParser(
        description = "pib points towards an object at the given coordinates"
    )

    parser.add_argument("x", type = float, help = "X coordinate of the object")
    parser.add_argument("y", type = float, help = "Y coordinate of the object")
    parser.add_argument("z", type = float, help = "Z coordinate of the object")

    parser.add_argument(
        "pib_side",
        choices = gestures.pib_side.keys(),
        metavar = "pib_side",
        help = "Side for the gesture",
    )

    parser.add_argument(
        "pib_mode",
        nargs = "?",
        choices = gestures.pib_gesture_modes["point_to"].keys(),
        default = gestures.pib_gesture_modes["none"],
        metavar = "pib_mode",
        help = "Gesture mode to use",
    )

    parser.add_argument(
        "pib_hand",
        nargs = "?",
        choices = gestures.pib_hand.keys(),
        default = gestures.pib_hand["none"],
        metavar = "pib_hand",
        help = "Hand configuration to use",
    )

    args = parser.parse_args()
    print(point_to(args.x, args.y, args.z, args.pib_side, args.pib_mode, args.pib_hand))
    
    
    
if __name__ == "__main__":
    main()
