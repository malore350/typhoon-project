from ultralytics import YOLO

model = YOLO(r"C:\Users\kamra\DataspellProjects\yolov8_test\himawara.pt")

model.predict(r"C:\Users\kamra\DataspellProjects\yolov8_test\images_download\20210410_3_cropped", imgsz = 2000, save=True)