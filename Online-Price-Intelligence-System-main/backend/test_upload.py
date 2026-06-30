import requests
import os
from PIL import Image
import io

BASE_URL = "http://localhost:8001/api/upload-image"
TEST_IMAGE_PATH = "test_image.jpg"
LARGE_IMAGE_PATH = "large_image.jpg"
TEXT_FILE_PATH = "test.txt"

def create_dummy_image(path, size_mb=0.1):
    # Create a simple image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    if size_mb > 1:
        # Create large file by saving and appending bytes? 
        # Easier to just write random bytes for size check if API checks content-length/body size 
        # But API checks len(contents) after reading.
        # So we need actual bytes. 
        # PIL might not support creating arbitrary large valid images easily without memory.
        # For 10MB limit test, we can just create a file with bytes.
        with open(path, "wb") as f:
            f.write(os.urandom(int(size_mb * 1024 * 1024)))
    else:
        img.save(path)

def test_valid_upload():
    print("Testing valid upload...")
    create_dummy_image(TEST_IMAGE_PATH)
    
    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"file": (TEST_IMAGE_PATH, f, "image/jpeg")}
        response = requests.post(BASE_URL, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Response: {data}")
        if "image_id" in data and "filename" in data:
            print("Response structure valid.")
        else:
            print("Response structure invalid.")
            
        # Verify file existence
        # Assuming backend is running locally and mapping 'temp_uploads'
        # precise path depends on where backend is running.
        # We can just trust the API response for now or try to check if we know the path.
    else:
        print(f"Failed. Status: {response.status_code}, Response: {response.text}")

def test_invalid_type():
    print("\nTesting invalid file type...")
    with open(TEXT_FILE_PATH, "w") as f:
        f.write("This is a text file.")
        
    with open(TEXT_FILE_PATH, "rb") as f:
        files = {"file": (TEXT_FILE_PATH, f, "text/plain")}
        response = requests.post(BASE_URL, files=files)
        
    if response.status_code == 400:
        print(f"Success! Got expected 400. Response: {response.text}")
    else:
        print(f"Failed. Expected 400, got {response.status_code}. Response: {response.text}")

def test_large_file():
    print("\nTesting large file (>10MB)...")
    # Create 11MB file
    with open(LARGE_IMAGE_PATH, "wb") as f:
        f.seek(11 * 1024 * 1024)
        f.write(b"\0")
        
    with open(LARGE_IMAGE_PATH, "rb") as f:
        # Send as image to bypass type check? Type check is on content_type header usually, 
        # but our code checks file.content_type.
        files = {"file": (LARGE_IMAGE_PATH, f, "image/jpeg")}
        response = requests.post(BASE_URL, files=files)
        
    if response.status_code == 400:
        print(f"Success! Got expected 400. Response: {response.text}")
    else:
        print(f"Failed. Expected 400, got {response.status_code}. Response: {response.text}")

if __name__ == "__main__":
    try:
        test_valid_upload()
        test_invalid_type()
        test_large_file()
    finally:
        # Cleanup
        if os.path.exists(TEST_IMAGE_PATH): os.remove(TEST_IMAGE_PATH)
        if os.path.exists(TEXT_FILE_PATH): os.remove(TEXT_FILE_PATH)
        if os.path.exists(LARGE_IMAGE_PATH): os.remove(LARGE_IMAGE_PATH)
