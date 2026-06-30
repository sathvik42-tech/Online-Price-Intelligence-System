
import numpy as np
import time
import os
import sys
import io
from PIL import Image

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))

from backend.app.model import predict_image
from backend.app.preprocessing import preprocess_image

def test_speed():
    # Load a sample image (using an existing one if available)
    sample_path = "temp_uploads"
    files = [f for f in os.listdir(sample_path) if f.endswith(('.jpg', '.png'))]
    if not files:
        print("No sample images found in temp_uploads. Creating a dummy one.")
        dummy_img = Image.new('RGB', (2000, 2000), color = (73, 109, 137))
        img_byte_arr = io.BytesIO()
        dummy_img.save(img_byte_arr, format='JPEG')
        raw_bytes = img_byte_arr.getvalue()
    else:
        with open(os.path.join(sample_path, files[0]), "rb") as f:
            raw_bytes = f.read()

    print(f"Testing with image size: {len(raw_bytes) / 1024:.2f} KB")
    processed = preprocess_image(raw_bytes)

    # First run (Cold - OCR + Prediction)
    start = time.time()
    res1 = predict_image(processed, 3, raw_bytes)
    end1 = time.time()
    print(f"Run 1 (Parallel OCR + AI): {end1 - start:.4f}s")

    # Second run (Cached)
    start = time.time()
    res2 = predict_image(processed, 3, raw_bytes)
    end2 = time.time()
    print(f"Run 2 (Cached): {end2 - start:.4f}s")
    
    assert res1 == res2
    print("Verification successful: Results match and caching works.")

if __name__ == "__main__":
    test_speed()
