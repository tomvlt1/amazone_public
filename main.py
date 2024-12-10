import os
import json
import ee
from PIL import Image, ImageOps
import numpy as np
import rasterio
from keras.layers import TFSMLayer
from GetImages import authenticate_earth_engine, load_selected_area, get_image_for_current_date, export_image_and_download

# Paths and constants
LOCAL_IMAGE_FOLDER = "Deforestation_Local"
CURRENT_IMAGE = os.path.join(LOCAL_IMAGE_FOLDER, "current_image.tif")
MODEL_PATH = "model.savedmodel"
LABELS_PATH = "labels.txt"

# Ensure local folder exists
os.makedirs(LOCAL_IMAGE_FOLDER, exist_ok=True)

# Load model as a TFSMLayer
model_layer = TFSMLayer(MODEL_PATH, call_endpoint="serving_default")

# Load class labels
with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f]

def preprocess_image(image_path):
    """
    Preprocesses a GeoTIFF image for the model.
    """
    with rasterio.open(image_path) as src:
        # Read Red, Green, Blue bands
        array = src.read([1, 2, 3])  # Bands 1, 2, 3 correspond to B4, B3, B2
    array = array / np.max(array)  # Normalize values to [0, 1]

    # Transpose from (bands, rows, cols) to (rows, cols, bands)
    array = np.transpose(array, (1, 2, 0))

    # Convert to RGB image
    image = Image.fromarray((array * 255).astype(np.uint8)).convert("RGB")

    # Resize to 224x224
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)

    # Normalize to [-1, 1]
    image_array = np.asarray(image).astype(np.float32) / 127.5 - 1

    return np.expand_dims(image_array, axis=0)


import matplotlib.pyplot as plt

def predict(image_path):
    """
    Predicts the forestation level for a given image.
    """
    processed_image = preprocess_image(image_path)

    # Save the processed image
    processed_img_array = ((processed_image[0] + 1) * 127.5).astype(np.uint8)  # Scale [-1, 1] to [0, 255]
    processed_img = Image.fromarray(processed_img_array)
    processed_image_path = os.path.join(LOCAL_IMAGE_FOLDER, "processed_image.jpg")
    processed_img.save(processed_image_path)

    # Visualize the processed image for debugging
    print("Processed image saved. Visualizing...")
    plt.imshow(processed_img_array)
    plt.title("Processed Image")
    plt.axis("off")
    plt.show()

    # Get predictions
    predictions = model_layer(processed_image)

    # Extract the actual tensor from the predictions dictionary
    predictions_tensor = predictions['sequential_7']  # Adjust key if needed
    predictions_array = predictions_tensor.numpy()  # Convert to NumPy array

    # Debug: Check extracted tensor
    print(f"Predictions Array: {predictions_array}")

    # Get the predicted index and confidence
    predicted_index = np.argmax(predictions_array[0])  # Index of max confidence
    confidence = predictions_array[0][predicted_index]  # Max confidence value

    # Get the corresponding label
    label = labels[predicted_index]

    # Return the predicted label and confidence
    return label, confidence


def main():
    # Step 1: Authenticate Earth Engine
    print("\nStep 1: Authenticating Earth Engine...\n")
    authenticate_earth_engine()

    # Step 2: Load the selected area
    print("\nStep 2: Loading selected area...\n")
    selected_area = load_selected_area()
    if not selected_area:
        print("Error: No selected area found. Run ZoneSelect.py first.")
        return

    # Extract center and radius
    center_lon = selected_area["center"]["lon"]
    center_lat = selected_area["center"]["lat"]
    radius = selected_area["radius"]
    geometry = ee.Geometry.Point([center_lon, center_lat]).buffer(radius)

    # Step 3: Fetch and download the current image
    print("\nStep 3: Exporting and downloading the image...\n")
    current_image = get_image_for_current_date(geometry)
    export_image_and_download(current_image, geometry, CURRENT_IMAGE)
    print(f"Image downloaded to {CURRENT_IMAGE}.")

    # Step 4: Analyze the image
    print("\nStep 4: Loading and analyzing the image...\n")
    label, confidence = predict(CURRENT_IMAGE)

    # Enhanced print statement
    print(f"Prediction: {label} with confidence {confidence:.2%}")

if __name__ == "__main__":
    main()
