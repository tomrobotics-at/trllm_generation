import base64
import requests
import json
import os
import time
import random
import pdb
import argparse

# Your API key. Replace "YOUR_API_KEY" with your actual key.
# You can get a key from Google AI Studio at https://aistudio.google.com/app/apikey
# It's recommended to store this in an environment variable for security.
API_KEY = "AIzaSyCA2t4H6VPWgK1Q27MASExuhZP_xBRFRjs"

# API_KEY = os.environ.get("API_KEY")
# if API_KEY:
#     # Use the API key
#     print("API Key loaded successfully!")
# else:
#     print("API Key not found.")

# pdb.set_trace()
# The Gemini model for image generation and editing
MODEL_ID = "gemini-2.5-flash-image-preview"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

def encode_image_to_base64(image_path):
    """
    Encodes a local image file to a base64 string.
    This is required for sending the image data to the API.
    """
    if not os.path.exists(image_path):
        print(f"Error: The image file '{image_path}' was not found.")
        return None
    
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

def edit_image_with_gemini(image_path, prompt_text, output_path="edited_image.jpg"):
    """
    Sends an image and a text prompt to the Gemini API for editing.

    Args:
        image_path (str): The local path to the image to be edited.
        prompt_text (str): The text prompt describing the desired edit.
        output_path (str): The path to save the edited image.
    """
    print("Preparing image and prompt for the API...")

    # Encode the image to base64
    image_base64 = encode_image_to_base64(image_path)
    if not image_base64:
        return

    # Create the payload for the API request
    payload = {
        "contents": [{
            "parts": [
                {
                    "text": prompt_text
                },
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",  # Using jpeg to match the .jpg file extension
                        "data": image_base64
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 0.1
        }
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    # Retry logic with exponential backoff
    retries = 0
    max_retries = 5
    wait_time = 10  # Initial wait time in seconds

    while retries < max_retries:
        print(f"Attempting to send request... (Attempt {retries + 1}/{max_retries})")
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for bad status codes
            
            result = response.json()
            
            # Extract the edited image data
            edited_image_data = None
            for candidate in result.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        edited_image_data = part["inlineData"]["data"]
                        break
                if edited_image_data:
                    break
            
            if edited_image_data:
                print("Successfully received edited image data. Decoding and saving...")
                # Decode the base64 data and save the image
                decoded_image = base64.b64decode(edited_image_data)
                with open(output_path, "wb") as f:
                    f.write(decoded_image)
                print(f"Edited image saved successfully to '{output_path}'")
                return  # Exit the function on success
            else:
                print("No image data found in the API response.")
                print(json.dumps(result, indent=2))
                return 
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retries += 1
                print(f"HTTP Error 429: Quota exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return
            
    print(f"Failed to get a successful response after {max_retries} attempts. Please try again later or check your quota.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate images with pedestrians and bicycles using Gemini API")
    parser.add_argument("--input_image", "-i", type=str, default="background_images/CAM1.png", 
                        help="Path to the input image (default: background_images/CAM1.png)")
    parser.add_argument("--dest_folder", "-d", type=str, 
                        default="output/CAM1_ped_bic_new_prompt/images",
                        help="Destination folder for generated images")
    parser.add_argument("--num_images", "-n", type=int, default=200,
                        help="Number of images to generate (default: 200)")

    args = parser.parse_args()
    
    # --- Configuration ---
    input_image_path = args.input_image
    dest_folder = args.dest_folder
    num_images_to_generate = args.num_images

    # Base name for output files
    base_output_name = "generated_CAM3_pedestrian_bicycle"
    output_extension = ".png"

    print(f"Starting to generate {num_images_to_generate} images...")
    print(f"Input image: {input_image_path}")
    print(f"Destination folder: {dest_folder}")

    # Destination folder for generated images
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for i in range(num_images_to_generate):
        # Create more balanced dataset by focusing on underrepresented classes
        # Current distribution: Car: 72.07%, Pedestrian: 15.5%, Truck: 3.18%, Bicycle: 4.57%, Motorcycle: 2.45%, Bus: 2.23%
        
        # Generate different scenarios to balance the dataset
        scenario = random.choice([
            "bicycle_heavy",     # 30% of images - boost bicycles significantly
            "pedestrian_heavy",  # 25% of images - boost pedestrians
            "truck_bus_heavy",   # 20% of images - boost trucks and buses
            "motorcycle_heavy",  # 15% of images - boost motorcycles
            "mixed_balanced"     # 10% of images - mixed with minimal cars
        ])
        
        if scenario == "bicycle_heavy":
            num_bicycles = random.randint(8, 15)
            num_pedestrians = random.randint(3, 6)
            num_trucks = random.randint(1, 3)
            num_buses = random.randint(0, 2)
            num_motorcycles = random.randint(1, 3)
            num_cars = random.randint(0, 2)  # Minimal cars
            
        elif scenario == "pedestrian_heavy":
            num_pedestrians = random.randint(10, 18)
            num_bicycles = random.randint(2, 5)
            num_trucks = random.randint(1, 2)
            num_buses = random.randint(0, 1)
            num_motorcycles = random.randint(1, 2)
            num_cars = random.randint(0, 3)  # Minimal cars
            
        elif scenario == "truck_bus_heavy":
            num_trucks = random.randint(4, 8)
            num_buses = random.randint(2, 5)
            num_pedestrians = random.randint(3, 7)
            num_bicycles = random.randint(2, 4)
            num_motorcycles = random.randint(1, 3)
            num_cars = random.randint(0, 2)  # Minimal cars
            
        elif scenario == "motorcycle_heavy":
            num_motorcycles = random.randint(6, 12)
            num_pedestrians = random.randint(4, 8)
            num_bicycles = random.randint(2, 5)
            num_trucks = random.randint(1, 3)
            num_buses = random.randint(0, 2)
            num_cars = random.randint(0, 3)  # Minimal cars
            
        else:  # mixed_balanced
            num_pedestrians = random.randint(6, 10)
            num_bicycles = random.randint(4, 7)
            num_trucks = random.randint(2, 4)
            num_buses = random.randint(1, 3)
            num_motorcycles = random.randint(3, 6)
            num_cars = random.randint(1, 4)  # Still minimal cars
        
        editing_prompt = (
            f"I have an imbalanced dataset and need to create a more balanced distribution of objects. "
            f"Please add the following objects to this street scene: "
            f"{num_pedestrians} pedestrians, {num_bicycles} bicycles, {num_trucks} trucks, "
            f"{num_buses} buses, {num_motorcycles} motorcycles, and {num_cars} cars. "
            f"Ensure all objects are proportionate to the scene and blend naturally with the environment. "
            f"Guidelines: "
            f"- Pedestrians should be on sidewalks, crosswalks, or designated walking areas "
            f"- Bicycles should be in bike lanes, on roads, or bike paths with riders wearing helmets "
            f"- Trucks and buses should be appropriately sized and positioned on roads "
            f"- Motorcycles should be on roads with riders wearing helmets "
            f"- Cars should be standard passenger vehicles on roads "
            f"- Maintain realistic perspective with distant objects appearing smaller "
            f"- Create a natural, realistic traffic scene with proper spacing between objects "
            f"- Vary the poses, orientations, and positions of objects for diversity"
        )

        rand_num = random.randint(1000, 9999)
        current_output_path = f"{base_output_name}_{scenario}_{i+1}_{rand_num}{output_extension}"
        print(f"\n--- Generating image {i+1}/{num_images_to_generate} (Scenario: {scenario}) ---")
        print(f"Objects: {num_pedestrians} pedestrians, {num_bicycles} bicycles, {num_trucks} trucks, {num_buses} buses, {num_motorcycles} motorcycles, {num_cars} cars")
        print(f"Output path for this image: {current_output_path}")

        edit_image_with_gemini(input_image_path, editing_prompt, current_output_path)

        # Move the generated image to the destination folder
        dest_path = os.path.join(dest_folder, os.path.basename(current_output_path))
        try:
            os.rename(current_output_path, dest_path)
            print(f"Moved generated image to {dest_path}")
        except Exception as e:
            print(f"Failed to move image: {e}")

        # Add a small delay between requests to be kinder to rate limits
        if i < num_images_to_generate - 1:
            time.sleep(2)
    
    print("\nFinished generating images!")



