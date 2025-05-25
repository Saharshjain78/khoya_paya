from PIL import Image
import numpy as np
import cv2

def load_image(image_path):
    """Load an image from the specified path."""
    image = Image.open(image_path)
    return np.array(image)

def resize_image(image, target_size):
    """Resize the image to the target size."""
    return cv2.resize(image, target_size)

def convert_to_grayscale(image):
    """Convert the image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def normalize_image(image):
    """Normalize the image data to the range [0, 1]."""
    return image / 255.0

def preprocess_image(image_path, target_size=(224, 224)):
    """Load, resize, convert to grayscale, and normalize the image."""
    image = load_image(image_path)
    image = resize_image(image, target_size)
    image = convert_to_grayscale(image)
    image = normalize_image(image)
    return image

def save_image(image, output_path):
    """Save the processed image to the specified output path."""
    output_image = Image.fromarray((image * 255).astype(np.uint8))
    output_image.save(output_path)