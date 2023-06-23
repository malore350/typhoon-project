import cv2
import numpy as np

def create_output_image(width, height):
    return np.zeros((height, width, 3), dtype=np.uint8)

def convert_globe_to_map(image_path, output_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Ensure the image is in RGB

    h, w, _ = img.shape
    output_image = create_output_image(w, h)

    for y in range(h):
        for x in range(w):
            polar_y = (y / float(h)) * np.pi # 0 <= polar_y <= pi
            polar_x = (x / float(w)) * 2 * np.pi # 0 <= polar_x <= 2pi

            # Compute spherical coordinates for the pixel location
            cartesian_y = int(((np.sin(polar_y) * np.cos(polar_x) + 1) / 2) * h)
            cartesian_x = int(((np.sin(polar_y) * np.sin(polar_x) + 1) / 2) * w)

            # Ensure the coordinates are within the bounds of the image
            cartesian_y = max(0, min(cartesian_y, h - 1))
            cartesian_x = max(0, min(cartesian_x, w - 1))

            # Set the output pixel's color to the input pixel's color
            output_image[y, x] = img[cartesian_y, cartesian_x]

    output_image = cv2.cvtColor(output_image, cv2.COLOR_RGB2BGR) # Convert back to BGR for saving
    cv2.imwrite(output_path, output_image)

# Usage
convert_globe_to_map(r"C:\Users\kamra\DataspellProjects\yolov8_test\runs\detect\predict24\image_0.jpg", r'C:\Users\kamra\DataspellProjects\yolov8_test')
