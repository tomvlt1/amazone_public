import ee
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import time
import os
import datetime

def authenticate_earth_engine():
    """
    Authenticate and initialize Earth Engine.
    """
    try:
        print("Authenticating Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project='bubbly-dynamo-443909-a5')  # Use your working project ID
        print("Earth Engine initialized successfully!")
    except Exception as e:
        print(f"Error during Earth Engine authentication: {e}")
        raise

def load_selected_area():
    """
    Load the selected area from the JSON file.
    Returns:
        dict: The selected area details or None if the file is missing or invalid.
    """
    try:
        with open("selected_area.json", "r") as f:
            data = json.load(f)
            print(f"Loaded selected area: {data}")
            return data
    except FileNotFoundError:
        print("Error: 'selected_area.json' not found. Please run ZoneSelect.py first.")
        return None
    except json.JSONDecodeError:
        print("Error: 'selected_area.json' is not valid JSON.")
        return None

import datetime

def get_image_for_current_date(geometry):
    """
    Fetch a single image for the current date or a nearby time range.
    """
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=30)  # 30 days before today
    end_date = today + datetime.timedelta(days=30)    # 30 days after today

    # Convert dates to strings in YYYY-MM-DD format
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    
    image_collection = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
        .filterDate(start_date_str, end_date_str) \
        .filterBounds(geometry) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)) \
        .select(['B4', 'B3', 'B2'])  # Red, Green, Blue bands

    
    num_images = image_collection.size().getInfo()
    print(f"Found {num_images} images for the selected dates: {start_date_str} to {end_date_str}")

    if num_images == 0:
        raise Exception(f"No images found for the selected dates: {start_date_str} to {end_date_str}")

    
    return image_collection.median()



def export_image_and_download(image, geometry, filename):
    """
    Exports the image to Google Drive and downloads it automatically.
    """
    base_name = os.path.basename(filename).replace(".tif", "")

    
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=base_name,
        folder='Deforestation',
        fileNamePrefix=base_name,
        scale=10,
        region=geometry.bounds().getInfo()['coordinates']
    )
    task.start()
    print(f"Export task for {base_name} started. Waiting for completion...")

    
    while task.active():
        print("Waiting for export to complete...")
        time.sleep(20)  

    task_status = task.status()
    if task_status['state'] != 'COMPLETED':
        raise Exception(f"Export failed: {task_status}")

    print(f"Export completed. Downloading {base_name} from Google Drive...")

    
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        
        gauth.Refresh()
    else:
        
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)

    
    query = f"title contains '{base_name}' and mimeType='image/tiff'"
    file_list = drive.ListFile({'q': query}).GetList()
    if not file_list:
        raise Exception(f"File {base_name}.tif not found in Google Drive.")

    
    drive_file = file_list[0]
    drive_file.GetContentFile(filename)
    print(f"Downloaded {filename} successfully.")
