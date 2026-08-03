import cv2

def to_grayscale(image_bgr):
    """
    Convert a BGR image to grayscale.
    """

    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)