from PIL import Image
import os

input_dir = 'images_download/20210410_3'   # input folder
output_dir = 'images_download/20210410_3_cropped' # output folder

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

left = 1100
upper = 6600
right = left + 2000
lower = upper + 2000
# Define the coordinates of the area you want to crop: (left, upper, right, lower)
crop_area = (left, upper, right, lower)

for filename in os.listdir(input_dir):
    if filename.endswith('.jpg'):  # you can add more file types if needed
        # Open the image file
        img = Image.open(os.path.join(input_dir, filename))
        
        # Crop the image
        cropped_img = img.crop(crop_area)

        # Save the cropped image to the output directory
        cropped_img.save(os.path.join(output_dir, filename))

print("All images have been cropped.")
