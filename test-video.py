from ultralytics import YOLO
import numpy as np
import cv2
from ultralytics.yolo.utils.plotting import Annotator
from kalmanfilter import KalmanFilter

kf = KalmanFilter()


model = YOLO(r"C:\Users\kamra\DataspellProjects\yolov8_test\runs\detect\train7\weights\best.pt")
cap = cv2.VideoCapture(r'C:\Users\kamra\Downloads\Video\test3.mp4')
# Create a list to store the boundary box information
bbox_info = []

while True:
    # Read the next frame from the video file
    ret, frame = cap.read()

    # If the frame is not read successfully, break the loop
    if not ret:
        break

    # Convert the frame to a NumPy array
    frame = np.array(frame)

    # Predict the bounding boxes for the objects in the frame
    results = model.predict(frame, conf = 0.61)

    # Loop over the results
    for result in results:
        # Get the bounding box information
        annotator = Annotator(frame)
        bbox = result.boxes
        # Add the bounding box information to the list
        for box in bbox:
            b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
            c = box.cls  # get the class label
            d = b.tolist()
            bbox_info.append(d)
            annotator.box_label(b, model.names[int(c)])

    # Display the frame with the bounding boxes
    frame = annotator.result()
    cv2.imshow("Frame", frame)

    # Wait for a key press
    key = cv2.waitKey(1)

    # If the key press is ESC, break the loop
    if key == 27:
        break

# Close the video file
cap.release()

# Destroy all windows
cv2.destroyAllWindows()
print(bbox_info)

coordinates = []
for i in bbox_info:
    coordinates.append((int((i[0]+i[2])/2), int((i[1]+i[3])/2)))

print(coordinates)

print(len(coordinates))
print(len(bbox_info))

# Create a VideoCapture object and pass the video file name to it.
cap2 = cv2.VideoCapture(r'C:\Users\kamra\Downloads\Video\test3.mp4')

# Read the first frame from the video file using the read() method.
ret, frame = cap2.read()

for pt in coordinates[:110]:
    cv2.circle(frame, pt, 10, (0, 20, 220), -1)
    predicted = kf.predict(pt[0], pt[1])
    cv2.circle(frame, predicted, 10, (20, 220, 0), 4)

print(predicted)

for i in range(15):
    predicted = kf.predict(predicted[0], predicted[1])
    cv2.circle(frame, predicted, 5, (200, 220, 0), 4)

for pt in coordinates[110:]:
    cv2.circle(frame, pt, 5, (0, 0, 0), 4)

# Display the first frame using the imshow() method.
cv2.imshow("First Frame", frame)

# Wait for a key press
cv2.waitKey(0)

# Close the VideoCapture object using the release() method.
cap2.release()