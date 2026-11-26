'''
Open hand function for pib
pib opens whether the left or right hand
'''

from core.open_hand_core import open_hand as open_hand_core
from config import gestures

import argparse
    
def open_hand(
    pib_side
):
    """pib opens the hand at the given side"""

    if pib_side not in gestures.pib_side.keys():
        raise ValueError(f"Invalid pib_side <{pib_side}>")
    
    return open_hand_core(pib_side)
    


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
    
    args = parser.parse_args()
    print(open_hand(args.pib_side))
    
    
    
if __name__ == "__main__":
    main()
