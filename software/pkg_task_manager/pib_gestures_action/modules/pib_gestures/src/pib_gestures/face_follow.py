'''
Face follow function for pib
pib moves his head continuously so that a detected face is shifted into the middle of the camera frame
'''

from core.face_follow_core import main as face_follow_core
    
def face_follow():
    """pib looks continuously to a detected face"""

    return face_follow_core("none")
    


def main():
    return face_follow("none")    
    
    
if __name__ == "__main__":
    main()
