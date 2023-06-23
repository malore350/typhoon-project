import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.image as mpimg

from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000  # Disable DecompressionBombError

def convert_globe_to_map(input_image_path, output_image_path):
    # Load the input image
    img = mpimg.imread(input_image_path)

    # Calculate the dpi
    height, width, _ = img.shape
    dpi = 100.  # Default dpi. It will be adjusted later.
    figsize = width / dpi, height / dpi

    # Create a figure with the calculated figure size
    fig = plt.figure(figsize=figsize)

    # Adjust the dpi to the real dpi
    dpi = fig.get_dpi()
    fig.set_size_inches(width / dpi, height / dpi)

    # Create a GeoAxes in the tile's projection
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Make the map global
    ax.set_global()

    # Show the loaded image in the map with extents
    ax.imshow(img, origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])

    # Save the output image at the original resolution
    plt.savefig(output_image_path, dpi=dpi)

# Usage
convert_globe_to_map(r"runs\detect\predict24\image_0.jpg", r'C:\Users\kamra\DataspellProjects\yolov8_test\output.jpg')