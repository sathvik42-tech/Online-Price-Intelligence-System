from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import io
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocesses the uploaded image bytes for EfficientNetB0.
    Steps:
    1. Open image from bytes.
    2. Convert to RGB.
    3. Resize to 224x224 (LANCZOS).
    4. Convert to array and expand dimensions.
    5. Preprocess input (EfficientNet specific scaling).
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB to ensure 3 channels
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # --- LETTERBOX RESIZING (Preserve Aspect Ratio) ---
        target_size = (224, 224)
        image.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create a new white background image
        new_image = Image.new("RGB", target_size, (255, 255, 255))
        # Paste the thumbnail onto the center
        paste_pos = ((target_size[0] - image.size[0]) // 2, (target_size[1] - image.size[1]) // 2)
        new_image.paste(image, paste_pos)
        
        # Convert to array
        img_array = img_to_array(new_image)
        
        # Expand dimensions to match model input shape (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess input (EfficientNet specific scaling)
        processed_image = preprocess_input(img_array)
        
        return processed_image
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

