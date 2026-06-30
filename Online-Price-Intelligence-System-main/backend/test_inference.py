import requests
from PIL import Image
import io

BASE_URL = "http://localhost:8001/api/predict"
TEST_IMAGE_PATH = "test_inference.jpg"

def create_dummy_image(path):
    # Create a simple image (red square)
    img = Image.new('RGB', (224, 224), color = 'red')
    img.save(path)

def test_inference():
    print(f"Testing inference at {BASE_URL}...")
    create_dummy_image(TEST_IMAGE_PATH)
    
    try:
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": (TEST_IMAGE_PATH, f, "image/jpeg")}
            response = requests.post(BASE_URL, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("Success! Prediction results:")
            print(data)
        else:
            print(f"Failed. Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_inference()
