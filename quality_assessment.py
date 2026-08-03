import cv2
import numpy as np

from utils import to_grayscale


def check_blur(image_bgr, threshold=10.0):
    """
    Check if the image is blurry using the variance of the Laplacian method.
    
    Args:
        image_bgr (numpy.ndarray): input image in BGR format.
        threshold (float): minimum acceptable blur score.

    Returns: dict
    """

    gray = to_grayscale(image_bgr)

    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return {
        "blur_score": round(float(blur_score), 2),
        "is_blurry": bool(blur_score < threshold)
    }

def check_brightness(image_bgr, dark_threshold=50, bright_threshold=200):
    """
    Checks if the image is too dark or too bright based on the average grayscale intensity.
    """
    gray = to_grayscale(image_bgr)

    brightness = gray.mean()

    return {
        "brightness": round(float(brightness), 2),
        "is_too_dark": bool(brightness < dark_threshold),
        "is_too_bright": bool(brightness > bright_threshold)
    }

def check_glare(image_bgr, glare_threshold=240, max_glare_fraction=0.05):
    """
    Detects glare by measuring the fraction of pixel that are overexposed
    Args:
        image_bgr: Input bgr image
        glare_threshold: Pixel values considered above this are considered glare.
        max_glare_fraction: Maximum acceptable glare percentage.
    """

    gray = to_grayscale(image_bgr)

    glare_pixels = np.sum(gray > glare_threshold)
    total_pixels = gray.size
    glare_fraction = glare_pixels / total_pixels

    return {
        "glare_fraction": round(float(glare_fraction), 4),
        "has_glare": bool(glare_fraction > max_glare_fraction)
    }

def check_roi_completeness(image_bgr, threshold=100, min_roi_fraction=0.15):

    gray = to_grayscale(image_bgr)

    _, mask = cv2.threshold(
        gray,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    finger_pixels = np.sum(mask == 255)
    total_pixels = gray.size
    roi_fraction = finger_pixels / total_pixels

    return {
        "roi_fraction": round(float(roi_fraction), 4),
        "roi_complete": bool(roi_fraction > min_roi_fraction)
    }

def check_ridge_quality(image_bgr, threshold=100.0):
    """
    Evaluate fingerprint ridge quality using the Gabor filter method.
    """

    gray = to_grayscale(image_bgr)

    kernel = cv2.getGaborKernel(
        ksize = (21, 21),
        sigma = 5,
        theta = 0,
        lambd = 10,
        gamma = 0.5,
        psi = 0,
        ktype = cv2.CV_32F
    )

    filtered = cv2.filter2D(gray, cv2.CV_32F, kernel)
    ridge_score = filtered.var()

    return {
        "ridge_score": round(float(ridge_score), 2),
        "ridges_clear": bool(ridge_score > threshold)
    }

#Normalization of the values

def normalize_blur(blur_score):
    """
    Normalize the blur score to a range [0, 1]
    """

    return min(blur_score / 100.0, 1.0)

def normalize_brightness(brightness):
    """
    Best brightness is around the middle of the grayscale range
    """
    score = 1 - abs(brightness - 128) / 128
    return max(0.0, min(score, 1.0))

def normalize_glare(glare_fraction):
    """
    Lower glare is better
    """
    return max(0.0, 1 - min(glare_fraction / 0.05, 1))

def normalize_roi(roi_fraction):
    """
    ROI is already between 0 and 1
    """
    return min(roi_fraction / 0.40, 1.0)

def normalize_ridge(ridge_score):
    """
    Normalize ridge score

    This constant is emperical and can be caliberated later.
    """

    return min(ridge_score / 15000.0, 1.0)

#Composite Score Function

def calculate_composite_score(blur, brightness, glare, roi, ridge):
    """
    Combine all the normalized scores into a value between 0 and 100.
    """

    blur_score = normalize_blur(blur["blur_score"])
    brightness_score = normalize_brightness(brightness["brightness"])
    glare_score = normalize_glare(glare["glare_fraction"])
    roi_score = normalize_roi(roi["roi_fraction"])
    ridge_score = normalize_ridge(ridge["ridge_score"])

    composite = (
        blur_score * 0.30 + brightness_score * 0.10 + glare_score * 0.10 + roi_score * 0.20 + ridge_score * 0.30
    ) * 100

    return round(composite, 2)

def generate_guidance(blur, brightness, glare, roi, ridge):
    """
    Generate guidance based on the quality assessment results.
    """

    guidance = []

    if blur["is_blurry"]:
        guidance.append("The image is blurry. Hold your phone steady.")

    if brightness["is_too_dark"]:
        guidance.append("The image is too dark. Increase lighting.")

    if brightness["is_too_bright"]:
        guidance.append("The image is too bright. Reduce lighting.")

    if glare["has_glare"]:
        guidance.append("Reduce the glare by changing the camera angle.")

    if not roi["roi_complete"]:
        guidance.append("Move your finger closer to the camera.")

    if not ridge["ridges_clear"]:
        guidance.append("Fingerprint ridges are unclear.")

    if guidance:
        return " ".join(guidance)

    return "Good capture - ready for processing." 

#Quality Gate function

def quality_gate(
    image_path,
    blur_threshold=10,
    dark_threshold=50,
    bright_threshold=200,
    glare_threshold=240,
    roi_threshold=0.15,
    ridge_threshold=100
):

    #Run all quality check on the image.

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    blur = check_blur(image, threshold=blur_threshold)
    brightness = check_brightness(image, dark_threshold=dark_threshold, bright_threshold=bright_threshold)
    glare = check_glare(image, glare_threshold=glare_threshold)
    roi = check_roi_completeness(image, min_roi_fraction=roi_threshold)
    ridge = check_ridge_quality(image, threshold=ridge_threshold)
    composite_score = calculate_composite_score(blur, brightness, glare, roi, ridge)

    passed = composite_score >= 60

    guidance = generate_guidance(blur, brightness, glare, roi, ridge)

    return {
        "passed": passed,
        "composite_score": composite_score,
        "blur": blur,
        "brightness": brightness,
        "glare": glare,
        "roi": roi,
        "ridge": ridge,
        "guidance": guidance
    }
