from pyproj import Proj, transform
import numpy as np
from scipy.optimize import curve_fit

# Define the projection
p1 = Proj(proj='latlong', datum='WGS84')
p2 = Proj('+proj=geos +lon_0=140.7 +h=35785831.0 +x_0=0 +y_0=0 +a=6378169.0 +b=6356583.8 +units=m +no_defs')

# Define the calibration points
latlon_points = [(-11.9, 92.6), (-14, 117.5), (-14.7, 153.6)]
pixel_points = [(1122, 6696), (3040, 6977), (6816, 7025)]

# Convert lat/lon to projected coordinates
proj_points = [transform(p1, p2, lon, lat) for lat, lon in latlon_points]

# Define the transformation functions
def func_x(x, a, b):
    return a * x + b
def func_y(y, a, b):
    return a * y + b

# Determine the parameters for the transformation functions
params_x, _ = curve_fit(func_x, [point[0] for point in proj_points], [point[0] for point in pixel_points])
params_y, _ = curve_fit(func_y, [point[1] for point in proj_points], [point[1] for point in pixel_points])

# Now you can use these transformation functions to convert any lat/lon to pixel coordinates
def latlon_to_pixel(lat, lon):
    x, y = transform(p1, p2, lon, lat)
    return func_x(x, *params_x), func_y(y, *params_y)


# cropping the image
cropped_image = image.crop((latlon_to_pixel(lat, lon)[0]-1000, latlon_to_pixel(lat, lon)[1]-1000, latlon_to_pixel(lat, lon)[0]+1000, latlon_to_pixel(lat, lon)[1]+1000))
cropped_image.save(f'{target_dir_cropped}/image_{index}.jpg')

print(latlon_to_pixel(-14, 117.5))