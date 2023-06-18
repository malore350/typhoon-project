from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

#%%
# Use the model
model.train(data=r"C:\Users\kamra\DataspellProjects\yolov8_test\datasets\typhoon\data.yaml", epochs=100)  # train the model
metrics = model.val()  # evaluate model performance on the validation set
success = model.export(format="onnx")  # export the model to ONNX format
