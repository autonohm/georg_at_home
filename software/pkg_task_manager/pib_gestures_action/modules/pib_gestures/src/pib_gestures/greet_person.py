'''
greeting function for pib
pib can greet a person with left or right arm
with different gestures

greeting gesture represents waving or shake hands

vector from center to person is required
greeting vector is calculated by DH matrices 
'''

from core.greet_person_core import greet_person as greet_person_core
from geometry import Object_Vector
from config import gestures

import argparse
    


def greet_person(
    x_value,
    y_value,
    z_value,
    pib_side,
    pib_mode = "none"
):
    """pib greets a person at the given coordinates"""

    if pib_side not in gestures.pib_side.keys():
        raise ValueError(f"Invalid pib_side: {pib_side}")

    if pib_mode not in gestures.pib_gesture_modes['greet_person'].keys():
        raise ValueError(f"Invalid pib_mode <{pib_mode}> for pib_gesture <greet_person>")
        
    object_vector_center = Object_Vector.create_object_vector(
        "vector from center to object",
        (float(x_value), float(y_value), float(z_value)),
    )

    return greet_person_core(object_vector_center, pib_side, pib_mode)
    
    

def main():
    parser = argparse.ArgumentParser(
        description = "pib greets person at the given coordinates"
    )

    parser.add_argument("x", type = float, help = "X coordinate of the person")
    parser.add_argument("y", type = float, help = "Y coordinate of the person")
    parser.add_argument("z", type = float, help = "Z coordinate of the person")

    parser.add_argument(
        "pib_side",
        choices = gestures.pib_side.keys(),
        metavar = "pib_side",
        help = "Side for the gesture",
    )

    parser.add_argument(
        "pib_mode",
        nargs = "?",
        choices = gestures.pib_gesture_modes["greet_person"].keys(),
        default = gestures.pib_gesture_modes["none"],
        metavar = "pib_mode",
        help = "Gesture mode to use",
    )

    args = parser.parse_args()
    print(greet_person(args.x, args.y, args.z, args.pib_side, args.pib_mode))
    
    
    
if __name__ == "__main__":
    main()
