import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep
import json

# --- MODIFICATION START ---

# 1. Load environment variables from .env file
load_dotenv()

# 2. Set API URL and get the key using standard os.getenv
#    IMPORTANT: Make sure your .env file has a key named HuggingFaceAPIKey
API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
api_key = os.getenv("HuggingFaceAPIKey")
headers = {"Authorization": f"Bearer {api_key}"}

# 3. Ensure the Data and Frontend folders exist for robust execution
os.makedirs("Data", exist_ok=True)
os.makedirs(r"Frontend\Files", exist_ok=True)
# Create the data file if it doesn't exist to prevent errors on first run
if not os.path.exists(r"Frontend\Files\ImageGeneration.data"):
    with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
        f.write("False, False")

def open_images(prompt):
    """Opens the four generated images."""
    folder_path = "Data"
    # Replace invalid characters for filenames
    safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()
    files = [f"{safe_prompt.replace(' ', '_')}_{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        # Use os.path.join for cross-platform compatibility
        image_path = os.path.join(folder_path, jpg_file)
        try:
            with Image.open(image_path) as img:
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1) # Give time for the image viewer to open
        except IOError:
            print(f"Error: Unable to open {image_path}. File may be missing or corrupt.")

async def query_api(payload):
    """Sends a single request to the Hugging Face API."""
    try:
        # Use asyncio.to_thread for blocking I/O calls
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)
        return response
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None

async def generate_images(prompt: str):
    """Generates 4 images concurrently based on the prompt."""
    print(f"Starting generation for prompt: '{prompt}'")
    tasks = []
    for _ in range(4):
        # The API uses a random seed by default if not provided, which is what we want.
        # Adding seed to the prompt string doesn't work for this API.
        payload = {"inputs": f"{prompt}, 4k, ultra high resolution"}
        # Create a separate task for each API call
        task = asyncio.create_task(query_api(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    # Process responses
    for i, response in enumerate(responses):
        if response is None:
            print(f"Image {i+1} failed due to a request error.")
            continue

        # 4. Correctly handle the API response
        content_type = response.headers.get('Content-Type')
        if 'application/json' in content_type:
            # This is an error from the API (e.g., model loading)
            error_data = response.json()
            print(f"API Error for image {i+1}: {error_data.get('error', 'Unknown JSON error')}")
        elif 'image/jpeg' in content_type:
            # This is a successful image response
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()
            filename = os.path.join("Data", f"{safe_prompt.replace(' ', '_')}_{i + 1}.jpg")
            try:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Successfully saved {filename}")
            except IOError as e:
                print(f"Error saving image {i+1}: {e}")
        else:
            print(f"Unexpected content type for image {i+1}: {content_type}")


def run_image_generation(prompt: str):
    """Main function to run the async generation and open images."""
    if not api_key:
        print("FATAL ERROR: 'HuggingFaceAPIKey' not found in .env file.")
        print("Please add 'HuggingFaceAPIKey=your_actual_key' to the .env file.")
        return

    asyncio.run(generate_images(prompt))
    print("Image generation process complete. Opening images...")
    open_images(prompt)

# Main execution loop to watch the file
print("Image Generation script is running and watching for requests...")
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read()

        prompt, status = data.split(",", 1) # Split only on the first comma
        status = status.strip()

        if status.lower() == "true":
            print("Request received. Starting generation...")
            run_image_generation(prompt=prompt)

            # Reset the file to prevent re-triggering
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
            print("Generation finished. Idling...")
    
    # 5. Use specific exceptions
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: Issue reading ImageGeneration.data file ({e}). Retrying...")
        # If file is malformed, reset it.
        with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
            f.write("False, False")
    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")

    sleep(2) # Check the file every 2 seconds

# --- MODIFICATION END ---