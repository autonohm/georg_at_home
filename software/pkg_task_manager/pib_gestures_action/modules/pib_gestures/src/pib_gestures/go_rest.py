'''
go rest function for pib
pib moves both arm in resting position simultaniously

pib_mode values:
arms_down: move arms down in resting position
arms_zero: move arms in zero position (calibration pose)
'''

from core.go_rest_core import go_rest as go_rest_core

import argparse
    


def go_rest(
    pib_mode = "none"
):
    """pib moves both arms in resting position"""


    return go_rest_core(pib_mode)
    


def main():
    parser = argparse.ArgumentParser(
        description = "pib moves both arms in resting position"
    )

    parser.add_argument(
        "pib_mode",
        nargs = "?",
        choices = gestures.pib_gesture_modes["go_rest"].keys(),
        default = gestures.pib_gesture_modes["none"],
        metavar = "pib_mode",
        help = "Gesture mode to use",
    )

    args = parser.parse_args()
    print(go_rest(pib_mode))
    
    
    
if __name__ == "__main__":
    main()
