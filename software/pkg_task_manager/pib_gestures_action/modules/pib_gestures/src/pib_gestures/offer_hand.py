'''
Offer hand function for pib
Pib moves his left or right arm in front with the grasping side up
'''

from core.offer_hand_core import offer_hand as offer_hand_core
from config import gestures

import argparse
    
def offer_hand(
    pib_side,
    pib_mode
):
    """pib offers his hand at the given side"""

    if pib_side not in gestures.pib_side.keys():
        raise ValueError(f"Invalid pib_side <{pib_side}>")

    if pib_mode not in gestures.pib_gesture_modes['offer_hand'].keys():
        raise ValueError(f"Invalid pib_mode <{pib_mode}> for pib_gesture <offer_hand>")

    return offer_hand_core(pib_side, pib_mode)
    


def main():
    parser = argparse.ArgumentParser(
        description = "pib opens the hand at the given side"
    )
    
    parser.add_argument(
        "pib_side",
        choices = gestures.pib_side.keys(),
        metavar = "pib_side",
        help = "Side for the gesture",
    )

    parser.add_argument(
        "pib_mode",
        choices = gestures.pib_gesture_modes["point_to"].keys(),
        metavar = "pib_mode",
        help = "Gesture mode to use",
    )
    
    args = parser.parse_args()
    print(offer_hand(args.pib_side, args.pib_mode))
    
    
    
if __name__ == "__main__":
    main()
